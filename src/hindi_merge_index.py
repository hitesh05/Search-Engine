from collections import defaultdict
import os, os.path
import sys
import heapq
import time

class Merger():
    def __init__(self, num_files, filename, dirname="data2"):
        self.num_files = num_files
        self.dirname = dirname
        self.filename = filename
        self.words = {}
        self.files = {}
        self.top = {}
        self.flag = [0] * self.num_files
        self.data = defaultdict(list)
        self.heap = []
        self.count = 0
                
    def merge(self):
        char = ':'
        for i in range(0, self.num_files):
            fname = self.dirname + '/index' + str(i) + '.txt'
            f = open(fname, 'r')
            self.files[i] = f
            self.flag[i] = 1
            self.top[i] = f.readline()
            self.words[i] = self.top[i].split(char)
            # print(self.words[i][0])
            if self.words[i][0] not in self.heap:
                heapq.heappush(self.heap, self.words[i][0])
                
        total = 0
        
        fname = open(self.filename, 'w')
        while any(self.flag) == 1:
            try:
                x = heapq.heappop(self.heap)
            except:
                break
            s = ''
            if not x:
                pass
            else:
                for i in range(0, self.num_files):
                    if self.flag[i] and self.words[i][0] == x:
                        # print(str(self.words[i]))

                        s += str(self.words[i][1].strip())
                        # print(s)
                        self.top[i] = self.files[i].readline().strip()
                        if self.top[i] == '':
                            self.flag[i] = 0
                            self.files[i].close()
                        else:
                            self.words[i] = self.top[i].split(char)
                            if self.words[i][0] not in self.heap:
                                heapq.heappush(self.heap, self.words[i][0])
                            
            string = str(x) + str(char) + str(s) + '\n'
            # print(string)
            fname.write(string)
                            
            
            
                          
  
# dirname = sys.argv[1]
if __name__ == '__main__':
    st = time.time()
    try:
        os.mkdir("../complete_hin")
    except:
        pass
    dirname = "../data_hin" 
    filename = '../complete_hin/final.txt'
    # num_files = 2
    num_files =  (len([name for name in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, name))]))
    m = Merger(num_files, filename, dirname)
    m.merge()
    # os.rmdir(dirname)
    et = time.time()
    t = et - st
    print('Execution time:', t, 'seconds')
    
# data_hin: for initial index
# complete_hin: for final merged index
            