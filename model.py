#encoding=utf8

import os
import re
import sys
import numpy as np
import time
reload(sys)
sys.setdefaultencoding( "utf-8" )

def myMatrix(rows,cols):
    mat = [[0 for col in range(cols)] for row in range(rows)]
    return mat
def getStatus():
    """
    6418
    :return:
    """
    status = []
    with open("./corpus/gb_table.txt","r") as f:
        lines = f.readlines()
        for line in lines:
            status.append(line.strip())
    status = set(status)
    return list(status),len(status)

def getStatusFromFreq():
    """
    3161个常出出现单字
    :return:
    """
    status = []
    dictf = {}
    with open("word_freq.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            tmp = line.strip().split("\t")[0]
            dictf[tmp] = int(line.strip().split("\t")[-1])
            if len(tmp)== 3:
                status.append(tmp)
    status = set(status)
    return list(status), len(status),dictf

def initStarting(status):
    """
    初始矩阵概率
    :param status:
    :return:
    """
    startdic = {}
    for s in status:
        startdic[s] = 0
    suml = 0
    with open("word_freq.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            tmp = line.split("\t")[0]
            if len(tmp) >3:
                startdic[tmp[0:3]] = startdic.get(tmp[0:3],0) + int(line.split("\t")[1])
                suml += int(line.split("\t")[1])
    ll =  len(startdic)
    for k ,v in startdic.items():
        #加1平滑
        # startdic[k] = ((v + 1) / float(suml + ll))
        startdic[k] = np.log((v+1)/float(suml+ll))

    return startdic

def initTransition(status,cols):
    """
    初始化转移矩阵,每个字后面跟着的字
    :param status:
    :param cols:
    :return: 字典:{'字':{},'':{}}
    """

    tranMat  = {}
    sum = 0
    # for i in status:
    #     tmp = {}
    #     for j in status:
    #         tmp[j] = 0
    #     tranMat[i] = tmp
    # print 'succ'
    with open('transition.txt','r') as f:
        lines = f.readlines()

        for line in lines:
            tmpline = line.strip().split('\t')
            # if tmpline[0][0:3] not in status or tmpline[0][3:6] not in status:continue
            tmpDict = tranMat.get(tmpline[0][0:3],{})

            tmpDict[tmpline[0][3:6]] = tmpDict.get(tmpline[0][3:6],0) + int(tmpline[-1])

            tranMat[tmpline[0][0:3]] =tmpDict

            sum += int(tmpline[-1])

    for k ,vD in tranMat.items():
        #加1平滑

        for k2,v in vD.items():
            # tranMat[k][k2] = (v+1) / float(sum+cols**2)
            tranMat[k][k2] = np.log((v+1)/float(sum+cols**2))
    # print tranMat
    return tranMat

def initEmission(status,wordFreDict,pinyin,lex):
    """

    :param status:
    :param wordFre:
    :param pinyin:
    :param lex:
    :return:
    """
    num1,num2 = len(status),len(pinyin)

    emisMat = myMatrix(num1,num2)
    iterNum = 0
    for k,v in lex.items():
        iterNum +=1
        # print '第%d轮迭代求发射矩阵'%iterNum
        zi = len(k)/3

        number = wordFreDict.get(k,0)
        # print k,number
        if zi == 1: #单个字
            if k[0:3] not in status: continue
            zii = status.index(k[0:3])
            # if zii is None: continue
            for py1 in v:
                pyinj = pinyin.index(py1.strip())
                emisMat[zii][pyinj] += number
        else:
            start = 0
            end = 3
            while end<len(k):
                if k[start:end] not in status:
                    start = end
                    end += 3
                    continue
                zii = status.index(k[start:end])
                tmpPys = v[0].strip().split(' ')[start/3]
                pyinj = pinyin.index(tmpPys)
                emisMat[zii][pyinj] += number
                start = end
                end += 3
    # print 'success'

    print type(emisMat[0][0])
    for i in range(num2):
        sum1 = 0
        for j in range(num1):
            sum1 += emisMat[j][i]
        # sum1 = np.sum(emisMat[i,:])
        if sum1!=0:
            for j in range(num1):
                emisMat[j][i] = (emisMat[j][i])/float(sum1)
    # for i in range(num1):
    #     sum1 = 0
    #     for j in range(num2):
    #         sum1 += emisMat[i][j]
    #
    #     if sum1!=0:
    #         for j in range(num2):
    #             emisMat[i][j] = (emisMat[i][j])/float(sum1)
    # print status[0],sum(emisMat[0]),emisMat[0]
    # print pinyin
    return emisMat



def getPinyin():
    """

    :return:
    """
    pinyin = []
    lex = {}

    with open('lexicon.txt','r') as f:

        lines = f.readlines()
        for line in lines:
            tmpList = []
            tmpLine = line.strip().split('	')
            word = tmpLine[0]
            py = re.sub(u"[1-9]","",tmpLine[-1])
            if word in lex and py not in lex[word]:
                lex[word].append(py)
            else:
                tmpList.append(py)
                lex[word] = tmpList
            pys = tmpLine[-1].split(' ')
            for py in pys:
                pinyin.append(re.sub(u'[1-9]','',py))
    pinyin = list(set(pinyin))

    return pinyin,lex

def hmm_viterbi(oberation,startdic,tranMat,emission,pinyin,status):
    """

    :param oberation:
    :param startdic:
    :param tranMat:
    :param emission:
    :param pinyin:
    :param status:
    :return:
    """

    topK = 10
    hmmstatus = {}
    hmmpath =[]
    for i in range(len(oberation)):
        #根据观测的拼音看有哪些状态
        pyIndex = pinyin.index(oberation[i])
        nowStatusDict = {}
        for j in range(len(status)):
            if emission[j][pyIndex]!=0:
                nowStatusDict[status[j]] = np.log(emission[j][pyIndex])
                # print nowStatusDict[status[j]]
        # nowStatusDict = dict(sorted(nowStatusDict.items(),key=lambda item:item[1],reverse=True)[0:topK])
        # print nowStatusDict

        startPi = 1 /float(len(nowStatusDict))
        if i==0: #起始
            tmpDict = {}
            for k,v in nowStatusDict.items():

                tmpDict[k] = v *  startPi      #发射概率*起始概率
            tmpStatus = sorted(tmpDict.items(),key=lambda item:item[1],reverse=True)

            if len(tmpStatus) >= topK:
                hmmstatus[i] = tmpStatus[0:topK]
            else:
                hmmstatus[i] = tmpStatus[0:len(tmpStatus)]
            # hmmstatus[i] = tmpStatus
        else:
            tmpDict = {}
            # print hmmstatus[i-1]

            for k, v in nowStatusDict.items():

                for (sta,prob) in hmmstatus[i-1]:
                    # print tranMat[sta][k]
                    if k not in tranMat[sta].keys() or sta not in tranMat.keys(): continue
                    if k not in tmpDict:

                        tmpDict[k] = prob*tranMat[sta][k]* v

                    elif  prob*tranMat[sta][k]* v > tmpDict[k]:
                        tmpDict[k] = prob * tranMat[sta][k] * v
                # for k, v in tmpDict.items():
                #         print k, v

            if tmpDict=={}:

                tmpDict = nowStatusDict
            # for k ,v in  tmpDict.items():
            #     print k,v

            tmpStatus = sorted(tmpDict.items(), key=lambda item: item[1], reverse=True)
            # print tmpStatus

            if len(tmpStatus) >= topK:
                hmmstatus[i] = tmpStatus[0:topK]
            else:
                hmmstatus[i] = tmpStatus[0:len(tmpStatus)]
            # hmmstatus[i] = tmpStatus

    for i in range(len((hmmstatus))):
        hs = hmmstatus[i]
        # print i,hs[0][0]
        hmmpath.append(hs[0][0])

    return "".join(hmmpath)




    pass

if __name__ == '__main__':
    startTime = time.time()
    #初始概率
    status,l = getStatus()
    # status = getStatusFromFreq()[0]
    startdic =  initStarting(status)   #字典
    #获取转移矩阵
    status = list(set(startdic.keys())) #列表list

    tranMat = initTransition(status,len(status))  #字典

    # print status[0]
    # print tranMat['我']['们'],tranMat['哦']['门']
    # 获取发射矩阵
    pinyin,lex = getPinyin()     #拼音列表,和音词表字典
    wD = getStatusFromFreq()[2]   #词频字典

    emission = initEmission(status,wD,pinyin,lex)
    # print status[9],emission[9]
    endTime = time.time()
    print '生成HMM模型需要的时间:',endTime-startTime
    while True:

        oberation = raw_input('请输入拼音:\n').split()
        print hmm_viterbi(oberation,startdic,tranMat,emission,pinyin,status)


    # wD = getStatusFromFreq()[2]  # 词频字典
    # for k, v in wD.items():
    #     print k, v
    # pinyin, lex = getPinyin()
    # print len(pinyin),pinyin
    # for k,v in lex.items():
    #     print k,v
    pass