__author__ = 'Pankaj Tripathi'

"""
dataset_cleaner.py
----------
Environment - Python 2.7.11
Description - Script to clean the documents in AP89 dataset by extracting only the document numbers, headers and text.
"""

import re
import os

if __name__ == '__main__':
    for dirpath, dirnames, filenames in os.walk("./AP_DATA/ap89_collection"):
        allfiles = [os.path.join(dirpath, filename).replace("\\","/") for filename in filenames if filename != "readme"]

    # Regular expressions to extract data from the corpus
    doc_regex = re.compile("<DOC>.*?</DOC>", re.DOTALL)
    docno_regex = re.compile("<DOCNO>.*?</DOCNO>")
    text_regex = re.compile("<TEXT>.*?</TEXT>", re.DOTALL)
    head_regex = re.compile("<HEAD>.*?</HEAD>", re.DOTALL)
    byline_regex = re.compile("<BYLINE>.*?</BYLINE>", re.DOTALL)

    for eachfile in allfiles:
        with open(eachfile, 'r') as f:
            data = f.read()  # Read the file when the file handle is opened
            result = re.findall(doc_regex, data)  # Match the <DOC> tags to separate out documents
            for document in result:
                doc_no = re.findall(docno_regex, document)[0].replace("<DOCNO>", "").replace("</DOCNO>", "").strip()

                heads = "\n".join(re.findall(head_regex, document)).replace("<HEAD>", "").replace("</HEAD>", "")\
                        .replace("\n", " ")

                bylines = " ".join(re.findall(byline_regex, document)).replace("<BYLINE>", "").replace("</BYLINE>", "")\
                          .replace("\n", " ")

                texts = "".join(re.findall(text_regex, document)).replace("<TEXT>", "").replace("</TEXT>", "")\
                        .replace("\n", " ")

                # Write the contents to a separate file
                path = "./ap89_cleaned/" + str(doc_no) + ".txt"
                with open(path, "w") as out:
                    out.write(heads + "\n" + bylines + "\n" + texts)
                print "Cleaned " + str(doc_no)