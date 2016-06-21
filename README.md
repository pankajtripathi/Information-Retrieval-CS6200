# Information-Retrieval

##Homework-1 : Retrieval Models
__Objective__      
Implement and compare various retrieval systems using vector space models and language models. Explain how and why their performance differs.

This assignment will also introduce you to elasticsearch: one of the many available commercial-grade indexes. These instructions will generally not spell out how to accomplish various tasks in elasticsearch; instead, you are encouraged to try to figure it out by reading the online documentation. If you are having trouble, feel free to ask for help on Piazza or in office hours.

This assignment involves writing two programs:

A program to parse the corpus and index it with elasticsearch
A query processor, which runs queries from an input file using a selected retrieval model     

__Document Indexing__    
Create an index of the downloaded corpus. You will need to write a program to parse the documents and send them to your elasticsearch instance.

The corpus files are in a standard format used by TREC. Each file contains multiple documents. The format is similar to XML, but standard XML and HTML parsers will not work correctly. Instead, read the file one line at a time with the following rules:

Each document begins with a line containing <DOC> and ends with a line containing </DOC>.
The first several lines of a document’s record contain various metadata. You should read the <DOCNO> field and use it as the ID of the document.
The document contents are between lines containing <TEXT> and </TEXT>.
All other file contents can be ignored.
Make sure to index term positions: you will need them later. You are also free to add any other fields to your index for later use. This might be the easiest way to get particular values used in the scoring functions. However, if a value is provided by elasticsearch then we encourage you to retrieve it using the elasticsearch API rather than calculating and storing it yourself.     

__Query execution__     
Write a program to run the queries in the file query_desc.51-100.short.txt, included in the data .zip file. You should run all queries (omitting the leading number) using each of the retrieval models listed below, and output the top 100 results for each query to an output file. If a particular query has fewer than 100 documents with a nonzero matching score, then just list whichever documents have nonzero scores.

You should write precisely one output file per retrieval model. Each line of an output file should specify one retrieved document, in the following format:

query-number Q0 docno rank score> Exp
Where:

is the number preceding the query in the query list
is the document number, from the <DOCNO> field (which we asked you to index)
is the document rank: an integer from 1-1000
is the retrieval model’s matching score for the document
Q0 and Exp are entered literally
Your program will run queries against elasticsearch. Instead of using their built in query engine, we will be retrieving information such as TF and DF scores from elasticsearch and implementing our own document ranking. It will be helpful if you write a method which takes a term as a parameter and retrieves the postings for that term from elasticsearch. You can then easily reuse this method to implement the retrieval models.

Implement the following retrieval models, using TF and DF scores from your elasticsearch index, as needed.     

__Okapi TF__    
__TF-IDF__       
__Okapi BM25__     
__Unigram LM with Laplace smoothing__      
__Unigram LM with Jelinek-Mercer smoothing__     
