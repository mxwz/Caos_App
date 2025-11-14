def reorder_messages(messages):
    system_message = None
    user_message = None
    assistant_messages = []

    for message in messages:
        if message['role'] == 'system':
            system_message = message
        elif message['role'] == 'user':
            user_message = message
        elif message['role'] == 'assistant':
            assistant_messages.append(message)

    # 构建新的消息列表
    reordered_messages = []
    if system_message:
        reordered_messages.append(system_message)
    if user_message:
        reordered_messages.append(user_message)
    reordered_messages.extend(assistant_messages)

    return reordered_messages

# 示例消息列表
messages = [
    {'role': 'assistant', 'content': '123456789+987654321=？'},
    {'role': 'assistant', 'content': '？'},
    {'role': 'system', 'content': 'You are a helpful assistant'},
    {'role': 'user', 'content': '？'}
]

# 调整顺序
reordered_messages = reorder_messages(messages)
print(reordered_messages)
