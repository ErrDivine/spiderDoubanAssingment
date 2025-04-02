#coding = 'utf-8'
import requests

headers = {
"Cookie":
'bid=l2KfqCMyn4g; ap_v=0,6.0; __utma=30149280.1753810326.1743582861.1743582861.1743582861.1; __utmc=30149280; __utmz=30149280.1743582861.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt_douban=1; dbcl2="258445163:hV3NAWe93tE"; ck=H8iW; __utmb=30149280.4.10.1743582861',

'User-Agent':
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}
url = "https://movie.douban.com/top250"

response = requests.get(url=url,headers=headers)
response.encoding = 'utf-8'
html = response.text


print(response.status_code)
print(html)