import requests
import re
from lxml import etree

#INITIALIZING

#Using cookie and user-agent to avoid being blocked. But the hole accepted header will cause a disorder in response and I still don't knoe why.
headers = {
"Cookie":
'bid=l2KfqCMyn4g; ap_v=0,6.0; __utma=30149280.1753810326.1743582861.1743582861.1743582861.1; __utmc=30149280; __utmz=30149280.1743582861.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt_douban=1; dbcl2="258445163:hV3NAWe93tE"; ck=H8iW; __utmb=30149280.4.10.1743582861',

'User-Agent':
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

url = 'https://movie.douban.com/subject/1291546/'

response = requests.get(url=url, headers=headers)
response.encoding = 'utf-8'
text = response.text
html = etree.HTML(text)

content = html.xpath('//*[@id="link-report-intra"]/span[1]/text()')

res = ''
for i in content:
    res += i.lstrip('\n').strip().strip('\u3000\u3000')

print(res)