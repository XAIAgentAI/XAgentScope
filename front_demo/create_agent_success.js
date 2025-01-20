// 创建Agent成功

fetch("http://127.0.0.1:5000/convert-to-py-and-run", {
  headers: {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "pragma": "no-cache",
    "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
  },
  referrer: "http://127.0.0.1:5000/workstation",
  referrerPolicy: "strict-origin-when-cross-origin",
  method: "POST",
  mode: "cors",
  credentials: "omit",
  body: JSON.stringify({
    data: JSON.stringify(
    {
      "3": {
        data: {
          args: {
            name: "User"
          }
        },
        inputs: {
          input_1: {
            connections: []
          }
        },
        name: "UserAgent",
        outputs: {
          output_1: {
            connections: [
              {
                node: "4",
                output: "input_1"
              }
            ]
          }
        }
      },
      "4": {
        data: {
          args: {
            model_config_name: "degpt_11_04",
            name: "Assistant",
            sys_prompt: "You are an assistant"
          }
        },
        inputs: {
          input_1: {
            connections: [
              {
                input: "output_1",
                node: "3"
              }
            ]
          }
        },
        name: "DialogAgent",
        outputs: {
          output_1: {
            connections: []
          }
        }
      },
      "5": {
        name: "degpt_chat",
        data: {
          args: {
            config_name: "degpt_11_04",
            model_name: "Llama3.3-70B",
            api_key: "123321",
            temperature: 0,
            seed: 0,
            model_type: "degpt_chat",
            messages_key: "input"
          }
        },
        inputs: {},
        outputs: {}
      }
    }
    )
    
    
  
  })
});