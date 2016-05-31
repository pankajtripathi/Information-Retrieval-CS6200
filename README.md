# Information-Retrieval

##Homework-1
__Objective__
Implement and compare various retrieval systems using vector space models and language models. Explain how and why their performance differs.

This assignment will also introduce you to elasticsearch: one of the many available commercial-grade indexes. These instructions will generally not spell out how to accomplish various tasks in elasticsearch; instead, you are encouraged to try to figure it out by reading the online documentation. If you are having trouble, feel free to ask for help on Piazza or in office hours.

This assignment involves writing two programs:

A program to parse the corpus and index it with elasticsearch
A query processor, which runs queries from an input file using a selected retrieval model     

__First Steps__     
Download and install elasticsearch, and the marvel/sense plugin
Download IR_data/AP89_DATA.zip from the Dropbox Data link. Contact the TAs if you need the password.      

__Document Indexing__    
Create an index of the downloaded corpus. The documents are found within the ap89_collection folder in the data .zip file. You will need to write a program to parse the documents and send them to your elasticsearch instance.

The corpus files are in a standard format used by TREC. Each file contains multiple documents. The format is similar to XML, but standard XML and HTML parsers will not work correctly. Instead, read the file one line at a time with the following rules:

Each document begins with a line containing <DOC> and ends with a line containing </DOC>.
The first several lines of a document’s record contain various metadata. You should read the <DOCNO> field and use it as the ID of the document.
The document contents are between lines containing <TEXT> and </TEXT>.
All other file contents can be ignored.
Make sure to index term positions: you will need them later. You are also free to add any other fields to your index for later use. This might be the easiest way to get particular values used in the scoring functions. However, if a value is provided by elasticsearch then we encourage you to retrieve it using the elasticsearch API rather than calculating and storing it yourself.     

__Query execution__     
Write a program to run the queries in the file query_desc.51-100.short.txt, included in the data .zip file. You should run all queries (omitting the leading number) using each of the retrieval models listed below, and output the top 100 results for each query to an output file. If a particular query has fewer than 100 documents with a nonzero matching score, then just list whichever documents have nonzero scores.

You should write precisely one output file per retrieval model. Each line of an output file should specify one retrieved document, in the following format:

<query-number> Q0 <docno> <rank> <score> Exp
Where:

is the number preceding the query in the query list
is the document number, from the <DOCNO> field (which we asked you to index)
is the document rank: an integer from 1-1000
is the retrieval model’s matching score for the document
Q0 and Exp are entered literally
Your program will run queries against elasticsearch. Instead of using their built in query engine, we will be retrieving information such as TF and DF scores from elasticsearch and implementing our own document ranking. It will be helpful if you write a method which takes a term as a parameter and retrieves the postings for that term from elasticsearch. You can then easily reuse this method to implement the retrieval models.

Implement the following retrieval models, using TF and DF scores from your elasticsearch index, as needed.     

__Okapi TF__    
This is a vector space model using a slightly modified version of TF to score documents. The Okapi TF score for term $w$ in document $d$ is as follows.

$$ okapi\_tf(w, d) = \frac{tf_{w,d}}{tf_{w,d} + 0.5 + 1.5 \cdot (len(d) / avg(len(d)))} $$
Where:

$tf_{w,d}$ is the term frequency of term $w$ in document $d$
$len(d)$ is the length of document $d$
$avg(len(d))$ is the average document length for the entire corpus
The matching score for document $d$ and query $q$ is as follows.

$$ tf(d, q) = \sum_{w \in q} okapi\_tf(w, d) $$    

__TF-IDF__
This is the second vector space model. The scoring function is as follows.

$$ tfidf(d, q) = \sum_{w \in q} okapi\_tf(w, d) \cdot \log \frac{D}{df_w} $$
Where:

$D$ is the total number of documents in the corpus
$df_w$ is the number of documents which contain term $w$     

__Okapi BM25__     
BM25 is a language model based on a binary independence model. Its matching score is as follows.

$$ bm25(d, q) = \sum_{w \in q} \left[ \log\left( \frac{D + 0.5}{df_w + 0.5} \right) \cdot \frac{tf_{w,d} + k_1 \cdot tf_{w,d}}{tf_{w,d} + k_1 \left((1-b) + b \cdot \frac{len(d)}{avg(len(d))}\right)} \cdot \frac{tf_{w,q} + k_2 \cdot tf_{w,q}}{tf_{w,q} + k_2} \right] $$
Where:

$tf_{w,q}$ is the term frequency of term $w$ in query $q$
$k_1$, $k_2$, and $b$ are constants. You can use the values from the slides, or try your own.     

__Unigram LM with Laplace smoothing__    
This is a language model with Laplace (“add-one”) smoothing. We will use maximum likelihood estimates of the query based on a multinomial model “trained” on the document. The matching score is as follows.

$$ lm\_laplace(d, q) = \sum_{w \in q} \log p\_laplace(w|d) \\ p\_laplace(w|d) = \frac{tf_{w,d} + 1}{len(d) + V} $$
Where:

$V$ is the vocabulary size – the total number of unique terms in the collection.     

__Unigram LM with Jelinek-Mercer smoothing__     
This is a similar language model, except that here we smooth a foreground document language model with a background model from the entire corpus.

$$ lm\_jm(d, q) = \sum_{w \in q} \log p\_jm(w|d) \\ p\_jm(w|d) = \lambda \frac{tf_{w,d}}{len(d)} + (1 - \lambda) \frac{\sum_{d'} tf_{w,d'}}{\sum_{d'} len(d')} $$
Where:

$\lambda \in (0, 1)$ is a smoothing parameter which specifies the mixture of the foreground and background distributions.
Think carefully about how to efficiently obtain the background model here. If you wish, you can instead estimate the corpus probability using      $\frac{cf_w}{V}$.

__Evaluation__    
Download trec_eval and use it to evalute your results for each retrieval model.

To perform an evaluation, run:

trec_eval [-q] qrel_file results_file
The -q option shows a summary average evaluation across all queries, followed by individual evaluation results for each query; without the -q option, you will see only the summary average. The trec_eval program provides a wealth of statistics about how well the uploaded file did for those queries, including average precision, precision at various recall cut-offs, and so on.

You should evaluate using the QREL file named qrels.adhoc.51-100.AP89.txt, included in the data .zip file.

Create a document showing the following metrics:

The uninterpolated mean average precision numbers for all five retrieval models.
Precision at 10 and precision at 30 documents for all five retrieval models.
Be prepared to answer questions during your demo as to how model performance compares, why the best model outperformed the others, and so on.
