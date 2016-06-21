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

##Homework-2: Indexing, Term Positions     
__Objective__     
Implement your own index to take the place of elasticsearch in the HW1 code, and index the document collection used for HW1. Your index should be able to handle large numbers of documents and terms without using excessive memory or disk I/O.

This involves writing two programs:

A tokenizer and indexer
An updated version of your HW1 ranker which uses your inverted index
You have some flexibility in the choice of algorithms and file formats for this assignment. You will be asked to explain and justify your approach, but any reasonable approach will work.    

__Step One: Tokenizing__         
The first step of indexing is tokenizing documents from the collection. That is, given a raw document you need to produce a sequence of tokens. For the purposes of this assignment, a token is a contiguous sequence of characters which matches a regular expression (of your choice) – that is, any number of letters and numbers, possibly separated by single periods in the middle. For instance, bob and 376 and 98.6 and 192.160.0.1 are all tokens. 123,456 and aunt's are not tokens (each of these examples is two tokens — why?). All alphabetic characters should be converted to lowercase during tokenization, so bob and Bob and BOB are all tokenized into bob.

You should assign a unique integer ID to each term and document in the collection. For instance, you might want to use a token’s hash code as its ID. However you decide to assign IDs, you will need to be able to convert tokens into term IDs and covert doc IDs into document names in order to run queries. This will likely require you to store the maps from term to term_id and from document to doc_id in your inverted index. One way to think about the tokenization process is as a conversion from a document to a sequence of (term_id, doc_id, position) tuples which need to be stored in your inverted index.

For instance, given a document with doc_id 20:

The car was in the car wash.
the tokenizer might produce the tuples:

(1, 20, 1), (2, 20, 2), (3, 20, 3), (4, 20, 4), (1, 20, 5), (2, 20, 6), (5, 20, 7)
with the term ID map:

1: the
2: car
3: was
4: in
5: wash           

__Step Two: Indexing__      
The next step is to record each document’s tokens in an inverted index. The inverted list for a term must contain the following information:

The DF and CF (aka TTF) of the term.
A list of IDs of the documents which contain the term, along with the TF of the term within that document and a list of positions within the document where the term occurs. (The first term in a document has position 1, the second term has position 2, etc.)
You should also store the following information.

The total number of distinct terms (the vocabulary size) and the total number of tokens (total CF) in the document collection.
The map between terms and their IDs, if required by your design.
The map between document names and their IDs, if required by your design.
Stemming and Stopping
Experiment with the affects of stemming and stop word removal on query performance. To do so, create four separate indexes:

An index where tokens are indexed as-is
An index where stop words are not indexed, and are removed from queries during query processing
An index where tokens are stemmed before indexing, and stemmed in queries during query processing
An index where tokens are stemmed and stop words are removed
You should use this list of stop words, obtained from NLTK.

You may use any standard stemming library. For instance, the python stemming package and the Java Weka package contain stemmer implementations.     

__Step Three: Searching__      
Update your solution to HW1 to use your index instead of elasticsearch. Compare your results to those you obtained in HW1. Are they different? If so, why? You dont have to run all 5 models; one VSM, one LM, and BM25 will suffice.     

__Proximity Search__      
Add one retrieval model, with scoring based on proximity on query terms in the document. You can use the ideas presented in slides, or skipgrams minimum span, or other ngram matching ideas.      
