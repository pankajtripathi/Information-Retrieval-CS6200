from elasticsearch import Elasticsearch

__author__ = "Pankaj Tripathi"

"""
document_length.py
----------
Environment - Python 3.5.1
Description - Script to calculate the length of each document.

"""

es = Elasticsearch(timeout=5000)
output = open("./AP_DATA/doclengths.txt", "a")

with open("./AP_DATA/doclist.txt", "r") as doc:
    for line in doc:
        if line != "":
            if line.split(" ")[0] != "0":
                doc_id = line.split(" ")[1].replace("\n", "")
                result = es.termvectors(index="ap_dataset",
                                        doc_type="document",
                                        id=doc_id,
                                        body={                # Body of the request for getting term vectors
                                            "fields": ["text"],
                                            "term_statistics": True,
                                            "field_statistics": True
                                        })["term_vectors"]
                doc_length = 0
                if len(result) > 0:
                    for term in result['text']['terms']:
                        doc_length += result['text']['terms'][term]['term_freq']
                    output.write(doc_id+" "+str(doc_length)+"\n")
                else:
                    output.write(doc_id + " " + str(0) + "\n")
                print("Finished " + doc_id)
output.close()
print("Doc length written in file")