import sys
import time
import numpy as np

from nltk.tokenize import word_tokenize
from collections import Counter

from datasource import Datasource
from pagerank import PageRank
from singleton import SingletonInstance


class SearchEngineGenerator(SingletonInstance):

    def __init__(self):
        self.db = Datasource()
        self.pagerank = PageRank()

    def __call__(self):
        start = time.time()
        print("Building tables...")

        self._init()
        self._generate_inverted_index()
        self._generate_pagerank()

        self._update_database()

        print("Total... {:02f}s".format(time.time() - start))
        print("Ready to search")

    def _init(self):
        self.inverted_index = {}
        self.doc_info = {}

    def _generate_inverted_index(self):
        '''
        Inverted Index 생성
        '''
        start = time.time()

        result = self.db.get_all_text()
        for doc_id, text in result:
            if doc_id not in self.doc_info.keys():
                self.doc_info[doc_id] = {}
            terms = word_tokenize(text.strip())
            self.doc_info[doc_id]['nd'] = len(terms)
            num_terms_in_doc = Counter(terms)

            for term, freq in num_terms_in_doc.items():
                if term not in self.inverted_index.keys():
                    self.inverted_index[term] = list()
                self.inverted_index[term].append((doc_id, freq))
        print("\tGenerate inverted index...{:02f}s".format(
            time.time() - start))

    def _generate_pagerank(self):
        '''
        Page Rank 생성
        '''
        start = time.time()

        ranks = self.pagerank()
        for doc_id, rank in ranks:
            if doc_id not in self.doc_info.keys():
                self.doc_info[doc_id] = {}
            self.doc_info[doc_id]['rank'] = rank

        print("\tGenerate page rank...{:02f}s".format(time.time() - start))

    def _update_database(self):
        '''
        Update Database
        '''
        start = time.time()
        print("\tUpdate database...", end='')
        self.db.bulk_update_inverted_index(self.inverted_index)
        self.db.bulk_update_doc_info(self.doc_info)
        print("{:02f}s".format(time.time() - start))
