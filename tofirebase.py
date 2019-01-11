import pyrebase
content = {}

feed  = feedparser.parse('https://www.google.ca/alerts/feeds/00090353185029031169/16879600919504319759')

dt = datetime.fromtimestamp(mktime(feed.feed.updated_parsed))

print(feed.feed.title + " " + feed.feed.updated )
exit()

for key, value in feed.feed:
    print(key)

exit()

config = {

    #config properties go here

}
firebase = pyrebase.initialize_app(config)
db = firebase.database()


for entry in feed.entries:
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
        a['image'] = article.top_image
        
        
        content['articles/' + db.generate_key()] = a

    except Exception as e:
        print("SKIPPING: ", e)
        pass
    
print("==============FINISHED===============")

pp.pprint(content)
#db.update(content)

