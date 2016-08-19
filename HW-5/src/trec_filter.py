import collections

outDict = dict()
tempDict = dict()
if __name__ == "__main__":
    with open('./Trec-Text-HW5.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line is "": break
            (queryID, dummy, docid, dummy, rel, dummy) = line.split()
            key = queryID + "$" + docid
            outDict[key] = float(rel)

    out = open('./trecTestNew.txt', 'w')
    for k in sorted(outDict, key=outDict.get, reverse=True):
        (queryNum, doc) = k.split('$')
        out.write(queryNum + " " + "Q0" + " " + doc + " " + str(333) + " " + str(outDict[k]) + " " + "Exp" + '\n')
    out.close()

    with open('./Trec-Text-HW5.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line is "": break
            (queryID, dummy, docid, dummy, rel, dummy) = line.split()
            if queryID not in tempDict:
                tempDict[queryID] = {}
            if docid not in tempDict[queryID]:
                tempDict[queryID][docid] = 0
            tempDict[queryID][docid] = rel

    outer = open('./trecTestFull.txt', 'w')
    count = 0
    temp = collections.OrderedDict(sorted(tempDict.items()))
    for queryID in temp:
        for docid in temp[queryID]:
            outer.write(queryID + " " + "Q0" + " " + docid + " " + str(333) + " " + str(temp[queryID][docid]) + " " + "Exp" + '\n')
    outer.close()
