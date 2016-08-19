import math

import collections

__author__ = "Pankaj Tripathi"

"""
trec_eval.py
----------
Environment - Python 2.7
Description - Script to generate a single qrel file
"""
qrel = dict()
out = dict()

def populateSingleQrel(file):
    with open(file, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line is "": break
            (queryID, author, url, rel) = line.split()
            rel = int(rel)
            if queryID not in qrel:
                qrel[queryID] = {}
            if url not in qrel[queryID]:
                qrel[queryID][url] = []
            qrel[queryID][url].append(rel)


def generateSingleQrel():
    output = open('./qrel_merged.txt', 'w')
    for queryID in qrel:
        for url in qrel[queryID]:
            l = qrel[queryID][url]
            qrel[queryID][url] = math.floor(sum(l) / len(l))
            out = collections.OrderedDict(sorted(qrel.items()))
    for queryID in out:
        for url in out[queryID]:
            output.write(str(queryID) + " " + "pankaj" + " " + str(url) + " " + str(out[queryID][url]) + '\n')
    output.close()


if __name__ == "__main__":
    files = ['./qrel_pankaj.txt', './qrel_wen.txt', './qrel_tianlu.txt']
    for file in files:
        populateSingleQrel(file)
    generateSingleQrel()
