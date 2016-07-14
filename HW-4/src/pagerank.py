import math

__author__ = "Pankaj Tripathi"

"""
pagerank.py
----------
Environment - Python 3.5.1
Description - Script to calculate page rank for each page crawled.
"""
P = []
S = []
d = 0.85
PR = {}
webGraph = {}
Lq = {}
convergenceItr = 4


def calculatePerplexity(PR):
    """
    :param PR: PageRank dictionary where page is key and pagerank is value
    :return: perplexity
    """
    entropy = 0
    for p in PR:
        p = PR[p]
        entropy += p * math.log(p, 2)
    return 2 ** (-entropy)


def dumpPRResults(PR):
    """
    :param PR: PageRank dictionary where page is key and pagerank is value
    Print a file with thte PR key values
    """
    output = open('./wt2g_output.txt', 'w')
    for k in sorted(PR, key=PR.get, reverse=True)[:500]:
        output.write(k + " " + str(PR[k]) + '\n')
    output.close()


def calculatePageRank(file):
    """
    :param file: wt2g_inlinks file
    :return: PR PageRank dictionary where page is key and pagerank is value
    """
    i = 0
    j = 0

    for line in file:
        line = line.replace('\n', '')
        lineData = line.split()
        p = lineData[0]
        P.append(p)
        Mp = lineData[1:len(lineData)]
        Mp = list(set(Mp))
        webGraph[p] = Mp
        Lq[p] = 0

    for values in webGraph.values():  # Finding the number of out-links for every page
        for value in values:
            if value in Lq:
                Lq[value] += 1
            else:
                Lq[value] = 1
                webGraph[value] = []
                continue

    for page in Lq.keys():  # Finding the pages that have no out-links
        if Lq[page] == 0:
            S.append(page)

    for p in webGraph.keys():
        PR[p] = 1/len(P)
    oldPerplexity = calculatePerplexity(PR)

    while i < convergenceItr:
        sinkPR = 0
        newPR = {}
        N = len(P)
        for p in S:
            sinkPR += PR[p]
        for p in webGraph.keys():
            newPR[p] = (1 - d) / N  # teleportation
            newPR[p] += d * sinkPR / N  # spread remaining sink PR evenly
            for q in webGraph[p]:  # pages pointing to p
                newPR[p] += d * PR[q] / Lq[q] # add share of PageRank from in-links
        for p in webGraph.keys():
            PR[p] = newPR[p]
        j += 1
        newPerplexity = calculatePerplexity(PR)
        # Check if the change in the perplexity is less than 1 for 4 iterations
        if abs(oldPerplexity - newPerplexity) < 1:
            i += 1
        oldPerplexity = newPerplexity  # Update the old perplexity
    dumpPRResults(PR)


if __name__ == "__main__":
    file = open('./wt2g_inlinks.txt', 'r')
    calculatePageRank(file)
