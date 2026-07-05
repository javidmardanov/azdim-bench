"""Human verification UI for extracted items.

Shows the rendered source page beside the extracted item; Javid approves,
edits, or rejects. Decisions append to data/verified/decisions.jsonl
(audit log, last decision per item wins).

Usage:
    uv run python -m azdim.verify_app          # serve on localhost:5050
    uv run python -m azdim.verify_app export   # apply decisions -> verified jsonl
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parents[2]
ITEMS_FILE = ROOT / "data" / "items" / "items_v0.jsonl"
PAGES_DIR = ROOT / "data" / "pages"
VERIFIED_DIR = ROOT / "data" / "verified"
DECISIONS = VERIFIED_DIR / "decisions.jsonl"

app = Flask(__name__)


def load_items() -> list[dict]:
    return [json.loads(line) for line in ITEMS_FILE.read_text().splitlines()]


def load_decisions() -> dict[str, dict]:
    decisions: dict[str, dict] = {}
    if DECISIONS.exists():
        for line in DECISIONS.read_text().splitlines():
            d = json.loads(line)
            decisions[d["item_id"]] = d
    return decisions


def is_flagged(it: dict) -> bool:
    return (it.get("extraction_confidence") != "high"
            or bool(it.get("notes"))
            or (it["question_type"] == "mcq"
                and not it.get("gold_answer_label")))


PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>AzDIM verify</title><style>
body{font-family:system-ui;margin:0;display:flex;height:100vh}
#left{width:55%;overflow:auto;background:#333}
#left img{width:100%}
#right{width:45%;padding:14px;overflow:auto;box-sizing:border-box}
textarea{width:100%;height:52vh;font:12px/1.4 monospace}
button{font-size:15px;padding:8px 18px;margin-right:8px;cursor:pointer}
#approve{background:#c8f7c5}#reject{background:#f7c5c5}
.meta{color:#555;font-size:13px;margin:6px 0}
#progress{font-weight:600}
</style></head><body>
<div id="left"><img id="pageimg"></div>
<div id="right">
  <div id="progress"></div>
  <div class="meta" id="meta"></div>
  <textarea id="editor" spellcheck="false"></textarea><br><br>
  <button id="approve" onclick="decide('approve')">Approve (a)</button>
  <button id="reject" onclick="decide('reject')">Reject (r)</button>
  <button onclick="skip()">Skip (s)</button>
  <input id="note" placeholder="note (optional)" size="30">
</div>
<script>
let item=null;
async function next(){
  const r=await fetch('/api/next');
  const d=await r.json();
  if(!d.item){document.getElementById('meta').innerText='All done!';return}
  item=d.item;
  document.getElementById('progress').innerText=
    `${d.n_done}/${d.n_total} reviewed — ${d.n_flagged_left} flagged left`;
  document.getElementById('meta').innerText=
    `${item.item_id} — conf=${item.extraction_confidence}`+
    ` — ${item.subject} — ${item.notes||''}`;
  document.getElementById('editor').value=JSON.stringify(item,null,2);
  document.getElementById('pageimg').src=
    `/pages/${item.source_id}/page-${String(item.source_page).padStart(2,'0')}.png`;
  document.getElementById('note').value='';
}
async function decide(action){
  let edited;
  try{edited=JSON.parse(document.getElementById('editor').value)}
  catch(e){alert('invalid JSON: '+e);return}
  await fetch('/api/decide',{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({item_id:item.item_id,action:action,item:edited,
      note:document.getElementById('note').value})});
  next();
}
function skip(){next()}
document.addEventListener('keydown',e=>{
  if(e.target.tagName==='TEXTAREA'||e.target.tagName==='INPUT')return;
  if(e.key==='a')decide('approve');
  if(e.key==='r')decide('reject');
  if(e.key==='s')skip();
});
next();
</script></body></html>"""


@app.get("/")
def index():
    return PAGE


@app.get("/pages/<source_id>/<name>")
def page_image(source_id, name):
    return send_from_directory(PAGES_DIR / source_id, name)


@app.get("/api/next")
def api_next():
    items = load_items()
    decisions = load_decisions()
    todo = [it for it in items if it["item_id"] not in decisions]
    todo.sort(key=lambda it: (not is_flagged(it), it["source_id"],
                              it["source_page"]))
    return jsonify({
        "item": todo[0] if todo else None,
        "n_done": len(decisions),
        "n_total": len(items),
        "n_flagged_left": sum(is_flagged(it) for it in todo),
    })


@app.post("/api/decide")
def api_decide():
    d = request.get_json()
    d["decided_at"] = datetime.now(timezone.utc).isoformat()
    VERIFIED_DIR.mkdir(parents=True, exist_ok=True)
    with open(DECISIONS, "a") as f:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")
    return jsonify({"ok": True})


def export() -> None:
    decisions = load_decisions()
    items = load_items()
    out = VERIFIED_DIR / "items_v0_verified.jsonl"
    n_app = n_rej = n_unreviewed = 0
    with open(out, "w") as f:
        for it in items:
            d = decisions.get(it["item_id"])
            if d is None:
                n_unreviewed += 1
                continue
            if d["action"] == "reject":
                n_rej += 1
                continue
            item = d.get("item") or it
            item["verification_status"] = "human_verified"
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            n_app += 1
    print(f"approved {n_app}, rejected {n_rej}, "
          f"unreviewed {n_unreviewed} -> {out}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        export()
    else:
        app.run(port=5050, debug=False)
