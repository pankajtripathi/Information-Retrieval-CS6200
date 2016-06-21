import json
from PorterStemmer import PorterStemmer
import math

__author__ = "Pankaj Tripathi"

"""
query_processor.py
----------
Environment - Python 3.5.1
Description -
    Script to process the index of documents against the a file containing queries. The retrieved documents are scored
    using the given models.
    1. OkapiTF
    2. TF-IDF
    3. OkapiBM25
    4. Unigram Language Model with Laplace Smoothing
    5. Unigram Language Model with Jelinek Mercer Smoothing
"""

catDict = {}
# function to get the term vectors


def getTermVector(term):
    catalog = open('./outputfolder/catalog.txt', 'r')
    merged = open('./outputfolder/invertIndex.txt', 'r')
    # File for in.0.50.txt
    #out50 = open('./outputfolder/out50.txt', 'a')
    for line in catalog.readlines():
        ent = line.split(" ")
        if ent[0] != ' ':
            token = ent[0]
            off = int(ent[1].replace('\n', ''))
            catDict[token] = off
    offset = catDict[term]
    merged.seek(offset)
    data = merged.readline().split(" ", 1)
    token = data[0]
    result = json.loads(data[1])
    catalog.close()
    merged.close()

    resultDF = len(result)
    resultTTF = 0
    resultTF = []

    for res in result:
        doc_id = res[0]
        docTF = res[1]
        resultTTF += docTF
        resultTF.append((doc_id, docTF))

    # File for in.0.50.txt
    #out50.write(term + " " + str(resultDF) + " " + str(resultTTF)+"\n")
    #out50.close()

    return resultTF, resultDF, resultTTF


# Function to get the stem words and remove the stop words
def getStemWords(query_line, stopwords):
    raw_data = query_line.replace(".", "").replace(",", "").replace('"', "").replace("\n", "").replace("-", " ") \
        .replace("(", "").replace(")", "").split(" ")

    for i in stopwords:
        while i in raw_data:
            raw_data.remove(i)

    stemmedArray = raw_data
    p = PorterStemmer()

    for i in range(1, stemmedArray.__len__()):
        while stemmedArray[i] != p.stem(stemmedArray[i], 0, len(stemmedArray[i]) - 1):
            stemmedArray[i] = p.stem(stemmedArray[i], 0, len(stemmedArray[i]) - 1)

    return raw_data[0], raw_data[1:], stemmedArray[1:]


#  Function to calculate the okapiTF score for a term
def okapiTF(term_freq_dict, avg_doc_length, queryNum):
    okapiTFScore = {}

    for doc_id in term_freq_dict.keys():
        doc_len = int(term_freq_dict[doc_id][0])

        okapi_tf_wd = 0
        for term in term_freq_dict[doc_id][1].keys():
            tf = term_freq_dict[doc_id][1][term]
            d = doc_len / float(avg_doc_length)
            denom = tf + 0.5 + 1.5 * d
            okapi_tf_wd += (tf / denom)
        okapiTFScore.update({doc_id: okapi_tf_wd})

    rank = 1
    out = open("./results/okapiTF.txt", "a")

    for k in sorted(okapiTFScore, key=okapiTFScore.get, reverse=True)[:1000]:
        out.write(queryNum.__str__() + " Q0 " + k.__str__() + " " + rank.__str__() + " " + okapiTFScore[
            k].__str__() + " " + "Exp" + "\n")
        rank += 1
    out.close()


def tfidf(term_freq_dict, avg_doc_length, queryNum, term_DF_dict, total_docs):
    tfidfScore = {}

    for doc_id in term_freq_dict.keys():
        doc_len = int(term_freq_dict[doc_id][0])

        tf_idf = 0
        for term in term_freq_dict[doc_id][1].keys():
            tf = term_freq_dict[doc_id][1][term]
            lt = math.log(int(total_docs) / int(term_DF_dict[term]))
            tf_idf += ((tf / (tf + 0.5 + (1.5 * (doc_len / float(avg_doc_length))))) * lt)

        tfidfScore.update({doc_id: tf_idf})

    rank = 1
    out = open("./results/tfidf.txt", "a")

    for k in sorted(tfidfScore, key=tfidfScore.get, reverse=True)[:1000]:
        out.write(queryNum.__str__() + " Q0 " + k.__str__() + " " + rank.__str__() + " " + tfidfScore[
            k].__str__() + " " + "Exp" + "\n")
        rank += 1
    out.close()


def okapiBM25(term_freq_dict, avg_doc_length, queryNum, term_DF_dict, total_docs, queryArray):
    okapiBM25Score = {}
    k1 = 1.2
    k2 = 100
    b = 0.75

    for doc_id in term_freq_dict.keys():
        doc_len = int(term_freq_dict[doc_id][0])

        okapiBM25 = 0
        for term in term_freq_dict[doc_id][1].keys():
            tf_wd = term_freq_dict[doc_id][1][term]
            new_total_docs = int(total_docs) + 0.5
            new_df = term_DF_dict[term] + 0.5

            log_term = math.log(new_total_docs / new_df)  # 1st part of formula

            lt_num = tf_wd + (k1 * tf_wd)
            lt_denom = tf_wd + (k1 * ((1 - b) + (b * (doc_len / float(avg_doc_length)))))
            large_term = lt_num / lt_denom  # 2nd part of formula

            tf_wq = queryArray.count(term)
            tf_num = tf_wq + (k2 * tf_wq)
            tf_denom = tf_wq + k2
            tf_term = tf_num / tf_denom  # 3rd part of formula

            okapiBM25 += (log_term * large_term * tf_term)
        okapiBM25Score.update({doc_id: okapiBM25})

    rank = 1
    out = open("./results/okapiBM25.txt", "a")

    for k in sorted(okapiBM25Score, key=okapiBM25Score.get, reverse=True)[:1000]:
        out.write(queryNum.__str__() + " Q0 " + k.__str__() + " " + rank.__str__() + " " + okapiBM25Score[
            k].__str__() + " " + "Exp" + "\n")
        rank += 1
    out.close()


def unigramLMLaplace(term_freq_dict, queryNum, vocab_size, stemmedArray):
    unigramLMLaplaceScore = {}

    for doc_id in term_freq_dict.keys():
        doc_len = float(term_freq_dict[doc_id][0])

        for word in stemmedArray:
            if word not in term_freq_dict[doc_id][1].keys():
                term_freq_dict[doc_id][1].update({word: 0})
        unigramLMLaplace = 0

        for term in term_freq_dict[doc_id][1].keys():
            tf = term_freq_dict[doc_id][1][term]
            new_tf = tf + 1.0
            new_doc_len = doc_len + float(vocab_size)
            p_laplace = new_tf / new_doc_len

            unigramLMLaplace += math.log(p_laplace)
        unigramLMLaplaceScore.update({doc_id: unigramLMLaplace})

    rank = 1
    out = open("./results/unigramLMLaplace.txt", "a")

    for k in sorted(unigramLMLaplaceScore, key=unigramLMLaplaceScore.get, reverse=True)[:1000]:
        out.write(queryNum.__str__() + " Q0 " + k.__str__() + " " + rank.__str__() + " " + unigramLMLaplaceScore[
            k].__str__() + " " + "Exp" + "\n")
        rank += 1
    out.close()


def unigramLMJelMer(term_freq_dict, queryNum, vocab_size, stemmedArray, term_TTF_dict, doc_length_dict):
    unigramLMJelMerScore = {}
    total_doc_len = sum(doc_length_dict.values())

    for doc_id in term_freq_dict.keys():
        doc_len = float(term_freq_dict[doc_id][0])

        for word in stemmedArray:
            if word not in term_freq_dict[doc_id][1].keys():
                term_freq_dict[doc_id][1].update({word: 0})
        unigramLMJelMer = 0

        for term in term_freq_dict[doc_id][1].keys():
            tf = term_freq_dict[doc_id][1][term]
            ttf = term_TTF_dict[term]

            corpus_prob = 0.21
            fg = tf / doc_len
            bg1 = ttf - tf
            bg2 = total_doc_len - doc_len
            bg = bg1 / bg2
            p_jm = (corpus_prob * fg) + ((1.0 - corpus_prob) * bg)

            unigramLMJelMer += math.log(p_jm)
        unigramLMJelMerScore.update({doc_id: unigramLMJelMer})

    rank = 1
    out = open("./results/unigramLMJelinekMercer.txt", "a")

    for k in sorted(unigramLMJelMerScore, key=unigramLMJelMerScore.get, reverse=True)[:1000]:
        out.write(queryNum.__str__() + " Q0 " + k.__str__() + " " + rank.__str__() + " " + unigramLMJelMerScore[
            k].__str__() + " " + "Exp" + "\n")
        rank += 1
    out.close()


# andMapDict() function is used in ProximitySearch
def andMapDict(boolDict):
    b = True
    for x in boolDict.values():
        b = b and x
    return b


# minDiff() function is used in ProximitySearch
def minDiff(intArr):
    copyArr = intArr
    if len(copyArr) == 1:
        return 1
    minD = copyArr[1]-copyArr[0]
    copyArr.sort()
    for i in range(2, len(copyArr)):
        minD = min(minD, copyArr[i]-copyArr[i-1])
    if minD<0:
        return -minD
    else:
        return minD


# getSmallestTerm() function is used in ProximitySearch
def getSmallestTerm(window):
    min_t = float("inf")
    min_term = ""
    for term in window.keys():
        if window[term] < min_t:
            min_t = window[term]
            min_term = term
    return min_term


# Proximity Search implementation
def proximitySearch(queryNum, term_freq_dict, stemmedArray, vocab_size):
    proxmityScore = {}
    termPosDict = {}
    docPosDict = {}
    mergeCatDict = {}

    merged = open('./outputfolder/merged.txt', 'r')
    catalog = open('./outputfolder/mergeCatalog.txt', 'r')

    for line in catalog.readlines():
        ent = line.split(" ")
        if ent[0] != ' ':
            token = ent[0]
            off = int(ent[1].replace('\n', ''))
            mergeCatDict[token] = off

    for term in stemmedArray:
        offset = mergeCatDict[term]
        merged.seek(offset)
        data = merged.readline().split(" ", 1)
        result = json.loads(data[1])

        for d in result:
            docPosDict[d[0]] = d[2]
        termPosDict.update({term: docPosDict})

    for docId in term_freq_dict.keys():
        docLen = int(term_freq_dict[docId][0])

        blurbDict = {}                      # blurbDict = {term : [list of pos]}
        window = {}                         # window = {term : position we are checking}
        termWindowIdx = {}                  # termWindowIdx = {term : index of positions in window}
        termsProcessed = {}                 # termProcessed = {term : true if all the positions are seen}

        for term in term_freq_dict[docId][1].keys():
            blurbDict.update({term: termPosDict[term][docId]})
            window.update({term: termPosDict[term][docId][0]})
            termWindowIdx.update({term: 0})
            termsProcessed.update({term: False})

        smallestRange = minDiff([window[x] for x in window.keys()])
        while not andMapDict(termsProcessed):
            for eachTerm in blurbDict.keys():

                if not termsProcessed[eachTerm]:
                    termPosition = blurbDict[eachTerm][termWindowIdx[eachTerm]]

                    tempWindow = {}
                    for eachT in window.keys():
                        if eachT == eachTerm:
                            tempWindow[eachT] = termPosition
                        else:
                            tempWindow[eachT] = window[eachT]
                    tempRange = minDiff([tempWindow[k] for k in tempWindow.keys()])
                    if 1 < tempRange < smallestRange:
                        window = tempWindow
                        smallestRange = tempRange

            smallestInWindow = getSmallestTerm(window)
            termWindowIdx[smallestInWindow] += 1
            if termWindowIdx[smallestInWindow] == len(blurbDict[smallestInWindow]):
                termsProcessed[smallestInWindow] = True
                window.pop(smallestInWindow)

        numOfContainTerms = len(blurbDict.keys())
        scoreToAdd = (1500 - smallestRange) * numOfContainTerms / (docLen + int(vocab_size))
        proxmityScore.update({docId: scoreToAdd})

    rank = 1
    out = open("./results/proximitySearch.txt", "a")
    for k in sorted(proxmityScore, key=proxmityScore.get, reverse=True)[:1000]:
        out.write(queryNum.__str__() + " Q0 " + k.__str__() + " " + rank.__str__() + " " + proxmityScore[
            k].__str__() + " " + "Exp" + "\n")
        rank += 1

    out.close()
    catalog.close()
    merged.close()

# BEGIN MAIN
if __name__ == '__main__':

    # Read the doc lengths
    doc_length_dict = dict()
    with open("./doclength.txt", "r") as doclengths:
        data = doclengths.read()
        doc_length_data = data.split("\n")[:-1]  # Read till the second last line ie avoid last line

        for l in doc_length_data:
            doc_id, doc_length = l.split(" ")
            doc_length_dict.update(
                {doc_id: int(doc_length)})  # Generate dictionary of doc_id as key and doc_length as value

    # Read the doc stats
    avg_doc_length = 0
    total_docs = 0
    vocab_size = 0
    with open("./docstats.txt", "r") as docstats:
        for line in docstats:
            if line.__contains__("doc_count"):
                total_docs = line.split(" ")[1]
                total_docs = total_docs.replace("\n", "")
            if line.__contains__("avg_doc_length"):
                avg_doc_length = line.split(" ")[1]
                avg_doc_length = avg_doc_length.replace("\n", "")
            if line.__contains__("vocab_size"):
                vocab_size = line.split(" ")[1]
                vocab_size = vocab_size.replace("\n", "")

    # Stop words manually added some more words
    stopwords = open("./AP_DATA/stoplist.txt", "r").read().split("\n")
    extra_words = ["document", "discuss", "report", "include", "describe", "identify", "predict", "cite"]
    stopwords += extra_words

    # Query file parsing
    #with open("./AP_DATA/in.0.50.txt", "r") as queryFile:
    with open("./AP_DATA/query_desc.51-100.short.txt", "r") as queryFile:
        for line in queryFile:
            term_freq_dict = {}
            term_DF_dict = {}
            term_TTF_dict = {}
            if line != "\n" and line != "":

                # Code to check for in.0.50.txt
                '''d = line.replace('\n', '').lower()
                print(d)
                p = PorterStemmer()
                term = p.stem(d, 0, len(d)-1)
                if term not in stopwords:
                    try:
                        getTermVector(term)
                    except KeyError:
                        continue'''

                queryNum, queryArray, stemmedArray = getStemWords(line.lower(), stopwords)

                for term in stemmedArray:
                    resultTF, resultDF, resultTTF = getTermVector(term)

                    if term not in term_TTF_dict.keys():
                        term_TTF_dict.update({term: resultTTF})

                    if term not in term_DF_dict.keys():
                        term_DF_dict.update({term: resultDF})

                    for docId, docTermFreq in resultTF:
                        docLen = doc_length_dict[docId]
                        if docId in term_freq_dict.keys():
                            term_freq_dict[docId][1].update({term: docTermFreq})
                        else:
                            term_freq_dict.update({docId: (docLen, {term: docTermFreq})})

                okapiTF(term_freq_dict, avg_doc_length, queryNum)
                tfidf(term_freq_dict, avg_doc_length, queryNum, term_DF_dict, total_docs)
                okapiBM25(term_freq_dict, avg_doc_length, queryNum, term_DF_dict, total_docs, queryArray)
                unigramLMLaplace(term_freq_dict, queryNum, vocab_size, stemmedArray)
                unigramLMJelMer(term_freq_dict, queryNum, vocab_size, stemmedArray, term_TTF_dict, doc_length_dict)
                proximitySearch(queryNum, term_freq_dict, stemmedArray, vocab_size)

        print('Processed for all the models')
