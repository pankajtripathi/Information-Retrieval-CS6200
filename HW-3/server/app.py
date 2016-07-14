from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from elasticsearch import Elasticsearch

app = Flask(__name__)
Bootstrap(app)

INDEX = "test"

es = Elasticsearch()

@app.route('/')
def index():

    return render_template('home.html')

@app.route('/', methods=['POST'])
def search():
    try:
        query = request.form['query']
    except:
        return render_template('404.html')

    try:
        resp = es.search(
        index = INDEX,
            doc_type = 'document',
            body = {
                'query':{
                    'query_string': {
                        'query': query
                    }
                },
                'fields' : ['docno', 'title', 'text', 'out_links'],
                'size': 100
            }
        )
    except:
        return render_template('404.html')

    res = []
    for item in resp['hits']['hits']:
        temp = {}
        temp['id'] = item['_id']

        if item['fields'].get('docno'):
            temp['docno'] = item['fields']['docno'][0]
        else:
            temp['docno'] = " "

        if item['fields'].get('title'):
            temp['title'] = item['fields']['title'][0]
        else:
            temp['title'] = " "

        if item['fields'].get('title'):
            temp['text'] = item['fields']['text'][0][:100]
        else:
            temp['text'] = " "

        if item['fields'].get('out_links'):
            temp['outlinks'] = len(item['fields'].get('out_links'))
        else:
            temp['outlinks'] = []
        res.append(temp)

    count = resp['hits'].get('total')
    return render_template('result.html', query = query, res = res, count = count)

def get_doc_by_url(url):
    try:
        res = es.get(
            index = INDEX,
            doc_type = 'document',
            id = url
        )
    except:
        return None
    return res

@app.route('/detail', methods=['GET'])
def detail():
    try:
        url = request.args.get('id')
    except:
        return render_template('404.html')
    res = get_doc_by_url(url)
    if res:
        title = res['_source']['title']

        text = res['_source']['text']

        link = res['_source']['docno']
        return render_template('detail.html', title = title, text = text, link = link)
    else:
        return render_template('404.html')

app.run(debug=True)
