window.AZDIM = {
 "generated": "2026-07-06",
 "spend_usd": 29.14,
 "dataset": {
  "n_items": 2249,
  "n_mcq": 1634,
  "by_type": {
   "mcq": 1634,
   "codable_open": 449,
   "written_open": 166
  },
  "by_language": {
   "en": 129,
   "az": 1390,
   "ru": 423,
   "fr": 142,
   "de": 138,
   "ar": 27
  },
  "by_subject": {
   "russian_language": 376,
   "mathematics": 337,
   "geography": 205,
   "chemistry": 173,
   "physics": 163,
   "history": 151,
   "azerbaijani_language": 148,
   "french": 142,
   "german": 138,
   "english": 134,
   "literature": 117,
   "biology": 84,
   "informatics": 52,
   "arabic": 29
  },
  "by_year": {
   "2026": 985,
   "2025": 1264
  },
  "n_sources": 20,
  "requires_image": 456
 },
 "models": [
  {
   "key": "gemini-3.1-pro",
   "name": "Gemini 3.1 Pro",
   "org": "Google",
   "open_weights": false,
   "tracks": {
    "A": {
     "n": 139,
     "acc": 0.9424,
     "ci": [
      0.8993,
      0.9784
     ],
     "invalid": 0.0,
     "by_subject": {
      "azerbaijani_language": 1.0,
      "biology": 1.0,
      "chemistry": 0.9,
      "english": 1.0,
      "geography": 1.0,
      "history": 0.9583,
      "informatics": 1.0,
      "literature": 0.7778,
      "mathematics": 0.9,
      "physics": 1.0
     },
     "by_year": {
      "2025": 0.9483,
      "2026": 0.913
     }
    }
   }
  },
  {
   "key": "gemini-3.5-flash",
   "name": "Gemini 3.5 Flash",
   "org": "Google",
   "open_weights": false,
   "tracks": {
    "A": {
     "n": 540,
     "acc": 0.9407,
     "ci": [
      0.9204,
      0.9593
     ],
     "invalid": 0.0,
     "by_subject": {
      "azerbaijani_language": 0.925,
      "biology": 0.9615,
      "chemistry": 0.96,
      "english": 0.75,
      "geography": 0.961,
      "history": 1.0,
      "informatics": 0.95,
      "literature": 0.697,
      "mathematics": 0.9421,
      "physics": 1.0
     },
     "by_year": {
      "2025": 0.9459,
      "2026": 0.9324
     }
    },
    "B": {
     "n": 223,
     "acc": 0.9372,
     "ci": [
      0.9058,
      0.9686
     ],
     "invalid": 0.0,
     "by_subject": {
      "literature": 0.9615,
      "russian_language": 0.934
     },
     "by_year": {
      "2025": 0.9256,
      "2026": 0.951
     }
    }
   }
  },
  {
   "key": "gpt-5.5",
   "name": "GPT-5.5",
   "org": "OpenAI",
   "open_weights": false,
   "tracks": {
    "A": {
     "n": 250,
     "acc": 0.88,
     "ci": [
      0.84,
      0.92
     ],
     "invalid": 0.0,
     "by_subject": {
      "azerbaijani_language": 0.6757,
      "biology": 0.8333,
      "chemistry": 0.9429,
      "english": 1.0,
      "geography": 0.9444,
      "history": 0.9333,
      "informatics": 0.8889,
      "literature": 0.5333,
      "mathematics": 0.9643,
      "physics": 1.0
     },
     "by_year": {
      "2025": 0.8904,
      "2026": 0.8654
     }
    },
    "B": {
     "n": 100,
     "acc": 0.91,
     "ci": [
      0.85,
      0.96
     ],
     "invalid": 0.0,
     "by_subject": {
      "literature": 0.9167,
      "russian_language": 0.9091
     },
     "by_year": {
      "2025": 0.8679,
      "2026": 0.9574
     }
    }
   }
  },
  {
   "key": "claude-opus-4-8",
   "name": "Claude Opus 4.8",
   "org": "Anthropic",
   "open_weights": false,
   "tracks": {
    "A": {
     "n": 250,
     "acc": 0.876,
     "ci": [
      0.832,
      0.916
     ],
     "invalid": 0.0,
     "by_subject": {
      "azerbaijani_language": 0.7568,
      "biology": 1.0,
      "chemistry": 0.9714,
      "english": 1.0,
      "geography": 0.8611,
      "history": 0.8667,
      "informatics": 1.0,
      "literature": 0.5333,
      "mathematics": 0.9107,
      "physics": 1.0
     },
     "by_year": {
      "2025": 0.8767,
      "2026": 0.875
     }
    },
    "B": {
     "n": 100,
     "acc": 0.94,
     "ci": [
      0.89,
      0.98
     ],
     "invalid": 0.0,
     "by_subject": {
      "literature": 0.9167,
      "russian_language": 0.9432
     },
     "by_year": {
      "2025": 0.9057,
      "2026": 0.9787
     }
    }
   }
  },
  {
   "key": "deepseek-v4-pro",
   "name": "DeepSeek v4 Pro",
   "org": "DeepSeek",
   "open_weights": true,
   "tracks": {
    "A": {
     "n": 540,
     "acc": 0.8074,
     "ci": [
      0.7741,
      0.8407
     ],
     "invalid": 0.0926,
     "by_subject": {
      "azerbaijani_language": 0.575,
      "biology": 0.8846,
      "chemistry": 0.92,
      "english": 0.75,
      "geography": 0.8442,
      "history": 0.7846,
      "informatics": 0.95,
      "literature": 0.3939,
      "mathematics": 0.9008,
      "physics": 0.9744
     },
     "by_year": {
      "2025": 0.8048,
      "2026": 0.8116
     }
    },
    "B": {
     "n": 223,
     "acc": 0.8565,
     "ci": [
      0.8117,
      0.8969
     ],
     "invalid": 0.0493,
     "by_subject": {
      "literature": 0.8846,
      "russian_language": 0.8528
     },
     "by_year": {
      "2025": 0.8843,
      "2026": 0.8235
     }
    }
   }
  },
  {
   "key": "qwen3-max",
   "name": "Qwen3 Max",
   "org": "Alibaba",
   "open_weights": true,
   "tracks": {
    "A": {
     "n": 540,
     "acc": 0.7648,
     "ci": [
      0.7315,
      0.8
     ],
     "invalid": 0.0537,
     "by_subject": {
      "azerbaijani_language": 0.4625,
      "biology": 0.7692,
      "chemistry": 0.8933,
      "english": 0.75,
      "geography": 0.8571,
      "history": 0.6308,
      "informatics": 0.8,
      "literature": 0.3939,
      "mathematics": 0.9339,
      "physics": 0.9487
     },
     "by_year": {
      "2025": 0.7598,
      "2026": 0.7729
     }
    },
    "B": {
     "n": 208,
     "acc": 0.8173,
     "ci": [
      0.7644,
      0.8654
     ],
     "invalid": 0.0288,
     "by_subject": {
      "literature": 0.8462,
      "russian_language": 0.8132
     },
     "by_year": {
      "2025": 0.8,
      "2026": 0.8387
     }
    }
   }
  },
  {
   "key": "llama-4-maverick",
   "name": "Llama 4 Maverick",
   "org": "Meta",
   "open_weights": true,
   "tracks": {
    "A": {
     "n": 179,
     "acc": 0.7207,
     "ci": [
      0.6592,
      0.7877
     ],
     "invalid": 0.0,
     "by_subject": {
      "azerbaijani_language": 0.5455,
      "english": 0.75,
      "geography": 0.8333,
      "history": 0.68,
      "literature": 0.6,
      "mathematics": 0.863
     },
     "by_year": {
      "2025": 0.7009,
      "2026": 0.7581
     }
    }
   }
  },
  {
   "key": "gpt-5.4-mini",
   "name": "GPT-5.4 mini",
   "org": "OpenAI",
   "open_weights": false,
   "tracks": {
    "A": {
     "n": 540,
     "acc": 0.7204,
     "ci": [
      0.6815,
      0.7593
     ],
     "invalid": 0.0,
     "by_subject": {
      "azerbaijani_language": 0.3875,
      "biology": 0.6923,
      "chemistry": 0.84,
      "english": 0.75,
      "geography": 0.7662,
      "history": 0.5846,
      "informatics": 0.8,
      "literature": 0.4242,
      "mathematics": 0.9091,
      "physics": 0.9487
     },
     "by_year": {
      "2025": 0.7357,
      "2026": 0.6957
     }
    },
    "B": {
     "n": 223,
     "acc": 0.7489,
     "ci": [
      0.6906,
      0.8027
     ],
     "invalid": 0.0,
     "by_subject": {
      "literature": 0.7692,
      "russian_language": 0.7462
     },
     "by_year": {
      "2025": 0.7273,
      "2026": 0.7745
     }
    }
   }
  },
  {
   "key": "qwen3-235b",
   "name": "Qwen3 235B-A22B",
   "org": "Alibaba",
   "open_weights": true,
   "tracks": {
    "A": {
     "n": 540,
     "acc": 0.6907,
     "ci": [
      0.6537,
      0.7296
     ],
     "invalid": 0.0574,
     "by_subject": {
      "azerbaijani_language": 0.275,
      "biology": 0.6538,
      "chemistry": 0.84,
      "english": 0.75,
      "geography": 0.6623,
      "history": 0.6308,
      "informatics": 0.95,
      "literature": 0.3333,
      "mathematics": 0.9008,
      "physics": 0.9487
     },
     "by_year": {
      "2025": 0.6817,
      "2026": 0.7053
     }
    },
    "B": {
     "n": 223,
     "acc": 0.7534,
     "ci": [
      0.6951,
      0.8072
     ],
     "invalid": 0.0852,
     "by_subject": {
      "literature": 0.8077,
      "russian_language": 0.7462
     },
     "by_year": {
      "2025": 0.7521,
      "2026": 0.7549
     }
    }
   }
  },
  {
   "key": "claude-haiku-4-5",
   "name": "Claude Haiku 4.5",
   "org": "Anthropic",
   "open_weights": false,
   "tracks": {
    "A": {
     "n": 540,
     "acc": 0.6852,
     "ci": [
      0.6463,
      0.7222
     ],
     "invalid": 0.0019,
     "by_subject": {
      "azerbaijani_language": 0.425,
      "biology": 0.5,
      "chemistry": 0.8267,
      "english": 0.75,
      "geography": 0.6234,
      "history": 0.5692,
      "informatics": 0.75,
      "literature": 0.4242,
      "mathematics": 0.9008,
      "physics": 0.8974
     },
     "by_year": {
      "2025": 0.6847,
      "2026": 0.686
     }
    },
    "B": {
     "n": 223,
     "acc": 0.7668,
     "ci": [
      0.7085,
      0.8161
     ],
     "invalid": 0.0493,
     "by_subject": {
      "literature": 0.8077,
      "russian_language": 0.7614
     },
     "by_year": {
      "2025": 0.7273,
      "2026": 0.8137
     }
    }
   }
  }
 ]
};
