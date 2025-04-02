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

    #Getting detail page.
    detailPageUrl = movieEnters[cnt].xpath('./div/div[1]/a/@href')[0]
    detailPageResponse = requests.get(url=detailPageUrl, headers=headers)
    detailPageResponse.encoding = 'utf-8'
    detailPageText = detailPageResponse.text
    detailPageHtml = etree.HTML(detailPageResponse.text)

    #Spidering information. Including a lot of information
    def getInfo(path:str) -> str:
        """
        Short for tree search.
        """
        return detailPageHtml.xpath(path)

    no = getInfo('//*[@id="content"]/div[1]/span[1]/text()')[0]
    title = getInfo('//*[@id="content"]/h1/span[1]/text()')[0]
    year = getInfo('//*[@id="content"]/h1/span[2]/text()')[0]

    #Next are informations that share common patterns. So I put them together using a shared parent root.
    infoRoot = detailPageHtml.xpath('//*[@id="info"]')
    #as long as we're concerned there's only one director.
    director = getInfo('//*[@id="info"]/span[1]/span[2]/a/text()')[0]
    #below are many lists.
    scriptwriter = [i.xpath('./text()')[0] for i in getInfo('//*[@id="info"]/span[2]/span[2]/a')]
    actors = getInfo('//*[@id="info"]//a[@rel = "v:starring"]/text()')#why is the latter invalid using xpath and list comprehension?
    genre = detailPageHtml.xpath('//*[@id="info"]/span[@property="v:genre"]/text()')
    region = re.findall('<span class="pl">制片国家/地区:</span> (.*?)<br/>',detailPageText)[0]
    language = re.findall('<span class="pl">语言:</span> (.*?)<br/>',detailPageText)[0]
    date = getInfo('//*[@id="info"]/span[@property="v:initialReleaseDate"]/text()')
    runtime = getInfo('//*[@id="info"]/span[@property="v:runtime"]/text()')
    nicknames = re.findall('<span class="pl">又名:</span> (.*?)<br/>',detailPageText)[0]
    IMDb = re.findall('<span class="pl">IMDb:</span> (.*?)<br>',detailPageText)[0]
    rating = getInfo('//*[@id="interest_sectl"]/div[1]/div[2]/strong/text()')[0]







    return res

singleMovie(0)

#DATA SAVING