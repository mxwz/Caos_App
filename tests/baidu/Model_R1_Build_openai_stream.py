import time

from openai import OpenAI

messages = [{
            "role": "user",
            "content": "1+1等于几？"
        },
    ]

def main(messages):
    client = OpenAI(
        base_url='https://qianfan.baidubce.com/v2',
        api_key='bce-v3/ALTAK-Q4DPopGoxOy7CJlZjHVzI/e98b5f7b8a59b33f49c9ad30412184f4606fd84c'
    )

    chat_completion = client.chat.completions.create(
        model="deepseek-r1",
        messages=messages,
        stream=True,
        stream_options={
            "include_usage": True,
        },
        max_tokens=8192,
        temperature=0.7,
        top_p=0.9,
    )

    # 处理流式响应
    for chunk in chat_completion:
        for choice in chunk.choices:
            if choice.delta.reasoning_content:
                yield choice.delta.reasoning_content
            if choice.delta.content:
                yield choice.delta.content

# 使用生成器函数
for content in main(messages):
    print(content, end='', flush=True)

messages.append({"role": "assistant", "content": content})
messages.append({"role": "user", "content": "我上一句说了啥？"})

print(messages)

for content in main(messages):
    print(content, end='', flush=True)
