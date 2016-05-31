import os
import re

from elasticsearch import Elasticsearch

__author__ = "Pankaj Tripathi"

"""
indexing.py
----------
Environment - Python 3.5.1
Description - Script to extract, clean and index all files in the given data corpus
              into ElasticSearch using elasticsearch.py Python API.
"""
es = Elasticsearch()

if es.ping():
    # Delete index /ap_dataset if it already exists
    es.indices.delete(index="ap_dataset", ignore=[400, 404])
    print("Deleted index ap_dataset if it already existed.")

    # Retrieve the names of all files to be indexed in folder ./AP_DATA/ap89_collection of the cwd.
    for dir_path, dir_names, file_names in os.walk("./AP_DATA/ap89_collection"):
        allfiles = [os.path.join(dir_path, filename).replace("\\", "/") for filename in file_names if (filename != "readme" and filename != ".DS_Store")]

    # Create index in elasticsearch and configure settings and mappings
    print("Creating index ap_dataset ....")
    es.indices.create(index="ap_dataset",
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
                                      "docno":{
                                          "type": "string",
                                          "store": True,
                                          "index": "not_analyzed"
                                      },
                                      "text": {
                                          "type": "string",
                                          "store": True,
                                          "index": "analyzed",
                                          "term_vector": "with_positions_offsets_payloads",
                                          "analyzer": "my_english"
                                      }
                                  }
                              }
                          }
                      })

    print("Created index 'ap_dataset' with type 'document'")

    # Regular expressions to extract data from the corpus
    doc_regex = re.compile("<DOC>.*?</DOC>", re.DOTALL)
    docno_regex = re.compile("<DOCNO>.*?</DOCNO>")
    text_regex = re.compile("<TEXT>.*?</TEXT>", re.DOTALL)

    # For all the files, read each file and fetch the documents. From the documents fetch the doc number and text
    for file in allfiles:
        with open(file, 'r', encoding='ISO-8859-1') as f:
            filedata = f.read()
            result = re.findall(doc_regex, filedata)  # Match the <DOC> tags and fetch documents

            for document in result:
                # Retrieve contents of DOCNO tag
                docno = re.findall(docno_regex, document)[0].replace("<DOCNO>", "").replace("</DOCNO>", "").strip()
                # Retrieve contents of TEXT tag
                texts = "".join(re.findall(text_regex, document)).replace("<TEXT>", "").replace("</TEXT>", "")\
                        .replace("\n", " ")

                es.index(index="ap_dataset",
                         doc_type="document",
                         id= docno,
                         body={
                             "docno": docno,
                             "text": texts
                         })
        print("Completed:{0}".format(file))

    print("Indexing completed")

    es.indices.refresh(index="ap_dataset")
    print("Index refreshed.")

else:
    print("Elastic search is not running")