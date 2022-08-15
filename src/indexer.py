import sys
from collections import defaultdict
import time
import re
import xml.sax
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import *
from Stemmer import Stemmer
import os

try:
    nltk.download('stopwords')
except:
    pass
stop_words = set(stopwords.words('english'))
stemmer = Stemmer('porter')

pagecount = 0
index = defaultdict(list)
max_tokens = 15000
max_docs = 15000
filecount = 0
tokens_encountered = 0
tokens_in_index = 0

try:
    os.mkdir('data2')
except:
    pass

directory = sys.argv[2]

## NOTES ##
# check about title_arr
# check out PyStemmer


class IndexBnaLe:
    def __init__(this, t, b, i, c, l, r):
        this.__r = r
        this.__l = l
        this.__c = c
        this.__i = i
        this.__b = b
        this.__t = t
        
    def get_ref(this):
        return this.__r
    
    def get_links(this):
        return this.__l
    
    def get_cat(this):
        return this.__c
    
    def get_info(this):
        return this.__i
    
    def get_body(this):
        return this.__b
    
    def get_title(this):
        return this.__t

    def create_dict(this, x):
        d = defaultdict(int)
        for i in x:
            d[i] += 1

        return d

    def indexer(this):
        global tokens_in_index
        global pagecount
        global max_tokens
        global index
        global filecount

        num = pagecount
        words = set()

        title = this.create_dict(this.get_title())
        words.update(this.get_title())

        body = this.create_dict(this.get_body())
        words.update(this.get_body())

        info = this.create_dict(this.get_info())
        words.update(this.get_info())

        categories = this.create_dict(this.get_cat())
        words.update(this.get_cat())

        links = this.create_dict(this.get_links())
        words.update(this.get_links())

        references = this.create_dict(this.get_ref())
        words.update(this.get_ref())

        for i in words:
            tokens_in_index +=1
            s = 'd' + str(num)

            tit = title[i]
            if tit:
                s += 't' + str(tit)
            bod = body[i]
            if bod:
                s += 'b' + str(bod)
            inf = info[i]
            if inf:
                s += 'i' + str(inf)
            cat = categories[i]
            if cat:
                s += 'c' + str(cat)
            lin = links[i]
            if lin:
                s += 'l' + str(lin)
            ref = references[i]
            if ref:
                s += 'r' + str(ref)

            index[i].append(s)

        pagecount += 1
        if pagecount % max_docs == 0:
            print(pagecount)
            printFile()


def printFile():
    global index
    global filecount

    name = directory + 'index' + str(filecount) + '.txt'
    file = open(name, 'w')

    for word in sorted(index.keys()):
        s = word + ':'
        posting = index[word]
        s += ' '.join(posting)
        file.write(s + '\n')
    file.close()

    index = defaultdict(list)
    print('created file', filecount)
    filecount += 1


class PtaNiBhai():
    def __init__(this):
        pass

    def tokenise(this, data):  # working
        global tokens_encountered
        data = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ', data) # removing html entities
        data = re.sub(r'http[s]?\S*[\s | \n]', r' ', data) # removing urls
        toks = re.split(r'[^A-Za-z0-9]+', data)
        finaal = list()
        for i in toks:
            tokens_encountered+=1
            word = stemmer.stemWord(i)
            if (
                len(word) <= 1 or len(word) > 45 or word in stop_words
            ):  # check for word length
                continue
            finaal.append(word)

        return finaal

    def processTitle(this, title):  # working
        title = title.lower()
        title = this.tokenise(title)
        return title

    def categoriesChahiye(this, text):  # working
        cat = list()

        cat = re.findall(r'\[\[category:(.*)\]\]',text)
        data = this.tokenise(' '.join(cat))
        return data

    def referencesChahiye(this, text):  # try to change
        refarr = list()
        reflist = re.findall(r'\|\s*title[^\|]*', text)
        for i in reflist:
            refarr.append(i.replace('title', '', 1))
        
        data = this.tokenise(' '.join(refarr))
        return data

    def linksChahiye(this, text):  # should http be removed?
        data = text.split('\n')
        links = list()

        for i in data:
            if re.match(r'\*\s*\[', i):  # confirm regex
                links.append(i)

        data = this.tokenise(' '.join(links))
        return data

    def infoboxChahiye(this, text):  # working
        # check = re.split(r'\{\{infobox', text)
        check = text.split('{{infobox')
        x = len(check)
        info = list()

        if x <= 1:
            return info

        flag = False
        data = text.split('\n')
        for i in data:
            f = re.match(r'\{\{infobox', i)
            if f:
                flag = True
                i = re.sub(r'\{\{infobox(.*)', r'\1', i)
                info.append(i)
            elif flag:
                if i == '}}':
                    flag = False
                    continue
                info.append(i)

        info = this.tokenise(' '.join(info))
        return info

    def bodyChahiye(this, text):  # check if 'redirect' has to be removed
        data = re.sub(r'\{\{.*\}\}', r' ', text)
        data = this.tokenise(data)
        return data

    def processContent(this, text, title):
        text = text.lower()
        title = this.processTitle(title)

        references = list()
        categories = list()
        links = list()

        data = re.split(r'==\s*references\s*==', text)
        if len(data) > 1:
            link_hai = True
            data2 = re.split(r'==\s*external links\s*==', data[1])
            if len(data2) == 1:
                links = list()
                link_hai = False
            if link_hai:
                x = data2[1]
                links = this.linksChahiye(x)
            
            x = data[1]
            references = this.referencesChahiye(x)
            categories = this.categoriesChahiye(x)
        else:
            link_hai = True
            categories = this.categoriesChahiye(data[0])

            data2 = re.split(r'==\s*external links\s*==', data[0])
            if len(data2) == 1:
                links = list()
                link_hai = False
            if link_hai:
                links = this.linksChahiye(data2[1])

        x = data[0]
        infobox = this.infoboxChahiye(x)
        body = this.bodyChahiye(x)

        return title, body, infobox, categories, links, references


class Document_Handler(xml.sax.ContentHandler):
    def __init__(this):
        this.abhi = ''
        this.title = ''
        this.text = ''
        this.data = ''
        print('handler called')

    # call when an element starts
    def startElement(this, tag, attributes):
        this.abhi = tag
        
    def index(this, t,b,i,c,l,r):
        ind = IndexBnaLe(t,b,i,c,l,r)
        ind.indexer()
        this.abhi = ''
        this.title = ''
        this.text = ''
        

    # Call when an elements ends
    def endElement(this, tag):
        global pagecount
        if tag == 'page':
            d = PtaNiBhai()
            title, body, info, categories, links, references = d.processContent(this.text, this.title)
            this.index(title, body, info, categories, links, references)
            print("page count: ", pagecount)

    def characters(this, content):
        if this.abhi == 'title':
            this.title += content
        elif this.abhi == 'text':
            this.text += content


        
def Parser(file):
    parser = xml.sax.make_parser() # create an XMLReader
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)  # turn off namepsaces
    handler = Document_Handler()  # making a custom handler
    parser.setContentHandler(handler)
    parser.parse(file)


if __name__ == '__main__':
    st = time.time()
    parser = Parser(sys.argv[1])
    printFile()

    filename = sys.argv[3]
    with open(filename, 'w') as f:
        string = "Total Tokens: " + str(tokens_encountered) + "\n"
        f.write(string)
        string = "Tokens in inverted index: " + str(tokens_in_index)
        f.write(string)
        
    et = time.time()
    total = et - st
    print('Execution time:', total, 'seconds')
