#repeat: My task is to spider down 10 movies' information.
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

#The url of douban top 250 movies
baseUrl = "https://movie.douban.com/top250"



#SEND REQUESTS

#getting response
response = requests.get(url=baseUrl, headers=headers)
response.encoding = 'utf-8'
print(response.status_code)


#DATA PRCESSING

#initialization

html = etree.HTML(response.text)
movieEnters = html.xpath('//*[@id="content"]/div/div[1]/ol/li')




#Function for processing a single movie.Parameters are numbers.Return values are a dict.Outer loops is only responsible for counting numbers.
def singleMovie(cnt:int) -> dict:

    #result for the final dictionary
    res = {}

    # Entering detail page
    newUrl = movieEnters[cnt].xpath('./div/div[1]/a/text()')
    print(newUrl)





    return res

singleMovie(0)

#DATA SAVING