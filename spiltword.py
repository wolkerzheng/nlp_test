#encoding=utf8
import re
import numpy as np

def getLexicon():
    """
    :return:
    """
    lexicon = []
    with open('lexicon.txt') as f:
        lines = f.readlines()
        for line in lines:
            lexicon.append(line.strip().split('\t')[0])
    lexicon = set(lexicon)
    return lexicon

def getMaxLenFromLexicon(lexicon):
    """
    :param lexicon:
    :return:
    """

    maxLen = 0
    for str in lexicon:
        if maxLen < len(str):
            maxLen = len(str)
    return maxLen

def preProcess(sentence):
    """
    去除标点符号
    :param sentence:
    :return:
    """
    sentence = re.sub(u"[。，,！……!《》<>\"':：？\?、\|“”‘'；]","",sentence)

    return sentence

def fmm(lexicon,sentenceList):
    """
    正向最大匹配法（由左到右的方向）
    :param lexicon:
    :param sentenceList:
    :return:
    """
    # maxlen = getMaxLenFromLexicon(lexicon)
    resultList = []
    maxlen = 10
    for sentence in sentenceList:
        sentence = preProcess(sentence)

        start = 0
        end = 0
        sLen = len(sentence)
        tmpRes = []
        while start<sLen:
            tmp = []

            if sLen-start > maxlen:
                end = start + maxlen
            else:
                end = sLen

            while not tmp:

                tmpWord = sentence[start:end]

                if tmpWord in lexicon:
                    tmp.append(tmpWord)
                #处理未登录词
                elif start + 1 == end:
                    tmp = tmpWord
                else:
                    end=end-1
            tmpRes.append("".join(tmp))
            start = end

        resultList.append(tmpRes)
    return resultList

def bmm(sentenceList):
    """
    逆向最大匹配法
    :param lexicon:
    :param sentenceList:
    :return:
    """
    # maxlen = getMaxLenFromLexicon(lexicon)
    lexicon = getLexicon()
    maxlen = 10
    resultList = []
    for sentence in sentenceList:
        # sentence = preProcess(sentence)
        sentence =sentence.encode("utf-8")
        sLen = len(sentence)
        start = sLen
        end = sLen
        tmpRes = []
        while end>0:
            tmp = ""
            if sLen-start > maxlen:
                start = start - maxlen
            else:
                start = 0

            while not tmp:

                tmpWord = sentence[start:end]

                if tmpWord in lexicon:

                    tmp = tmpWord
                elif start + 1 == end:
                    tmp = tmpWord
                else:
                    start = start + 1

            tmpRes.insert(0,tmp)
            end = start

        resultList.append(tmpRes)
    return resultList


if __name__ == '__main__':

    lexicon = getLexicon()

    sentenceList = ["我是中国人,我爱中国","研究生活很好","哈尔滨工业大学校门有很多人在拍照",
                    "2016年12月31日一样","阅领构以此"]
    print '正向最大匹配法'
    res =  fmm(lexicon,sentenceList)
    for r in res:
        print "|".join(r)
    print '逆向最大匹配法'
    res = bmm( sentenceList)
    for r in res:
        print "|".join(r)
    pass