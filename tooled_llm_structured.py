import requests
import os
from datetime import datetime
import json




# 定义工具列表，模型在选择使用哪个工具时会参考工具的name和description
tools = [
    # 工具1 获取当前时刻的时间
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "当你想知道现在的时间时非常有用。",
            "parameters": {}  # 因为获取当前时间无需输入参数，因此parameters为空字典
        }
    },
    # 工具2 获取指定城市的天气
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的天气时非常有用。",
            "parameters": {  # 查询天气时需要提供位置，因此参数设置为location
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。"
                    }
                }
            },
            "required": [
                "location"
            ]
        }
    }
]


# 模拟天气查询工具。返回结果示例：“北京今天是晴天。”
def get_current_weather(location):
    if isinstance(location, dict):
        location = location['location']
    def get_weather_info(location):
        params = {
            "key": "So8QqzdeTxup9prhM",
            "location": location,
            "language": "zh-Hans",
            "unit": "c",
        }

        url = "https://api.seniverse.com/v3/weather/now.json"
        r = requests.get(url, params=params)
        ## 免费用戶只能调用实时天气等功能，对特定日期不做强求
        data = r.json()["results"][0]['now']
        # TODO： 完成对天气、温度等的信息提取，并返回一段message
        return data
    result = get_weather_info(location)
    print(result)
    return f"{location}今天是{result['text']}天。"#some errors here


# 查询当前时间的工具。返回结果示例：“当前时间：2024-04-15 17:15:18。“
def get_current_time():
    # 获取当前日期和时间
    current_datetime = datetime.now()
    # 格式化当前日期和时间
    formatted_time = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    # 返回格式化后的当前时间
    return f"当前时间：{formatted_time}。"


def get_response(messages):
    # TODO：你自己的API
    api_key = "sk-46f61c60859f4d19a1de714803d10f3e"
    url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {api_key}'}
    body = {
        'model': 'qwen-turbo',
        "input": {
            "messages": messages
        },
        "parameters": {
            "result_format": "message",
            "tools": tools
        }
    }

    print(messages)
    response = requests.post(url, headers=headers, json=body)
    return response.json()


messages = [
    {
        "role": "user",
        "content": "今天天气怎么样？"
    }
]


def call_with_messages():
    messages = [
        {
            "content": input('请输入：'),  # 提问示例："现在几点了？" "一个小时后几点" "北京天气如何？"
            "role": "user"
        }
    ]

    # 模型的第一轮调用
    first_response = get_response(messages)
    print(f"\n第一轮调用结果：{first_response}")
    assistant_output = first_response['output']['choices'][0]['message']
    messages.append(assistant_output)
    if 'tool_calls' not in assistant_output:  # 如果模型判断无需调用工具，则将assistant的回复直接打印出来，无需进行模型的第二轮调用
        print(f"最终答案：{assistant_output['content']}")
        return
    # 如果模型选择的工具是get_current_weather
    elif assistant_output['tool_calls'][0]['function']['name'] == 'get_current_weather':
        tool_info = {"name": "get_current_weather", "role": "tool"}
        location = json.loads(assistant_output['tool_calls'][0]['function']['arguments'])['location']
        tool_info['content'] = get_current_weather(location)
    # 如果模型选择的工具是get_current_time
    elif assistant_output['tool_calls'][0]['function']['name'] == 'get_current_time':
        tool_info = {"name": "get_current_time", "role": "tool"}
        tool_info['content'] = get_current_time()
    print(f"工具输出信息：{tool_info['content']}")
    messages.append(tool_info)

    # 模型的第二轮调用，对工具的输出进行总结
    second_response = get_response(messages)
    print(f"第二轮调用结果：{second_response}")
    print(f"最终答案：{second_response['output']['choices'][0]['message']['content']}")


if __name__ == '__main__':
    call_with_messages()