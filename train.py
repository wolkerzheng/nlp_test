#encoding=utf8

import os
import re
import sys
import time
reload(sys)
sys.setdefaultencoding( "utf-8" )
def readCorpus():
    startTime = time.clock()

    filepath = './corpus/'
    fileList = os.listdir(filepath)
    numTxt = 0
    wordTransition = {}
    for filName in fileList:
        tmp = ""
        numTxt += 1
        print '处理第%d篇日报'%numTxt
        with open(filepath+filName,'r') as f:
            lines = f.readlines()
            for line in lines:
                line =  line.strip().decode('gbk','ignore')
                line = re.sub(u"■／[。，,！……!《》<>\"':：？\?、\|“”‘'；＊]・","",line.strip())
                for ci in line:
                    w = (tmp+ci).strip()
                    wordTransition[w] = wordTransition.get(w,0)+1
                    tmp = ci
    print sorted(wordTransition.items(),key=lambda item:item[1],reverse=True)[0:15]
    print len(wordTransition)

    with open("transition.txt","w") as f:
        for k,v in sorted(wordTransition.items(),key=lambda item:item[1],reverse=True):
            f.write("%s\t%d\n"%(k,v))

if __name__ == '__main__':
    readCorpus()