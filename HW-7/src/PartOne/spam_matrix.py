import numpy
import collections
from sklearn import tree
from elasticsearch import Elasticsearch

__author__ = "Pankaj Tripathi"

"""
spam_matrix.py
----------
Environment - Python 2.7.11
Description - Script to create a feature matrix with spam/ham as label.
"""

es = Elasticsearch(timeout=1500)
spamWords = list()
spamDict = dict()
indexName = 'spam_dataset_test'
document = 'document'
indexSize = 75419
featureDict = dict()


def generateSpamDict(dataset):
    """
    :param dataset: training/test
    :return: a dictionary with all the email docs that contain spam words in spamWords list
    """
    for word in spamWords:
        body = {
            "query": {
                "filtered": {
                    "query": {
                        "query_string": {
                            "default_field": "split",
                            "query": dataset
                        }
                    },
                    "filter": {
                        "term": {
                            "body": word
                        }
                    }
                }
            },
            "size": 60335
        }
        res = es.search(index=indexName, body=body)
        ids = [d['_id'] for d in res['hits']['hits']]
        spamDict[word] = ids
    return spamDict


def createMatrix(dataset):
    """
    :param dataset: training/test
    Create a matrix for training data and test data with their label
    """
    generateSpamDict(dataset)
    if dataset == 'training':
        trainDocList = dict()
        with open('./trainingMatrix.txt', 'w') as trainMatrix:
            res = es.search(index=indexName, doc_type=document,
                            body={
                                'query': {
                                    'query_string': {
                                        "default_field": "split",
                                        "query": "training"
                                    }
                                },
                                "size": indexSize
                            })
            ids = [d['_id'] for d in res['hits']['hits']]
            count = 0
            for id in ids:
                print "Spam Matrix done for " + id
                count += 1
                trainDocList[id] = count
                tempList = list()
                for features in spamWords:
                    try:
                        if id in spamDict[features]:
                            tempList.append("1")
                        else:
                            tempList.append("0")
                    except KeyError:
                        tempList.append("0")
                out = ' '.join(tempList)
                lab = es.get(index=indexName, doc_type='document', id=id)['_source']['label']
                if lab == 'spam':
                    label = '1'
                else:
                    label = '0'
                trainMatrix.write(label + " " + out + '\n')
        with open('./train_ids_list.txt', 'w') as trains:
            for k in sorted(trainDocList, key=trainDocList.get):
                trains.write(str(k)+" "+str(trainDocList[k])+'\n')
    else:
        testDocList = dict()
        with open('./testMatrix.txt', 'w') as testMatrix:
            res = es.search(index=indexName, doc_type=document,
                            body={
                                'query': {
                                    'query_string': {
                                        "default_field": "split",
                                        "query": "test"
                                    }
                                },
                                "size": indexSize
                            })
            ids = [d['_id'] for d in res['hits']['hits']]
            count = 0
            for id in ids:
                print "Spam Matrix done for " + id
                count += 1
                testDocList[id] = count
                tempList = list()
                for features in spamWords:
                    try:
                        if id in spamDict[features]:
                            tempList.append("1")
                        else:
                            tempList.append("0")
                    except KeyError:
                        tempList.append("0")
                out = ' '.join(tempList)
                lab = es.get(index=indexName, doc_type='document', id=id)['_source']['label']
                if lab == 'spam':
                    label = '1'
                else:
                    label = '0'
                testMatrix.write(label + " " + out + '\n')
        with open('./test_ids_list.txt', 'w') as tests:
            for k in sorted(testDocList, key=testDocList.get):
                tests.write(str(k)+" "+str(testDocList[k])+'\n')


def generateInverseMapping():
    """
    Dictionary with number as key and doc name as value
    """
    inverse_map = dict()
    with open('./test_ids_list.txt', 'r') as f:
        for line in f.readlines():
            docID, docNo = line.split()
            docNo = docNo.replace('\n', '')
            inverse_map[int(docNo)] = docID
    return inverse_map


def storeOutput(outDict, output_filename):
    """
    :param outDict: dictionary with docs based on their probability of being spam
    :param output_filename: filename to contain top 50 spam docs
    :return:
    """
    out = open(output_filename, 'w')
    fullOut = open('./spamTestAll.txt', 'w')
    for k in sorted(outDict, key=outDict.get, reverse=True)[:50]:
        lab = es.get(index=indexName, doc_type='document', id=k)['_source']['label']
        out.write(str(k) + " " + str(outDict[k])+ " " + str(lab) + '\n')
    out.close()
    for k in sorted(outDict, key=outDict.get, reverse=True):
        lab = es.get(index=indexName, doc_type='document', id=k)['_source']['label']
        fullOut.write(str(k) + " " + str(outDict[k])+ " " + str(lab) + '\n')
    fullOut.close()


def storeResult(testRes, output_filename, matrix_file):
    """
    :param testRes: Result from decision tree
    :param output_filename: filename to contain top 50 spam docs
    :param matrix_file: test matrix file
    :return:
    """
    outDict = dict()
    count = 0
    ln = 0
    inverMap = generateInverseMapping()
    with open(matrix_file, 'r') as f:
        for line in f.readlines():
            ln += 1
            con = line.split()
            doc = inverMap[ln]

            outDict[doc] = testRes[count][1]
            count += 1
    storeOutput(outDict, output_filename)


def modelData():
    """
    Classify the email docs based on their probability of being spam/ham. Generate a file with
    top 50 spam docs
    """
    t = list()
    for i in range(1, 71, 1):
        t.append(i)
    columns = tuple(t)

    trainingMatrix = numpy.loadtxt('./trainingMatrix.txt', usecols=columns)
    trainingLabel = numpy.loadtxt('./trainingMatrix.txt', usecols=(0, ))

    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(trainingMatrix, trainingLabel)

    testMatrix = numpy.loadtxt('./testMatrix.txt', usecols=columns)
    testRes = clf.predict_proba(testMatrix)
    storeResult(testRes, './spamTop50.txt', './testMatrix.txt')


def getOverallAccuracy():
    """
    Get accuracy for all the email docs. Accuracy is determined by checking their labels with their probability of being
    a spam. Threshold taken 0.6
    """
    hits = 0
    miss = 0
    with open('./spamTestAll.txt', 'r') as f:
        for line in f.readlines():
            if line != '\n':
                doc, prob, label = line.split()
                prob = float(prob)
                label = label.replace('\n', '')
                if prob >= 0.6:
                    if label == 'spam':
                        hits += 1
                    else:
                        miss += 1
        num = float(hits) / float(hits + miss)
        acc = num * 100
        print "Overall accuracy: " + str(acc)

if __name__ == "__main__":
    with open('./spam_words.txt', 'r') as f:
        for line in f.readlines():
            word = line.replace('\n', '')
            spamWords.append(word)
    i = 0
    for word in spamWords:
        i += 1
        featureDict[word] = i
    createMatrix("training")
    createMatrix("test")
    modelData()
    getOverallAccuracy()
