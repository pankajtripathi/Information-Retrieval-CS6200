from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap
from elasticsearch import Elasticsearch

app = Flask(__name__)
Bootstrap(app)

queries = {"151601": "Harvard famous alumni", "151602": "Harvard rankings", "151603": "Harvard costs"}
qrel = {"151601": [], "151602": [], "151603": []}
res_list = {"151601": [], "151602": [], "151603": []}
currentuser = "Wen"

es = Elasticsearch()

def init():
    for i in queries:
        res_list[i] = get_res_list(queries[i])
    read_res()

def read_res():
    global qrel
    fo = open("./data/qrel.txt")
    for line in fo:
        qid, _, docid, rel = line.split()
        qrel[qid].append(docid)
    fo.close()

def write_res(qid, user, docid, rel):
    fo = open("./data/qrel.txt", "a")
    line = "{} {} {} {}\n".format(qid, user, docid, rel)
    fo.write(line)

def get_res_list(query):
    try:
        resp = es.search(
            index = 'test',
            doc_type = 'document',
            body = {
                'query':{
                    'query_string': {
                        'query': query.lower()
                    }
                },
                'fields' : ['docno', 'title', 'text'],
                'size': 200
            }
        )
    except:
        return []

    res = []
    for item in resp["hits"]["hits"]:
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
        res.append(temp)
    return res

def get_doc_by_url(url):
    try:
        res = es.get(
            index = 'test',
            doc_type = 'document',
            id = url
        )
    except:
        return None
    return res


@app.route("/")
def set_username():
    return render_template("home.html")

@app.route("/assess", methods=['GET', 'POST'])
def assess_list():
    global currentuser
    global qrel
    try:
        qid = request.args.get('id')
    except:
        return render_template('404.html')

    try:
        username = request.form['query']
        currentuser = username
    except:
        currentuser = currentuser

    print currentuser
    if not qid:
        return render_template('result.html', res = res_list["151601"], queries = queries, index = "151601", rel = qrel["151603"])
    else:
        return render_template('result.html', res = res_list[qid], queries = queries, index = qid, rel = qrel[qid])

@app.route('/detail', methods=['GET'])
def detail():
    try:
        url = request.args.get('id')
        qid = request.args.get('qid')
    except:
        return render_template('404.html')

    res = get_doc_by_url(url)
    if res:
        title = res['_source']['title']

        text = res['_source']['text']

        link = res['_source']['docno']
        return render_template('detail.html', title = title, text = text, link = link, qid = qid, did = url)
    else:
        return render_template('404.html')

@app.route('/score', methods=['GET'])
def score():
    global currentuser
    global qrel
    try:
        qid = request.args.get('qid')
        did = request.args.get('did')
        score = request.args.get('score')
    except:
        return render_template('404.html')

    if qid and did and score:
        write_res(qid, currentuser, did, score)
        qrel[qid].append(did)
        return redirect('./assess?id=' + qid)
    else:
        return redirect('./assess')

init()
app.run(debug=True)
