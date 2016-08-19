from elasticsearch import Elasticsearch

__author__ = 'Pankaj Tripathi'

"""
trec_eval.py
----------
Environment - Python 2.7
Description - Script to generate a trec file for query id 151601 i.e. Harvard famous alumni
"""

out = dict()

if __name__ == '__main__':
    es = Elasticsearch(timeout=5000)
    if es.ping():
        indexName = "test"
        docType = "document"
        query = ["151601-Harvard famous alumni"]
        count = 0
        for q in query:
            qid = q.split('-')[0]
            queryTerm = q.split('-')[1]
            results = es.search(index=indexName, doc_type=docType, body={
                "query": {
                    "query_string": {
                        "default_field": "text",
                        "query": queryTerm
                    }
                },
                "fields": ["docno"],
                "size": 200
            })['hits']['hits']

            f = open("trec_file_" + qid + '.txt', "w")
            for val in results:
                url = val['_id']
                score = format(val['_score'], '.10f')
                out[url] = score

            for url in sorted(out, key=out.get, reverse=True):
                count += 1
                line = str(qid) + " Pankaj " + str(url) + " " + str(count) + " " + str(out[url]) + ' Exp \n'
                f.write(line)

    else:
        "No connection to ElasticSearch."
