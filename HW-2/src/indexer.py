import glob
import json
import os
import re
import pickle
import timeit
import multiprocessing
from PorterStemmer import PorterStemmer

__author__ = "Pankaj Tripathi"

"""
indexer.py
----------
Environment - Python 3.5.1
Description - Given a raw document you need to produce a sequence of tokens.  One way to think about the tokenizing
              process is as a conversion from a document to a sequence of (term_id, doc_id, position) tuples which need
              to be stored in your inverted index.
"""
p = PorterStemmer()
doclengthfile = open("./doclength.txt", "a")
docstatsfile = open('./docstats.txt', 'a')
totaldocs = 0
vocab_size = 0


# Function to tokenize the text from the corpus
def tokenize(docid, doctext, stopwords):
    doctext = doctext.lower()
    doctext = [match.group() for match in re.finditer(r"\w+('\w+)*(\.?\w+)*", doctext, re.M | re.I)]

    indexed_tokens = [(index + 1, word) for index, word in enumerate(doctext) if word not in stopwords]
    unique = 1
    data = {}
    for pos, token in indexed_tokens:
        token2 = p.stem(token, 0, len(token) - 1)
        while token != token2:
            token = token2
            token2 = p.stem(token, 0, len(token) - 1)

        if token not in data:
            data[token] = {"tf": 1,
                           "positions": [pos],
                           "unique": unique}
            unique += 1
        else:
            data[token]["tf"] += 1
            data[token]["positions"].append(pos)
    doclengthfile.write(str(docid) + " " + str(len(indexed_tokens)) + "\n")
    doclengthfile.flush()

    return {"docid": docid,
            "tokens": data}


# Function to merge all the data ie docid, TF, pos for a term  and create a dict
def merge(tokenized_data):
    merged_dict = {}
    for data in tokenized_data:
        docid = data["docid"]
        for token, tokdata in data["tokens"].items():
            e = (docid, tokdata["tf"], tokdata["positions"])
            if token in merged_dict:
                merged_dict[token].append(e)
            else:
                merged_dict[token] = [e]
    return merged_dict


# Funciton to read all the data from the file name ie docid and text
def readDocs(filename):
    # Regular expressions to extract data from the corpus
    doc_regex = re.compile("<DOC>.*?</DOC>", re.DOTALL)
    docno_regex = re.compile("<DOCNO>.*?</DOCNO>")
    text_regex = re.compile("<TEXT>.*?</TEXT>", re.DOTALL)

    data = []
    with open(filename, 'r', encoding='ISO-8859-1') as f:
        filedata = f.read()
        result = re.findall(doc_regex, filedata)  # Match the <DOC> tags and fetch documents

        for document in result:
            # Retrieve contents of DOCNO tag
            docno = re.findall(docno_regex, document)[0].replace("<DOCNO>", "").replace("</DOCNO>", "").strip()
            # Retrieve contents of TEXT tag
            texts = "".join(re.findall(text_regex, document)).replace("<TEXT>", "").replace("</TEXT>", "") \
                .replace("\n", " ")
            data.append((docno, texts))
    return data


# Function to dump the merged data to temp files
def dump_merged_data(merged_data, param):
    with open('./outputfolder/index-' + param + '.txt', 'w') as output:
        json.dump(merged_data, output, sort_keys=True, indent=4, separators=(',', ': '))


# Function to tokenize the docs for the files from corpus
def tokenizeDocs(docinfos, stopwords, counter):
    print("Process {0} working...".format(counter))
    tokenized_data = [tokenize(docid, doctext, stopwords)
                      for (docid, doctext) in docinfos]
    merged_data = merge(tokenized_data)
    pickleData(merged_data, "./outputfolder/temp-merged-{0}.p".format(counter))
    print("Process {0} finished.".format(counter))


# Function to write a file with token value pairs where value is [[docid, TF, [pos]]]
def serializeData(merged_data, filename):
    outfile = open(filename, 'w')
    for token in sorted(merged_data.keys()):
        value = merged_data[token]
        outfile.write("{0} {1}\n".format(token, value))
    outfile.close()


# Function is used to picke the merged text file and then keep merging the files
def pickleData(merged_data, filename):
    outfile = open(filename, 'wb')
    for token in sorted(merged_data.keys()):
        value = merged_data[token]
        pickle.dump((token, value), outfile)
    outfile.close()


# Function to compare lines in temp files
def compare(l1, l2):
    t1, v1 = l1
    t2, v2 = l2
    if t1 < t2:
        return -1
    if t1 == t2:
        return 0
    return 1


# Function to merge lines in case they have same term
def mergeLines(l1, l2):
    t1, v1 = l1
    t2, v2 = l2
    return (t1, v1 + v2)


# Function to re pickle the data back to text file
def pickleToText(infilename, outfilename):
    print("Converting " + infilename)
    infile = open(infilename, "rb")
    outfile = open(outfilename, "w")
    try:
        while True:
            token, value = pickle.load(infile)
            outfile.write(token + " " + json.dumps(value) + "\n")
    except EOFError:
        outfile.close()
        infile.close()


# Function which tokenizes all the files by taking 1000 docs at once
def tokenizeAll(filenames, stopwords, docsize=1000):
    processes = []
    docs = []
    counter = 1
    tokenized_data = []
    final_dict = {}
    for i, filename in enumerate(filenames):
        docs += readDocs(filename)
        if len(docs) >= docsize:
            p = multiprocessing.Process(target=tokenizeDocs, args=(docs[0:docsize], stopwords, counter))
            p.start()
            processes.append(p)
            docs = docs[docsize:]
            counter += 1

    if len(docs) > 0:
        p = multiprocessing.Process(target=tokenizeDocs, args=(docs, stopwords, counter))
        p.start()
        processes.append(p)
    for process in processes: process.join()


# Function to read the corpus for tokenizing and indexing
def readCorpus():
    stopwords = set(open("./AP_DATA/stoplist.txt", "r").read().split("\n"))
    # Retrieve the names of all files to be indexed in folder ./AP_DATA/ap89_collection of the cwd.
    for dir_path, dir_names, file_names in os.walk("./AP_DATA/ap89_collection"):
        allfiles = [os.path.join(dir_path, filename).replace("\\", "/") for filename in file_names if
                    (filename != "readme" and filename != ".DS_Store")]
    tokenizeAll(allfiles, stopwords)
    doclengthfile.close()
    # pprint.pprint(tokenizeAll(allfiles))


# Function which writes all the document stats to a file
def getDocStats():
    with open('./doclength.txt', 'r') as doc, open('./outputfolder/merged.txt', 'r') as idx:
        data = doc.read()
        vs = idx.read()
        doclength_data = data.split("\n")[:-1]  # Read till the second last line ie avoid last line
        index_data = vs.split("\n")[:-1]  # Read till the second last line ie avoid last line
        doc_stats_dict = dict()

        for l in doclength_data:
            doc_id, doc_length = l.split(" ")
            doc_stats_dict.update(
                {doc_id: int(doc_length)})  # Generate dictionary of doc_id as key and doc_length as value

        total_docs = len(doc_stats_dict.keys())
        avg_doc_length = round(sum(doc_stats_dict.values()) / total_docs)
        vocab_size = len(index_data)

        docstatsfile.write("doc_count " + str(total_docs) + "\n")
        docstatsfile.write("avg_doc_length " + str(avg_doc_length) + "\n")
        docstatsfile.write("vocab_size " + str(vocab_size) + "\n")
        docstatsfile.flush()


# Function which recursively merges the files until a single merged file remains
def combineMergeFiles(recurse=0):
    processes = []
    for dir_path, dir_names, file_names in os.walk("./outputfolder"):
        allfiles = [os.path.join(dir_path, filename).replace("\\", "/") for filename in file_names if
                    (filename != "readme" and filename != ".DS_Store")]

    if len(allfiles) is 1:
        return
    size = len(allfiles)
    for i in range(0, size - size % 2, 2):
        process = multiprocessing.Process(target=mergeFiles,
                                          args=(allfiles[i],
                                                allfiles[i + 1],
                                                "./outputfolder/merged-{0}_{1}.p".format(recurse, i)))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    combineMergeFiles(recurse + 1)


# Function to obtain the size of file in bytes
def fileSize(f):
    fileobject = open(f, "rb")
    fileobject.seek(0, 2)  # move the cursor to the end of the file
    size = fileobject.tell()
    fileobject.close()
    return size


# Function to merge files by comparing each line
def mergeFiles(file1, file2, file):
    print("Generating " + file)
    f = open(file, "wb")
    print("{0} + {1} => {2}".format(file1, file2, file))
    s1 = fileSize(file1)
    s2 = fileSize(file2)
    f1 = open(file1, "rb")
    f2 = open(file2, "rb")
    l1 = pickle.load(f1)
    l2 = pickle.load(f2)
    i1 = f1.tell()
    i2 = f2.tell()

    while i1 < s1 and i2 < s2:
        while i1 < s1 and i2 < s2 and compare(l1, l2) < 0:
            pickle.dump(l1, f)
            l1 = pickle.load(f1)
            i1 = f1.tell()

        while i1 < s1 and i2 < s2 and compare(l1, l2) == 0:
            pickle.dump(mergeLines(l1, l2), f)
            l1 = pickle.load(f1)
            l2 = pickle.load(f2)
            i1 = f1.tell()
            i2 = f2.tell()

        while i1 < s1 and i2 < s2 and compare(l1, l2) > 0:
            pickle.dump(l2, f)
            l2 = pickle.load(f2)
            i2 = f2.tell()

    while i1 < s1:
        pickle.dump(l1, f)
        l1 = pickle.load(f1)
        i1 = f1.tell()

    while i2 < s2:
        pickle.dump(l2, f)
        l2 = pickle.load(f2)
        i2 = f2.tell()

    f.close()
    os.remove(file1)
    os.remove(file2)


# Function to create a inverted index file
def createInvertedIndex(infilename, outfilename):
    infile = open(infilename, "r")
    outfile = open(outfilename, "w")
    for inline in infile.readlines():
        entries = inline.split(" ", 1)
        values = json.loads(entries[1])
        outfile.write(entries[0] + " " + json.dumps([(t[0], t[1]) for t in values]) + '\n')

    infile.close()
    outfile.close()


# Function to create a catalog file for inverted index
def createCatalog():
    catalog = open('./outputfolder/catalog.txt', 'a')
    size = fileSize('./outputfolder/invertIndex.txt')
    file = open('./outputfolder/invertIndex.txt', 'r')
    curpos = 0
    while curpos < size:
        l = file.readline()
        newpos = file.tell()
        token = l.split()[0]
        catalog.write(token + " " + str(curpos) + '\n')
        curpos = newpos
    catalog.close()
    file.close()


# Function to create a catalog file for merged file
def createMergedCatalog():
    catalog = open('./outputfolder/mergeCatalog.txt', 'a')
    size = fileSize('./outputfolder/merged.txt')
    file = open('./outputfolder/merged.txt', 'r')
    curpos = 0
    while curpos < size:
        l = file.readline()
        newpos = file.tell()
        token = l.split()[0]
        catalog.write(token + " " + str(curpos) + '\n')
        curpos = newpos
    catalog.close()
    file.close()


# Function to check whether the catalog is generated correctly
def testCatalog():
    catalog = open('./outputfolder/catalog.txt', 'r')
    merged = open('./outputfolder/merged.txt', 'r')
    for line in catalog.readlines():
        entries = line.split(" ")
        merged.seek(int(entries[1]))
        mergedLine = merged.readline()
        if entries[0] != mergedLine.split(" ")[0]:
            print("Error: {0} not correctly catalogued".format(entries[0]))
            print(mergedLine)
    catalog.close()
    merged.close()

# BEGIN MAIN
if __name__ == "__main__":
    start = timeit.default_timer()
    readCorpus()
    combineMergeFiles()
    pickleToText(glob.glob("./outputfolder/*.p")[0], "./outputfolder/merged.txt")
    createInvertedIndex("./outputfolder/merged.txt", "./outputfolder/invertIndex.txt")
    getDocStats()
    createCatalog()
    createMergedCatalog()
    #testCatalog()
    end = timeit.default_timer()
    print((end - start) / 60)
