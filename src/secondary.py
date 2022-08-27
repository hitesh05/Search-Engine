import os
import time


def split(dirname):
    lines = list()
    filecount = 0
    threshold = 15000
    name = dirname + "/final.txt"
    filename = open(name,'r')
    name = dirname + "/sec.txt"
    secondary = open(name, 'w')
    
    line = filename.readline().strip('\n')
    
    while(line):
        char = ':'
        words = line.split(char)
        word = words[0]
        
        if not(len(word)> 10 and word[0:7].isdecimal()):
            lines.append(line)
        if len(lines) == threshold:
            main_word = lines[0].split(char)[0]
            secondary.write(str(main_word)+'\n')
            name = dirname + '/f' + str(filecount) + '.txt'
            sec = open(name,'w')
            for line in lines:
                sec.write(line + '\n')
            filecount+=1
            lines = list()
        line = filename.readline().strip()
        
    if(len(lines)>0):
        main_word = lines[0].split(char)[0]
        secondary.write(str(main_word)+'\n')
        
        name = dirname + '/f' + str(filecount) + '.txt'
        sec = open(name,'w')
        for line in lines:
            sec.write(line + '\n')
        filecount+=1
        lines = list()
        
    filename.close()
    secondary.close()
    return filecount
    
 
if __name__ == '__main__':   
    st = time.time()
    
    dirname = "../complete"
    files = split(dirname)
    
    et = time.time()
    total = et - st
    print(f"Exectution time is {total} seconds")
        
        