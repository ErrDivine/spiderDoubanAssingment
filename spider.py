#remind! xpath tells you whats next after the current root.
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


#DATA PROCESSING

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
    year = getInfo('//*[@id="content"]/h1/span[2]/text()')[0].lstrip('(').rstrip(')')

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
    runtime = getInfo('//*[@id="info"]/span[@property="v:runtime"]/text()')[0]
    nicknames = re.findall('<span class="pl">又名:</span> (.*?)<br/>',detailPageText)[0]
    IMDb = re.findall('<span class="pl">IMDb:</span> (.*?)<br>',detailPageText)[0]
    rating = getInfo('//*[@id="interest_sectl"]/div[1]/div[2]/strong/text()')[0]
    ratingPeople = getInfo('//*[@id="interest_sectl"]/div[1]/div[2]/div/div[2]/a/span/text()')[0]
    ratingsOnWeight = getInfo('//*[@id="interest_sectl"]//span[@class="rating_per"]/text()')
    betterThan = ['好于'+i.xpath('./text()')[0] for i in getInfo('//*[@id="interest_sectl"]/div[@class="rating_betterthan"]/a')]
    introductionList = getInfo('//*[@id="link-report-intra"]//span[@class="all hidden"]/text()')
    if len(introductionList) == 0:
        introductionList = getInfo('//*[@id="link-report-intra"]/span[1]/text()')
    introduction = ''
    for paragraph in introductionList:
        paragraph = paragraph.strip()
        introduction += paragraph


    basicInfo = {"no":no,
                 "title":title,
                 "year":year,
                 "director":director,
                 "scriptwriter" : scriptwriter,
                 "genre":genre,
                 "region" : region,
                 "language" : language,
                 "date":date,
                 "runtime":runtime,
                 "nicknames":nicknames,
                 "IMDb": IMDb,
                 "rating":rating,
                 "ratingPeople":ratingPeople,
                 "ratingsOnWeight":ratingsOnWeight,
                 "betterThan":betterThan,
                 "introduction" : introduction
                 }

    #start spidering short comments here. I found this page requires turing pages 'cause we need to scrape 30 pieces but in a single page there is only 20. And before all those we need to first enter the 'all comments' link causes it's another site.

    #For the first page:

    #initializing all comments page html etree and text
    allCommentsUrl = getInfo('//*[@id="comments-section"]/div[1]/h2/span/a/@href')[0]
    allCommentsResponse = requests.get(url=allCommentsUrl, headers=headers)
    allCommentsResponse.encoding = 'utf-8'
    allCommentsText = allCommentsResponse.text
    allCommentsHtml = etree.HTML(allCommentsResponse.text)

    #function for scraping a single comment
    def scrapeSingleComment(commentItemRoot) -> dict:#root is xpathable
        commentVote = commentItemRoot.xpath('.//span[@class="votes vote-count"]/text()')[0]
        userName = commentItemRoot.xpath('.//span[@class="comment-info"]/a/text()')[0]
        userRating = commentItemRoot.xpath('./div[2]/h3/span[2]/span[2]/@title')[0]
        commentTime = commentItemRoot.xpath('.//span[@class="comment-time"]/text()')[0].strip()
        commentContent = commentItemRoot.xpath('.//p[@class="comment-content"]/span[1]/text()')[0]
        return {"commentVote":commentVote,
                "userName":userName,
                "userRating":userRating,
                "commentTime":commentTime,
                "commentContent":commentContent
                }

    #getting 20 comment roots of the first page
    #list structure: VOTE,NAME,RATING,TIME,CONTENT  ALL STRING.
    commentList = []
    for root in allCommentsHtml.xpath('//*[@id="comments"]/div[@class="comment-item"]'):
        commentList.append(scrapeSingleComment(root))


    #Now move on to the next page to scrape the last 10 comments. All I have to do is to change the url.
    #initializing html and text
    nextPageUrl = allCommentsUrl[0:-9]+allCommentsHtml.xpath('//*[@id="paginator"]/a[3]/@href')[0]
    nextPageResponse = requests.get(url=nextPageUrl, headers=headers)
    nextPageResponse.encoding = 'utf-8'
    nextPageHtml = etree.HTML(nextPageResponse.text)

    for root in nextPageHtml.xpath('//*[@id="comments"]/div[@class="comment-item"]'):
        commentList.append(scrapeSingleComment(root))
        if len(commentList) == 30:
            break

    #successfully scraping 30 comments and basic information about a single movie. Now return in list and apply the function in a loop.


    res = basicInfo
    res['commentDictionaryList'] = commentList
    return res


finalResult = []
for i in range(10):
    finalResult.append(singleMovie(i))
    print(finalResult[i])

#DATA SAVING
#No I think I'll use json to store the data.
import json
test = json.dumps(finalResult[0])



#initializing
