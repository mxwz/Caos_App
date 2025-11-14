import requests


def get_external_ip():
    response = requests.get('https://cn.apihz.cn/api/ip/ipbaidu.php?id=设置id&key=设置密钥')

    data = response.json()
    return data  # 返回解析后的字典
    # 确保请求成功
    # if response.status_code == 200:
    #     # 解析 JSON 数据
    #     data = response.json()
    #     return data  # 返回解析后的字典
    # else:
    #     print("请求失败:", response.status_code)
    #     return None  # 或者返回一个合适的错误值



if __name__ == "__main__":
    ip = get_external_ip()
    print(ip)
    print(ip['ip'])
