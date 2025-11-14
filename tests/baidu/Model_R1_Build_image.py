
import requests
import json


def main():
    url = "https://qianfan.baidubce.com/v2/chat/completions"

    payload = json.dumps({
        "model": "deepseek-vl2",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "分别使用1句话描述以下3张图片的内容"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://aidp-qa***"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://qianfan-test***"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://aidp-***"
                        }
                    }
                ]
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer bce-v3/ALTAK-Q4DPopGoxOy7CJlZjHVzI/e98b5f7b8a59b33f49c9ad30412184f4606fd84c'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


if __name__ == '__main__':
    main()