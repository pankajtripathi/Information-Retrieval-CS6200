__author__ = "Pankaj Tripathi"

"""
unigram _matrix.py
----------
Environment - Python 2.7.11
Description - Script to create a feature matrix with all unigrams as features.
"""
prob = dict()
label = dict()
docMap = dict()
spamDict = dict()
featureDict = dict()


def generateDocMapping():
    """
    :return: a dcoMap dictionary with docs and their corresponding sequence of occurrence
    """
    with open('./test_ids_list.txt', 'r') as f:
        for line in f.readlines():
            docID, docNo = line.split()
            docNo = docNo.replace('\n', '')
            docMap[int(docNo)] = docID
    return docMap


def storeOutput():
    """
    Generate a file with top 50  spam docs and their corresponding labels
    """
    unigramTop50 = open('./unigramTop50.txt', 'w')
    for k in sorted(prob, key=prob.get, reverse=True)[:50]:
        if label[k] == "1":
            lab = "spam"
        else:
            lab = "ham"
        unigramTop50.write(str(k) + " " + str(prob[k]) + " " + lab + '\n')
    unigramTop50.close()


def getSpamDict():
    """
    a dictionary of all spam words with the sequence of occurrence
    """
    spamWords = list()
    with open('./spam_words.txt', 'r') as f:
        for line in f.readlines():
            word = line.replace('\n', '')
            spamWords.append(word)
    i = 0
    for word in spamWords:
        i += 1
        spamDict[i] = word


def getFeatureDict():
    """
    a dictionary of all words used as features with the sequence of occurrence
    """
    with open('feature_list.txt', 'r') as f:
        for line in f.readlines():
            seq, word = line.split()
            seq = int(seq)
            featureDict[seq] = word.replace('\n', '')


def topSpams():
    """
    Generate file with top spam words for both some Spam words as features processing and all Unigrams as
    feature processing
    """
    with open('./spamModel.txt', 'r') as f:
        spam = dict()
        getSpamDict()
        c = 0
        for line in f.readlines():
            if line != '\n':
                c += 1
                spamScore = line.replace('\n', '')
                s = spamDict[c]
                spam[s] = float(spamScore)
        out = open('./partOneTopSpams.txt', 'w')
        for k in sorted(spam, key=spam.get, reverse=True):
            if spam[k] > 0:
                out.write(str(k)+ "\t" + str(spam[k]) +'\n')

    with open('./unigramModel.txt', 'r') as f:
        spam = dict()
        getFeatureDict()
        c = 0
        for line in f.readlines():
            if line != '\n':
                c += 1
                spamScore = line.replace('\n', '')
                s = featureDict[c]
                spam[s] = float(spamScore)
        out = open('./partTwoTopSpams.txt', 'w')
        for k in sorted(spam, key=spam.get, reverse=True):
            if spam[k] > 0:
                out.write(str(k)+ "\t" + str(spam[k]) +'\n')


if __name__ == "__main__":
    generateDocMapping()
    with open('./unigramPredict.txt', 'r') as f:
        c = 0
        for line in f.readlines():
            if line != '\n':
                c += 1
                lab, pro, dum = line.split()
                doc = docMap[c]
                prob[doc] = float(pro)
                label[doc] = lab
    storeOutput()
    topSpams()

