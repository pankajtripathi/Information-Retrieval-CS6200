import os

import itertools
import lda
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans
import time
from elasticsearch import Elasticsearch

__author__ = "Pankaj Tripathi"

"""
lda_topic_clustering.py
----------
Environment - Python 2.7.11
Description - Script to create lda topic model and cluster the data.
"""
es = Elasticsearch()
docCluster = dict()
queryDoc = dict()


def setClusters(filenames):
    docs = [file.replace('.txt', '') for file in filenames]
    temp = dict()

    c = 0
    for d in docs:
        c += 1
        temp[c] = d

    with open('./clusterNos.txt', 'r') as f:
        data = f.read().split('\n')[:-1]
        c = 0
        for no in data:
            c += 1
            no = int(no.replace('\n', ''))
            if no not in docCluster:
                docCluster[no] = list()
                docCluster[no].append(temp[c])
            else:
                docCluster[no].append(temp[c])
    for no in docCluster:
        body={
            'documents': docCluster[no]
        }
        es.index(index='cluster_dataset', doc_type='document', id=no, body=body)


def getClusterName(doc):
    for cluster in docCluster:
        if doc in docCluster[cluster]:
            return cluster
    return 0


def getQuery(doc):
    for query in queryDoc:
        if doc in queryDoc[query]:
            return query
    return 0


def getAccuracy():
    sc_sq = 0
    sc_dq = 0
    dc_sq = 0
    dc_dq = 0
    with open('./qrels.adhoc.51-100.AP89.txt', 'r') as qf:
        data = qf.read().split('\n')[:-1]
        for line in data:
            query, dum, doc, rel = line.split()
            query = int(query)
            rel = int(rel.replace('\n', ''))
            if rel == 1:
                if query not in queryDoc:
                    queryDoc[query] = list()
                    queryDoc[query].append(doc)
                else:
                    queryDoc[query].append(doc)
    with open('./relevantDocs.txt', 'r') as f:
        data = f.read().split('\n')[:-1]
        relDocs = list()
        for line in data:
            query, doc = line.split()
            relDocs.append(doc.replace('\n', ''))
    count = 0
    for doc1, doc2 in itertools.combinations(relDocs, 2):
        count += 1
        print "Started for " + doc1 + " " + doc2
        c1 = getClusterName(doc1)
        c2 = getClusterName(doc2)
        q1 = getQuery(doc1)
        q2 = getQuery(doc2)

        if c1 == c2 and q1 == q2:
            sc_sq += 1
        if c1 != c2 and q1 != q2:
            dc_dq += 1
        if c1 == c2 and q1 != q2:
            sc_dq += 1
        if c1 != c2 and q1 == q2:
            dc_sq += 1
    num = float(sc_sq + dc_dq)
    den = float(sc_sq + sc_dq + dc_dq + dc_sq)
    with open('./val.txt', 'a') as f:
        f.write("\nNum: "+ str(num) + '\n')
        f.write("Den: " + str(den) + '\n')
    acc = (num / den) * 100.0
    print "Accuracy: " + str(acc)


if __name__ == '__main__':
    for dirpath, dirnames, filenames in os.walk("./ap89_cleaned"):
        allfiles = [os.path.join(dirpath, filename).replace("\\", "/") for filename in filenames]
    print "Read file names."

    vectorizer = CountVectorizer(input='filename', analyzer='word', stop_words='english', decode_error='ignore')

    print "Creating document to term matrix...."
    dtm = vectorizer.fit_transform(allfiles)

    print "Starting LDA..."
    s = time.time()
    model = lda.LDA(n_topics=200, n_iter=10, random_state=1)
    model.fit_transform(dtm)
    e = time.time()
    print 'time taken ' + str(e - s)

    # To get top topics for each document in the query
    print "Starting transform..."
    start = time.time()
    rel_top = model.transform(dtm)
    end = time.time()
    print "Time taken for transform " + str(end - start)

    print 'Starting with K Means clustering...'
    st = time.time()
    km = KMeans(n_clusters=25)
    km.fit(rel_top)
    et = time.time()
    print "time for clustering " + str(et - st)

    print km.labels_
    cl = open('./clusterNos.txt', 'w')
    for no in km.labels_:
        cl.write(str(no) + '\n')
    cl.close()

    setClusters(filenames)
    getAccuracy()
    print "Done............."
