import json
import socket
import urllib.request

import pickle
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
from avl import AVLTree

__author__ = "Pankaj Tripathi"

"""
indexer.py
----------
Environment - Python 3.5.1
Description - Script to implement a web crawler.
"""

frontier = dict()
visited = set()
outlinks = dict()
parserDict = dict()


class Key:
    def __init__(self, link, count=1):
        self.link = link
        self.count = count
        self.time = time.time()

    def __eq__(self, other):
        return other.link == self.link

    def __lt__(self, other):
        return (self.count < other.count) or (self.count == other.count and self.time > other.time)

    def __gt__(self, other):
        return (self.count > other.count) or (self.count == other.count and self.time < other.time)

    def merge(self, other):
        self.count += 1


class TimeoutRobotFileParser(urllib.robotparser.RobotFileParser):
    def __init__(self, url='', timeout=5):
        super().__init__(url)
        self.timeout = timeout

    def read(self):
        """Reads the robots.txt URL and feeds it to the parser."""
        try:
            f = urllib.request.urlopen(self.url, timeout=self.timeout)
        except urllib.error.HTTPError as err:
            if err.code in (401, 403):
                self.disallow_all = True
            elif err.code >= 400:
                self.allow_all = True
        else:
            raw = f.read()
            self.parse(raw.decode("utf-8").splitlines())


def isAllowedByRobot(cannon_url):
    """
        Check the robots.txt for the domain of the canonicalized url. If robots.txt says the page is allowed to be
        crawled return true else false
    """
    scheme, netloc_host, path, params, query, fragment = urlparse(cannon_url)
    url = scheme + "://" + netloc_host
    robotUrl = url + "/robots.txt"
    try:
        if robotUrl not in parserDict:
            print("Robot URL: {0}".format(robotUrl))
            rp = TimeoutRobotFileParser(robotUrl)
            rp.read()
            parserDict[robotUrl] = rp
        r = parserDict[robotUrl]
        return r.can_fetch("*", cannon_url.encode('utf-8'))
    except Exception:
        return True


def urlCanonicalization(url, base_url=None):
    """
        1. Convert the scheme and host to lower case:
           HTTP://www.Example.com/SomeFile.html → http://www.example.com/SomeFile.html
        2. Remove port 80 from http URLs, and port 443 from HTTPS URLs:
           http://www.example.com:80 → http://www.example.com
        3. Make relative URLs absolute: if you crawl http://www.example.com/a/b.html and find the URL ../c.html,
           it should canonicalize to http://www.example.com/c.html.
        4. Remove the fragment, which begins with #:
           http://www.example.com/a.html#anything → http://www.example.com/a.html
        5. Remove duplicate slashes: http://www.example.com//a.html → http://www.example.com/a.html
    """
    url = url.lower()
    if not url.startswith("http"):
        url = urljoin(base_url, url)
    if url.startswith("http") and url.endswith(":80"):
        url = url[:-3]
    if url.startswith("https") and url.endswith(":443"):
        url = url[:-4]
    url = url.rsplit('#', 1)[0]
    return url


def dumpContentsToFile(raw_html, canonUrl, text, header, title, filename):
    """
    :param raw_html: Raw HTML contents fetched from the files.
    :param canonUrl: Canoncalized url used for crawling.
    :param text: Raw text obtained from the HTML file.
    :param header: HTTP header from the HTML response.
    :param title: Title from the HTML page.
    :param output: File on which the the contents are written.

    Write the parameters to a file.
    """
    output = open(filename, "w")
    data = '<DOC>' + '<DOCNO>' + canonUrl + '</DOCNO>' + '<TEXT>' + text + '</TEXT>' + '<CONTENT>' + \
           raw_html.decode('utf-8') + '</CONTENT>' + '<HEADER>' + header + '</HEADER>' + '<TITLE>' + title + \
           '</TITLE>' + '</DOC>'
    output.write(data)
    output.close()


def dumpOutlinks(outlinks):
    """
    :param outlinks: Out links for a url.
    :param output: File on which the the contents are written.
    Write the out links corresponding to a url to a file.
    """
    outlinkFile = open('./outLinks', 'w')
    json.dump(outlinks, outlinkFile)
    outlinkFile.close()


def parse_bs(url, response, outlinks):
    """
    :param url: canonicalized url, http response for the url, and outlinks ie the <a> tags in the page(url)
    :param response:
    :param outlinks:
    :return: raw_html fetched from the url, url, body of the html page obtained from the <p> tag, HTTP header of the url
             and the title of the html page
    """
    ol = []
    raw_html = response.read()
    soup = BeautifulSoup(raw_html, 'html.parser')
    header = ' '.join(response.info())
    title = soup.title.string
    body = [''.join(s.findAll(text=True)) for s in soup.findAll('p')]
    body = ' '.join(body)
    baseurl = urlparse(url)[0] + '://' + urlparse(url)[1] + urlparse(url)[2]

    for a in soup.find_all('a', href=True):
        l = urlCanonicalization(a['href'], baseurl)
        if ('javascript' not in l) and ('.pdf' not in l):
            frontier.insert(Key(l))
            ol.append(l)
    outlinks[url] = ol
    return raw_html, url, body, header, title


def startCrawl(frontier, UPPER_LIMIT=30000):
    """
    :param frontier: Data structure containing the links to be crawled along their inlink counts and time stamp.
    :param UPPER_LIMIT: Documents to be crawled.
    Crawl the urls in the frontier.
    """
    urls_crawled = 0

    while urls_crawled < UPPER_LIMIT:
        t0 = time.time()
        url = frontier.remove_biggest().link
        if url in visited or not isAllowedByRobot(url): continue
        visited.add(url)
        ta = time.time()
        tb = None
        tc = None
        td = None
        parsetime = 0
        storetime = 0
        try:
            print("Downloading {0}".format(url))
            ta = time.time()
            with urllib.request.urlopen(url, timeout=5) as response:
                print("Downloaded {0}".format(url))
                tb = time.time()
                (raw_html, url, body, header, title) = parse_bs(url, response, outlinks)
                tc = time.time()
                dumpContentsToFile(raw_html, url, body, header, title, './HW3_Dataset/contentFile-{0}'.format(urls_crawled))
                td = time.time()
                requesttime = tb - ta
                parsetime = tc - tb
                storetime = td - tc
                urls_crawled += 1
        except urllib.error.HTTPError:
            # print("ERROR: Could not connect to page (HTTPError)" + url)
            continue
        except socket.gaierror:
            # print("ERROR: Could not connect to page (gaierror)" + url)
            continue
        except urllib.error.URLError:
            # print("ERROR: Could not connect to page (URLError)" + url)
            continue
        except socket.timeout:
            # print("ERROR: Could not connect to page (socket.timeout)" + url)
            continue
        except Exception:
            # print("ERROR: Could not connect to page (generic)" + url)
            continue

        sleeptime = 1.0
        if ta is not None:
            sleeptime = 1.0 - (parsetime + storetime + requesttime)
            print("[REQ] {0:.2f} - [PAR] {1:.2f} - [STR] {2:.2f} - [SLP] {3:.2f}".format(requesttime,
                                                                                          parsetime,
                                                                                          storetime,
                                                                                          sleeptime))
        if sleeptime <= 1:
            time.sleep(1 - sleeptime)

        if (urls_crawled % 100) == 0:
            frontOutput = open("./frontier", 'wb')
            visitedOutput = open("./visited", 'wb')
            pickle.dump(visited, visitedOutput)
            pickle.dump(frontier, frontOutput)
            frontOutput.close()
            visitedOutput.close()
    dumpOutlinks(outlinks)


if __name__ == '__main__':
    seed_urls = ['http://en.wikipedia.org/wiki/Harvard_University',
                 'http://www.harvard.edu',
                 'http://colleges.usnews.rankingsandreviews.com/best-colleges/harvard-university-166027/overall-rankings',
                 'http://colleges.usnews.rankingsandreviews.com/best-colleges/harvard-university-2155',
                 'http://www.webometrics.info/en/world',
                 'http://www.timeshighereducation.co.uk/world-university-rankings/2014-15/world-ranking']
    frontier = AVLTree()
    for u in seed_urls:
        frontier.insert(Key(u, 100000000))
    startCrawl(frontier)
