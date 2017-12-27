import random, json, requests, time
from bs4 import BeautifulSoup

'''
Variables to set within code. 
-re-visit already visit SE links and Blog links: uncomment the lines in runGetSELinks and runGetBlogContent
-to change how many pages / links to fetch, uncomment the "if" at the bottom of the above functions
-if datastore is being made from scratch, comment out the "load" call in every save. Else code will crash trying to read file that does not exist. Uncomment it after the first pass.
-skip google pages in fetchSEPages else Google bans you. Perhaps add extra get params to get around, shuffling IP doesn't work.

-todo: save pages of the meta object to visit next aka save pagination of url. AND do no skip google pages.
 
'''

meta = {
    "se":{
        "g":"https://www.google.com/search?q=site:", 
        "b":"https://www.bing.com/search?q=site:",
        "y":"https://search.yahoo.com/search?q=site:",
        },

    "pub": [
        "time-to-change.org.uk", 
        "themighty.com",
        "tonic.vice.com", 
        "teenvogue.com", 
       # "neatorama.com", 
        "buzzfeed.com", 
        "headsupguys.org",
        "bustle.com",
        "vogue.com",
        "teenvogue.com",
        "7cups",
        "thriveglobal.com",
        #"thesecretlifeofamanicdepressive.wordpress.com",
        "mind.org.uk",
        "nami.org",
        #"sectioneduk.wordpress.com",
        #"mentalhealth.org",
        #"hyperboleandahalf.blogspot.ca",
        "spring.org.uk", 
        "letstalk.12kindsofkindness.com",

    ], 
#episode
    "seterms":{
        "conditions":["anxiety","mental health", "mental illness","panic attack", "holiday blues"], 
        "state":["functioning", "struggle", "recovery", ], 
        "type": ["blog", "story", "feels like", "personal story", "experience", "facts"]
        },

    "se_pg":{
        "g":"&start=", 
        "b":"&first=", 
        "y":"&b=", 
        }, 
    
    "pagenum":{
        "g":0, #multiple of 10
        "b":1, #multiplf or 10 + 1
        "y":1, #multiplf or 10 + 1
        }, 
        
    "urlchecker":{
        "indexurl":["blogs", "experiences", "category", "information"], 
        "articleurl":["article", "story", "stories"],
        "badurls": ['careers', 'contact', 'about', 'faq', 'terms', 'privacy',
              'advert', 'preferences', 'feedback', 'info', 'browse',
              'account', 'subscribe', 'donate', 'shop', 'admin']
        }
}


def hash(strarg):           
    import hashlib
    return str(hashlib.md5(strarg.encode('utf-8')).hexdigest())

#Generate search engine links or read from file
def getSELinks(new = None):
    if new is None:
        print("Genegrating SE Links")
        selinks = {}
        smeta = {}
        for key, se in meta['se'].items():
            for i in range(3):
                pub = random.choice(meta['pub'])
                for i in range(3):
                    condition = random.choice(meta['seterms']['conditions'])
                    for i in range(3):
                        state = random.choice(meta['seterms']['state'])
                        for i in range(3):
                            type = random.choice(meta['seterms']['type'])
                            url = ('{0}{1}+{2}+{3}+{4}{5}{6}'.format(se, pub, condition, state, type, meta['se_pg'][key], meta['pagenum'][key])).replace(" ", "+")
                            selinks[hash(url)] = {'url': url, 'visited':0}

        with open('store/selinks.json', 'w') as outfile:
            json.dump(selinks, outfile)

    else:
        print("Genegrating SE Links")
        with open('store/selinks.json', 'r') as file:
            selinks = json.load(file)
    return selinks


rmade = 0       
arequests = requests.session()     
def makeRequest(url):
    from stem import Signal
    from stem.control import Controller
    from fake_useragent import UserAgent
    ua = UserAgent()

    global rmade, arequests
    
    headers = {'User-Agent': ua.random}
    
    if rmade == 0 or rmade > 13:
        rmade = random.randint(1, 20)
        arequests = requests.session()    

        arequests.proxies = {'http':  'socks5://127.0.0.1:9050',
                             'https': 'socks5://127.0.0.1:9050'}
        
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password="anonbynuamf1204vujw")
            controller.signal(Signal.NEWNYM)
            print("IP changed to " + arequests.get("http://httpbin.org/ip").text)

    t = arequests.get(url, headers=headers).text 
    rmade = rmade + 1
    return t



#Fetch search engine pages and get links from it
def fetchSEPages(selink):
    url = selink['url']
    print("Fetching SE pages from " + url)

    if 'google' in url:
        print('Skipping... because google')
        return 

    html = makeRequest(url)
    import time

    soup = BeautifulSoup(html, 'lxml')
    if 'search.yahoo' in url and not 'We did not find results for' in html:
        links = map(lambda x: x['href'], soup.find_all('a', href=True))
        return filter( lambda x: all( word not in x for word in ['yahoo', 'cache']) and 'http' in x , links)

    elif 'bing' in url and not 'No results found for' in html:
        links = map(lambda x: x['href'], soup.find_all('a', href=True))
        return  filter( lambda x: 'microsoft' not in x and 'http' in x , links)

    elif 'google' in url and not 'did not match any documents' in html:
        links = map(lambda x: x['href'], soup.find_all('a', href=True))
        results = list(filter( lambda x: 'google' not in x and x.rfind("http") != -1 , links))
        return  map( lambda x: x[x.find('http') : x.find('&sa')]  , results)
           

def parseBlogLinks(mapofbloglinks):
    print("Parsing Blog Links")
    blinks = {}
    for link in mapofbloglinks:
        blinks[hash(link)]={'url': link, 'visited':0}
    return blinks

def updateSELinks(newselinks):
    print("Updating SE Links")
    selinks = {}
    with open('store/selinks.json', 'r') as file:
        selinks = json.load(file)
    selinks.update(newselinks)
    with open('store/selinks.json', 'w') as outfile:
       json.dump(selinks, outfile)

def loadBlogLinks():
    with open('store/bloglinks.json', 'r') as file:
        return json.load(file)

def saveBlogLinks(newbloglinks):
    print("Saving blog links")
    bloglinks = loadBlogLinks()
    bloglinks.update(newbloglinks)
    with open('store/bloglinks.json', 'w') as outfile:
        json.dump(bloglinks, outfile)

def getBlogLinks(selinks):
    if selinks is not None:
        try:
            mapofdicts = map(parseBlogLinks, map(fetchSEPages, list(selinks.values())))
            from functools import reduce
            bloglinks = reduce( lambda a,b: a.update(b) or a, mapofdicts)
            #print(bloglinks)
            saveBlogLinks(bloglinks)
            return bloglinks
        except Exception as e:
            print(e)
            return 0
    else:
        return loadbloglinks()

def runGetBlogLinks(selinks):
    
    deletes = []
    for key, value in selinks.items():
        if "google" in value['url']:
            deletes.append(key)
    for x in deletes:
        del selinks[x]

    from collections import OrderedDict
    selinks = OrderedDict(selinks)

    print("total selinks:" + str(len(selinks)))
    selinks = {key:value for key, value in selinks.items() if value['visited'] is 0}
    #selinks = {key:value for key, value in selinks.items()}

    print("filtered selinks:" + str(len(selinks)))

    numlinks = 8
    numloops = (len(selinks) / numlinks) + 1
    i = 0
    while i <= numloops:
        toprocess = dict(list(selinks.items())[ i*numlinks : (i+1)*numlinks ])
        bloglinks = getBlogLinks(toprocess)
        for key, value in toprocess.items():
            toprocess[key]['visited'] = time.time()  
        updateSELinks(toprocess)
        
        #fetch 8*i number of se pages, use this to control how many links to fetc
        if i == 3:
            print("GOT ", 3 * 8 , "SE LINKS")
            break
        i = i+1 

def fetchBlogContent(link):
    from newspaper import Article
    print("Fetching blog content for " + link)
    article = Article(link)
    article.download()
    import time
    time.sleep(1)  
    article.parse()
    article.nlp()
    a = {"title":article.title, 
         "image":article.top_image, 
         "text": article.text, 
         "url":link, 
         "summary":article.summary, 
         "timescraped": time.time()
      }

    return a

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



def loadBlogContent():
    with open('store/blogcontent.json', 'r') as file:
        return json.load(file)

def saveBlogContent(blogcontent):
    print("Saving blog content")
    blogcontent.update(loadBlogContent())
    with open('store/blogContent.json', 'w') as outfile:
        json.dump(blogcontent, outfile)


def getBlogContent(bloglinks):
    if bloglinks is not None:
        try:
            from collections import OrderedDict
            bloglinks = OrderedDict(bloglinks)
            content = {}
            for key, value in bloglinks.items():
                article = fetchBlogContent(value['url'])
                article = cleanBlogContent(article)
                article =  classifyBlogText(article)
                article['url'] = value['url']
                content[key] = article

                bloglinks[key]['visited'] = article['timescraped']
                bloglinks[key]['category'] = article['category']

            saveBlogLinks(bloglinks)
            saveBlogContent(content)
            return [bloglinks, content]
        except Exception as  e:
            print(e)
            return [0,0]                                 
    else:
         getBlogContent(loadBlogLinks())



def runGetBlogContent(blinks):
    numlinks = 8
    numloops = (len(blinks) / numlinks) + 1
    i = 0
    bloglinks = {key:value for key, value in blinks.items() if value['visited'] is 0}
    #bloglinks = {key:value for key, value in blinks.items()}
    while i <= numloops:
        toprocess = dict(list(bloglinks.items())[ i*numlinks : (i+1)*numlinks ]) 
        bl, content = getBlogContent(toprocess)
        i = i+1 
        #fetch 8*i number of blog pages, use this to control how many links to fetc
        '''
        if i == 50:
            print("GOT ", 50 * 8 , "BLOG CONTENT PIECES")
            break
        '''

def uploadToFirebase(dryrun=True):
    import pyrebase
    config = {
        "apiKey": "firebase-adminsdk-491um@airohealthpractice.iam.gserviceaccount.com",
        "authDomain": "https://airohealthpractice.firebaseio.com/",
        "databaseURL": "https://airohealthpractice.firebaseio.com/",
        "storageBucket": "airohealthpractice.appspot.com",
        "serviceAccount": "./airohealthpractice-firebase-adminsdk-491um-9564567345.json"     
        }
     
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()


    bc = loadBlogContent()
    bl = loadBlogLinks()
    bltr = [key for key, value in bl.items() if 'published' not in value or value['published'] is 0]
    blogcontent = {key:bc[key] for key in bltr }

    
    x = sorted(blogcontent.items(),key=lambda x: (x[1]['category']['condition'], x[1]['category']['personal']), reverse=True)

    #x = sorted(blogcontent.items(),key=lambda x: (x[1]['category']['words'], x[1]['category']['condition'], x[1]['category']['personal']), reverse=True)

    y = 0
    content = {}
    for key, value in x[:50]:
        if value['category']['words'] > 1000:
            
            if "https://" in value['image']:
                pass
            elif "http://" in value['image']:
                continue
            else:
                continue

            print(str(y) + " " + value['title'] + str(value['category']))
            y = y+1

            a = {}
            bl[key]['published'] = 1

            import re, urllib
            a['title'] = re.sub('<[^<]+?>', '', value['title'])
            sum = re.sub('<[^<]+?>', '', value['summary'])
            a['summary'] = sum[:sum.find('.')+1]

            a['url'] = urllib.parse.unquote(value['url'])
            a['date'] = value['timescraped']
            a['text'] = value['text']
            a['image'] = value['image']
        
            try:
                print("")
                if not dryrun:
                    db.child("articles").push(a)
                    print("update to firebase worked")
            except Exception as e:
                print("update to firebase failed" + e)
            
            #content['articles/' + db.generate_key()] = a 

    if not dryrun:
        saveBlogLinks(bl)
    print("Total articles: "+ str(y))
    #print(content)
    #db.update(content)




#selinks = getSELinks()
#bloglinks = runGetBlogLinks(selinks)

#runGetBlogContent(loadBlogLinks())

#blogcontent = loadBlogContent()
#print(len(blogcontent))
uploadToFirebase()
