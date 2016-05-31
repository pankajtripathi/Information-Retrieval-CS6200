from elasticsearch import Elasticsearch

__author__ = "Pankaj Tripathi"

"""
documents_stats.py
----------
Environment - Python 3.5.1
Description - Script to extract average document length, document count and the
              number of unique terms in the entire index.
"""

es = Elasticsearch(timeout=5000)
output = open("./AP_DATA/docstats.txt", "a")

with open("./AP_DATA/doclengths.txt", "r") as doc:
    data = doc.read()
    doclength_data = data.split("\n")[:-1]  # Read till the second last line ie avoid last line
    doc_stats_dict = dict()

    for l in doclength_data:
        doc_id, doc_length = l.split(" ")
        doc_stats_dict.update({doc_id: int(doc_length)})  # Generate dictionary of doc_id as key and doc_length as value

    total_docs = len(doc_stats_dict.keys())
    avg_doc_length = round(sum(doc_stats_dict.values())/total_docs)

    output.write("doc_count " + str(total_docs) + "\n")
    output.write("avg_doc_length " + str(avg_doc_length) + "\n")

# Get vocabulary size
result = es.search(index="ap_dataset",
                   doc_type="document",
                   body={
                       "aggs": {
                           "unique_terms": {
                               "cardinality": {
                                   "field": "text"
                               }
                           }
                       }
                   })

vocab_size = result["aggregations"]["unique_terms"]["value"]

output.write("vocab_size " + str(vocab_size) + "\n")
output.close()


