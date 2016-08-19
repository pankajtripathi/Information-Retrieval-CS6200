import random
import re
import string
import warnings

from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import os

__author__ = "Pankaj Tripathi"

"""
create_index.py
----------
Environment - Python 2.7.11
Description - Script to clean the data and index in Elasticsearch.
"""

es = Elasticsearch()
corpus_path = './trec07p/data'
label_path = './trec07p/full'
lable_filename = 'index'
stopwords = list()
dictionary = list()


def getLabels():
    """
    :return: labels ie spam/ham for email docs
    """
    labelDict = dict()
    # 1 for spam and 0 for ham
    with open(label_path+'/'+lable_filename, 'r') as f:
        for line in f:
            label_list = line.split()
            labelDict[label_list[1].split('/')[2]] = '1' if label_list[0] == 'spam' else '0'
    return labelDict


def computeIndex(dataSet, labelDict, setname):
    """
    :param dataSet: training/test
    :param labelDict: labels for email docs
    :param setname: name of set whether training/test
    :return: index in elastic search with mapped fields
    """
    warnings.warn("deprecated", DeprecationWarning)
    for file in dataSet:
        print 'Processing file ' + file
        with open(file, 'r') as f:
            fileData = f.read()
            data = fileData.replace('\n', ' ').replace('\t', '')

            words = data.split()
            withoutStopwords= list()

            # check if word is in dictionary if it is check if it is a stopword
            for i in range(len(words)):
                if re.match("^[A-Za-z]*$", words[i]) and len(words[i]) < 35:
                    if words[i] in stopwords:
                        withoutStopwords.append('')
                    else:
                        withoutStopwords.append(words[i])
                else:
                    withoutStopwords.append('')
            text = ' '.join(withoutStopwords)
            text = re.sub(' +', ' ', text)
            text = text.lower()

            # Remove punctuations from text
            for p in string.punctuation:
                if p != '_' and p != '-' and p != '\'':
                    text = text.replace(p, " ")
            text = text.replace("  ", " ")
            text = BeautifulSoup(text, "html.parser").text

            # get the name of file from ./trec/data/inmail.1 where inmail.1 is filename
            dataFile = f.name.split('/')[3]

            if labelDict[dataFile] == '1':
                spamVal = 'spam'
            else:
                spamVal = 'ham'

            bodyText = {
                'file_name': dataFile,
                'label': spamVal,
                'body': text,
                'split': setname
            }

            es.index(index='spam_dataset_test', doc_type='document', id=dataFile, body=bodyText)
    print 'Indexing completed for ' + setname


def createIndex():
    labelDict = getLabels()
    print "Labels Computed.............."

    for dir_path, dir_names, file_names in os.walk(corpus_path):
        allfiles = [os.path.join(dir_path, filename).replace("\\", "/") for filename in file_names]
    training = allfiles
    test = list(random.sample(training, 15084))
    for f in test:
        training.remove(f)

    es.indices.create(index="spam_dataset_test",
                      body={
                          'settings': {
                              'index': {
                                  'store': {
                                      'type': "default"
                                  },
                                  'number_of_shards': 1,
                                  'number_of_replicas': 1
                              },
                              'analysis': {
                                  'analyzer': {
                                      'my_english': {
                                          'type': 'english',
                                          'stopwords_path': 'stoplist.txt'
                                      }
                                  }
                              }
                          },
                          "mappings": {
                              "document": {
                                  "properties": {
                                      "file_name": {
                                          "type": "string",
                                          "store": True,
                                          "index": "not_analyzed"
                                      },
                                      "body": {
                                          "type": "string",
                                          "store": True,
                                          "index": "analyzed",
                                          "term_vector": "with_positions_offsets_payloads",
                                          "analyzer": "my_english"
                                      },
                                      "label":{
                                          "type": "string",
                                          "store": True,
                                          "index": "not_analyzed"
                                      },
                                      "split": {
                                          "type": "string",
                                          "store": True,
                                          "index": "not_analyzed"
                                      }
                                  }
                              }
                          }
                      })

    print("Created index 'ap_dataset' with type 'document'")

    computeIndex(training, labelDict, 'training')
    computeIndex(test, labelDict, 'test')


if __name__ == "__main__":
    if es.ping():
        es.indices.delete(index="spam_dataset_test", ignore=[400, 404])
        print("Deleted index spam_dataset if it already existed.")

        with open('./stoplist.txt', 'r') as f:
            for line in f.readlines():
                word = line.replace('\n', '')
                stopwords.append(word)
        createIndex()
    else:
        print("Elastic search is not running")