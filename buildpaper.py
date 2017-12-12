from newspaper import Article
import random, json, requests
from bs4 import BeautifulSoup


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
        "neatorama.com", 
        "buzzfeed.com", 
        "headsupguys.org",
        "bustle.com",
        "vogue.com",
        "teenvogue.com",
        "7cups",
        "thriveglobal.com",
        "thesecretlifeofamanicdepressive.wordpress.com",
        "mind.org.uk",
        "nami.org",
        "sectioneduk.wordpress.com",
        "mentalhealth.org",
        "hyperboleandahalf.blogspot.ca",
        "spring.org.uk", 
        "letstalk.12kindsofkindness.com",

    ], 

    "seterms":{
        "conditions":["anxiety","mental health", "mental illness","panic attack"], 
        "state":["functioning", "struggle", "recovery"], 
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
                            hkey = hash(url)
                            selinks[hkey] = url
                            smeta[hkey]  = 0

        with open('store/selinks.json', 'w') as outfile:
            json.dump(selinks, outfile)

        with open('store/selinks_meta.json', 'w') as file:
            json.dump(smeta, file)

    else:
        with open('store/selinks.json', 'r') as file:
            selinks = json.load(file)
            
    return selinks

def updateSEmeta(slinks):
    with open('store/selinks_meta.json', 'r') as file:
        metadata = json.load(file)
    metadata.update(slinks)
    with open('store/selinks_meta.json', 'w') as outfile:
        json.dump(metadata, outfile)

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
def fetchSEPages(url):
    #if "google" in url:
     #   return
    print("Getting blog links from " + url)
    html = makeRequest(url)
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
    blinks = {}
    for link in mapofbloglinks:
        blinks[hash(link)]=link
    return blinks

def loadBlogLinks():
    with open('store/bloglinks.json', 'r') as file:
        return json.load(file)

def saveBlogLinks(bloglinks):
   bloglinks.update(loadBlogLinks())
    with open('store/bloglinks.json', 'w') as outfile:
        json.dump(bloglinks, outfile)

def getBlogLinks(selinks):
    if selinks is not None:
        try:
            mapofbloglinks = map(fetchSEPages, selinks.values())
            mapofdicts = map(parseBlogLinks, mapofbloglinks)
            from functools import reduce
            bloglinks = reduce( lambda a,b: a.update(b) or a, mapofdicts)
            print(bloglinks)
            saveBlogLinks(bloglinks)
            return bloglinks
        except:
            return 0
    else:
        return loadbloglinks()

def cleanBlogLinks(url):
    return link


selinks = getSELinks()

deletes = []
for key, value in selinks.items():
    if "google" in value:
        deletes.append(key)
for x in deletes:
    del selinks[x]

print("left urls: " + str(len(selinks)))

from collections import OrderedDict
selinks = OrderedDict(selinks)

numlinks = 8
numloops = len(selinks) / numlinks
i = 0
while i <= numloops:
    toprocess = dict(list(selinks.items())[ i*numlinks : (i+1)*numlinks ])
    bloglinks = getBlogLinks(toprocess)
    for key, value in toprocess.items():
        toprocess[key] = 1    
    updateSEmeta(toprocess)
    i = i+1

print("DONE")
print("========================================")

exit()
for hash, link in bloglinks.items():
    article = Article(link)
    article.download()
    article.parse()
    print(link + "  " + len(article.text))
