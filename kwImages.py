# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 09:57:31 2016

@author: roberto
"""

import SearchUtils
import DatabaseFunctions
import time
# from threading import Thread


class Search:
    def __init__(self):
        self.iterations = self.get_iterations()

    def run(self):
        """
        Does a google images search for the keywords in the last iteration of the database,
        but only if it hasn't been done before (i.e., if there's no "thumbnails" entry
        in the last iteration) and if the keywords list is not empty.
        The results from the google search are saved in the "thumbnails" entry.
        @return: the google images results (i.e., a list of dictionaries consisting of
        the url of the thumbnail, and the website where the image comes from.
        """
        if self.is_search_needed():
            keywords = self.get_keywords()
            if keywords:
                tlast = self.get_time_of_last_search()
                t = time.time()
                if t - tlast < 10:
                    time.sleep(t - tlast)
                gi = SearchUtils.GoogleImagesSearch(keywords)
                results = gi.run()
                self.save_results(results)
                #gi.download_thumbnails(
                 #   results = results, 
                  #  savein = "ipc/images/",
                #)
                return results
        return []

    def get_time_of_last_search(self):
        for iteration in self.get_iterations():
            if "thumbnails" in iteration:
                return iteration["thumbnails"]["search time"]
        return 0

    def is_search_needed(self):
        last_iteration = self.get_iterations()[-1]
        return "thumbnails" not in last_iteration

    def get_iterations(self):
        if "iterations" in DatabaseFunctions.list_database_entries():
            return DatabaseFunctions.read_database("iterations")
        else:
            return [{}]

    def get_keywords(self):
        last_iteration = self.get_iterations()[-1]
        if "keywords" in last_iteration:
            kw_list = last_iteration["keywords"]
        else:
            kw_list = []
        return " ".join(kw_list)

    def save_results(self, results):
        new_item = {"search time": time.time(), "thumbnails info": results}
        iterations = self.get_iterations()
        iterations[-1]["thumbnails"] = new_item
        DatabaseFunctions.write_database("iterations", iterations)


def add_url_text_to_database(url):
    ws = SearchUtils.WebsiteScrapper(url)
    text = ws.get_meaningful_visible_text(min_words=50)
    if text:
        # DatabaseFunctions.semaphore_on()
        iterations = DatabaseFunctions.read_database("iterations")
        last_iteration = iterations[-1]
        if "added text" in last_iteration:
            last_iteration["added text"] += "\n" + text
        else:
            last_iteration["added text"] = text
        iterations[-1] = last_iteration
        DatabaseFunctions.write_database("iterations", iterations)

                
