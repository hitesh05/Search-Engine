import sys
from collections import defaultdict
import time
import re
from turtle import title
import xml.sax
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import *
from Stemmer import Stemmer
import os

## GLOBAL ##
stop_words = list()
stem_words = list()
with open('hindi_stemwords.txt', 'r') as f:
	stem_words = [word.strip() for word in f]

with open('hindi_stopwords.txt', 'r') as f:
    stop_words = [word.strip() for word in f]
    
stem_words = set(stem_words)
stop_words = set(stop_words)

pagecount = 0
index = defaultdict(list)
max_tokens = 15000
max_docs = 1000
filecount = 0
tokens_encountered = 0
tokens_in_index = 0

titlearr = list()
titledir = "../titles_hindi/"

# try:
#     os.mkdir('data2')
# except:
#     pass

directory = sys.argv[2]
if directory[-1] != "/":
    directory += '/'

## NOTES ##
# check about title_arr


class IndexBnaLe:
    def __init__(self, t, b, i, c, l, r):
        self.__r = r
        self.__l = l
        self.__c = c
        self.__i = i
        self.__b = b
        self.__t = t
        
    def get_ref(self):
        return self.__r
    
    def get_links(self):
        return self.__l
    
    def get_cat(self):
        return self.__c
    
    def get_info(self):
        return self.__i
    
    def get_body(self):
        return self.__b
    
    def get_title(self):
        return self.__t

    def create_dict(self, x):
        d = defaultdict(int)
        for i in x:
            d[i] += 1

        return d

    def indexer(self):
        global tokens_in_index
        global pagecount
        global max_tokens
        global index
        global filecount

        num = pagecount
        words = set()

        title = self.create_dict(self.get_title())
        words.update(self.get_title())

        body = self.create_dict(self.get_body())
        words.update(self.get_body())

        info = self.create_dict(self.get_info())
        words.update(self.get_info())

        categories = self.create_dict(self.get_cat())
        words.update(self.get_cat())

        links = self.create_dict(self.get_links())
        words.update(self.get_links())

        references = self.create_dict(self.get_ref())
        words.update(self.get_ref())

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
    global titlearr

    name = directory + 'index' + str(filecount) + '.txt'
    file = open(name, 'w')

    for word in sorted(index.keys()):
        s = word + ':'
        posting = index[word]
        s += ' '.join(posting)
        file.write(s + '\n')
    file.close()

    index = defaultdict(list)
    
    # writing title array
    titlefile = open(titledir + str(filecount) + '.txt','w')
    titlefile.writelines(titlearr)
    titlefile.close()
    titlearr = list()
    
    print('created file', filecount)
    filecount += 1


class PtaNiBhai():
    def __init__(self):
        pass
    
    def stem(self, word):
        for w in stem_words:
            if word.endswith(w):
                word = word[:-len(w)]
                return word
            
        return word

    def tokenise(self, data):  # working
        global tokens_encountered
        data = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ', data) # removing html entities
        data = re.sub(r'http[s]?\S*[\s | \n]', r' ', data) # removing urls
        data = re.sub(r'\{.*?\}|\[.*?\]|\=\=.*?\=\=', ' ', data)
        data = ''.join(ch if ch.isalnum() else ' ' for ch in data)
        toks = data.split()
        finaal = list()
        for i in toks:
            tokens_encountered+=1
            word = self.stem(i)
            word = i
            if (
                len(word) <= 1 or len(word) > 45 or word in stop_words
            ):  # check for word length
                continue
            finaal.append(word)

        return finaal

    def processTitle(self, title):  # working
        title = title.lower()
        title = self.tokenise(title)
        return title

    def categoriesChahiye(self, text):  # working
        cat = list()

        cat = re.findall(r'\[\[category:(.*)\]\]',text)
        data = self.tokenise(' '.join(cat))
        return data

    def referencesChahiye(self, text):  # try to change
        refarr = list()
        reflist = re.findall(r'\|\s*title[^\|]*', text)
        for i in reflist:
            refarr.append(i.replace('title', '', 1))
        
        data = self.tokenise(' '.join(refarr))
        return data

    def linksChahiye(self, text):  # should http be removed?
        data = text.split('\n')
        links = list()

        for i in data:
            if re.match(r'\*\s*\[', i):  # confirm regex
                links.append(i)

        data = self.tokenise(' '.join(links))
        return data

    def infoboxChahiye(self, text):  # working
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

        info = self.tokenise(' '.join(info))
        return info

    def bodyChahiye(self, text):  # check if 'redirect' has to be removed
        data = re.sub(r'\{\{.*\}\}', r' ', text)
        data = self.tokenise(data)
        return data

    def processContent(self, text, title):
        text = text.lower()
        title = self.processTitle(title)

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
                links = self.linksChahiye(x)
            
            x = data[1]
            references = self.referencesChahiye(x)
            categories = self.categoriesChahiye(x)
        else:
            link_hai = True
            categories = self.categoriesChahiye(data[0])

            data2 = re.split(r'==\s*external links\s*==', data[0])
            if len(data2) == 1:
                links = list()
                link_hai = False
            if link_hai:
                links = self.linksChahiye(data2[1])

        x = data[0]
        infobox = self.infoboxChahiye(x)
        body = self.bodyChahiye(x)

        return title, body, infobox, categories, links, references


class Document_Handler(xml.sax.ContentHandler):
    def __init__(self):
        self.abhi = ''
        self.title = ''
        self.text = ''
        self.data = ''
        print('handler called')

    # call when an element starts
    def startElement(self, tag, attributes):
        self.abhi = tag
        
    def index(self, t,b,i,c,l,r):
        ind = IndexBnaLe(t,b,i,c,l,r)
        ind.indexer()
        self.abhi = ''
        self.title = ''
        self.text = ''
        

    # Call when an elements ends
    def endElement(self, tag):
        global pagecount
        global titlearr
        
        if tag == 'page':
            self.title = self.title.strip()
            titlearr.append(self.title + '\n')  
            d = PtaNiBhai()
            title, body, info, categories, links, references = d.processContent(self.text, self.title)
            self.index(title, body, info, categories, links, references)
            # print("page count: ", pagecount)

    def characters(self, content):
        if self.abhi == 'title':
            self.title += content
        elif self.abhi == 'text':
            self.text += content


        
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
        string = "Tokens in inverted index: " + str(tokens_in_index) + '\n'
        f.write(string)
        
    et = time.time()
    total = et - st
    print('Execution time:', total, 'seconds')
    
    
# 3 arguments to run
# 1st: path to data
# 2nd: path to dir to store index
# 3rd: file to store stats
# python hindi_indexer.py ../../hindi_data/data ../data_hin stats_hin.txt
