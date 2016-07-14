import base64
import random

import math
from elasticsearch import Elasticsearch

__author__ = "Pankaj Tripathi"

"""
HITS_crawl.py
----------
Environment - Python 2.7
Description - Script to calculate Hubs and Auth score for pages.
"""
es = Elasticsearch(timout=200)
hub = dict()
auth = dict()
base_set = set()
D = 200


def initializeHubAndAuth():
    """
    :return: hub and auth scores for each page initialised to 1
    """
    for p in base_set:
        hub[p] = 1
        auth[p] = 1


def hubsAndAuthorities():
    """
    Function calculates hub and authority score for each page in base set.
    :return: hub and auth score for each page p in base_set
    """
    i = 0
    while i < 4:
        for p in base_set:
            try:
                idx = str(p).encode('utf-8')
                res = es.get(index='test', doc_type='document', id=base64.urlsafe_b64encode(idx))
                inLinks = set(res['_source']['in_links'])

                auth[p] = 0
                for q in inLinks:
                    auth[p] += hub[q]
            except Exception:
                    auth[p] = 0

        for p in base_set:
            try:
                idx = str(p).encode('utf-8')
                res = es.get(index='test', doc_type='document', id=base64.urlsafe_b64encode(idx))
                outLinks = set(res['_source']['out_links'])

                hub[p] = 0
                for r in outLinks:
                    hub[p] += auth[r]
            except Exception:
                    hub[p] = 0

        normAuthDen = math.sqrt(sum([a ** 2 for a in auth.values()]))
        normHubDen = math.sqrt(sum([a ** 2 for a in hub.values()]))

        for p in auth:
            auth[p] /= normAuthDen
        for p in hub:
            hub[p] /= normHubDen
        i += 1


def dumpAuthToFile():
    """
    Function writes all the top 500 auth values in a file
    :return: file with top 500 auth values
    """
    print('Dumping Auth file..........')
    output = open('./authScore.txt', 'w')
    for k in sorted(auth, key=auth.get, reverse=True)[:500]:
        output.write(k + "\t" + str(auth[k]) + '\n')
    output.close()


def dumpHubToFile():
    """
    Function writes all the top 500 hub values in a file
    :return: file with top 500 hub values
    """
    print('Dumping Hub file...........')
    output = open('./hubScore.txt', 'w')
    for k in sorted(hub, key=hub.get, reverse=True)[:500]:
        output.write(k + "\t" + str(hub[k]) + '\n')
    output.close()


def generateBaseSet():
    """
    Function to generate base set base on some conditions mentioned below.
      1. For each page in the set, add all pages that the page points to
      2. For each page in the set, obtain a set of pages that pointing to the page
         i. if the size of the set is less than or equal to d, add all pages in the set to the root set
         ii. if the size of the set is greater than d, add an RANDOM (must be random) set of d pages from
             the set to the root set
    :return: base_set
    """
    root = open('./root_gen.txt', 'r')
    for line in root:
        if len(base_set) <= 20000:
            root_url = line.replace('\n', '')
            idx = str(root_url).encode('utf-8')

            res = es.get(index='test', doc_type='document', id=base64.urlsafe_b64encode(idx))
            outLinks = set(res['_source']['out_links'])
            inLinks = set(res['_source']['in_links'])

            base_set.update(outLinks)
            if len(inLinks) <= D:
                base_set.update(inLinks)
            else:
                temp = set(random.sample(inLinks, D))
                base_set.update(temp)
        else:
            break


if __name__ == "__main__":
    generateBaseSet()
    initializeHubAndAuth()
    hubsAndAuthorities()
    dumpAuthToFile()
    dumpHubToFile()