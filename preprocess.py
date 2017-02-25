# -*- coding: utf-8 -*-
__author__ = 'ZGD'

import re
import os
import sys
import spiltword
import  time
reload(sys)
sys.setdefaultencoding('utf8')
def readCorpus():
    starttime = time.clock()
    filePath = u'F:\Master\课件\自然语言处理\实验课资料\实验课资料\人民日报96年语料/'

    fileList = os.listdir(filePath)
    numTxt = 0
    wordFreq = {}
    bigramFr = {}
    for fileName in fileList:
        numTxt += 1
        print '处理第%d篇日报'%numTxt
        with open(filePath+fileName,'r') as f:
            line = f.readline().decode("gb2312", 'ignore')

            while line:
                oneText = []
                while line.strip()!="" and line.strip()[-1] != u'＊' :
                    oneText.append(re.sub(u"　■","",line.strip()))
                    line = f.readline().decode("gb2312", 'ignore')
                tmpSen = []
                sentence = "".join(oneText)
                tmpSen.append(sentence)
                resultList = spiltword.bmm(tmpSen)
                for res in resultList:
                    for w in res:

                        if  not wordFreq.has_key(w):
                            wordFreq[w] = 0
                        wordFreq[w] += 1
                    for i in range(len(res)-2):
                        w = "|".join(res[i:i+2])
                        if  not bigramFr.has_key(w):
                            bigramFr[w] = 0
                        bigramFr[w] += 1

                line = f.readline().decode("gb2312", 'ignore')
    endtime = time.clock()
    print (endtime-starttime)
    return wordFreq,bigramFr

def wordSaveToTxt(wordFreq,bigramFr):

    print "writing unigram to file.."
    with open("word_freq.txt","w") as f:

        for w in wordFreq.keys():
            f.write("%s\t%d\n"%(w,wordFreq[w]))
    print "writing bigram to file.."
    with open('bigram.txt','w') as f:
        for key in bigramFr.keys():
            f.write("%s\t%d\n"%(key,bigramFr[key]))
    print "writing bigram SUCCESS!"
    pass
def cleanTransition(lex):

    words = lex.keys()
    str = "&".join(words)
    tranDict = {}
    with open('transition.txt','r') as f:
        lines = f.readlines()

        for line in lines:

            tmpline = line.strip().split('\t')
            # if tmpline[0][0:3] not in status or tmpline[0][3:6] not in status:continue
            if len(tmpline[0]) < 6: continue
            if tmpline[0] in str:
                tranDict[tmpline[0]] = int(tmpline[-1])


    with open('new_transition.txt','w') as f:
        for k, v in sorted(tranDict.items(), key=lambda item: item[1], reverse=True):
            f.write("%s\t%d\n" % (k, v))

if __name__ == '__main__':

    wordFreq,bigramFr = readCorpus()
    wordSaveToTxt(wordFreq,bigramFr)
