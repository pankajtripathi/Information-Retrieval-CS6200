## Homework-2: Indexing, Term Positions     
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
