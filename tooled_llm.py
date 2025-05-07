import json

from spiderDoubanAssingment.tooled_llm_structured import get_current_weather,get_current_time
from tooled_llm_structured import call_with_messages,get_response
from tooled_llm_structured import tools
import requests

tools_append = [
    {
        'type' : 'function',
        'function' :{
            'name': 'get_weather_anytime',
            'description' : '当你想查询指定城市指定时间的天气时非常有用。',
            'parameters' : {
                'type' : 'object',
                'properties' : {
                    'location' :{
                        'type' : 'string',
                        'description' : '城市或县区，比如北京市、杭州市、余杭区等。'
                    },
                    'time' : {
                        'type' : 'string',
                        'description' : '具体到日期的时间，比如2025-06-04、2023-04-05、2021-11-23。如果为今天、明天、后天等形式，需要调用get_current_time获取当前时间再推出具体日期。'
                    },
                }
            },
        }
    },
    {
        'type' : 'function',
        'function' :{
            'name' : 'get_movie_info',
            'description':'当你想查询电影的资料的时候非常有用。',
            'parameters' : {
                'type' : 'object',
                'properties' : {
                    'name':{
                        'type' : 'string',
                        'description' : '中文的电影名，如果是其他语言先转化成中文再提交。'
                    }
                }
            }
        }
    },
    {
        'type' : 'function',
        'function' :{
            'name' : 'calculator_tool',
            'description' : '当你想进行计算的时候非常有用。',
            'parameters' : {
                'type' : 'object',
                'properties' : {
                    'expression' :{
                        'type' : 'string',
                        'description' : '符合Python语法的计算式，比如2+2、3*4、10/2、2.5+3.5、（1+2）*3，1e7+3。'
                    },
                }
            } ,
        }
    },
]


tools.extend(tools_append)


#FUNCTIONS----------------------------------------
def get_weather_anytime(para):
    location = para['location']
    time = para['time']
    params = {
        "key": "Smab3zQeEWIlOGGRA",
        "location": location,
        "language": "zh-Hans",
        "unit": "c",
        "start" : 0,
        'days' : 15
    }

    url = "https://api.seniverse.com/v3/weather/daily.json"
    r = requests.get(url, params=params)
    data = r.json()["results"][0]['daily']
    for i in data:
        if i['date'] == time:
            data = i
            break
    print(data)
    # TODO： 完成对天气、温度等的信息提取，并返回一段message
    return str(data)
    #return f"{location}在{time}是{data['text_day']}天，气温最低{data['low']}度,最高{data['high']}度。"


def get_movie_info(para):
    name = para['name']
    movie_list = ['肖申克的救赎','霸王别姬','泰坦尼克号','阿甘正传','千与千寻','美丽人生','这个杀手不太冷','星际穿越','盗梦空间','楚门的世界']
    if name not in movie_list:
        return "这部电影不在豆瓣前十，暂无信息。"
    index = movie_list.index(name)
    with open(f'dataJsonDir/{index}_movie.json','r') as file:
        movie_dict = json.load(file)
    return str(movie_dict)


def calculator_tool(para) :
    """
    计算数学表达式的值

    Args:
        expression (str): 要计算的数学表达式字符串

    Returns:
        float: 计算结果

    Raises:
        ValueError: 当表达式无效或包含非法字符时
    """
    #转化参数
    expression = para['expression']
    # 移除所有空格
    expression = expression.replace(" ", "")

    # 检查表达式是否只包含允许的字符
    allowed_chars = set("0123456789+-*/().")
    if not all(char in allowed_chars for char in expression):
        return "表达式包含非法字符"

    try:
        # 使用 eval 计算表达式
        result = eval(expression)
        return f"结果是{result}。"
    except Exception as e:
        return f"表达式计算错误: {str(e)}"




#----------------------------------------------------------------



#MAPPER-----------------------------------------------------------
function_mapper = {
    'get_weather_anytime' : get_weather_anytime,
    'get_current_time' : get_current_time,
    'get_current_weather' : get_current_weather,
    'get_movie_info' : get_movie_info,
    'calculator_tool' : calculator_tool,
}

#-----------------------------------------------------------------

#EXECUTION--------------------------------------------------------

def llm_action(messages):
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
    print(response.json())
    choice = response.json()['output']['choices'][0]
    messages.append(choice['message'])
    if choice['finish_reason'] == 'tool_calls':
        tool_info = {"name": choice['message']['tool_calls'][0]['function']['name'], "role": "tool"}
        arguments = eval(choice['message']['tool_calls'][0]['function']['arguments'])
        if arguments:
            tool_info["content"] = function_mapper[tool_info['name']](arguments)
        else:
            tool_info["content"] = function_mapper[tool_info['name']]()
        messages.append(tool_info)
        return llm_action(messages)

    elif choice['finish_reason'] == 'stop':
        return choice['message']['content'],messages




def converse(messages):
    query = str(input('请与大模型对话:'))
    if query == 'exit':
        print('goodbye!')
        return None
    messages.append({"content":query,
                     "role":"user"
                })
    response = llm_action(messages)
    print(response[0])
    converse(response[1])



#---------------------------------------------------------------

if __name__ == '__main__':
    converse(
        [
            {
                'role':'system',
                'content' : '尽量调用多个函数。优先在上下文中查找。'
            }
        ]
    )

