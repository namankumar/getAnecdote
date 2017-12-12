import json, feedparser, pprint, re, urllib.parse
from newspaper import Article
from time import mktime
from datetime import datetime
import hashlib,  pickle, ast

pp = pprint.PrettyPrinter(depth=6)
content = {}
date = ''
feeds = json.load(open('store/feedlist.json'))
#feeds = feeds['list']

for name in feeds:
    newfeed  = feedparser.parse(feeds[name]['url'])

    prevfeed = datetime.strptime(feeds[name]['prevfeed'] ,'%Y-%m-%dT%H:%M:%SZ')
    updatedat = datetime.fromtimestamp(mktime(newfeed.feed.updated_parsed))
    
    if prevfeed >= updatedat:
        print(name, " feed not updated. Skipping.")
        continue

    #update previous feed 
    feeds[name]['prevfeed'] = newfeed.feed.updated
    
    print("Getting for FEED: ", name)
    for entry in newfeed.entries:

        a = {}
        a['title'] = re.sub('<[^<]+?>', '', entry.title)
        a['summary'] = re.sub('<[^<]+?>', '', entry.summary)
        a['url'] = link = urllib.parse.unquote(entry.link[entry.link.find('url=')+4    :   entry.link.find("&ct=")])
        a['date'] = entry.published
    
        try:
            print('trying for this:  ', link)
            article = Article(link)
            article.download()
            article.parse()
            a['text'] = article.text
    
        
            #skip if less than 300 words
            if len(a['text'].split(' ')) < 300:
                continue

            a['image'] = article.top_image
            a['subject'] = name
            content[str(hashlib.md5(link.encode('utf-8')).hexdigest())] = a


            with open('story/'+a['title']+'.txt', 'w') as file:
                file.write(a['text'])


        except Exception as e:
            print("SKIPPING: ", e)
            pass

print("==============FINISHED===============")
pp.pprint(content)

with open('store/feedlist.json', 'w') as outfile:
    json.dump(feeds, outfile)

oldcontent = ''
with open('store/content.json', 'r') as file:
    oldcontent = json.load(file)
    print(oldcontent)

oldcontent.update(content)

with open('store/content.json', 'w') as file:
    json.dump(oldcontent, file)
