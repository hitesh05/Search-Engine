import sys
import re
from tqdm import tqdm_notebook as tqdm
from math import log2
from bisect import bisect
from collections import defaultdict
import time
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import *
from Stemmer import Stemmer
import random

## GLOBAL ##

dirname = "../complete_hin/"
sec_file = open(dirname  + "sec.txt",'r')
secwords = sec_file.readlines()
sec_file.close()

max_docs = 1000
titledir = "../titles_hindi/"

stop_words = list()
stem_words = list()
with open('hindi_stemwords.txt', 'r') as f:
	stem_words = [word.strip() for word in f]

with open('hindi_stopwords.txt', 'r') as f:
    stop_words = [word.strip() for word in f]
    
stem_words = set(stem_words)
stop_words = set(stop_words)

doccount = 12000 # CHANGE FOR FINAL DATA # 


class Extra():
    def __init__(self):
        pass
    
    def stem(self, word):
        for w in stem_words:
            if word.endswith(w):
                word = word[:-len(w)]
                return word
            
        return word

    def tokenise(self, data):  # working
        data = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ', data) # removing html entities
        data = re.sub(r'http[s]?\S*[\s | \n]', r' ', data) # removing urls
        data = re.sub(r'\{.*?\}|\[.*?\]|\=\=.*?\=\=', ' ', data)
        data = ''.join(ch if ch.isalnum() else ' ' for ch in data)
        toks = data.split()
        finaal = list()
        for i in toks:
            word = self.stem(i)
            word = i
            if (
                len(word) <= 1 or len(word) > 45 or word in stop_words
            ):  # check for word length
                continue
            finaal.append(word)

        return finaal

    def get_postinglist(self, token):
        tok2 = token + '\n'
        pos = bisect(secwords, tok2)
        pos = pos - 1
        
        if pos < 0:
            return False
        else:
            x = str(pos)
            file = open(dirname + "f" + x + '.txt','r')
            line = file.readline().strip()
            while line:
                if(line.split(':')[0] == token):
                    return line.split(':')[1]
                line = file.readline().strip()
        
        return False

class Search():
    
    def __init__(self):
        self.fieldtype = ['t', 'b', 'r', 'c', 'l', 'i']
        self.intlist = ['0','1','2','3','4','5','6','7','8','9']
        self.results = 10
        self.strtoprint = list()
        self.fieldmap = {'t':0, 'b':1, 'r':2, 'c':3, 'l':4, 'i':5}
        
    def get_title(self, doc_num):
        global max_docs
        global titledir
        
        off = doc_num // max_docs
        # off += 1
        f = open(titledir + str(off) + '.txt','r')
        title = f.readlines()[doc_num % max_docs].strip()
        return title
        
    def getnum(self, doc):
        # print(doc)
        l = ['','','','','','']
        current = 'x'
        flag = 0
        
        for i in range(len(doc)):
            if flag and (doc[i] not in self.fieldtype):
                x = self.fieldmap[current]
                # print('x',x)
                l[x] += doc[i]
            elif doc[i] in self.fieldtype:
                current = doc[i]
                flag = 1
        for i in range(len(l)):
            if not l[i]:
                l[i] = 0
            else:
                l[i] = int(l[i])
                
        # print(l)       
        return l
    
    # CHANGE #
    def scorer(self, scores):
        s = [200, 10, 8, 8, 8, 28]
        
        for i in range(len(scores)):
            scores[i] *= s[i]
        
        return scores
    
    def query_search(self, line):
        global doccount
        cl = Extra()
        
        parsed = defaultdict(int)
        score = defaultdict(int)
        inpstr = line
        prsd =[]
        lis = inpstr.split(":")
        first = 0
        for kr in range(len(lis)):
            if not first:
                first = 1 
            else :
                spltlst = lis[kr-1].split()
                contlst = lis[kr].split()
                category = spltlst[len(spltlst)-1]
                content = cl.tokenise(' '.join(contlst))
                prsd.append((category,content))
        x = len(prsd)
        for i in range (x):
            y = prsd[i][1]
            for tok in y:
                parsed[tok]=prsd[i][0]
        # print (parsed)
        # quit()
        
        for token in parsed.keys():
            posting_list = cl.get_postinglist(token)
            if posting_list:
                token_count = defaultdict(int)
                # doclist = posting_list.split('d')[1:]
                doclist = re.split('d', posting_list)[1:]
                # print(doclist, end='\n\n')
                idf = log2(doccount/len(doclist))
                for doc in doclist:
                    pageid=''
                    for i in doc:
                        if i not in self.intlist:
                            break
                        else :
                            pageid+=i
                    pageid=int(pageid)
                    # print(pageid)
                    scores = self.getnum(doc)
                    scores = self.scorer(scores)
                    scores[self.fieldmap[parsed[tok]]]*=15000
                    for s in scores:
                        token_count[pageid] += s
                    score[pageid] += log2(token_count[pageid]) * idf
        
        final = sorted(score.items(), key=lambda x: x[1], reverse = True)
        # lenfin=len(final)
        
        for i in range(0, min(self.results, len(final))):
            self.strtoprint.append(str(final[i][0]) + ',' + self.get_title(final[i][0]) + '\n')
            
        # if self.results > len(final):
        #     for x in range (self.results-len(final)):
        #         randpage = random.randint(0,doccount)
        #         self.strtoprint.append(str(randpage) + ',' + self.get_title(randpage) + '\n')
                
        return self.strtoprint 
    
    def simple_search(self,line):
        global doccount
        cl = Extra()
        tokens = cl.tokenise(line)
        # print(tokens)
        score = defaultdict(int)
        for token in tokens:
            # print(token, end= '\n')
            posting_list = cl.get_postinglist(token)
            # print(posting_list, end = '\n\n')
            if posting_list:
                token_count = defaultdict(int)
                # doclist = posting_list.split('d')[1:]
                doclist = re.split('d', posting_list)[1:]
                # print(doclist, end='\n\n')
                idf = log2(doccount/len(doclist))
                # print(idf)
                for doc in doclist:
                    pageid=''
                    for i in doc:
                        if i not in self.intlist:
                            break
                        else :
                            pageid+=i
                    pageid=int(pageid)
                    # print(pageid)
                    scores = self.getnum(doc)
                    scores = self.scorer(scores)
                    for s in scores:
                        token_count[pageid] += s
                    score[pageid] += log2(token_count[pageid]) * idf
                    # print(score[pageid])
                    
        final = sorted(score.items(), key=lambda x: x[1], reverse = True)
        # lenfin=len(final)
        # print(final)
        
        for i in range(0, min(self.results, len(final))):
            self.strtoprint.append(str(final[i][0]) + ',' + self.get_title(final[i][0]) + '\n')
            
        # if self.results > len(final):
        #     for jl in range (self.results-len(final)):
        #         randpage = random.randint(0,10)
        #         self.strtoprint.append(str(randpage) + ',' + self.get_title(randpage) + '\n')
                
        return self.strtoprint
                    
                
    
    def init_search(self, line):
        # print("Starting search engine\n")
        strtoprint = list()
        if re.match(r'[t|b|i|c|l|r]:', line):
            # print('here')
            strtoprint = self.query_search(line)
        else:
            strtoprint = self.simple_search(line)
            
        return strtoprint
        
    
if __name__ == '__main__':
    query_filename = sys.argv[1]
    query_file = open(query_filename,'r')
    lines = query_file.readlines()
    query_file.close()
    search = Search()
    
    strtoprint = list()
    for line in lines:
        st = time.time()
        strtoprint = search.init_search(line)
        et = time.time()
        # ky=int(line.split(',')[0])
        strtoprint.append(str(et-st)+'\n\n')
        # break
    
    op = sys.argv[2]
    opfile = open(op,'a')
    opfile.writelines(strtoprint)
    opfile.close()
    
# complete_hin : final merged and secondary index
# titles_hindi: titles for hindi data