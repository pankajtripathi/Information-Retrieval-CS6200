# coding=utf-8

import numpy
from sklearn import tree

__author__ = "Pankaj Tripathi"

"""
decision_tree.py
----------
Environment - Python 2.7.11
Description - Performs linear regression on a training set and tests the results on a test set.
"""


def generateInverseMapping(file):
    """
    :param file: file with list of docs and a number associated with their sequential occurrence
    :return: dictionary with number as key and doc name as value
    """
    inverse_map = dict()
    with open(file, 'r') as f:
        for line in f.readlines():
            docID, docNo = line.split()
            inverse_map[docNo] = docID
    return inverse_map


def storeOutput(outDict, output_filename):
    """
    :param outDict: queryID as key and value is combination of (docName, result vector from the clf.predict)
    :param output_filename:
    :return: generate a file with output values in trec format
    """
    output = open('./features/data/' + output_filename, 'w')
    for qid in outDict:
        docsWithResults = outDict[qid]
        docsWithResults = sorted(docsWithResults, key=lambda x: x[1], reverse=True)
        rank = 1
        for docName, val in docsWithResults:
            output.write(' '.join([str(qid), 'Q0', str(docName), str(rank), str(val), "Exp\n"]))
            rank += 1
    output.close()


def storeResult(model_result, output_filename, matrix_file, flag):
    """
    :param model_result: result form clf.predict for training/test
    :param output_filename:
    :param matrix_file:
    :param flag: True for training data, False for test data
    :return: outDict: queryID as key and value is combination of (docName, result vector from the clf.predict)
    """
    if flag:
        inverse_map = generateInverseMapping('./features/data/trainingData_docList.txt')
    else:
        inverse_map = generateInverseMapping('./features/data/testData_docList.txt')
    outDict = dict()
    count = 0
    with open(matrix_file, 'r') as f:
        for line in f.readlines():
            content = line.split()
            queryID = content[0]
            docName = inverse_map[content[1]]

            if queryID not in outDict:
                outDict[queryID] = [(docName, model_result[count])]
            else:
                outDict[queryID].append((docName, model_result[count]))
            count += 1
    storeOutput(outDict, output_filename)


if __name__ == "__main__":
    training_feature_matrix = numpy.loadtxt('./trainingDataMatrix.txt', usecols=(2, 3, 4, 5, 6, 7, 8, 9, 10))
    training_label = numpy.loadtxt('./trainingDataMatrix.txt', usecols=(11,))

    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(training_feature_matrix, training_label)
    training_result = clf.predict(training_feature_matrix)
    storeResult(training_result, 'trainingPerformance.txt', './trainingDataMatrix.txt', True)
    print "Completed for Training data............"

    test_feature_matrix = numpy.loadtxt('./testDataMatrix.txt', usecols=(2, 3, 4, 5, 6, 7, 8, 9, 10))
    test_result = clf.predict(test_feature_matrix)
    storeResult(test_result, 'testPerformance.txt', './testDataMatrix.txt', False)
    print "Completed for Test data................"
