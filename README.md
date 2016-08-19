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

##Homework3: Crawling, Vertical Search
__Objective__     
In this assignment, you will work with a team to create a vertical search engine using elasticsearch. Please read these instructions carefully: although you are working with teammates, you will be graded individually for most of the assignment.

You will write a web crawler, and crawl Internet documents to construct a document collection focused on a particular topic. Your crawler must conform strictly to a particular politeness policy. Once the documents are crawled, you will pool them together.

Form a team of three students with your classmates. Your team will be assigned a single query with few associated seed URLs. You will each crawl web pages starting from a different seed URL. When you have each collected your individual documents, you will pool them together, index them and implement search.

Although you are working in a team, you are each responsible for developing your own crawlers individually, and for crawling from your own seeds for your team’s assigned topic.

__Obtaining a topic__      
Form a team of three students with your classmates. If you have trouble finding teammates, please contact the TAs right away to be placed in a team.

Once your team has been formed, have each team member create a file in Dropbox named teamXYabcd.txt (using your first initial and the last name). This file should contain the names team members. The TAs will update this file with a topic and three seed URLs.

Each individual on your team will crawl using three seed URLs: one of the URLs provided to the team, and at least two additional seed URLs you devise on your own. In total, the members of your team will crawl from at least nine seed URLs.

__Crawling Documents__      
Each individual is responsible for writing their own crawler, and crawling from their own seed URLs.

Set up Elastic Search with your teammates to have the same cluster name and the same index name.

Your crawler will manage a frontier of URLs to be crawled. The frontier will initially contain just your seed URLs. URLs will be added to the frontier as you crawl, by finding the links on the web pages you crawl.

1. You should crawl at least 20,000 documents individually, including your seed URLs. This will take several hours, so think carefully about how to adequately test your program without running it to completion in each debugging cycle.      
2. You should choose the next URL to crawl from your frontier using a best-first strategy. See Frontier Management, below.     
3. Your crawler must strictly conform to the politeness policy detailed in the section below. You will be consuming resources owned by the web sites you crawl, and many of them are actively looking for misbehaving crawlers to permanently block. Please be considerate of the resources you consume.       
4. You should only crawl HTML documents. It is up to you to devise a way to ensure this. However, do not reject documents simply because their URLs don’t end in .html or .htm.     
5. You should find all outgoing links on the pages you crawl, canonicalize them, and add them to your frontier if they are new. See the Document Processing and URL Canonicalization sections below for a discussion.      
6. For each page you crawl, you should store the following filed with ElasticSearch : an id, the URL, the HTTP headers, the page contents cleaned (with term positions), the raw html, and a list of all in-links (known) and out-links for the page.      
Once your crawl is done, you should get together with your teammates and figure out how to merge the indexes. With proper ids, the ElasticSearch will do the merging itself, you still have to manage the link graph.

__Politeness Policy__      
Your crawler must strictly observe this politeness policy at all times, including during development and testing. Violating these policies can harm to the web sites you crawl, and cause the web site administrators to block the IP address from which you are crawling.

Make no more than one HTTP request per second from any given domain. You may crawl multiple pages from different domains at the same time, but be prepared to convince the TAs that your crawler obeys this rule. The simplest approach is to make one request at a time and have your program sleep between requests. The one exception to this rule is that if you make a HEAD request for a URL, you may then make a GET request for the same URL without waiting.
Before you crawl the first page from a given domain, fetch its robots.txt file and make sure your crawler strictly obeys the file. You should use a third party library to parse the file and tell you which URLs are OK to crawl.

__Frontier Management__      
The frontier is the data structure you use to store pages you need to crawl. For each page, the frontier should store the canonicalized page URL and the in-link count to the page from other pages you have already crawled. When selecting the next page to crawl, you should choose the next page in the following order:

Seed URLs should always be crawled first.
Must use BFS as the baseline graph traversal (variations and optimizations allowed)
Prefer pages with higher in-link counts.
If multiple pages have maximal in-link counts, choose the option which has been in the queue the longest.
If the next page in the frontier is at a domain you have recently crawled a page from and you do not wish to wait, then you should crawl the next page from a different domain instead.

__URL Canonicalization__         
Many URLs can refer to the same web resource. In order to ensure that you crawl 20,000 distinct web sites, you should apply the following canonicalization rules to all URLs you encounter.

Convert the scheme and host to lower case: HTTP://www.Example.com/SomeFile.html → http://www.example.com/SomeFile.html
Remove port 80 from http URLs, and port 443 from HTTPS URLs: http://www.example.com:80 → http://www.example.com
Make relative URLs absolute: if you crawl http://www.example.com/a/b.html and find the URL ../c.html, it should canonicalize to http://www.example.com/c.html.
Remove the fragment, which begins with #: http://www.example.com/a.html#anything → http://www.example.com/a.html
Remove duplicate slashes: http://www.example.com//a.html → http://www.example.com/a.html
You may add additional canonicalization rules to improve performance, if you wish to do so.

__Document Processing__         
Once you have downloaded a web page, you will need to parse it to update the frontier and save its contents. You should parse it using a third party library. We suggest jsoup for Java, and Beautiful Soup for Python. 

__Link Graph__
You should also write a link graph reporting all out-links from each URL you crawl, all the inlinks you have encountered (obviously there will be inlinks on the web that you dont discover). This will be used in a future assignment to calculate PageRank for your collection.

option 1 : We prefer that you store the canonical links as two fields “inlinks” and “outlinks” in ElasticSearch, for each document. You will have to manage these fields appropriately, such that when you are done, your team has correct links for all document crawled.

option 2: maintain a separate links file (you can do this even if you also do option1). Each line of this file contains a tab-separated list of canonical URLs. The first URL is a document you crawled, and the remaining URLs are out-links from the document. When all team members are finished with their crawls, you should merge your link graphs. Only submit one file, containing this merged graph. During the merge process, reduce any URL which was not crawled to just a domain.      

__Merging team indexes__          

Ideally we would like to have the crawling process send any stored data directly to the team-index, while merging. But this is too much of a headache for students to keep their ES servers connected while crawling; so we allow for individual crawls, then merged in ES. If you use individual crawls to be merged at the end, you have to simulate a realistic environment: merge indexes (or the crawled data) into one ES index. Merging should happen as independent agents : everyone updates the index independently while ES servers are connected. Meaning not in a Master-Slave or Server-Client manner. This is team work.

 Once all team members are finished with their crawls, you will combine the documents to create a vertical search engine. It is required that team computer/ES are connected are the time of merging, and that each team member runs merging code against the merged index in an independent manner (no master-slave design)        

__Vertical Search__     

Add all 90,000 documents to an elasticsearch index, using the canonical URL as the document ID for de-duplication, and create a simple HTML page which runs queries against your elasticsearch index. You may either write your own interface, or use an existing tool such as Calaca or FacetView. Or modify this one written by one of our grad students. Your search engine should allow users to enter text queries, and display elasticsearch results to those queries from your index. The result list should contain at minimum the URL to the page you crawled.
Make sure you run several queries on your group’s topic, and you think about the result quality. During your demo, you will be asked to explain how your seeds and crawls affected the search results.
