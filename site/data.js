window.AZDIM = {
 "generated": "2026-07-07",
 "spend_usd": 34.24,
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
     "n": 250,
     "acc": 0.956,
     "ci": [
      0.928,
      0.98
     ],
     "invalid": 0.0,
     "by_subject": {
      "azerbaijani_language": 0.973,
      "biology": 1.0,
      "chemistry": 0.9429,
      "english": 1.0,
      "geography": 1.0,
      "history": 0.9667,
      "informatics": 1.0,
      "literature": 0.8,
      "mathematics": 0.9286,
      "physics": 1.0
     },
     "by_year": {
      "2025": 0.9589,
      "2026": 0.9519
     }
    },
    "B": {
     "n": 100,
     "acc": 0.95,
     "ci": [
      0.9,
      0.99
     ],
     "invalid": 0.01,
     "by_subject": {
      "literature": 0.9167,
      "russian_language": 0.9545
     },
     "by_year": {
      "2025": 0.9245,
      "2026": 0.9787
     }
    },
    "F": {
     "n": 176,
     "acc": 0.9375,
     "ci": [
      0.9034,
      0.9716
     ],
     "invalid": 0.0,
     "by_subject": {
      "english": 0.9434,
      "french": 0.9577,
      "german": 0.9038
     },
     "by_year": {
      "2025": 0.9242,
      "2026": 0.9455
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
    },
    "F": {
     "n": 176,
     "acc": 0.9034,
     "ci": [
      0.858,
      0.9432
     ],
     "invalid": 0.0,
     "by_subject": {
      "english": 0.9245,
      "french": 0.9155,
      "german": 0.8654
     },
     "by_year": {
      "2025": 0.8939,
      "2026": 0.9091
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
    },
    "F": {
     "n": 176,
     "acc": 0.9091,
     "ci": [
      0.8636,
      0.9489
     ],
     "invalid": 0.0,
     "by_subject": {
      "english": 0.9057,
      "french": 0.9296,
      "german": 0.8846
     },
     "by_year": {
      "2025": 0.9394,
      "2026": 0.8909
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
    },
    "F": {
     "n": 176,
     "acc": 0.9318,
     "ci": [
      0.892,
      0.9659
     ],
     "invalid": 0.0,
     "by_subject": {
      "english": 0.9245,
      "french": 0.9437,
      "german": 0.9231
     },
     "by_year": {
      "2025": 0.9394,
      "2026": 0.9273
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
    },
    "F": {
     "n": 176,
     "acc": 0.892,
     "ci": [
      0.8466,
      0.9375
     ],
     "invalid": 0.017,
     "by_subject": {
      "english": 0.9245,
      "french": 0.9014,
      "german": 0.8462
     },
     "by_year": {
      "2025": 0.8788,
      "2026": 0.9
     }
    }
   }
  },
  {
   "key": "claude-sonnet-5",
   "name": "Claude Sonnet 5",
   "org": "Anthropic",
   "open_weights": false,
   "tracks": {
    "A": {
     "n": 250,
     "acc": 0.796,
     "ci": [
      0.744,
      0.848
     ],
     "invalid": 0.0,
     "by_subject": {
      "azerbaijani_language": 0.5946,
      "biology": 0.8333,
      "chemistry": 0.9429,
      "english": 1.0,
      "geography": 0.7778,
      "history": 0.6667,
      "informatics": 0.8889,
      "literature": 0.4667,
      "mathematics": 0.9107,
      "physics": 1.0
     },
     "by_year": {
      "2025": 0.7808,
      "2026": 0.8173
     }
    },
    "B": {
     "n": 100,
     "acc": 0.85,
     "ci": [
      0.78,
      0.92
     ],
     "invalid": 0.0,
     "by_subject": {
      "literature": 0.75,
      "russian_language": 0.8636
     },
     "by_year": {
      "2025": 0.7925,
      "2026": 0.9149
     }
    },
    "F": {
     "n": 176,
     "acc": 0.9091,
     "ci": [
      0.8636,
      0.9489
     ],
     "invalid": 0.0,
     "by_subject": {
      "english": 0.8868,
      "french": 0.9014,
      "german": 0.9423
     },
     "by_year": {
      "2025": 0.9394,
      "2026": 0.8909
     }
    }
   }
  },
  {
   "key": "gemma-4-31b",
   "name": "Gemma 4 31B",
   "org": "Google",
   "open_weights": true,
   "tracks": {
    "A": {
     "n": 540,
     "acc": 0.7796,
     "ci": [
      0.7463,
      0.8148
     ],
     "invalid": 0.0056,
     "by_subject": {
      "azerbaijani_language": 0.5375,
      "biology": 0.7308,
      "chemistry": 0.88,
      "english": 0.75,
      "geography": 0.8182,
      "history": 0.6615,
      "informatics": 0.9,
      "literature": 0.5758,
      "mathematics": 0.9174,
      "physics": 0.9231
     },
     "by_year": {
      "2025": 0.7718,
      "2026": 0.7923
     }
    },
    "B": {
     "n": 223,
     "acc": 0.8386,
     "ci": [
      0.7892,
      0.8879
     ],
     "invalid": 0.0,
     "by_subject": {
      "literature": 0.8077,
      "russian_language": 0.8426
     },
     "by_year": {
      "2025": 0.8595,
      "2026": 0.8137
     }
    },
    "F": {
     "n": 176,
     "acc": 0.8977,
     "ci": [
      0.8523,
      0.9375
     ],
     "invalid": 0.0,
     "by_subject": {
      "english": 0.8868,
      "french": 0.8873,
      "german": 0.9231
     },
     "by_year": {
      "2025": 0.8939,
      "2026": 0.9
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
    },
    "F": {
     "n": 159,
     "acc": 0.9057,
     "ci": [
      0.8616,
      0.9497
     ],
     "invalid": 0.0,
     "by_subject": {
      "english": 0.9038,
      "french": 0.9,
      "german": 0.9149
     },
     "by_year": {
      "2025": 0.8852,
      "2026": 0.9184
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
     "n": 540,
     "acc": 0.7333,
     "ci": [
      0.6963,
      0.7704
     ],
     "invalid": 0.0,
     "by_subject": {
      "azerbaijani_language": 0.5,
      "biology": 0.6538,
      "chemistry": 0.8133,
      "english": 0.75,
      "geography": 0.8182,
      "history": 0.6154,
      "informatics": 0.7,
      "literature": 0.5455,
      "mathematics": 0.8678,
      "physics": 0.8974
     },
     "by_year": {
      "2025": 0.7447,
      "2026": 0.715
     }
    },
    "B": {
     "n": 223,
     "acc": 0.8206,
     "ci": [
      0.7713,
      0.87
     ],
     "invalid": 0.0,
     "by_subject": {
      "literature": 0.8846,
      "russian_language": 0.8122
     },
     "by_year": {
      "2025": 0.8182,
      "2026": 0.8235
     }
    },
    "F": {
     "n": 176,
     "acc": 0.875,
     "ci": [
      0.8239,
      0.9205
     ],
     "invalid": 0.0057,
     "by_subject": {
      "english": 0.9057,
      "french": 0.8873,
      "german": 0.8269
     },
     "by_year": {
      "2025": 0.8939,
      "2026": 0.8636
     }
    }
   }
  },
  {
   "key": "mistral-large-2512",
   "name": "Mistral Large 2512",
   "org": "Mistral",
   "open_weights": true,
   "tracks": {
    "A": {
     "n": 540,
     "acc": 0.7259,
     "ci": [
      0.687,
      0.763
     ],
     "invalid": 0.0,
     "by_subject": {
      "azerbaijani_language": 0.4375,
      "biology": 0.5385,
      "chemistry": 0.8533,
      "english": 0.75,
      "geography": 0.7792,
      "history": 0.6308,
      "informatics": 0.85,
      "literature": 0.4242,
      "mathematics": 0.9091,
      "physics": 0.8718
     },
     "by_year": {
      "2025": 0.7177,
      "2026": 0.7391
     }
    },
    "B": {
     "n": 223,
     "acc": 0.8386,
     "ci": [
      0.7892,
      0.8879
     ],
     "invalid": 0.0,
     "by_subject": {
      "literature": 0.8846,
      "russian_language": 0.8325
     },
     "by_year": {
      "2025": 0.8099,
      "2026": 0.8725
     }
    },
    "F": {
     "n": 176,
     "acc": 0.875,
     "ci": [
      0.8239,
      0.9205
     ],
     "invalid": 0.0,
     "by_subject": {
      "english": 0.8679,
      "french": 0.8592,
      "german": 0.9038
     },
     "by_year": {
      "2025": 0.8939,
      "2026": 0.8636
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
    },
    "F": {
     "n": 176,
     "acc": 0.858,
     "ci": [
      0.8068,
      0.9091
     ],
     "invalid": 0.0,
     "by_subject": {
      "english": 0.8868,
      "french": 0.8873,
      "german": 0.7885
     },
     "by_year": {
      "2025": 0.8485,
      "2026": 0.8636
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
    },
    "F": {
     "n": 176,
     "acc": 0.8807,
     "ci": [
      0.8295,
      0.9261
     ],
     "invalid": 0.0,
     "by_subject": {
      "english": 0.8868,
      "french": 0.9014,
      "german": 0.8462
     },
     "by_year": {
      "2025": 0.8485,
      "2026": 0.9
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
    },
    "F": {
     "n": 176,
     "acc": 0.8466,
     "ci": [
      0.7898,
      0.8977
     ],
     "invalid": 0.0909,
     "by_subject": {
      "english": 0.8679,
      "french": 0.8451,
      "german": 0.8269
     },
     "by_year": {
      "2025": 0.8636,
      "2026": 0.8364
     }
    }
   }
  },
  {
   "key": "llama-3.1-8b",
   "name": "Llama 3.1 8B",
   "org": "Meta",
   "open_weights": true,
   "tracks": {
    "A": {
     "n": 540,
     "acc": 0.2481,
     "ci": [
      0.213,
      0.2852
     ],
     "invalid": 0.0556,
     "by_subject": {
      "azerbaijani_language": 0.2,
      "biology": 0.1923,
      "chemistry": 0.3067,
      "english": 0.75,
      "geography": 0.2338,
      "history": 0.3077,
      "informatics": 0.2,
      "literature": 0.1212,
      "mathematics": 0.2645,
      "physics": 0.2308
     },
     "by_year": {
      "2025": 0.2342,
      "2026": 0.2705
     }
    },
    "B": {
     "n": 223,
     "acc": 0.4081,
     "ci": [
      0.3408,
      0.4709
     ],
     "invalid": 0.0359,
     "by_subject": {
      "literature": 0.3462,
      "russian_language": 0.4162
     },
     "by_year": {
      "2025": 0.4132,
      "2026": 0.402
     }
    },
    "F": {
     "n": 176,
     "acc": 0.5852,
     "ci": [
      0.5114,
      0.6591
     ],
     "invalid": 0.0114,
     "by_subject": {
      "english": 0.566,
      "french": 0.6197,
      "german": 0.5577
     },
     "by_year": {
      "2025": 0.5606,
      "2026": 0.6
     }
    }
   }
  }
 ],
 "dim_scores": [
  {
   "key": "claude-haiku-4-5",
   "name": "Claude Haiku 4.5",
   "org": "Anthropic",
   "s1": {
    "central": 194.0,
    "floor": 99.7
   },
   "groups": {
    "I (RK)": {
     "central": 356.6,
     "min_n": 39,
     "floor": 235.7,
     "total700_central": 550.6,
     "total700_floor": 335.4
    },
    "I (Rİ)": {
     "central": 347.7,
     "min_n": 20,
     "floor": 229.3,
     "total700_central": 541.7,
     "total700_floor": 329.0
    },
    "II": {
     "central": 278.6,
     "min_n": 65,
     "floor": 180.0,
     "total700_central": 472.6,
     "total700_floor": 279.7
    },
    "III (DT)": {
     "central": 169.9,
     "min_n": 33,
     "floor": 102.3,
     "total700_central": 363.9,
     "total700_floor": 202.0
    },
    "IV": {
     "central": 270.2,
     "min_n": 26,
     "floor": 174.0,
     "total700_central": 464.2,
     "total700_floor": 273.7
    }
   }
  },
  {
   "key": "claude-opus-4-8",
   "name": "Claude Opus 4.8",
   "org": "Anthropic",
   "s1": {
    "central": 249.7,
    "floor": 128.4
   },
   "groups": {
    "I (RK)": {
     "central": 391.4,
     "min_n": 18,
     "floor": 260.5,
     "total700_central": 641.1,
     "total700_floor": 388.9
    },
    "I (Rİ)": null,
    "II": {
     "central": 354.8,
     "min_n": 30,
     "floor": 234.4,
     "total700_central": 604.5,
     "total700_floor": 362.8
    },
    "III (DT)": {
     "central": 283.3,
     "min_n": 15,
     "floor": 183.3,
     "total700_central": 533.0,
     "total700_floor": 311.7
    },
    "IV": {
     "central": 395.0,
     "min_n": 12,
     "floor": 263.1,
     "total700_central": 644.7,
     "total700_floor": 391.5
    }
   }
  },
  {
   "key": "claude-sonnet-5",
   "name": "Claude Sonnet 5",
   "org": "Anthropic",
   "s1": {
    "central": 223.0,
    "floor": 114.3
   },
   "groups": {
    "I (RK)": {
     "central": 382.7,
     "min_n": 18,
     "floor": 254.3,
     "total700_central": 605.7,
     "total700_floor": 368.6
    },
    "I (Rİ)": null,
    "II": {
     "central": 311.6,
     "min_n": 30,
     "floor": 203.5,
     "total700_central": 534.6,
     "total700_floor": 317.8
    },
    "III (DT)": {
     "central": 221.1,
     "min_n": 15,
     "floor": 138.9,
     "total700_central": 444.1,
     "total700_floor": 253.2
    },
    "IV": {
     "central": 360.8,
     "min_n": 12,
     "floor": 238.7,
     "total700_central": 583.8,
     "total700_floor": 353.0
    }
   }
  },
  {
   "key": "deepseek-v4-pro",
   "name": "DeepSeek v4 Pro",
   "org": "DeepSeek",
   "s1": {
    "central": 213.2,
    "floor": 110.0
   },
   "groups": {
    "I (RK)": {
     "central": 387.3,
     "min_n": 39,
     "floor": 257.9,
     "total700_central": 600.5,
     "total700_floor": 367.9
    },
    "I (Rİ)": {
     "central": 390.3,
     "min_n": 20,
     "floor": 259.9,
     "total700_central": 603.5,
     "total700_floor": 369.9
    },
    "II": {
     "central": 350.8,
     "min_n": 65,
     "floor": 232.5,
     "total700_central": 564.0,
     "total700_floor": 342.5
    },
    "III (DT)": {
     "central": 245.1,
     "min_n": 33,
     "floor": 159.4,
     "total700_central": 458.3,
     "total700_floor": 269.4
    },
    "IV": {
     "central": 363.9,
     "min_n": 26,
     "floor": 241.2,
     "total700_central": 577.1,
     "total700_floor": 351.2
    }
   }
  },
  {
   "key": "gemini-3.1-pro",
   "name": "Gemini 3.1 Pro",
   "org": "Google",
   "s1": {
    "central": 268.5,
    "floor": 137.7
   },
   "groups": {
    "I (RK)": {
     "central": 393.3,
     "min_n": 18,
     "floor": 261.9,
     "total700_central": 661.8,
     "total700_floor": 399.6
    },
    "I (Rİ)": null,
    "II": {
     "central": 396.1,
     "min_n": 30,
     "floor": 263.9,
     "total700_central": 664.6,
     "total700_floor": 401.6
    },
    "III (DT)": {
     "central": 370.8,
     "min_n": 15,
     "floor": 245.8,
     "total700_central": 639.3,
     "total700_floor": 383.5
    },
    "IV": {
     "central": 390.0,
     "min_n": 12,
     "floor": 259.5,
     "total700_central": 658.5,
     "total700_floor": 397.2
    }
   }
  },
  {
   "key": "gemini-3.5-flash",
   "name": "Gemini 3.5 Flash",
   "org": "Google",
   "s1": {
    "central": 267.8,
    "floor": 136.5
   },
   "groups": {
    "I (RK)": {
     "central": 395.3,
     "min_n": 39,
     "floor": 263.3,
     "total700_central": 663.1,
     "total700_floor": 399.8
    },
    "I (Rİ)": {
     "central": 394.2,
     "min_n": 20,
     "floor": 262.5,
     "total700_central": 662.0,
     "total700_floor": 399.0
    },
    "II": {
     "central": 393.2,
     "min_n": 65,
     "floor": 261.8,
     "total700_central": 661.0,
     "total700_floor": 398.3
    },
    "III (DT)": {
     "central": 356.3,
     "min_n": 33,
     "floor": 235.5,
     "total700_central": 624.1,
     "total700_floor": 372.0
    },
    "IV": {
     "central": 386.3,
     "min_n": 26,
     "floor": 256.9,
     "total700_central": 654.1,
     "total700_floor": 393.4
    }
   }
  },
  {
   "key": "gemma-4-31b",
   "name": "Gemma 4 31B",
   "org": "Google",
   "s1": {
    "central": 215.4,
    "floor": 110.7
   },
   "groups": {
    "I (RK)": {
     "central": 372.5,
     "min_n": 39,
     "floor": 247.1,
     "total700_central": 587.9,
     "total700_floor": 357.8
    },
    "I (Rİ)": {
     "central": 374.9,
     "min_n": 20,
     "floor": 248.7,
     "total700_central": 590.3,
     "total700_floor": 359.4
    },
    "II": {
     "central": 329.2,
     "min_n": 65,
     "floor": 216.2,
     "total700_central": 544.6,
     "total700_floor": 326.9
    },
    "III (DT)": {
     "central": 221.2,
     "min_n": 33,
     "floor": 139.2,
     "total700_central": 436.6,
     "total700_floor": 249.9
    },
    "IV": {
     "central": 322.9,
     "min_n": 26,
     "floor": 211.6,
     "total700_central": 538.3,
     "total700_floor": 322.3
    }
   }
  },
  {
   "key": "gpt-5.4-mini",
   "name": "GPT-5.4 mini",
   "org": "OpenAI",
   "s1": {
    "central": 206.4,
    "floor": 105.8
   },
   "groups": {
    "I (RK)": {
     "central": 367.1,
     "min_n": 39,
     "floor": 243.2,
     "total700_central": 573.5,
     "total700_floor": 349.0
    },
    "I (Rİ)": {
     "central": 362.5,
     "min_n": 20,
     "floor": 239.9,
     "total700_central": 568.9,
     "total700_floor": 345.7
    },
    "II": {
     "central": 305.4,
     "min_n": 65,
     "floor": 199.1,
     "total700_central": 511.8,
     "total700_floor": 304.9
    },
    "III (DT)": {
     "central": 156.0,
     "min_n": 33,
     "floor": 92.4,
     "total700_central": 362.4,
     "total700_floor": 198.2
    },
    "IV": {
     "central": 312.2,
     "min_n": 26,
     "floor": 203.9,
     "total700_central": 518.6,
     "total700_floor": 309.7
    }
   }
  },
  {
   "key": "gpt-5.5",
   "name": "GPT-5.5",
   "org": "OpenAI",
   "s1": {
    "central": 235.5,
    "floor": 120.5
   },
   "groups": {
    "I (RK)": {
     "central": 393.3,
     "min_n": 18,
     "floor": 261.9,
     "total700_central": 628.8,
     "total700_floor": 382.4
    },
    "I (Rİ)": null,
    "II": {
     "central": 382.5,
     "min_n": 30,
     "floor": 254.2,
     "total700_central": 618.0,
     "total700_floor": 374.7
    },
    "III (DT)": {
     "central": 295.0,
     "min_n": 15,
     "floor": 191.7,
     "total700_central": 530.5,
     "total700_floor": 312.2
    },
    "IV": {
     "central": 360.8,
     "min_n": 12,
     "floor": 238.7,
     "total700_central": 596.3,
     "total700_floor": 359.2
    }
   }
  },
  {
   "key": "llama-3.1-8b",
   "name": "Llama 3.1 8B",
   "org": "Meta",
   "s1": {
    "central": 124.1,
    "floor": 66.0
   },
   "groups": {
    "I (RK)": {
     "central": 57.5,
     "min_n": 39,
     "floor": 24.5,
     "total700_central": 181.6,
     "total700_floor": 90.5
    },
    "I (Rİ)": {
     "central": 45.9,
     "min_n": 20,
     "floor": 16.5,
     "total700_central": 170.0,
     "total700_floor": 82.5
    },
    "II": {
     "central": 54.9,
     "min_n": 65,
     "floor": 21.8,
     "total700_central": 179.0,
     "total700_floor": 87.8
    },
    "III (DT)": {
     "central": 40.0,
     "min_n": 33,
     "floor": 13.5,
     "total700_central": 164.1,
     "total700_floor": 79.5
    },
    "IV": {
     "central": 50.7,
     "min_n": 26,
     "floor": 18.0,
     "total700_central": 174.8,
     "total700_floor": 84.0
    }
   }
  },
  {
   "key": "llama-4-maverick",
   "name": "Llama 4 Maverick",
   "org": "Meta",
   "s1": {
    "central": 217.8,
    "floor": 111.6
   },
   "groups": {
    "I (RK)": {
     "central": 342.0,
     "min_n": 39,
     "floor": 225.2,
     "total700_central": 559.8,
     "total700_floor": 336.8
    },
    "I (Rİ)": {
     "central": 328.8,
     "min_n": 20,
     "floor": 215.8,
     "total700_central": 546.6,
     "total700_floor": 327.4
    },
    "II": {
     "central": 305.0,
     "min_n": 65,
     "floor": 198.8,
     "total700_central": 522.8,
     "total700_floor": 310.4
    },
    "III (DT)": {
     "central": 192.2,
     "min_n": 33,
     "floor": 118.2,
     "total700_central": 410.0,
     "total700_floor": 229.8
    },
    "IV": {
     "central": 294.8,
     "min_n": 26,
     "floor": 191.5,
     "total700_central": 512.6,
     "total700_floor": 303.1
    }
   }
  },
  {
   "key": "mistral-large-2512",
   "name": "Mistral Large 2512",
   "org": "Mistral",
   "s1": {
    "central": 213.3,
    "floor": 109.2
   },
   "groups": {
    "I (RK)": {
     "central": 355.2,
     "min_n": 39,
     "floor": 234.7,
     "total700_central": 568.5,
     "total700_floor": 343.9
    },
    "I (Rİ)": {
     "central": 354.8,
     "min_n": 20,
     "floor": 234.4,
     "total700_central": 568.1,
     "total700_floor": 343.6
    },
    "II": {
     "central": 313.1,
     "min_n": 65,
     "floor": 204.6,
     "total700_central": 526.4,
     "total700_floor": 313.8
    },
    "III (DT)": {
     "central": 172.4,
     "min_n": 33,
     "floor": 104.1,
     "total700_central": 385.7,
     "total700_floor": 213.3
    },
    "IV": {
     "central": 278.6,
     "min_n": 26,
     "floor": 180.0,
     "total700_central": 491.9,
     "total700_floor": 289.2
    }
   }
  },
  {
   "key": "qwen3-235b",
   "name": "Qwen3 235B-A22B",
   "org": "Alibaba",
   "s1": {
    "central": 191.5,
    "floor": 98.4
   },
   "groups": {
    "I (RK)": {
     "central": 371.7,
     "min_n": 39,
     "floor": 247.0,
     "total700_central": 563.2,
     "total700_floor": 345.4
    },
    "I (Rİ)": {
     "central": 383.6,
     "min_n": 20,
     "floor": 255.2,
     "total700_central": 575.1,
     "total700_floor": 353.6
    },
    "II": {
     "central": 298.0,
     "min_n": 65,
     "floor": 194.6,
     "total700_central": 489.5,
     "total700_floor": 293.0
    },
    "III (DT)": {
     "central": 148.5,
     "min_n": 33,
     "floor": 89.1,
     "total700_central": 340.0,
     "total700_floor": 187.5
    },
    "IV": {
     "central": 309.1,
     "min_n": 26,
     "floor": 202.8,
     "total700_central": 500.6,
     "total700_floor": 301.2
    }
   }
  },
  {
   "key": "qwen3-max",
   "name": "Qwen3 Max",
   "org": "Alibaba",
   "s1": {
    "central": 224.1,
    "floor": 114.6
   },
   "groups": {
    "I (RK)": {
     "central": 379.5,
     "min_n": 39,
     "floor": 252.3,
     "total700_central": 603.6,
     "total700_floor": 366.9
    },
    "I (Rİ)": {
     "central": 369.4,
     "min_n": 20,
     "floor": 245.3,
     "total700_central": 593.5,
     "total700_floor": 359.9
    },
    "II": {
     "central": 333.3,
     "min_n": 65,
     "floor": 219.4,
     "total700_central": 557.4,
     "total700_floor": 334.0
    },
    "III (DT)": {
     "central": 176.8,
     "min_n": 33,
     "floor": 109.6,
     "total700_central": 400.9,
     "total700_floor": 224.2
    },
    "IV": {
     "central": 337.3,
     "min_n": 26,
     "floor": 222.5,
     "total700_central": 561.4,
     "total700_floor": 337.1
    }
   }
  }
 ]
};
