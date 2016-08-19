# coding=utf-8
import random
import collections

__author__ = "Pankaj Tripathi"

"""
matrix_setup.py
----------
Environment - Python 2.7.11
Description -
    Script to build a query-doc static feature matrix in format qid-docid f1 f2 f3 … fd label
    The data is divided in to training and test data to test on a model.
"""


def splitData():
    """
    Function to split the 25 queries between the test and training model
    :return: list of queries for test and train
    """
    trainingData = set()

    with open('./AP_DATA/query_desc.51-100.short.txt') as f:
        for line in f.readlines():
            if line != '\n':
                data = line.split('.')[0]
                trainingData.add(data)
    # testData = set(['64', '56', '59', '71', '85'])
    testData = set(random.sample(trainingData, 5))
    print testData
    for q in testData:
        trainingData.remove(q)
    return trainingData, testData


def getDocsAndLabels(dataSet, setName):
    """
    :param dataSet: trainingData/ testData
    :param setName: training/test
    :return: dictionary queryDocLabel which has key(queryNum, docID) and value relevance from qrel as label.
             dictionary docMap which has docName as key and number which gives sequential listing of the doc in the map.
    """
    docList = list()
    queryDocLabel = dict()

    with open('./AP_DATA/qrels.adhoc.51-100.AP89.txt') as qrelFile:
        for line in qrelFile.readlines():
            if line != '\n':
                queryNum, dummy, docID, label = line.split()
                if queryNum in dataSet:
                    docList.append(docID)
                    queryDocLabel[(queryNum, docID)] = label

    orderedQueryDocLabel = collections.OrderedDict(sorted(queryDocLabel.items(), key=lambda x: x[0]))
    docMap = dict()
    i = 0
    for doc in docList:
        i += 1
        docMap[doc] = i

    ordered_DocMap = collections.OrderedDict(sorted(docMap.items(), key=lambda x: x[1], reverse=True))
    out = open('./features/data/' + setName + '_docList.txt', 'w')
    for doc in ordered_DocMap.keys():
        out.write(str(doc) + " " + str(ordered_DocMap[doc]) + '\n')
    out.close()

    return orderedQueryDocLabel, docMap


def retrieveData(queryAndDocs, filename):
    """
    :param queryAndDocs: list of query and doc keys from queryDocLabel
    :param filename: feature file ie okapiTF, okapiBM25 etc.
    :return: tempDict{(queryNum, docID)} => score form feature file i.e. from okapiTF file
             lowestDict{q} => lowest score from feature file for a queryNum
    """
    tempDict = dict()
    scoreDict = dict()
    lowestDict = dict()
    with open(filename, 'r') as f:
        for line in f.readlines():
            if line != '\n':
                queryNum, dummy, docID, dummy, score, dummy = line.split()
                if (queryNum, docID) in queryAndDocs:
                    tempDict[(queryNum, docID)] = score
                    if queryNum not in scoreDict:
                        scoreDict[queryNum] = []
                    scoreDict[queryNum].append(score)
    for q in scoreDict:
        scoreList = scoreDict[q]
        l = min(scoreList)
        lowestDict[q] = l
    return tempDict, lowestDict


def retrieveScore(dataMap, lowest, q, d):
    """
    :param dataMap: dataMap has scores from the features for a (q, d) combination
    :param lowest: lowestDict{q} => lowest score from feature file for a queryNum
    :param q: query
    :param d: doc
    :return: score for a (q, d) from dataMap if the combiantion has no value in dataMap then return the lowest value
             from the lowest for that query.
    """
    if (q, d) in dataMap.keys():
        return dataMap[(q, d)]
    else:
        return lowest[q]


def lowestForTermFreqs(freqDict):
    """
    :param freqDict: TF/TTF/DF for the (q, d) combiantion
    :return: lowest TF/TTF/DF values for query
    """
    temp = dict()
    lowestDict = dict()
    for (q, d) in freqDict:
        if q not in temp:
            temp[q] = []
        temp[q].append(freqDict[(q, d)])
    for q in temp:
        scoreList = temp[q]
        l = min(scoreList)
        lowestDict[q] = l
    return lowestDict


def generateMatrix(dataSetWithLabel, dataSetDocs, filename):
    """
    :param dataSetWithLabel: dictionary which has key(queryNum, docID) and value relevance from qrel as label.
    :param dataSetDocs: docList for the model
    :param filename: output file name
    :return: file with a matrix generated for (q,d) combination
    """
    out = open(filename, 'w')
    queryAndDocs = dataSetWithLabel.keys()
    totalTF = dict()
    totalTTF = dict()
    totalDF = dict()

    okapiData, okapiLowest = retrieveData(queryAndDocs, './features/okapiTF.txt')
    tfidfData, tfidfLowest = retrieveData(queryAndDocs, './features/tfidf.txt')
    bm25Data, bm25Lowest = retrieveData(queryAndDocs, './features/okapiBM25.txt')
    jmData, jmLowest = retrieveData(queryAndDocs, './features/unigramLMJelinekMercer.txt')
    laplaceData, laplaceLowest = retrieveData(queryAndDocs, './features/unigramLMLaplace.txt')
    proximityData, proximityLowest = retrieveData(queryAndDocs, './features/proximitySearch.txt')

    with open('./features/termFreqStats.txt', 'r') as termFreqStats:
        for line in termFreqStats.readlines():
            if line != '\n':
                query, doc, TF, TTF, DF = line.split()
                if (query, doc) in queryAndDocs:
                    totalTF[(query, doc)] = TF
                    totalTTF[(query, doc)] = TTF
                    totalDF[(query, doc)] = DF

    lowestTF = lowestForTermFreqs(totalTF)
    lowestTTF = lowestForTermFreqs(totalTTF)
    lowestDF = lowestForTermFreqs(totalDF)

    for (q, d) in queryAndDocs:
        docNum = dataSetDocs[d]
        okapi = retrieveScore(okapiData, okapiLowest, q, d)
        tfidf = retrieveScore(tfidfData, tfidfLowest, q, d)
        bm25 = retrieveScore(bm25Data, bm25Lowest, q, d)
        jm = retrieveScore(jmData, jmLowest, q, d)
        laplace = retrieveScore(laplaceData, laplaceLowest, q, d)
        proximity = retrieveScore(proximityData, proximityLowest, q, d)
        tf = retrieveScore(totalTF, lowestTF, q, d)
        ttf = retrieveScore(totalTTF, lowestTTF, q, d)
        df = retrieveScore(totalDF, lowestDF, q, d)
        label = dataSetWithLabel[(q, d)]

        out.write(str(q) + " "
                  + str(docNum) + " "
                  + str(okapi) + " "
                  + str(tfidf) + " "
                  + str(bm25) + " "
                  + str(jm) + " "
                  + str(laplace) + " "
                  + str(proximity) + " "
                  + str(tf) + " "
                  + str(ttf) + " "
                  + str(df) + " "
                  + str(label) + "\n")
    out.close()


if __name__ == '__main__':
    trainingData, testData = splitData()
    print 'Building data set for training data'
    trainingDataWithLabel, trainingDataDocs = getDocsAndLabels(trainingData, 'trainingData')
    generateMatrix(trainingDataWithLabel, trainingDataDocs, './trainingDataMatrix.txt')
    print 'Done with training data............ '

    print 'Building data set for test data'
    testDataWithLabel, testDataDocs = getDocsAndLabels(testData, 'testData')
    generateMatrix(testDataWithLabel, testDataDocs, './testDataMatrix.txt')
    print 'Done with test data............ '
