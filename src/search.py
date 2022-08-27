import sys
import re
from tqdm import tqdm_notebook as tqdm
import math
from bisect import bisect
from collections import defaultdict
import time
import random
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import *
from Stemmer import Stemmer

dirname = "../complete/"
sec_file = open(dirname  + "sec.txt",'r')
secwords = sec_file.readlines()
sec_file.close()

max_docs = 15000
titledir = "../titles/"
# try:
nltk.download('stopwords')
# except:
#     pass
stop_words = set(stopwords.words('english'))
stemmer = Stemmer('porter')


class Extra():
    def __init__(self):
        pass
    
    def tokenise(self, data):  # working
        data = data.lower()
        data = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ', data) # removing html entities
        data = re.sub(r'http[s]?\S*[\s | \n]', r' ', data) # removing urls
        toks = re.split(r'[^A-Za-z0-9]+', data)
        finaal = list()
        for i in toks:
            word = stemmer.stemWord(i)
            if (
                len(word) <= 1 or len(word) > 45 or word in stop_words
            ):  # check for word length
                continue
            finaal.append(word)

        return finaal
    
    def get_title(self, doc_num):
        global max_docs
        global titledir
        
        off = doc_num // max_docs
        off += 1
        f = open(titledir + str(off) + '.txt','r')
        title = f.readlines()[doc_num % max_docs].strip()
        return title

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

def init_search(line):
    # print("Starting search engine\n")
    cl = Extra()
    if re.match(r'[t|b|i|c|l|r]:', line):
        pass
    else:
        tokens = cl.tokenise(line)
        # print(tokens)
        for token in tokens:
            # print(token, end= '\n')
            posting_list = cl.get_postinglist(token)
            # print(posting_list, end = '\n\n')
            if posting_list:
                pass
        
    
if __name__ == '__main__':
    query_filename = sys.argv[1]
    query_file = open(query_filename,'r')
    lines = query_file.readlines()
    query_file.close()
    
    for line in lines:
        init_search(line)
        break
    