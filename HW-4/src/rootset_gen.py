from elasticsearch import Elasticsearch

_author__ = 'Pankaj Tripathi'

if __name__ == '__main__':
    es = Elasticsearch(timeout=5000)
    if es.ping():
        indexName = "test"
        docType = "document"
        query = ["Harvard University"]
        for q in query:
            results = es.search(index=indexName, doc_type=docType, body={
                "query": {
                    "query_string": {
                        "default_field": "text",
                        "query": q
                    }
                },
                "fields": ["docno"],
                "size": 1000
            })['hits']['hits']

            with open("./root_gen.txt", "a") as f:
                for val in results:
                    line = val['fields']['docno'][0] + '\n'
                    f.write(line)
    else:
        "No connection to ElasticSearch."
