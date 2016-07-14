import math
import sys
from imp import reload

from elasticsearch import Elasticsearch

__author__ = "Pankaj Tripathi"

"""
pagerank_crawled.py
----------
Environment - Python 2.7
Description - Script to calculate page rank for each page crawled.
"""
reload(sys)
sys.setdefaultencoding('utf-8')
es = Elasticsearch(timeout=1500)
P = []
S = []
PR = dict()
webGraph = dict()
Lq = dict()
convergenceItr = 4


def calculatePerplexity(PR):
    """
    :param PR: PageRank dictionary where url is key and pagerank is value
    :return: perplexity
    """
    entropy = 0
    try:
        for value in PR.values():  # Finding the Shannon entropy for each inlink
            entropy += - (value * math.log(value, 2))
            perplexity = math.pow(2, entropy)  # Calulating the perplexity
        return perplexity
    except ValueError:
        return 0


def dumpPRResults(PR):
    """
    :param PR: PageRank dictionary where url is key and pagerank is value
    Print a file with thte PR key values
    """
    print("Dumping Results.........")
    output = open('./pagerank_crawled_output.txt', 'w')
    for k in sorted(PR, key=PR.get, reverse=True)[:500]:
        output.write(k + "\t" + str(PR[k]) + "\t" + str(len(webGraph[k])) + '\n')
    output.close()


def calculatePageRank():
    """
    :return: PR PageRank dictionary where url is key and pagerank is value
    """
    D = 0.85
    i = 0
    j = 0
    res = es.search(index='test', body={"query": {"match_all": {}}, 'fields': ["_id"], 'size': 69903})
    ids = [d['_id'] for d in res['hits']['hits']]
    for id in ids:
        result = es.get(index='test', doc_type='document', id=id)
        url = result['_source']['docno']
        Mp = result['_source']['in_links']
        Lq[url] = list(set(result['_source']['out_links']))
        if len(Lq[url]) != 0:
            P.append(url)
            webGraph[url] = Mp

    for url in Lq.keys():  # Finding the pages that have no out-links
        if Lq[url] == 0:
            S.append(url)

    for p in webGraph.keys():
        PR[p] = 1 / len(P)

    oldPerplexity = calculatePerplexity(PR)

    while i < convergenceItr:
        sinkPR = 0
        newPR = dict()
        N = float(len(P))
        for p in S:
            sinkPR += PR[p]
        for p in webGraph.keys():
            newPR[p] = ((1 - D) / N) + D * sinkPR / N
            try:
                for q in webGraph[p]:  # pages pointing to p
                    newPR[p] += D * PR[q] / float(len(Lq[q]))  # add share of PageRank from in-links
            except KeyError:
                newPR[p] = 0
        for p in webGraph.keys():
            PR[p] = newPR[p]
        j += 1
        newPerplexity = calculatePerplexity(PR)
        # Check if the change in the perplexity is less than 1 for 4 iterations
        if abs(oldPerplexity - newPerplexity) < 1:
            i += 1
        oldPerplexity = newPerplexity  # Update the old perplexity
    dumpPRResults(PR)


if __name__ == '__main__':
    calculatePageRank()
