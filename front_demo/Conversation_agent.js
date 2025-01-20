fetch("http://127.0.0.1:5000/convert-to-py-and-run", {
    "headers": {
      "accept": "*/*",
      "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
      "content-type": "application/json",
      "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": "\"macOS\"",
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "cors",
      "sec-fetch-site": "same-origin"
    },
    "referrer": "http://127.0.0.1:5000/workstation",
    "referrerPolicy": "strict-origin-when-cross-origin",
    "body": "{\"data\":\"{\\n    \\\"3\\\": {\\n        \\\"data\\\": {\\n            \\\"args\\\": {\\n                \\\"condition_func\\\": \\\"lambda *args: True\\\"\\n            },\\n            \\\"elements\\\": [\\n                \\\"4\\\"\\n            ]\\n        },\\n        \\\"inputs\\\": {\\n            \\\"input_1\\\": {\\n                \\\"connections\\\": []\\n            }\\n        },\\n        \\\"name\\\": \\\"WhileLoopPipeline\\\",\\n        \\\"outputs\\\": {\\n            \\\"output_1\\\": {\\n                \\\"connections\\\": []\\n            }\\n        }\\n    },\\n    \\\"4\\\": {\\n        \\\"data\\\": {\\n            \\\"elements\\\": [\\n                \\\"5\\\",\\n                \\\"6\\\"\\n            ]\\n        },\\n        \\\"inputs\\\": {\\n            \\\"input_1\\\": {\\n                \\\"connections\\\": []\\n            }\\n        },\\n        \\\"name\\\": \\\"SequentialPipeline\\\",\\n        \\\"outputs\\\": {\\n            \\\"output_1\\\": {\\n                \\\"connections\\\": []\\n            }\\n        }\\n    },\\n    \\\"5\\\": {\\n        \\\"data\\\": {\\n            \\\"args\\\": {\\n                \\\"name\\\": \\\"User\\\"\\n            }\\n        },\\n        \\\"inputs\\\": {\\n            \\\"input_1\\\": {\\n                \\\"connections\\\": []\\n            }\\n        },\\n        \\\"name\\\": \\\"UserAgent\\\",\\n        \\\"outputs\\\": {\\n            \\\"output_1\\\": {\\n                \\\"connections\\\": []\\n            }\\n        }\\n    },\\n    \\\"6\\\": {\\n        \\\"data\\\": {\\n            \\\"args\\\": {\\n                \\\"model_config_name\\\": \\\"degpt\\\",\\n                \\\"name\\\": \\\"Assistant\\\",\\n                \\\"sys_prompt\\\": \\\"You are a helpful assistant.\\\"\\n            }\\n        },\\n        \\\"inputs\\\": {\\n            \\\"input_1\\\": {\\n                \\\"connections\\\": []\\n            }\\n        },\\n        \\\"name\\\": \\\"DialogAgent\\\",\\n        \\\"outputs\\\": {\\n            \\\"output_1\\\": {\\n                \\\"connections\\\": []\\n            }\\n        }\\n    },\\n    \\\"7\\\": {\\n        \\\"name\\\": \\\"degpt_chat\\\",\\n        \\\"data\\\": {\\n            \\\"args\\\": {\\n                \\\"config_name\\\": \\\"degpt\\\",\\n                \\\"model_name\\\": \\\"Llama3.3-70B\\\",\\n                \\\"api_key\\\": \\\"123\\\",\\n                \\\"temperature\\\": 0,\\n                \\\"seed\\\": 0,\\n                \\\"model_type\\\": \\\"degpt_chat\\\",\\n                \\\"messages_key\\\": \\\"input\\\"\\n            }\\n        },\\n        \\\"inputs\\\": {},\\n        \\\"outputs\\\": {}\\n    }\\n}\"}",
    "method": "POST",
    "mode": "cors",
    "credentials": "omit"
  });