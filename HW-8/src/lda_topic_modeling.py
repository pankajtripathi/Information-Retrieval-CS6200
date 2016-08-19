import numpy as np
import lda
from sklearn.feature_extraction.text import CountVectorizer

__author__ = "Pankaj Tripathi"

"""
lda_topic_modeling.py
----------
Environment - Python 2.7.11
Description - Script to create lda topic model for AP89 dataset.
"""


def generateLDA(queryDocMap):
    for query in queryDocMap:
        all_docs = list()
        vectorizer = CountVectorizer(input='file', analyzer='word', stop_words='english', max_df=0.95, min_df=2,
                                     decode_error='ignore')

        docs = queryDocMap[query]
        for doc in docs:
            all_docs.append(file('./ap89_cleaned/' + doc + '.txt'))

        # Create term matrix
        print "Creating document term matrix for " + query
        docTermMatrix = vectorizer.fit_transform(all_docs)

        # Extracting vocabulary
        vocab = vectorizer.get_feature_names()
        vocab = np.array(vocab)

        print "Starting LDA"
        model = lda.LDA(n_topics=20, n_iter=1500, random_state=1)
        model.fit_transform(docTermMatrix)

        topic_word = model.topic_word_  # model.components_ also works

        out = open('./topicModel.txt', 'a')
        topic = dict()
        topicSum = dict()
        n_top_words = 20
        c = 0
        for words in topic_word:
            topicSum[c] = sum(words)
            topic[c] = words
            c += 1
        out.write('For query ' + query + "\n")
        for k in sorted(topicSum, key=topicSum.get, reverse=True):
            words = topic[k]
            topic_words = np.array(vocab)[np.argsort(words)][:-(n_top_words + 1):-1]
            topic_score = np.array(words)[np.argsort(words)][:-(n_top_words + 1):-1]
            temp = list()
            for i, word in enumerate(topic_words):
                t = str(word) + ' ' + str(topic_score[i])
                temp.append(t)
            out.write('Topic {}: {}'.format(k, '\t'.join(temp)) + '\n')
        out.write('\n\n')
        out.close()

        with open('./Top3Topics.txt', 'a') as outt:
            # To get top topics for each document in the query
            rel_top = model.transform(docTermMatrix)
            docIdx = 0
            tot = dict()
            for li in rel_top:
                i = 0
                top = dict()
                for score in li:
                    top[i] = score
                    i += 1
                topics = ''
                for k in sorted(top, key=top.get, reverse=True)[:3]:
                    topics += 'topic ' + str(k) + ' '
                tot[docIdx] = topics
                docIdx += 1
            outt.write('For query ' + query + "\n" + "\n")
            outt.write('Top 3 Topics for each document:\n')
            for i, doc in enumerate(docs):
                outt.write(doc + ':\n')
                outt.write(str(tot[i]) + '\n')
            outt.write('\n\n')


if __name__ == "__main__":
    queryDocMap = dict()
    relDocs = list()
    with open('./okapiBM25.txt', 'r') as of, open('./qrels.adhoc.51-100.AP89.txt', 'r') as qf:
        okapiData = of.read()
        qrelData = qf.read()

        okapiData = okapiData.split('\n')[:-1]
        qrelData = qrelData.split('\n')[:-1]

        for line in okapiData:
            query, dum, doc, dum, dum, dum = line.split()
            if query not in queryDocMap:
                queryDocMap[query] = set()
                queryDocMap[query].add(doc)
            else:
                queryDocMap[query].add(doc)
        for line in qrelData:
            query, dum, doc, rel = line.split()
            rel = int(rel.replace('\n', ''))
            if query in queryDocMap:
                if rel > 0:
                    relDocs.append((query, doc))
                    queryDocMap[query].add(doc)
    out = open('./relevantDocs.txt', 'w')
    for query, doc in relDocs:
        out.write(str(query) + " " + str(doc) + '\n')
    out.close()
    generateLDA(queryDocMap)
