## Homework4: Web graph computation
__Objective__
  Compute link graph measures for each page crawled using the adjacency matrix. While you have to use the merged team index, this assignment is individual (can compare with teammates the results)      
__Page Rank - crawl__
Compute the PageRank of every page in your crawl (merged team index). You can use any of the methods described in class: random walks (slow), transition matrix, algebraic solution etc. List the top 500 pages by the PageRank score. You can take a look at this PageRank pseudocode (for basic iteration method) to get an idea       
__Page Rank - other graph__    
Get the graph linked by the in-links in file resources/wt2g_inlinks.txt.zip
Compute the PageRank of every page. List the top 500 pages by the PageRank score.       
__HITS- crawl__     
Compute Hubs and Authority score for the pages in the crawl (merged team index)         
A. Create a root set: Obtain the root set of about 1000 documents by ranking all pages using an IR function (e.g. BM25, ES Search). You will need to use your topic as your query       

B. Repeat few two or three time this expansion to get a base set of about 10,000 pages: 
For each page in the set, add all pages that the page points to
For each page in the set, obtain a set of pages that pointing to the page
if the size of the set is less than or equal to d, add all pages in the set to the root set
if the size of the set is greater than d, add an RANDOM (must be random) set of d pages from the set to the root set
Note: The constant d can be 200. The idea of it is trying to include more possibly strong hubs into the root set while constraining the size of the root size.        
C. Compute HITS. For each web page, initialize its authority and hub scores to 1. Update hub and authority scores for each page in the base set until convergence       

Authority Score Update: Set each web page's authority score in the root set to the sum of the hub score of each web page that points to it      
Hub Score Update: Set each web pages's hub score in the base set to the sum of the authority score of each web page that it is pointing to       
After every iteration, it is necessary to normalize the hub and authority scores. Please see the lecture note for detail.
Create one file for top 500 hub webpages, and one file for top 500 authority webpages. The format for both files should be:     
[webpageurl][tab][hub/authority score]\n   
