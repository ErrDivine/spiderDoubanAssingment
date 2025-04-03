import json
import os


with open('dataJsonDir/0_movie.json','r',encoding='utf-8') as f:
    data = json.load(f)
    print(data)


try :
    os.chdir('testDir')
except:
    os.mkdir('testDir')