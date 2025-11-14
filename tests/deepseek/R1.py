from openai import OpenAI
client = OpenAI(api_key="sk-382b3bd8e6b6435b8ffb1ab79ab88cb8", base_url="https://api.deepseek.com")

# Round 1
messages = [{"role": "user", "content": "9.11 and 9.8, which is greater?"}]
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages,
    stream=True
)

reasoning_content = ""
content = ""

print(response)

for chunk in response:
    if chunk.choices[0].delta.reasoning_content:
        reasoning_content += chunk.choices[0].delta.reasoning_content
        print(reasoning_content)
    else:
        content += chunk.choices[0].delta.content
        print(content)

# Round 2
messages.append({"role": "assistant", "content": content})
messages.append({'role': 'user', 'content': "How many Rs are there in the word 'strawberry'?"})
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages,
    stream=True
)


reasoning_content = ""
content = ""

for chunk in response:
    if chunk.choices[0].delta.reasoning_content:
        reasoning_content += chunk.choices[0].delta.reasoning_content
        print(reasoning_content)
    else:
        content += chunk.choices[0].delta.content
        print(content)


# from openai import OpenAI
# client = OpenAI(api_key="sk-382b3bd8e6b6435b8ffb1ab79ab88cb8", base_url="https://api.deepseek.com")
#
# # Round 1
# messages = [{"role": "user", "content": "9.11 and 9.8, which is greater?"}]
# response = client.chat.completions.create(
#     model="deepseek-reasoner",
#     messages=messages
# )
#
#
# print(response)
#
# reasoning_content = response.choices[0].message.reasoning_content
# content = response.choices[0].message.content
#
# print(reasoning_content)
# print(content)
#
#
# # Round 2
# messages.append({'role': 'assistant', 'content': content})
# messages.append({'role': 'user', 'content': "How many Rs are there in the word 'strawberry'?"})
# response = client.chat.completions.create(
#     model="deepseek-reasoner",
#     messages=messages
# )
#
#
# print(response)
#
# reasoning_content = response.choices[0].message.reasoning_content
# content = response.choices[0].message.content
#
# print(reasoning_content)
# print(content)