# DeepSeek Chat

### 补全对话
- body
```json
{
  "messages": [
    {
      "content": "You are a helpful assistant",
      "role": "system"
    },
    {
      "content": "你叫什么？",
      "role": "user"
    }
  ],
  "model": "deepseek-chat",
  "frequency_penalty": 0,
  "max_tokens": 2048,
  "presence_penalty": 0,
  "response_format": {
    "type": "text"
  },
  "stop": null,
  "stream": true,
  "stream_options": null,
  "temperature": 1,
  "top_p": 1,
  "tools": null,
  "tool_choice": "none",
  "logprobs": false,
  "top_logprobs": null
}
```
- response
  - 流式
```Text
data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"role":"assistant","content":""},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"我"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"是一个"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"人工智能"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"助手"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"，"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"没有"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"具体的"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"名称"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"，"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"你可以"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"随意"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"称呼"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"我"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"。"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"如果你"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"有"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"任何"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"问题"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"或"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"需要"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"帮助"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"，"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"我会"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"尽力"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"为你"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"提供"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"支持"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":"。"},"logprobs":null,"finish_reason":null}]}

data: {"id":"24cf6cd3-b4b3-46cc-9347-0928013daea0","object":"chat.completion.chunk","created":1732591576,"model":"deepseek-chat","system_fingerprint":"fp_1c141eb703","choices":[{"index":0,"delta":{"content":""},"logprobs":null,"finish_reason":"stop"}],"usage":{"prompt_tokens":12,"completion_tokens":28,"total_tokens":40,"prompt_cache_hit_tokens":0,"prompt_cache_miss_tokens":12}}

data: [DONE]
```
```json
{
  "cache-control": "no-cache",
  "content-type": "text/event-stream; charset=utf-8"
}
```
- response
  - 非流式
```json
{
  "id": "dc38814f-a504-4aa4-8df7-d15c02e9b1eb",
  "object": "chat.completion",
  "created": 1732591899,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "我是一个人工智能助手，没有具体的姓名，你可以随意称呼我。如果你有任何问题或需要帮助，我会尽力为你提供支持。"
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 28,
    "total_tokens": 40,
    "prompt_cache_hit_tokens": 0,
    "prompt_cache_miss_tokens": 12
  },
  "system_fingerprint": "fp_1c141eb703"
}
```
