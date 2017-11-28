import os,re, sys; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import string
from pattern.web import Google, plaintext, DOM, SOUP
from pattern.web import SEARCH
from pattern.web import Crawler, DEPTH, BREADTH, FIFO, LIFO

from pattern.db import Database, SQLITE, MYSQL
from pattern.db import STRING, DATE, NOW, field, pk, pd

email_regex = re.compile('([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4})', re.IGNORECASE)
author_regex = re.compile('(author|creator|Person)', re.IGNORECASE)
descr_regex = re.compile('(description)', re.IGNORECASE)


q = "mental health"


db = Database(pd("scrape_store.db"), type=SQLITE)
if not "emails" in db:
    schema = ( pk(), 
               field("email", STRING(50)),
               field("author", STRING(50)),
               field("url", STRING(50)),
               field("attr_rel", STRING(50)),
               field("attr_text", STRING(50)),
               field("context", STRING(50)),
               field("date_scraped", DATE, default=NOW),
               field("referrer", STRING(50)),
               field("search_term", STRING(50)),
               field("source", STRING(50)),
               )
    db.create("emails", schema)


def getProperties(source):
    author=''
    descr=''

    dom = DOM(source)

    for elem in dom.head:
        if elem.type is "element":
            try:
                for auth in author_regex.findall(elem.source):
                    author = elem.attrs["content"]
            except Exception as e:
                print("EXCEPTION ENCOUNTERED")

            
            try:
                for desc in descr_regex.findall(elem.source):
                    descr = elem.attrs["content"]
                    descr = dom.head.by_tag('title')[0].content +" || "+ descr
            except Exception as e:
                print("EXCEPTION ENCOUNTERED")
                
            
    if author == '':        
        for elem in dom.body:
            if elem.type is "element":
                try:
                    for auth in author_regex.findall(elem.source):
                        author = elem.content
                except Exception as e:
                    print("EXCEPTION ENCOUNTERED")

  
        

    return [author, descr]



class MineTheWeb(Crawler):

    def visit(self, link, source=None):
        print("Visiting: %s from: %s" % (link.url, link.referrer))
    
        author, descr = getProperties(source)
	
        emails = []
        for email in email_regex.findall(source):
            emails.append(email)
    
        db.emails.append(
            email=string.join(emails), 
            author=author,
            url=link.url, 
            attr_rel=link.relation, 
            attr_text=link.text, 
            context=descr, 
            referrer=link.referrer, 
            search_term=q,
            source="scrape"
            )
            

    def fail(self, link):
        print("failed: %s" % link.url)

    def priority(self, link, method):
        if "airohealth.com" in link.url:
            return 0.0
        elif "airohealth.com" in link.referrer:
            return 0.0
        else:
            return Crawler.priority(self, link, method)


# Google is very fast but you can only get up to 100 (10x10) results per query.
engine = Google(license=None, language="en")
for i in range(1, 10):
    for result in engine.search(q, start=i, count=10, type=SEARCH, cached=True):
        print("Crawling: ", result.title)
        crawler = MineTheWeb(links=[result.url])
        while len(crawler.visited) < 10:
            crawler.crawl(method=DEPTH, cached=True)
        
