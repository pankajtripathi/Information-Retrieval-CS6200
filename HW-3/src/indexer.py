import base64
import gzip
import json
import os
import re
from functools import partial
from imp import reload
import multiprocessing

from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
import sys

__author__ = 'Pankaj Tripathi'

"""
indexing.py
----------
Environment - Python 3.5.1
Description - Script to extract, clean and index all files in the given data corpus
              into ElasticSearch using elasticsearch.py Python API.
"""
indexName = 'test'
reload(sys)
sys.setdefaultencoding('utf-8')
es = Elasticsearch(timeout=100)
outLinkData = dict()
inLinkData = dict()


def processIndex(filedata, soup, docno):
    doc_regex = re.compile("<DOC>.*?</DOC>", re.DOTALL)
    header_regex = re.compile('<HEADER>.*?</HEADER>', re.DOTALL)
    text_regex = re.compile('<TEXT>.*?</TEXT>', re.DOTALL)

    h = HTMLParser()
    content = ''
    result = ''.join(re.findall(doc_regex, filedata))  # Match the <DOC> tags and fetch documents

    texts = ''.join(re.findall(text_regex, result)).replace('<TEXT>', '').replace('</TEXT>', '') \
        .replace('\n', ' ')

    try:
        if soup.find('content').contents:
            for c in soup.find('content').contents:
                content += str(h.unescape(c))
        else:
            content = ''
    except Exception:
        content = ''

    outLinks = outLinkData[docno]
    try:
        inLinks = inLinkData[docno]
    except KeyError:
        inLinks = []

    header = ''.join(re.findall(header_regex, result)).replace('<HEADER>', '').replace('</HEADER>', '') \
        .replace('\n', ' ')

    try:
        if soup.find('title').contents:
            title = ''.join(soup.find('title').contents)
        else:
            title = ''
    except Exception:
        title = ''

    body = dict(docno=docno, HTTPheader=header, title=title, text=texts, html_Source=content, in_links=inLinks,
                out_links=outLinks, author='Pankaj')
    return body


def checkForExistence(file):
    with open(file, 'r') as f:
        filedata = f.read()
        soup = BeautifulSoup(filedata, "html.parser")
        docno = soup.find('docno').contents[0]
        idx = str(docno).encode('utf-8')
        try:
            il = inLinkData[docno]
        except KeyError:
            il = []
        try:
            res = es.get(index=indexName, doc_type='document', id=base64.urlsafe_b64encode(idx))
            inLink = res['_source']['in_links']
            newIl = list(set(inLink + il))
            body = {
                'doc': {
                    'in_links': newIl,
                    'author': res['_source']['author'] + ';' + 'Pankaj'
                }
            }
            es.update(index=indexName, doc_type='document', id=base64.urlsafe_b64encode(idx),
                      body=body)
        except Exception:
            body = processIndex(filedata, soup, docno)
            es.index(index=indexName,
                     doc_type="document",
                     id=base64.urlsafe_b64encode(idx),
                     body=body)
        print("Completed Indexing for file :{0}".format(file))


def createIndex():
    print("Creating index test5 ....")
    es.indices.create(index=indexName,
                      body={
                          'settings': {
                              'index': {
                                  'store': {
                                      'type': "default"
                                  },
                                  'number_of_shards': 1,
                                  'number_of_replicas': 0
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
                                      "docno": {
                                          "type": "string",
                                          "store": True,
                                          "index": "analyzed",
                                          "term_vector": "with_positions_offsets_payloads"
                                      },
                                      "HTTPheader": {
                                          "type": "string",
                                          "store": True,
                                          "index": "not_analyzed"
                                      },
                                      "title": {
                                          "type": "string",
                                          "store": True,
                                          "index": "analyzed",
                                          "term_vector": "with_positions_offsets_payloads"
                                      },
                                      "text": {
                                          "type": "string",
                                          "store": True,
                                          "index": "analyzed",
                                          "term_vector": "with_positions_offsets_payloads"
                                      },
                                      "html_Source": {
                                          "type": "string",
                                          "store": True,
                                          "index": "no"
                                      },
                                      "in_links": {
                                          "type": "string",
                                          "store": True,
                                          "index": "no"
                                      },
                                      "out_links": {
                                          "type": "string",
                                          "store": True,
                                          "index": "no"
                                      },
                                      "author": {
                                          "type": "string",
                                          "store": True,
                                          "index": "analyzed"
                                      }
                                  }
                              }
                          }
                      })

    print("Created index " + indexName + " with type 'document'")


if __name__ == '__main__':
    if es.ping():
        # Delete index /ap_dataset if it already exists
        # es.indices.delete(index="test5", ignore=[400, 404])
        # print("Deleted index test5 if it already existed.")

        # createIndex()

        # Retrieve the names of all files to be indexed in folder ./HW3_Dataset of the cwd.
        for dir_path, dir_names, file_names in os.walk("./HW3_Dataset"):
            allfiles = [os.path.join(dir_path, filename).replace("\\", "/") for filename in file_names if
                        (filename != "readme" and filename != ".DS_Store")]
        with gzip.open('./outLinks.gz', 'rt') as f:
            print("Reading" + f.name)
            outLinkData = json.load(f)
        with gzip.open('./inLinks.gz', 'rt') as f:
            print("Reading" + f.name)
            inLinkData = json.load(f)

        #p = multiprocessing.Pool(10)
        #p.map(checkForExistence, allfiles)
        # For all the files, read each file and fetch the documents. From the documents fetch the doc number and text
        for file in allfiles:
            checkForExistence(file)
    else:
        print("Elastic search is not running")
