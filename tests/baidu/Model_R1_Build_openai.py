# 请安装 OpenAI SDK : pip install openai
# apiKey 获取地址： https://console.bce.baidu.com/iam/#/iam/apikey/list
# 支持的模型列表： https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu
import time

from openai import OpenAI

messages = [{
            "role": "user",
            "content": "1+1等于几？"
        },
    ]

def main(message):
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
    print(chat_completion)

    response = ""
    response_reasoning = ""
    start_time_reasoning = None
    end_time_reasoning = None
    start_time_content = None
    end_time_content = None

    # 处理流式响应
    for chunk in chat_completion:
        # print(chunk)
        for choice in chunk.choices:
            if choice.delta.reasoning_content:
                if start_time_reasoning is None:
                    start_time_reasoning = chunk.created  # 记录第一条reasoning_content的创建时间

                print(choice.delta.reasoning_content, end='')
                response_reasoning += choice.delta.reasoning_content
            if choice.delta.content:
                if start_time_content is None:
                    end_time_reasoning = time.time()

                    start_time_content = chunk.created  # 记录第一条content的创建时间

                print(choice.delta.content, end='')
                response += choice.delta.content
        # 为了确保实时输出，使用flush
        print('', flush=True)
    end_time_content = time.time()

    duration_reasoning = end_time_reasoning - start_time_reasoning
    duration_content = end_time_content - start_time_content

    print(
        f"Reasoning Duration: {duration_reasoning:.2f} seconds")
    print(f"Content Duration: {duration_content:.2f} seconds")

    return response_reasoning, response, duration_reasoning, duration_content

response_reasoning, response, duration_reasoning, duration_content = main(messages)


messages.append({"role": "assistant", "content": response_reasoning})
messages.append({"role": "assistant", "content": response})
messages.append({"role": "user", "content": "我上一句说了啥？"})

print(messages)
response_reasoning, response, duration_reasoning, duration_content = main(messages)


# chat_completion = client.chat.completions.create(
#     model="deepseek-r1",
#     messages=messages,
#     stream=True,
#     stream_options={
#         "include_usage": True,
#     },
#     max_tokens=8192,
#     temperature=0.7,
#     top_p=0.9,
# )
# print(chat_completion)
#
# response = ""
# response_reasoning = ""
#
# # 处理流式响应
# for chunk in chat_completion:
#     for choice in chunk.choices:
#         if choice.delta.reasoning_content:
#             print(choice.delta.reasoning_content, end='')
#             response_reasoning += choice.delta.reasoning_content
#         if choice.delta.content:
#             print(choice.delta.content, end='')
#             response += choice.delta.content
#     # 为了确保实时输出，使用flush
#     print('', flush=True)