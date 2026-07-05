"""Run the MCQ benchmark against a panel of models.

Usage:
    uv run python -m azdim.eval.runner discover          # list provider models
    uv run python -m azdim.eval.runner run <model_key>   # run one panel model
    uv run python -m azdim.eval.runner run --all

Panel is defined in manifest/models.json:
    {"model_key": {"provider": "openrouter", "model": "qwen/qwen3-...",
                   "max_tokens": 512, "notes": ""}}

Eval set: canonical MCQ items with a gold label and no required image.
Raw outputs land in results/raw/<model_key>__<track>.jsonl (resumable).
"""

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from azdim.extract import load_env
from azdim.eval.parse import parse_answer
from azdim.eval.prompts import format_mcq

ROOT = Path(__file__).resolve().parents[2].parent
ITEMS_FILE = ROOT / "data" / "items" / "items_v0.jsonl"
MODELS_FILE = ROOT / "manifest" / "models.json"
RAW_DIR = ROOT / "results" / "raw"

WORKERS = 8


def eval_items(track: str) -> list[dict]:
    items = [json.loads(line) for line in ITEMS_FILE.read_text().splitlines()]
    lang = {"A": "az", "B": "ru"}[track]
    return [it for it in items
            if it["question_type"] == "mcq"
            and it.get("gold_answer_label") in tuple("ABCDE")
            and not it.get("requires_image")
            and it.get("question_language") == lang]


# --- provider adapters ------------------------------------------------------

def _complete_anthropic(model: str, prompt: str, max_tokens: int) -> tuple:
    import anthropic
    client = _client_cache.setdefault("anthropic", anthropic.Anthropic())
    resp = client.messages.create(
        model=model, max_tokens=max_tokens,
        thinking={"type": "disabled"},
        messages=[{"role": "user", "content": prompt}])
    text = next((b.text for b in resp.content if b.type == "text"), "")
    return text, {"in": resp.usage.input_tokens,
                  "out": resp.usage.output_tokens}


def _complete_openai_compat(provider: str, model: str, prompt: str,
                            max_tokens: int, spec: dict) -> tuple:
    import os

    import openai
    if provider == "openrouter":
        client = _client_cache.setdefault(provider, openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"]))
    else:
        client = _client_cache.setdefault(provider, openai.OpenAI())
    kwargs = {"model": model, "max_completion_tokens": max_tokens,
              "messages": [{"role": "user", "content": prompt}]}
    if spec.get("reasoning_effort"):
        kwargs["reasoning_effort"] = spec["reasoning_effort"]
    try:
        resp = client.chat.completions.create(temperature=0, **kwargs)
    except openai.BadRequestError as e:
        if "temperature" not in str(e):
            raise
        resp = client.chat.completions.create(**kwargs)
    text = resp.choices[0].message.content or ""
    usage = resp.usage
    return text, {"in": getattr(usage, "prompt_tokens", None),
                  "out": getattr(usage, "completion_tokens", None)}


def _complete_google(model: str, prompt: str, max_tokens: int,
                     spec: dict) -> tuple:
    from google import genai
    from google.genai import types
    client = _client_cache.setdefault("google", genai.Client())
    config = types.GenerateContentConfig(
        temperature=0, max_output_tokens=max_tokens)
    if spec.get("thinking_level"):
        config.thinking_config = types.ThinkingConfig(
            thinking_level=spec["thinking_level"])
    resp = client.models.generate_content(
        model=model, contents=prompt, config=config)
    usage = resp.usage_metadata
    return resp.text or "", {"in": usage.prompt_token_count,
                             "out": usage.candidates_token_count}


_client_cache: dict = {}


def complete(spec: dict, prompt: str) -> tuple:
    provider = spec["provider"]
    max_tokens = spec.get("max_tokens", 512)
    if provider == "anthropic":
        return _complete_anthropic(spec["model"], prompt, max_tokens)
    if provider in ("openai", "openrouter"):
        return _complete_openai_compat(provider, spec["model"], prompt,
                                       max_tokens, spec)
    if provider == "google":
        return _complete_google(spec["model"], prompt, max_tokens, spec)
    raise ValueError(f"unknown provider {provider}")


# --- run --------------------------------------------------------------------

def run_model(model_key: str, track: str) -> None:
    load_env()
    specs = json.loads(MODELS_FILE.read_text())
    spec = specs[model_key]
    items = eval_items(track)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / f"{model_key}__{track}.jsonl"
    done = set()
    if out_path.exists():
        done = {json.loads(line)["item_id"]
                for line in out_path.read_text().splitlines()}
    todo = [it for it in items if it["item_id"] not in done]
    print(f"{model_key} track {track}: {len(todo)} to run "
          f"({len(done)} cached, {len(items)} total)")

    def one(it: dict) -> dict:
        prompt = format_mcq(it)
        raw, usage, t0 = "", None, time.time()
        for attempt in range(4):
            try:
                t0 = time.time()
                raw, usage = complete(spec, prompt)
                break
            except Exception as e:  # noqa: BLE001 — retry then surface
                if attempt == 3:
                    return {"item_id": it["item_id"], "error": str(e)[:500]}
                time.sleep(5 * 2 ** attempt)
        parsed = parse_answer(raw)
        return {"item_id": it["item_id"], "raw": raw, "parsed": parsed,
                "gold": it["gold_answer_label"],
                "correct": parsed == it["gold_answer_label"],
                "usage": usage, "latency_s": round(time.time() - t0, 2)}

    n_ok = n_err = 0
    with open(out_path, "a") as out, ThreadPoolExecutor(WORKERS) as pool:
        for rec in pool.map(one, todo):
            rec["model_key"] = model_key
            rec["model"] = spec["model"]
            rec["track"] = track
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            n_err += "error" in rec
            n_ok += "error" not in rec
    print(f"done: {n_ok} ok, {n_err} errors -> {out_path}")


def discover() -> None:
    load_env()
    import os

    import anthropic
    import openai
    print("== anthropic ==")
    for m in anthropic.Anthropic().models.list():
        print(" ", m.id)
    print("== openai ==")
    for m in openai.OpenAI().models.list():
        if any(k in m.id for k in ("gpt", "o3", "o4")):
            print(" ", m.id)
    print("== google ==")
    from google import genai
    gclient = genai.Client()
    for m in gclient.models.list():
        if "gemini" in (m.name or ""):
            print(" ", m.name)
    print("== openrouter: see https://openrouter.ai/models ==")
    _ = os


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["discover"]:
        discover()
    elif args[:1] == ["run"]:
        specs = json.loads(MODELS_FILE.read_text())
        keys = list(specs) if "--all" in args else args[1:]
        for key in keys:
            for track in ("A", "B"):
                run_model(key, track)
    else:
        sys.exit("usage: runner discover | runner run <model_key>|--all")
