import sys
from collections import defaultdict
import timeit
import time
import re
import os
import xml.sax
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.stem.snowball import SnowballStemmer
from tqdm import tqdm

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))
stemmer = SnowballStemmer(language="english")

pagecount = 0
index = defaultdict(list)
max_tokens = 15000
filecount = 0

## NOTES ##
# check about title_arr


class IndexBnaLe():
    def __init__(this, t, b, i, c, l, r):
        this.r = r
        this.l = l
        this.c = c
        this.i = i
        this.b = b
        this.t = t

    def create_dict(this, x):
        d = defaultdict(int)
        for i in x:
            d[i] += 1

        return d

    def indexer(this):
        global pagecount
        global max_tokens
        global index
        global filecount

        num = pagecount
        words = set()

        title = this.create_dict(this.t)
        words.update(this.t)

        body = this.create_dict(this.b)
        words.update(this.b)

        info = this.create_dict(this.i)
        words.update(this.i)

        categories = this.create_dict(this.c)
        words.update(this.c)

        links = this.create_dict(this.l)
        words.update(this.l)

        references = this.create_dict(this.r)
        words.update(this.r)

        for i in words:
            s = "d" + str(num)

            tit = title[i]
            if tit:
                s += "t" + str(tit)
            bod = body[i]
            if bod:
                s += "b" + str(bod)
            inf = info[i]
            if inf:
                s += "i" + str(inf)
            cat = categories[i]
            if cat:
                s += "c" + str(cat)
            lin = links[i]
            if lin:
                s += "l" + str(lin)
            ref = references[i]
            if ref:
                s += "r" + str(ref)
                
            index[i].append(s)
            
        pagecount +=1
        # print(index)
        # print(sorted(index.keys()))
        if pagecount % max_tokens == 0:
            print(pagecount)
            printFile()
            
def printFile():
    global index
    global filecount
    
    name = 'data2/' + 'index' + str(filecount) + '.txt'
    file = open(name, 'w')
    
    for word in (sorted(index.keys())):
        s = word + ':'
        posting = index[word]
        s += ' '.join(posting)
        file.write(s + '\n')
    file.close()
    
    index = defaultdict(list)
    print('created file', filecount)
    filecount+=1
        


class PtaNiBhai():
    def __init__(this):
        pass

    def tokenise(this, data):  # working
        toks = re.split(r"[^A-Za-z0-9]+", data)
        finaal = list()
        for i in toks:
            word = stemmer.stem(i)
            if (
                len(word) <= 1 or len(word) > 45 or word in stop_words
            ):  # check for word length
                continue
            finaal.append(word)

        return finaal

    def processTitle(this, title):  # working
        title = title.lower()
        title = this.tokenise(title)
        # print(title)
        return title

    def categoriesChahiye(this, text):  # working
        cat = list()
        data = text.split("\n")

        for i in data:
            if re.match(r"\[\[category:(.*)\]\]", i):
                # cat.append(i)
                cat.append(re.sub(r"\[\[category:(.*)\]\]", r"\1", i))

        data = this.tokenise(" ".join(cat))
        return data

    def referencesChahiye(this, text):  # try to change
        refarr = list()
        reflist = re.findall(r"\|[\ ]*title[^\|]*", text)
        for i in reflist:
            refarr.append(i.replace("title", " ", 1))

        data = this.tokenise(" ".join(refarr))
        # print(data)
        return data

    def linksChahiye(this, text):  # should http be removed?
        data = re.split("\n", text)
        links = list()

        for i in data:
            if re.match(r"\*\s*\[", i):  # confirm regex
                links.append(i)

        data = this.tokenise(" ".join(links))
        return data

    def infoboxChahiye(this, text):  # working
        check = re.split(r"\{\{infobox", text)
        x = len(check)
        info = list()

        if x <= 1:
            return info

        flag = False
        data = text.split("\n")
        for i in data:
            f = re.match(r"\{\{infobox", i)
            if f:
                flag = True
                i = re.sub(r"\{\{infobox(.*)", r"\1", i)
                info.append(i)
            elif flag:
                if i == "}}":
                    flag = False
                    continue
                info.append(i)

        info = this.tokenise(" ".join(info))
        return info

    def bodyChahiye(this, text):  # check if "redirect" has to be removed
        data = re.sub(r"\{\{.*\}\}", r" ", text)
        data = this.tokenise(data)
        return data

    def processContent(this, text, title):
        text = text.lower()
        title = this.processTitle(title)

        references = list()
        categories = list()
        links = list()

        data = re.split(r"==\s*references\s*==", text)
        if len(data) != 1:
            link_hai = True
            data2 = re.split(r"==\s*external links\s*==", data[1])
            if len(data2) == 1:
                links = list()
                link_hai = False
            if link_hai == True:
                links = this.linksChahiye(data2[1])

            references = this.referencesChahiye(data[1])
            categories = this.categoriesChahiye(data[1])
        else:
            link_hai = True
            categories = this.categoriesChahiye(data[0])

            data2 = re.split(r"==\s*external links\s*==", data[0])
            if len(data2) == 1:
                links = list()
                link_hai = False
            if link_hai == True:
                links = this.linksChahiye(data2[1])

        infobox = this.infoboxChahiye(data[0])
        body = this.bodyChahiye(data[0])

        return title, body, references, categories, links, infobox


class Document_Handler(xml.sax.ContentHandler):
    def __init__(this):
        this.abhi = ""
        this.title = ""
        this.text = ""
        this.data = ""
        print("handler called")

    # call when an element starts
    def startElement(this, tag, attributes):
        this.abhi = tag

    # Call when an elements ends
    def endElement(this, tag):
        if tag == "page":
            d = PtaNiBhai()
            title, body, info, categories, links, references = d.processContent(
                this.text, this.title
            )
            ind = IndexBnaLe(title, body, info, categories, links, references)
            ind.indexer()
            this.abhi = ""
            this.title = ""
            this.text = ""

    def characters(this, content):
        if this.abhi == "title":
            this.title += content
        elif this.abhi == "text":
            this.text += content


class Parser():
    def __init__(this, file):
        this.parser = xml.sax.make_parser()  # create an XMLReader
        this.parser.setFeature(
            xml.sax.handler.feature_namespaces, 0
        )  # turn off namepsaces
        Handler = Document_Handler()  # making a custom handler
        this.parser.setContentHandler(Handler)
        this.parser.parse(file)  # parse the file


if __name__ == "__main__":
    st = time.time()
    parser = Parser(sys.argv[1])
    printFile()
    
    et = time.time()
    total = et - st
    print('Execution time:', total, 'seconds')
