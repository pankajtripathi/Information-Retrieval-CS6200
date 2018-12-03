##Homework8: Clustering and Topic Models 
__Objective__      
In this assignment, you will cluster documents, detect topics, and represent documents in topic space.
Data : We are using the AP89 collection. 

__A) Topic Models per Query__     
For any given query, select a set of documents that is union of top 1000 BM25 docs (for that query) and the qrel docs (for that query). The set will be a little over 1000 docs since there will be considerable overlap.      
Then use package listed below to perform LDA. Your output must contain     
1. the topics detected, with each topic represented as distribution over words (list the top 20-30 words)
2. the documents represented as topic distribution. Each document should have listed the most relevant 10 topics or so
Repeat the process for each one of the 25 queries.     

__LDA: python sklearn__       

1) Install scikit i.e. sklearn package for python

2)Convert the Top set of documents for each query into document-term matrix. You can use CountVectorizer from sklearn.feature_extraction.text package
It is good idea to restrict stop words, words with very high document frequency and also words not occouring more than say 1 or 2 time. These all can be passed in CountVectorizer

3)Train by fitting the sparse matrix obtained from above to LatentDirichletAllocation from sklearn.decomposition. This will fetch N topics with M features as word. Sort features probability to get top K words.

4)Transform the model to get distribution of topic over documents. Sort them again and list top 3 topics per document.
Also fetch top 3 topics for each query by performing by rank measure of topics or by checking for feature occurrences in each document and sorting top 3 topic for max score 


__B) LDA-topics and clustering__     
Run LDA on the entire AP89 collection, with about T=200 topics. Obtain a representation of all documents in these topics.
Then run a clustering-partition algorithm on documents in this topic representation. partition means every document gets assigned to exactly one cluster, like with K-means. You are free to use any clustering library/package. Target K=25 clusters. List each cluster with its documents IDs. You should have an ES index set up so we can look up documents by ID.

How to evaluate: There are about 1831 relevant documents in total. Consider all the pairs of two relevant documents, that is (1831 choose 2).     
For each pair, count a 1 in the appropriate cell of the following confusion table:       

|                 | same cluster | different cluster |
|-----------------|--------------|-------------------|
| same query      |              |                   |
| different query |              |                   |
