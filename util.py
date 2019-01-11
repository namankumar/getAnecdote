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

