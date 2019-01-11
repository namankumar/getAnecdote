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


def cleanBlogContent(article):
    print("Cleaning strings")
    def clean(blogtext):
        import re
        blogtext = re.sub(r'(^.*\[Embed\].*$)', '\n', blogtext, flags=re.IGNORECASE|re.MULTILINE)
        blogtext = re.sub(r'(^.*click here.*$)', '\n', blogtext, flags=re.IGNORECASE|re.MULTILINE)
        blogtext = re.sub(r'(^.*Bustle on.*$)', '\n', blogtext, flags=re.IGNORECASE|re.MULTILINE)
        blogtext = re.sub(r'(^.*Share This.*$)', '\n', blogtext, flags=re.IGNORECASE|re.MULTILINE)
        blogtext = re.sub(r'(^.*Share On.*$)', '\n', blogtext, flags=re.IGNORECASE|re.MULTILINE)
        blogtext = re.sub(r'(^.*Advertisement.*$)', '\n', blogtext, flags=re.IGNORECASE|re.MULTILINE)
        blogtext = re.sub(r'(^.*Advertisements.*$)', '\n', blogtext, flags=re.IGNORECASE|re.MULTILINE)
        blogtext = re.sub(r'(^.*more from tonic:.*$)', '\n', blogtext, flags=re.IGNORECASE|re.MULTILINE)
        blogtext = re.sub(r'(^.*images.*$)', '\n', blogtext, flags=re.IGNORECASE|re.MULTILINE)
        blogtext = re.sub(r'(^.*read this next:.*$)', '\n', blogtext, flags=re.IGNORECASE|re.MULTILINE)
        blogtext = re.sub(r'(\n.\n)', '\n', blogtext, flags=re.IGNORECASE|re.MULTILINE)
        blogtext = re.sub(r'(^.*image:.*$)', '\n', blogtext, flags=re.IGNORECASE|re.MULTILINE)
        blogtext = re.sub(r'(^.*illustration by.*$)', '\n', blogtext, flags=re.IGNORECASE|re.MULTILINE)
        blogtext = re.sub('\n\s*\n', '\n\n', blogtext, flags=re.IGNORECASE|re.MULTILINE)
        return blogtext

    article['text'] = clean(article['text'])
    article['summary'] = clean(article['summary'])
    return article

def classifyBlogText(article):
    print("Extracting classification features ")
    firstperson = ['i', 'im', 'we', 'us','me','mine', 'our', 'ours']
    secondperson = ['you', 'your']
    thirdperson = ['he', 'she', 'his', 'her', 'they', 'them', 'their']
    condition = ['anxiety','anxious', 'depression', 'depressed', 'mental']
    recovery = ['recover', 'recovery', 'functioning', 'high-functioning']
    
    numpers = numsec = numthird = numcond = numre = 0
    
    w = 0
    for word in article['text'].lower().replace('\'',' ').split(' '):
        w = w + 1
        if word in firstperson:
            numpers = numpers + 1
        if word in secondperson:
            numsec = numsec + 1
        if word in thirdperson:
            numthird = numthird + 1
        if word in condition:
            numcond = numcond + 1
        if word in recovery:
            numre = numre + 1
    
    cat = {'words': w,'personal': numpers, 'thirdperson': numthird,'condition': numcond, 'recovery': numre}

    article['category'] = cat
    return article

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
            a = cleanBlogContent(a)
            a =  classifyBlogText(a)

            content[str(hashlib.md5(link.encode('utf-8')).hexdigest())] = a

            '''
            with open('story/'+a['title']+'.txt', 'w') as file:
                file.write(a['text'])
            '''

        except Exception as e:
            print("SKIPPING: ", e)
            pass

print("==============FINISHED===============")
pp.pprint(content)

#with open('store/feedlist.json', 'w') as outfile:
#    json.dump(feeds, outfile)

oldcontent = ''
with open('store/content.json', 'r') as file:
    oldcontent = json.load(file)
    print(oldcontent)

oldcontent.update(content)

with open('store/content.json', 'w') as file:
    json.dump(oldcontent, file)
