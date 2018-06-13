# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 21:46:03 2016

@author: roberto
"""
import nltk
from nltk.corpus import stopwords
#from nltk.metrics import BigramAssocMeasures
#from nltk.util import tokenwrap
#from nltk.collocations import BigramAssocMeasures
#from nltk.collocations import BigramCollocationFinder
import nltk.collocations
import re
from collections import Counter
#import sys; reload(sys)
#
#sys.setdefaultencoding("utf-8")


"""
From this paper: https://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf

External dependencies: nltk, numpy, networkx

Based on https://gist.github.com/voidfiles/1646117
"""

# import io
import nltk
import itertools
# from operator import itemgetter
import networkx as nx
# import os
# from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer

# apply syntactic filters based on POS tags
def filter_for_tags(tagged, tags=['NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS']):#['NN', 'JJ', 'NNP']):
    return [item for item in tagged if item[1] in tags]


def normalize(tagged):
    return [(item[0].replace('.', ''), item[1]) for item in tagged]


def unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in itertools.ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


# def ld(s, t):
#     """
#     recursive version of lDistance below.
#     :param s:
#     :param t:
#     :return:
#     """
# 	if not s: return len(t)
# 	if not t: return len(s)
# 	if s[0] == t[0]: return ld(s[1:], t[1:])
# 	l1 = ld(s, t[1:])
# 	l2 = ld(s[1:], t)
# 	l3 = ld(s[1:], t[1:])
# 	return 1 + min(l1, l2, l3)


def lDistance(firstString, secondString):
    "Function to find the Levenshtein distance between two words/sentences - gotten from http://rosettacode.org/wiki/Levenshtein_distance#Python"
    if len(firstString) > len(secondString):
        firstString, secondString = secondString, firstString
    distances = range(len(firstString) + 1)
    for index2, char2 in enumerate(secondString):
        newDistances = [index2 + 1]
        for index1, char1 in enumerate(firstString):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1], distances[index1 + 1], newDistances[-1])))
        distances = newDistances
    return distances[-1]


def buildGraph(nodes):
    "nodes - list of hashables that represents the nodes of the graph"
    gr = nx.Graph()  # initialize an undirected graph
    gr.add_nodes_from(nodes)
    nodePairs = list(itertools.combinations(nodes, 2))

    # add edges to the graph (weighted by Levenshtein distance)
    for pair in nodePairs:
        firstString = pair[0]
        secondString = pair[1]
        # levDistance = ld(firstString, secondString)#recursive version, very slow.
        levDistance = lDistance(firstString, secondString)
        gr.add_edge(firstString, secondString, weight=levDistance)

    return gr


# def cleanup_text(text=""):
#     text_list = text.split()
#     regex = re.compile('[^a-zA-Z]')
#     stemmer = WordNetLemmatizer()
#     new_list = []
#     for word in text_list:
#         w = regex.sub(" ", word).strip()
#         for ww in w.split():
#             www = stemmer.lemmatize(ww.strip())#stem(w)
#             new_list.append(www)
#     return " ".join(new_list)


# def filterout_gibberish(text=""):
#     regex = re.compile('[^a-zA-Z]')
#     filtered_text = regex.sub("", text).strip()
#     filtered_text = filtered_text.split()
#     return " ".join([w if len(w)<20 else "" for w in filtered_text])


# def cleanup_text(text=""):
#     text_list = text.split()
#     stemmer = WordNetLemmatizer()
#     new_list = []
#     for word in text_list:
#         w = stemmer.lemmatize(word)
#         new_list.append(w)
#     return " ".join(new_list)

def is_word_gibberish(word="hi%%"):
    # can't be too long or too short:
    if len(word)>20 or len(word)<2: return True  # articles, unfortunately, die here too.

    if not word[0].isalpha(): return True # first element must be a letter

    regex1 = re.compile('[b-df-hj-np-tv-xz]{4}')  # 4 consonants in a row.
    if regex1.findall(word.lower()): return True

    regex2 = re.compile('[^0-9a-zA-Z]{2}')  # 2 non alphanumeric in a row
    if regex2.findall(word): return True

    # no filter caught something then consider it not gibberish:
    return False

def filterout_gibberish(text=""):
    # regex = re.compile('[^a-zA-Z]')
    word_list = []
    for word in text.split():
        if not is_word_gibberish(word):
            word_list.append(word.strip())
        # w = regex.sub("", word).strip()
        # if len(word)<20 and len(word)>3:
        #     if word[0].isalpha():
        #         word_list.append(word)
    return " ".join(word_list)

def cleanup_text(text=""):
    text_list = text.split()
    stemmer = WordNetLemmatizer()
    new_list = []
    for word in text_list:
        w = stemmer.lemmatize(word)
        new_list.append(w)
    return " ".join(new_list)


def extractKeyphrases(text):
    text = filterout_gibberish(text)
    text = cleanup_text(text)

    # tokenize the text using nltk
    wordTokens = nltk.word_tokenize(text)

    # assign POS tags to the words in the text
    tagged = nltk.pos_tag(wordTokens)
    textlist = [x[0] for x in tagged]

    tagged = filter_for_tags(tagged)
    tagged = normalize(tagged)

    unique_word_set = unique_everseen([x[0] for x in tagged])
    word_set_list = list(unique_word_set)

    # this will be used to determine adjacent words in order to construct keyphrases with two words

    graph = buildGraph(word_set_list)

    # pageRank - initial value of 1.0, error tolerance of 0,0001,
    calculated_page_rank = nx.pagerank(graph, weight='weight')

    # most important words in ascending order of importance
    keyphrases = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)

    # the number of keyphrases returned will be relative to the size of the text (a third of the number of vertices)
    aThird = len(word_set_list) / 3#min(10, len(word_set_list) / 3)
    keyphrases = keyphrases[0:aThird + 1]
    # if len(word_set_list) > 100:
    #     keyphrases = keyphrases[0:100]

    # take keyphrases with multiple words into consideration as done in the paper - if two words are adjacent in the text and are selected as keywords, join them
    # together
    modifiedKeyphrases = set([])
    dealtWith = set([])  # keeps track of individual keywords that have been joined to form a keyphrase
    i = 0
    j = 1
    while j < len(textlist):
        firstWord = textlist[i]
        secondWord = textlist[j]
        if firstWord in keyphrases and secondWord in keyphrases:
            keyphrase = firstWord + ' ' + secondWord
            modifiedKeyphrases.add(keyphrase)
            dealtWith.add(firstWord)
            dealtWith.add(secondWord)
        else:
            if firstWord in keyphrases and firstWord not in dealtWith:
                modifiedKeyphrases.add(firstWord)

            # if this is the last word in the text, and it is a keyword,
            # it definitely has no chance of being a keyphrase at this point
            if j == len(textlist) - 1 and secondWord in keyphrases and secondWord not in dealtWith:
                modifiedKeyphrases.add(secondWord)

        i = i + 1
        j = j + 1

    return modifiedKeyphrases


def extract_scored_keyphrases(text):
    text = filterout_gibberish(text)
    text = cleanup_text(text)

    # tokenize the text using nltk
    wordTokens = nltk.word_tokenize(text)

    # assign POS tags to the words in the text
    tagged = nltk.pos_tag(wordTokens)
    textlist = [x[0] for x in tagged]

    tagged = filter_for_tags(tagged)
    tagged = normalize(tagged)

    unique_word_set = unique_everseen([x[0] for x in tagged])
    word_set_list = list(unique_word_set)

    # this will be used to determine adjacent words in order to construct keyphrases with two words

    graph = buildGraph(word_set_list)

    # pageRank - initial value of 1.0, error tolerance of 0,0001,
    calculated_page_rank = nx.pagerank(graph, weight='weight')

    # most important words in ascending order of importance
    keyphrases = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)
    scores = sorted(calculated_page_rank.values(), reverse=True)

    # the number of keyphrases returned will be relative to the size of the text (a third of the number of vertices)
    aThird = len(word_set_list) / 3#min(10, len(word_set_list) / 3)
    keyphrases = keyphrases[0:aThird + 1]
    # if len(word_set_list) > 100:
    #     keyphrases = keyphrases[0:100]

    # take keyphrases with multiple words into consideration as done in the paper - if two words are adjacent in the text and are selected as keywords, join them
    # together
    modifiedKeyphrases = set([])
    dealtWith = set([])  # keeps track of individual keywords that have been joined to form a keyphrase
    i = 0
    j = 1
    while j < len(textlist):
        firstWord = textlist[i]
        secondWord = textlist[j]

        if firstWord in keyphrases and secondWord in keyphrases:
            keyphrase = firstWord + ' ' + secondWord
            modifiedKeyphrases.add(keyphrase)
            dealtWith.add(firstWord)
            dealtWith.add(secondWord)
        else:
            if firstWord in keyphrases and firstWord not in dealtWith:
                modifiedKeyphrases.add(firstWord)

            # if this is the last word in the text, and it is a keyword,
            # it definitely has no chance of being a keyphrase at this point
            if j == len(textlist) - 1 and secondWord in keyphrases and secondWord not in dealtWith:
                modifiedKeyphrases.add(secondWord)


        i = i + 1
        j = j + 1

    # get the scores, for compound keywords add the individual scores:
    keyphases_values = zip(keyphrases, scores)
    modifiedScores = []
    for keyphrase in list(modifiedKeyphrases):
        score = 0
        for subkey in keyphrase.split():
            for k, v in keyphases_values:
                if k == subkey:
                    score += v
                    break
        modifiedScores.append(score)

    return modifiedKeyphrases, modifiedScores


def extractSentences(text):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentenceTokens = sent_detector.tokenize(text.strip())
    graph = buildGraph(sentenceTokens)

    calculated_page_rank = nx.pagerank(graph, weight='weight')

    # most important sentences in ascending order of importance
    sentences = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)

    # return a 100 word summary
    summary = ' '.join(sentences)
    summaryWords = summary.split()
    summaryWords = summaryWords[0:101]
    summary = ' '.join(summaryWords)

    return summary


# def writeFiles(summary, keyphrases, fileName):
#     "outputs the keyphrases and summaries to appropriate files"
#     print "Generating output to " + 'keywords/' + fileName
#     keyphraseFile = io.open('keywords/' + fileName, 'w')
#     for keyphrase in keyphrases:
#         keyphraseFile.write(keyphrase + '\n')
#     keyphraseFile.close()
#
#     print "Generating output to " + 'summaries/' + fileName
#     summaryFile = io.open('summaries/' + fileName, 'w')
#     summaryFile.write(summary)
#     summaryFile.close()
#
#     print "-"
#
#
# # retrieve each of the articles
# articles = os.listdir("articles")
# for article in articles:
#     print 'Reading articles/' + article
#     articleFile = io.open('articles/' + article, 'r')
#     text = articleFile.read()
#     keyphrases = extractKeyphrases(text)
#     summary = extractSentences(text)
#     writeFiles(summary, keyphrases, article)

##### not related to TextRank:


def count_words(text=""):
    text_list = text.split()
    nonPunct = re.compile('.*[A-Za-z0-9].*')  # must contain a letter or digit
    filtered = [w for w in text_list if nonPunct.match(w)]
    return len(filtered)


def remove_stop_words(word_list=[]):
    stp = set(stopwords.words('english'))
    return [word for word in word_list if word not in stp]


def limit_number_of_words(text="", maxwords=1000):
    return " ".join(text.split()[:maxwords])


class ExtractKeywords():
    def __init__(self, text):
        self._text = text.encode('utf-8').strip()
        
    def run(self):
        self.tokenize()
        self.get_collocations()
        self.get_collocation_strings()
        return self._keywords_list, self._keywords_scores
        
    def tokenize(self):
        tokens = nltk.word_tokenize(self._text)
        self._nltk_text = nltk.Text(tokens)
    
    def get_collocations(self, window_size = 2,
                         num = 20):
        tokens = self._nltk_text
        
        ignored_words = stopwords.words('english')
        ignored_words += ["citation", "download", "editor", "authors", 
                          "book", "article"]
                          
        bigram_measures = nltk.collocations.BigramAssocMeasures()
        finder = nltk.collocations.BigramCollocationFinder.from_words(tokens)#, window_size)
        finder.apply_freq_filter(2)
        finder.apply_word_filter(lambda w: len(w) < 3 or w.lower() in ignored_words)
        
        self._scored_collocations =\
        finder.score_ngrams( bigram_measures.likelihood_ratio  )
        
#        from nltk.metrics import BigramAssocMeasures
#        text = self._nltk_text
#        ignored_words = stopwords.words('english')
#        finder = BigramCollocationFinder.from_words(text, window_size)
#        finder.apply_freq_filter(2)
#        finder.apply_word_filter(lambda w: len(w) < 3 or w.lower() in ignored_words)
#        bigram_measures = BigramAssocMeasures()
#        self._collocations =\
#        finder.nbest(bigram_measures.likelihood_ratio, num)
    
    def get_collocation_strings(self):
        scored_collocations = self._scored_collocations
        regex = re.compile('[^a-zA-Z09]')
        self._keywords_list = []
        self._keywords_scores = []
        for coll, score in scored_collocations:
            self._keywords_scores.append(score)
            kw = ""
            for w in coll:
                #replace non-alphanumeric characters with spaces.
                kw += " " + regex.sub(" ", w).strip()
            self._keywords_list.append( kw.strip() )
            
#        collocations = self._collocations
#        regex = re.compile('[^a-zA-Z09]')
#        self._keywords_list = []
#        for coll in collocations:
#            kw = ""
#            for w in coll:
#                kw += " " + regex.sub(" ", w).strip()
#            self._keywords_list.append( kw.strip() )
    
#        self._keywords_list =\
#        [regex.sub("", w1)+' '+regex.sub("", w2) for w1, w2 in collocations]
