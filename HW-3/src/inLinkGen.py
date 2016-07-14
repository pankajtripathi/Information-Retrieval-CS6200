import gzip
import json
import pprint
import re
import os

inLinksDict = dict()


def dumpInLinks(inlinks, fname):
    print('Dumping File ' + fname)
    with gzip.open(fname, 'wt') as f:
        json.dump(inlinks, f)
    print("Done..................")


def getInlinks():
    doc_regex = re.compile("<DOC>.*?</DOC>", re.DOTALL)
    docno_regex = re.compile('<DOCNO>.*?</DOCNO>', re.DOTALL)

    with gzip.open('./outLinksTest.gz', 'rt') as f:
        outLinksData = json.load(f)

    # Retrieve the names of all files to be indexed in folder ./HW3_Dataset of the cwd.
    for dir_path, dir_names, file_names in os.walk("./HW3_Data"):
        allfiles = [os.path.join(dir_path, filename).replace("\\", "/") for filename in file_names if
                    (filename != "readme" and filename != ".DS_Store")]

    for file in allfiles:
        with open(file, 'r') as f:
            il = []
            print('Reading: ' + f.name)
            filedata = f.read()
            result = ''.join(re.findall(doc_regex, filedata))  # Match the <DOC> tags and fetch documents

            url = ''.join(re.findall(docno_regex, result)).replace('<DOCNO>', '').replace('</DOCNO>', '')

            for key in outLinksData:
                if url in outLinksData[key]:
                    il.append(key)
            inLinksDict[url] = il
    dumpInLinks(inLinksDict, './inLinksTest.gz')


def readInLinks():
    with gzip.open('./inLinks.gz', 'rt') as f:
        data = json.load(f)
    pprint.pprint(data)


if __name__ == '__main__':
    getInlinks()
    #readInLinks()
