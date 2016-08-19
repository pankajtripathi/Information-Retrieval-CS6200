from elasticsearch import Elasticsearch

__author__ = "Pankaj Tripathi"

"""
unigram _matrix.py
----------
Environment - Python 2.7.11
Description - Script to create a feature matrix with all unigrams as features.
"""

es = Elasticsearch()
features = dict()
indexName = 'spam_dataset_test'
document = 'document'
indexSize = 75419
trainDocs = dict()
testDocs = dict()
trainWords = dict()


def buildFeatureList():
    """
    Create a file with all words in dataset with their sequence of occurrence
    """
    with open('./feature_list.txt', 'w')as out:
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
        for id in ids:
            text = es.get(index=indexName, doc_type=document, id=id)['_source']['body']
            terms = text.split()
            for term in terms:
                features[term] = term
        count = 0
        for term in features:
            count += 1
            out.write(str(count)+ " " + term + '\n')


def buildTrainMatrix():
    """
    Create a train matrix file with label for each email doc and features( feauture occurrence in featurelist : tf )
    """
    with open('./feature_list.txt', 'r') as f:
        for line in f.readlines():
            seq, word = line.split()
            word = word.replace('\n', '')
            trainWords[word] = int(seq)
    out = open('./trainSparseMatrix.txt', 'w')
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
    for id in ids:
        print "Matirx for " + id
        tf = dict()
        lab = es.get(index=indexName, doc_type=document, id=id)['_source']['label']
        if lab == 'spam':
            label = '1'
        else:
            label = '0'

        text = es.get(index=indexName, doc_type=document, id=id)['_source']['body']
        words = text.split()
        featureOut = dict()
        for word in words:
            featureOut[str(word)] = trainWords[str(word)]
            if word not in tf:
                tf[word] = 1
            else:
                tf[word] += 1
        outText = list()
        pDict = dict()
        for word in sorted(featureOut, key=featureOut.get):
            if word in pDict:
                continue
            else:
                pDict[word] = word
                outText.append(str(trainWords[word]) + ":" + str(tf[word]))
        outT = " ".join(outText)
        out.write(str(label) + " " + outT + "\n")
    out.close()


def buildTestMatrix():
    """
    Create a test matrix file with label for each email doc and features( feauture occurrence in featurelist : tf )
    """
    testWords = dict()
    with open('./feature_list.txt', 'r') as f:
        for line in f.readlines():
            seq, word = line.split()
            word = word.replace('\n', '')
            testWords[word] = int(seq)
    out = open('./testSparseMatrix.txt', 'w')
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
    for id in ids:
        print "Matirx for " + id
        tf = dict()
        lab = es.get(index=indexName, doc_type=document, id=id)['_source']['label']
        if lab == 'spam':
            label = '1'
        else:
            label = '0'

        text = es.get(index=indexName, doc_type=document, id=id)['_source']['body']
        words = text.split()
        featureOut = dict()
        for word in words:
            try:
                featureOut[str(word)] = testWords[str(word)]
            except KeyError:
                continue
            if word not in tf:
                tf[word] = 1
            else:
                tf[word] += 1
        outText = list()
        pDict = dict()
        for word in sorted(featureOut, key=featureOut.get):
            if word in pDict:
                continue
            else:
                pDict[word] = word
                outText.append(str(testWords[word]) + ":" + str(tf[word]))
        outT = " ".join(outText)
        out.write(str(label) + " " + outT + "\n")
    out.close()


if __name__ == "__main__":
    buildFeatureList()
    with open('./train_ids_list.txt', 'r') as f:
        for line in f.readlines():
            seq, doc = line.split()
            doc = doc.replace('\n', '')
            trainDocs[doc] = seq
    with open('./test_ids_list.txt', 'r') as f:
        for line in f.readlines():
            seq, doc = line.split()
            doc = doc.replace('\n', '')
            testDocs[doc] = seq
    buildTrainMatrix()
    buildTestMatrix()



