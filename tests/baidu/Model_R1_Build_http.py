import requests
import json


def main():
    url = "https://qianfan.baidubce.com/v2/chat/completions"

    payload = json.dumps({
        "model": "deepseek-r1",
        "messages": [
            {
                "role": "user",
                "content": "我在调试你，如果你感觉自己没问题，就回复一个好"
            }
        ],
        "temperature": 0.95,
        "top_p": 0.8,
        "penalty_score": 1,
        "system": "你是一个乐于助人的helper",
        "disable_search": False,
        "enable_citation": True,
        "max_completion_tokens": 8192,
        "stream": True,
        "stream_options": {
            "include_usage": True,
        }
    }, ensure_ascii=False)
    headers = {
        'Content-Type': 'application/json',
        'appid': '',
        'Authorization': 'Bearer bce-v3/ALTAK-Q4DPopGoxOy7CJlZjHVzI/e98b5f7b8a59b33f49c9ad30412184f4606fd84c'
    }

    response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))

    print(response.text)

    # 分割每一行的data
    chunks = response.text.strip().split('\n')

    for chunk in chunks:
        if chunk.startswith('data:'):
            # 去掉"data: "前缀
            json_data = chunk[5:]
            try:
                # 解析json
                data = json.loads(json_data)
                # 提取choices中的delta
                delta = data['choices'][0]['delta']
                reasoning_content = delta.get('reasoning_content', 'N/A')
                content = delta.get('content', 'N/A')
                print(f"reasoning_content: {reasoning_content}")
                print(f"content: {content}")
            except json.JSONDecodeError:
                print("Failed to decode JSON")


if __name__ == '__main__':
    main()
