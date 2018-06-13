 # -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 21:10:42 2014

@author: Roberto
"""
import time
#from threading import Thread
#from mechanize import Browser
#import mechanize
#import cookielib
# change the following to change the search specifics:
import SearchUtils as utils #need to put the functions in a new 
#file called SearchUtils.
import DatabaseFunctions as dbs
import TextProcessing as txtproc

class kwSearch():
    def __init__(self, keywords= ["ultrafast", "lasers"],
                 debug_mode = True):
        """
        run a general keyword search in which the keywords are
        iteratively improved. The target for the keyword search
        is general (can be a book, the web, etc.) and specified
        by the functions imported as "utils".
        """
        self._debug_mode = debug_mode
        self._max_keywords = 10

        self._compound_text = ""

        # self.initialize(keywords)
        dbs.reset_search_database()  # dbs.write_database("stop", False)
        dbs.unstop()
        dbs.running_off()
        dbs.pause_off()
        dbs.write_database("iterations", [])

        # self._tsearch = 0.

        if keywords:
         self._initial_keywords = keywords
         self._persistent_keywords = keywords
         self._firsttier_keywords = []
         self._secondtier_keywords = []
         self._removed_keywords = []
         self._stop_search = False
        else:
         dbs.stop()
         self._stop_search = True

    def run(self):
        # self._stop_search = False
        keywords = persistent_kwds = self._initial_keywords
        keywords_scores = (keywords, [0]*len(keywords))
        # keywords = ["-".join(self._initial_keywords)]
        # persistent_kwds = self._initial_keywords
        # keywords_scores = (keywords, [0])

        # search_terms = " ".join(keywords)
        first_tier_kwds, second_tier_kwds = [], []
        removed_kwds, banned_kwds = [], []
        keywords_scores = ([],[])
        tsearch = 0
        stop = self._stop_search
        while not stop:
            self.check_pause()
            self.initialize_iteration(keywords, persistent_kwds,
                                      first_tier_kwds, second_tier_kwds,
                                      removed_kwds, banned_kwds)

            tsearch, results, new_urls, keywords, new_keywords_scores, kwd_groups =\
                self.get_results_from_keywords(keywords, tsearch, keywords_scores,
                                               maxtextlength=30000,
                                               max_html_memsize=1e6,
                                               new_keywords=2,
                                               maxwords=3000,
                                               minwords=15,
                                               len_power=0.5,
                                               attempts=5)

            keywords_scores =\
                self.merge_keywords_scores_tuples([keywords_scores,
                                                   new_keywords_scores])

            persistent_kwds, first_tier_kwds, second_tier_kwds, \
            removed_kwds, banned_kwds = kwd_groups

            has_converged = \
                self.assess_search_convergence(new_urls)

            self.save_iteration_data(results, tsearch)
            self.wait()
            stop = self.check_stop(has_converged, keywords_scores)
    
    # def run(self):
    #     # self._stop_search = False
    #     keywords = self._initial_keywords
    #     tsearch = 0
    #     stop = self._stop_search
    #     while not stop:#self._stop_search:
    #         self.initialize_iteration(keywords)
    #         search_results, tsearch =\
    #             self.search(keywords, tsearch)
    #         results, new_urls =\
    #             self.get_text_from_links(search_results)
    #         compound_text =\
    #             self.extract_compound_text(results)
    #         keywords =\
    #             self.determine_next_keywords(compound_text[:1000])
    #         has_converged =\
    #             self.assess_search_convergence(new_urls, compound_text)
    #         self.save_iteration_data(results, compound_text, tsearch)
    #         self.check_pause()
    #         self.wait()
    #         stop = self.check_stop(has_converged)

    ###### second-tier methods:
#     def initialize(self, keywords = []):#""):
#         """
#         - Check if the database file exists, if so empty it, if not
#         create it.
#         - Then create an entry/value: "stop": False
#         For later: might want to save the contents of any previous
#         database file into one file that has all the searches history.
#         """
# #        self.initialize_database()
#         dbs.reset_search_database()
#         # dbs.write_database("stop", False)
#         dbs.unstop()
#         dbs.running_off()
#         dbs.pause_off()
#         # dbs.write_database("pause", False)
#         # dbs.write_database("running", False)
#         dbs.write_database("iterations", [])
#
#         self._tsearch = 0.
#
#         if keywords:
#             self._next_keywords = keywords
#             self._persistent_keywords = keywords
#             self._firsttier_keywords = []
#             self._secondtier_keywords = []
#             self._removed_keywords = []
#         else:
#             dbs.stop()
#             self._stop_search = True
        
    # def initialize_iteration(self, keywords):#change to input-output
    #     """
    #     Setup the new iteration using self._next_keywords (which should be
    #     defined during program initialization or by the end of the
    #     previus iteration). Also append a new item to the "iterations"
    #     entry in the database.
    #     """
    #     dbs.running_on()#needed, e.g., a gui could
    #     #want to assume this isn't running yet.
    #     iterations = dbs.read_database("iterations")
    #     iteration = {"iteration number": len(iterations)}
    #     iteration["keywords"] = keywords#self._keywords = self._next_keywords#.strip()
    #     iteration["persistent keywords"] = []#self._persistent_keywords
    #     iteration["first-tier keywords"] = self._firsttier_keywords
    #     iteration["second-tier keywords"] = self._secondtier_keywords
    #     iteration["removed keywords"] = self._removed_keywords
    #     iterations.append(iteration)
    #     dbs.write_database("iterations", iterations)

    def initialize_iteration(self, keywords, persistent_kwds,
                             first_tier_kwds, second_tier_kwds,
                             removed_kwds, banned_kwds):
        """
        Setup the new iteration using self._next_keywords (which should be
        defined during program initialization or by the end of the
        previus iteration). Also append a new item to the "iterations"
        entry in the database.
        """
        dbs.running_on()  # needed, e.g., a gui could
        # want to assume this isn't running yet.
        iterations = dbs.read_database("iterations")
        iteration = {"iteration number": len(iterations)}
        iteration["keywords"] = keywords  # self._keywords = self._next_keywords#.strip()
        iteration["persistent keywords"] = persistent_kwds
        # iteration["inserted keywords"] = inserted_kwds
        iteration["first-tier keywords"] = first_tier_kwds
        iteration["second-tier keywords"] = second_tier_kwds
        iteration["removed keywords"] = removed_kwds
        iteration["banned keywords"] = banned_kwds
        iterations.append(iteration)
        dbs.write_database("iterations", iterations)

    # def search_more(self, keywords, tsearch, keywords_scores=([],[]),
    #                 persistent_kwds=[], removed_kwds=[], banned_kwds=[],
    #                 new_keywords=2):
    #     # TODO: make it really detect failed google search
    #     search_results, tsearch = self.search(keywords, tsearch)
    #     if len(search_results)>5:
    #         return search_results, tsearch
    #     else:
    #         k, s = keywords_scores
    #         while k and not dbs.check_stop():
    #             k, s = k[new_keywords:], s[new_keywords:]
    #             new_ks = k, s
    #             kwds, __ = self.group_keywords(new_ks, persistent_kwds,
    #                                            removed_kwds, banned_kwds,
    #                                            new_keywords)
    #             search_results, tsearch = self.search(kwds, tsearch)
    #             if len(search_results)>5:
    #                 return search_results, tsearch
    #
    #     return search_results, tsearch

    def get_results_from_keywords(self, keywords=[],
                                  tsearch=0,
                                  keywords_scores = (),
                                  maxtextlength=30000,
                                  max_html_memsize=1e6,
                                  new_keywords=2,
                                  maxwords=3000,
                                  minwords=15,
                                  len_power=0.5,
                                  attempts = 5):
        locally_banned_kwds = []
        # try attempts times to find results with new urls:
        for k in range(attempts):
            search_results, tsearch = \
                self.search(keywords, tsearch)

            results, new_urls = \
                self.get_text_from_links(search_results, maxtextlength,
                                         max_html_memsize)

            keywords, keywords_scores, kwd_groups = \
                self.extract_keywords(results, keywords_scores,
                                      new_keywords, maxwords,
                                      minwords, len_power)
            # if no new urls try with lower scored keywords:
            if new_urls or dbs.check_stop():
                break
            else:
                (persistent_kwds, first_tier_kwds, second_tier_kwds,
                 removed_kwds, banned_kwds) = kwd_groups
                keywords, locally_banned_kwds =\
                    self.rotate_keywords(persistent_kwds, first_tier_kwds,
                                         second_tier_kwds, removed_kwds,
                                         locally_banned_kwds)

        return tsearch, results, new_urls, keywords, keywords_scores, kwd_groups
            # persistent_kwds, first_tier_kwds, second_tier_kwds, \
            # removed_kwds, banned_kwds = kwd_groups
            #
            # # rotate the top keywords if no new urls:
            # if new_urls:
            #     break
            # else:
            #     k, s = keywords_scores
            #     if len(k)>new_keywords:
            #         keywords_scores = k[new_keywords:], s[new_keywords:]
            #         keywords, kwd_groups =\
            #             self.group_keywords(keywords_scores, persistent_kwds,
            #                                 removed_kwds, banned_kwds,
            #                                 new_keywords)
            #         # write to database so that gui could be updated:
            #         persistent_kwds, first_tier_kwds, second_tier_kwds, \
            #         removed_kwds, banned_kwds = kwd_groups;print first_tier_kwds
            #         dbs.write_iteration_list("keywords", keywords)
            #         dbs.write_iteration_list("first-tier keywords",
            #                                  first_tier_kwds)
            #         dbs.write_iteration_list("second-tier keywords",
            #                                  second_tier_kwds)
        #
        # return tsearch, results, new_urls, keywords, keywords_scores, kwd_groups
        
    def search(self, keywords, tsearch):
        # make sure that at least 15s have passed since the last search.
        t = time.time()
        if t - tsearch<15:
            time.sleep(15 - (t - tsearch))
        search_terms = " ".join(keywords)
        search_results = utils.GoogleSearch(search_terms).run()
        return search_results, time.time()
    
    def get_text_from_links(self, search_results,
                            maxtextlength=3000,
                            max_html_memsize=1e6):
        """
        Get the abstract corresponding to each result in 
        _current_search_results. Check first if any result's link has already 
        been visited before and if so replace with the previously found data. 
        If it's an unvisited link, go through this and past iterations to 
        see whether/when the same domain has been visited before. If it's to
        soon to visit the domain again, go to the next result. Continue until 
        all the results are processed. Implemented as a state machine.
        """
        new_urls = []
        # self._new_urls = []
        results = search_results[:]  #self._current_search_results#a reference not a copy
        stop = False
        next_action = "initialize"
        while not stop and not dbs.check_stop():
            if next_action == "initialize":
                current_index = -1
                Nresults = len(results)
                iterations = dbs.read_database("iterations")
                #                Niters = len(iterations)
                next_action = "next result"
                
            elif next_action == "next result":
                current_index += 1
                if current_index < Nresults:
                    result = results[current_index]
                    url = result["link"]
                    next_action = "already processed?"
                else:
                    next_action = "stop?"
                
            elif next_action == "already processed?":
                next_action = "processed in previous iteration?"
                if "processed" in result:
                    if result["processed"]:
                        next_action = "last result?"                
                
            elif next_action == "processed in previous iteration?":
                found = False
                for iteration in iterations:
                    if not "items" in iteration:
                        iteration["items"] = []
                    for old_result in iteration["items"]:
                        if url.strip().lower() ==\
                                old_result["link"].strip().lower():# and old_result['abstract']:
                            result = old_result
                            result["processed"] = True
                            found = True
                            break
                    if found:
                        break
                if found:
                    next_action = "save changes"
                else:
                    next_action = "has domain been visited recently?"
                    
            elif next_action == "has domain been visited recently?":
                next_action = "visit url"
                domain = utils.get_url_domain(url).lower().strip()
                #check first on the current results:
                for r in results:
                    r_domain = utils.get_url_domain(r["link"]).lower().strip()
                    if domain == r_domain:
                        if "time of visit" in r:
                            if time.time() - r["time of visit"] < 15:
                                result["processed"] = False
                                next_action = "save changes"
                                break
                #next check on previous iterations starting from the last one:
                if next_action == "visit url":
                    t_it = time.time()
                    for iteration in iterations[::-1]:
                        if time.time() - t_it > 15:
                            break
                        r = iteration["items"]
                        if self.domain_visited_recently_in_search_results(url,r):
                            result["processed"] = False
                            next_action = "save changes"
                            break
                        if "search time" in iteration:
                            t_it = iteration["search time"]
                
            elif next_action == "visit url":
                # result["abstract"] = utils.PaperWebsiteScrapper(url).run()
                if not url.endswith(".pdf") and ("/pdf/" not in url):
                    ws = utils.WebsiteScrapper(url, maxmemsize=max_html_memsize)
                    r_abstract = ws.get_meaningful_visible_text()[:maxtextlength]
                    result["abstract"] = txtproc.filterout_gibberish(r_abstract)
                result["time of visit"] = time.time()
                result["processed"] = True
                next_action = "save changes"
                new_urls.append(url);print url
                # self._new_urls.append(url);print url
                
            elif next_action == "save changes":
                results[current_index] = result
                next_action = "last result?"
                
            elif next_action == "last result?":
                if current_index >= Nresults -1:
                    time.sleep(1)
                    next_action = "stop?"
                else:
                    next_action = "next result"
                                       
            elif next_action == "stop?":
                #stop unless there're still unprocessed results:
                unprocessed_results = False
                for indx in range(Nresults):
                    r = results[indx]
                    if "processed" in r:
                        if not r["processed"]:
                            unprocessed_results = True
                            break
                    else:
                        unprocessed_results = True                      
                        break
                    
                if unprocessed_results:
                    current_index = indx - 1
                    next_action = "next result"
                else:
                    stop = True
                
            else:
                print "action {} in get_text_from_links() was not understood".format(next_action)
                stop = True
            # print "results = {}".format(results)
            # self._current_search_results = results#just in case.
        return results, new_urls

    def extract_keywords(self, results, keywords_scores=([],[]),
                         new_keywords = 2, maxwords=500,
                         minwords=10, len_power=1.):
        """
        Go through the text available in each of the items in results and
        extract scored keywords for each. Then merge and sort the results.
        Once that's done check the user input in the form of removed,
        banned, and inserted keywords and modify the keywords set
        accordingly. Finally, merge the new set of scored keywords with
        the cummulated set.
        :param results: list of dictionaries with item information.
        :return: keywords, list.
        """
        # there won't be a need to save the compound text to the database
        # since all is needed from each iteraction is the set of scored
        #keywords.
        # loop over the results. get the text for each and run text-rank on
        # it, merge the extracted (keywords, scores) with the cumulated ones.

        # wait for any ongoing user interaction to end:
        dbs.wait_for_pause()

        added_text_list = self.get_added_text_list()
        keywords_scores = \
            self.get_new_keywords(results, added_text_list,
                                  maxwords, minwords, len_power)
        # k_new, s_new =\
        #     self.get_new_keywords(results, added_text_list,
        #                           maxwords, minwords, len_power)
        #
        # keywords_scores =\
        #     self.merge_keywords_scores_tuples([keywords_scores,
        #                                        (k_new, s_new)])

        keywords_scores, removed_kwds, banned_kwds =\
            self.remove_keywords(keywords_scores)

        # inserted_kwds = self.get_inserted_keywords()
        persistent_kwds =\
            dbs.read_iteration_list("persistent keywords", -1)

        keywords, first_tier_kwds, second_tier_kwds =\
            self.group_keywords(keywords_scores, persistent_kwds,
                                removed_kwds, new_keywords)
        # keywords is now list, keywords_scores, pick now only two new keywords
        # but still check not to put too many search terms.
        # kwd_groups = persistent_kwds, first_tier_kwds, second_tier_kwds, removed_kwds

        # search_terms = self.add_negative_terms(search_terms, negative_kwds)

        kwd_groups = (persistent_kwds, first_tier_kwds, second_tier_kwds,
                      removed_kwds, banned_kwds)

        return keywords, keywords_scores, kwd_groups
    
    # def extract_compound_text(self, results):
    #     """
    #     Go through _current_search_results, extract adequate text from each
    #     and insert it into _compound_text.
    #     also include any added text in the database in this iteration.
    #     """
    #     # compound_text = ""
    #     compound_text = ""#self._compound_text + "\n"
    #     # compound_text = compound_text.strip()
    #     for result in results:#self._current_search_results:
    #         if "abstract" in result:
    #             title = result["title"].lower().strip()
    #             title = title.replace("citation", "")
    #             title = title.replace("book", "")
    #             compound_text += (" " + title)
    #             if result["abstract"]:
    #                 body_text = result["abstract"][:10000]
    #                 compound_text += (" " + body_text)
    #             else:
    #                 abs_lines = result["text lines"]
    #                 abs_lines = abs_lines.lower().replace("abstract", "")
    #                 compound_text += ( " " + abs_lines.strip() )
    #
    #     # check if there was any added text to iteration:
    #     dbs.wait_for_pause()
    #     iteration = dbs.read_database("iterations")[-1]
    #     if "added text" in iteration:
    #         compound_text += "\n" + iteration["added text"]
    #
    #     # self._compound_text = compound_text.lower().strip();
    #     print "compound text length: {}".format(len(compound_text))
    #     return compound_text.lower().strip()

#    def get_new_compound_text_from_search_results(self):
#        """
#        - visit each source and extract the relevant text. 
#        During each visit. 
#        
#        - check if the website (or mother website) 
#        has been visited within the last, say, 10 seconds. If so 
#        move the link to the bottom of the list and attempt to visit 
#        the following link.
#        
#        - Join together all the extracted text and save it in 
#        self._compound_text
#        """
#        compound_text = ""
#        # loop over each result returned by google:
#        links = self._current_search_links[:]
#        if links:
#            stop = False
#            link_index = 0
#            N = len(links)
#        else:
#            stop = True
#        
#        while not stop:
#            link = links[link_index]
#            #check if current link has be visited within, say, 10seconds
#            # if it was wait, move it to the bottom of the list and 
#            # go to the next link:
#            
#            # try to get the abstract from the linked website and 
#            # attach it to abstracts:
#            abstract = utils.PaperWebsiteScrapper(link).run()
#            
#            compound_text += (" " + abstract)
#            
#            link_index += 1
#            if link_index >= N:
#                stop = True
#        self._compound_text = compound_text.lower()


    # def determine_next_keywords(self, compound_text=""):
    #     """
    #     First extract keywords from the compound text. Then check the
    #     database for inserted or removed keywords (i.e., allowing user
    #     control through a gui modifying the database) as well as any
    #     persistent keywords (usually the seed keywords). Finally,
    #     generate the next keywords string from the information above.
    #     """
    #     # extract keywords from the compound text:
    #     extracted = txtproc.extractKeyphrases(compound_text)#self._compound_text[:3000])
    #
    #     # extracted = \
    #     #     txtproc.ExtractKeywords(self._compound_text).run()
    #     # txtproc.ExtractKeywords(self._compound_text).run()
    #
    #     #        self._extracted_keywords = extracted_kwds =\
    #     #        txtproc.ExtractKeywords(self._compound_text).run()
    #
    #     # check the database for inserted or removed keywords:
    #     iteration = dbs.read_database("iterations")[-1]
    #     inserted_kwds, removed_kwds, persistent_kwds = [], [], []
    #     if "inserted keywords" in iteration:
    #         inserted_kwds = iteration["inserted keywords"]
    #     if "removed keywords" in iteration:
    #         removed_kwds = iteration["removed keywords"]
    #     self._removed_keywords = removed_kwds[:]
    #
    #     # get the persistent keywords, if any:
    #     # if "persistent keywords" in iteration:
    #     #     persistent_kwds = self._persistent_keywords = \
    #     #         iteration["persistent keywords"]
    #     persistent_kwds = []
    #
    #     # generate from the above a new self._next_keywords list:
    #     next_kwds = persistent_kwds + inserted_kwds
    #     next_kwds = " ".join(next_kwds).replace('"', "").split(" ")
    #     No = len(next_kwds)
    #     Nmax = self._max_keywords
    #     N1st = int((Nmax - No) / 2)
    #     #        Nextr = len(extracted_kwds)
    #
    #     # remove permanent or inserted keywords from the extracted set:
    #     next_kwds_string = " ".join(next_kwds)
    #     extracted_kwds = [w for w in extracted if w not in next_kwds_string]
    #
    #     # extracted = zip(extracted[0], extracted[1])
    #     # new_extracted = extracted[:]
    #     # for item in extracted:
    #     #     kwd = item[0]
    #     #     if kwd in next_kwds_string:
    #     #         try:
    #     #             new_extracted.remove(item)
    #     #         except:
    #     #             pass
    #     # if new_extracted:
    #     #     extracted_kwds, scores = zip(*new_extracted)
    #     # else:
    #     #     extracted_kwds, scores = [], []
    #     self._extracted_keywords = extracted_kwds
    #     Nextr = len(extracted_kwds)
    #
    #     # # find extracted keywords over threshold:
    #     # if scores:
    #     #     score_threshold = scores[0] * 0.25
    #     # else:
    #     #     score_threshold = 0
    #     # Nth = Nextr
    #     # for k in range(Nextr):
    #     #     if scores[k] < score_threshold:
    #     #         Nth = k
    #     #         break
    #     # if Nth < N1st: Nth = N1st
    #
    #     if Nextr >= N1st:
    #         first_kwds = extracted_kwds[0:N1st]
    #         sec_kwds = extracted_kwds[N1st:]
    #     else:
    #         first_kwds = extracted_kwds[:]
    #         sec_kwds = []
    #
    #     self._firsttier_keywords = first_kwds[:]
    #     self._secondtier_keywords = sec_kwds[:]
    #
    #     next_kwds += " ".join(first_kwds).replace('"', "").split(" ")
    #     if len(next_kwds) > Nmax: next_kwds = next_kwds[0:Nmax]
    #
    #     for kw in removed_kwds:
    #         if len(kw.split()) > 1:
    #             next_kwds.append('-"' + kw.replace('"', "") + '"')
    #         else:
    #             next_kwds.append('-' + kw.replace('"', ""))
    #
    #     self._next_keywords = next_kwds[:]
    #     return next_kwds
    
#     def determine_next_keywords(self):
#         """
#         First extract keywords from the compound text. Then check the
#         database for inserted or removed keywords (i.e., allowing user
#         control through a gui modifying the database) as well as any
#         persistent keywords (usually the seed keywords). Finally,
#         generate the next keywords string from the information above.
#         """
#         # extract keywords from the compound text:
#         extracted =\
#             txtproc.ExtractKeywords(self._compound_text).run()
#         # txtproc.ExtractKeywords(self._compound_text).run()
#
# #        self._extracted_keywords = extracted_kwds =\
# #        txtproc.ExtractKeywords(self._compound_text).run()
#
#         # check the database for inserted or removed keywords:
#         iteration = dbs.read_database("iterations")[-1]
#         inserted_kwds, removed_kwds, persistent_kwds = [], [], []
#         if "inserted keywords" in iteration:
#             inserted_kwds = iteration["inserted keywords"]
#         if "removed keywords" in iteration:
#             removed_kwds = iteration["removed keywords"]
#         self._removed_keywords = removed_kwds[:]
#
#         # get the persistent keywords, if any:
#         if "persistent keywords" in iteration:
#             persistent_kwds = self._persistent_keywords =\
#             iteration["persistent keywords"]
#
#         # generate from the above a new self._next_keywords list:
#         next_kwds = persistent_kwds + inserted_kwds
#         next_kwds = " ".join(next_kwds).replace('"',"").split(" ")
#         No = len(next_kwds)
#         Nmax = self._max_keywords
#         N1st = int( (Nmax-No)/2 )
# #        Nextr = len(extracted_kwds)
#
#         # remove permanent or inserted keywords from the extracted set:
#         next_kwds_string = " ".join(next_kwds)
#         extracted = zip(extracted[0], extracted[1])
#         new_extracted = extracted[:]
#         for item in extracted:
#             kwd = item[0]
#             if kwd in next_kwds_string:
#                 try:
#                     new_extracted.remove(item)
#                 except:
#                     pass
#         if new_extracted:
#             extracted_kwds, scores = zip(*new_extracted)
#         else:
#             extracted_kwds, scores = [], []
#         self._extracted_keywords = extracted_kwds
#         Nextr = len(extracted_kwds)
#
#         #find extracted keywords over threshold:
#         if scores:
#             score_threshold = scores[0]*0.25
#         else:
#             score_threshold = 0
#         Nth = Nextr
#         for k in range(Nextr):
#             if scores[k] < score_threshold:
#                 Nth = k
#                 break
#         if Nth < N1st: Nth = N1st
#
#         if Nextr >= N1st:
#             first_kwds = extracted_kwds[0:N1st]
#             sec_kwds = extracted_kwds[N1st:]
#         else:
#             first_kwds = extracted_kwds[:]
#             sec_kwds = []
#
#         self._firsttier_keywords = first_kwds[:]
#         self._secondtier_keywords = sec_kwds[:]
#
#         next_kwds += " ".join(first_kwds).replace('"',"").split(" ")
#         if len(next_kwds) > Nmax: next_kwds = next_kwds[0:Nmax]
#
# #        next_kwds = persistent_kwds + inserted_kwds + extracted_kwds
# #        next_kwds_str = " ".join(next_kwds)
# #        next_kwds = next_kwds_str.split(" ")[0:max_kwds]
#
#         for kw in removed_kwds:
#             if len(kw.split())>1:
#                 next_kwds.append('-"' + kw.replace('"', "") + '"')
#             else:
#                 next_kwds.append('-' + kw.replace('"', ""))
#
#         self._next_keywords = next_kwds[:]
        
    def assess_search_convergence(self, new_urls):#, compound_text):
        """
        basically compare current keywords to previous keywords (or 
        with a global histogram of all the keywords found) to 
        quantify whether the search is converging. update the plot 
        with the result.
        get graph widget from kivy garden.
        """
        if not new_urls:# or not compound_text:
            return True
        else:
            return False
        # if not self._new_urls or not self._compound_text:
        # if not new_urls or not self._compound_text:
        #     self._has_converged = True
        # else:
        #     self._has_converged = False
#        convergence = 0
#        if len(self.papers_data_iterations)>2:
#            current_keywords = self.keywords
#            previous_keywords =\
#            self.iterations_metrics[-2]["keywords"]
#            convergence = compare_lists(current_keywords,
#                                        previous_keywords)
#        self.iterations_metrics[-1]["convergence"] = convergence
        
    def save_iteration_data(self, results, tsearch):
        iterations = dbs.read_database("iterations")
        iteration = iterations[-1]
        iteration["items"] = results
        iteration["search time"] = tsearch
        iterations[-1] = iteration
        dbs.write_database("iterations", iterations)
        
    def check_stop(self, has_converged, keywords_scores=([],[])):
        """
        Check the database for the stop entry.
        """
        stop = dbs.check_stop()
        if has_converged: stop = True
        if stop:
            dbs.stop()
            dbs.running_off()
            # display the last set of cumulated keywords:
            k, s = keywords_scores
            if k:
                dbs.write_iteration_list("first-tier keywords", k)
                dbs.write_iteration_list("second-tier keywords", [])
        if self._debug_mode and stop == True:
            stop_time = time.strftime("at %H:%M:%S on %Y/%m/%d")
            print "stopping kwsearch {}".format(stop_time)
        return stop
        # stop = dbs.check_stop()
        # if self._has_converged: stop = True
        # if stop:
        #     # self._stop_search = True
        #     dbs.stop()
        #     dbs.running_off()
        # if self._debug_mode and stop == True:
        #     stop_time = time.strftime("at %H:%M:%S on %Y/%m/%d")
        #     print "stoping kwsearch {}".format(stop_time)
        # return stop

    def wait(self):
        """
        See how long has it been since the last iteration and wait if
        needed in order not to overwhelm the cpu
        :return: nothing, just wait if needed
        """
        entries = dbs.list_database_entries()
        # pause if time elapsed since the last iteration < 1s:
        if "iteration times" in entries:
            it_times = dbs.read_database("iteration times")
            last_time = it_times[-1]
            first_iteration = False
        else:
            first_iteration = True
            it_times = []
            last_time = 0
        time_elapsed = time.time() - last_time
        if time_elapsed < 1:
            time.sleep(1)
        new_time = time.time()
        it_times.append(new_time)
        dbs.write_database("iteration times", it_times)
        
        # for debugging:
        if self._debug_mode and not first_iteration:
            print "iteration time = {}".format(new_time-last_time)
            
    def check_pause(self):
        """
        Check the database for the pause entry, if True, wait 1s and check 
        again, repeat until pause = False.
        """
        pause = dbs.check_pause()
        while pause:
            time.sleep(1)
            pause = dbs.check_pause()
            
#    ###### >>>>>>>> third-tier methods:

    def get_added_text_list(self):
        iterations = dbs.read_database("iterations")
        if iterations:
            iteration = iterations[-1]
            if "added text" in iteration:
                added_text = iteration["added text"]
                if type(added_text) is list:
                    return added_text
                else:
                    return [added_text]
        return []

    def get_new_keywords(self, results=[], added_text_list=[],
                         maxwords=3000, minwords=10, len_power = 1.):
        keywords, scores = [], []
        # extract keywords from search results:
        for result in results:
            text = self.get_text_from_result(result, maxwords)
            text = txtproc.filterout_gibberish(text)
            if txtproc.count_words(text)>minwords:
                k, s = self.get_keywords_from_text(text)
                s = self.scale_scores(s, text, len_power)
                keywords, scores =\
                    self.merge_keywords_scores_tuples([(keywords,scores),
                                                       (k,s)])
        # now extract keywors from added_text_list:
        for text in added_text_list:
            text = txtproc.filterout_gibberish(text)
            if txtproc.count_words(text) > minwords:
                text = txtproc.limit_number_of_words(text, maxwords)
                k, s = self.get_keywords_from_text(text)
                s = self.scale_scores(s, text, len_power)
                keywords, scores = \
                    self.merge_keywords_scores_tuples([(keywords, scores),
                                                       (k, s)])
        return (keywords, scores)

    def remove_keywords(self, keywords_scores, removed_kwds=[],
                        banned_kwds=[]):
        keywords, scores = keywords_scores
        # removed_kwds, banned_kwds = [], []
        try:
            iteration = dbs.read_database("iterations")[-1]
        except:
            pass
        try:
            removed_kwds += iteration["removed keywords"]
        except:
            pass
        try:
            banned_kwds += iteration["banned keywords"]
        except:
            pass

        # filtered_keywords = []
        # for kwd in keywords:
        #     if kwd not in removed_kwds:
        #         filtered_keywords.append(kwd)
        black_list = removed_kwds + banned_kwds
        filtered_keywords = [kwd for kwd in keywords if kwd not in black_list]
        filtered_keywords = [kwd for kwd in filtered_keywords if not txtproc.is_word_gibberish(kwd)]
        filtered_keywords = txtproc.remove_stop_words(filtered_keywords)

        kdict = dict(zip(keywords, scores))
        filtered_scores = [kdict[k] for k in filtered_keywords]

        return (filtered_keywords, filtered_scores), removed_kwds, banned_kwds

    # def get_inserted_keywords(self):
    #     try:
    #         iteration = dbs.read_database("iterations")
    #         return iteration["inserted keywords"]
    #     except:
    #         return []

    def group_keywords(self, keywords_scores, persistent_kwds=[],
                       removed_kwds=[], new_keywords=2):
        # black_list = removed_kwds + banned_kwds
        # keywords = [kwd for kwd in persistent_keywords if kwd not in black_list]

        k, s = keywords_scores
        sk = zip(s,k)
        k = [kph for (val, kph) in sorted(sk, reverse=True)]
        first_tier_kwds = k[:new_keywords]
        # keywords += first_tier_kwds
        if len(k)>new_keywords:
            second_tier_kwds = k[new_keywords:]
        else:
            second_tier_kwds = []

        kwd_groups = persistent_kwds[:], first_tier_kwds[:], \
                     second_tier_kwds[:], removed_kwds[:]

        # for kw in removed_kwds:
        #     if len(kw.split()) > 1:
        #         keywords.append('-"' + kw.replace('"', "") + '"')
        #     else:
        #         keywords.append('-' + kw.replace('"', ""))

        keywords = self.build_keywords_list(persistent_kwds, first_tier_kwds,
                                            removed_kwds)

        return keywords, first_tier_kwds, second_tier_kwds
        # new_keywords = inserted_kwds + keywords
        # max_score = max(scores)
        # new_scores = len(inserted_kwds)*[max_score] + scores
        #
        # # get the search terms:
        # included_kwds = []
        # for kwd in new_keywords:
        #     sent = " ".join(included_kwds)
        #     nwords = len(sent.split()) + len(kwd.split())
        #     if nwords < max_search_terms:
        #         included_kwds.append(kwd)
        #     else:
        #         break
        # search_terms = " ".join(included_kwds)
        #
        # # get the first and second-tier keywords:
        # first_tier_kwds = []
        # second_tier_kwds = []
        # for kwd in keywords:
        #     if kwd in search_terms:
        #         first_tier_kwds.append(kwd)
        #     else:
        #         second_tier_kwds.append(kwd)
        #
        # return keywords, keywords_scores, kwd_groups

    def build_keywords_list(self, persistent_kwds=[], first_tier_kwds=[],
                            removed_kwds=[]):
        # black_list = removed_kwds + banned_kwds
        # keywords = [kwd for kwd in persistent_kwds if kwd not in black_list]
        # keywords += [kwd for kwd in first_tier_kwds if kwd not in black_list]
        keywords = persistent_kwds[:] + first_tier_kwds[:]
        for kw in removed_kwds:
            if len(kw.split()) > 1:
                keywords.append('-"' + kw.replace('"', "") + '"')
            else:
                keywords.append('-' + kw.replace('"', ""))
        return keywords


    # def group_keywords(self, keywords, scores,
    #                    inserted_kwds, max_search_terms=8):
    #     # add any inserted keywords to the top of the keywords list:
    #     new_keywords = inserted_kwds + keywords
    #     max_score = max(scores)
    #     new_scores = len(inserted_kwds)*[max_score] + scores
    #
    #     # get the search terms:
    #     included_kwds = []
    #     for kwd in new_keywords:
    #         sent = " ".join(included_kwds)
    #         nwords = len(sent.split()) + len(kwd.split())
    #         if nwords < max_search_terms:
    #             included_kwds.append(kwd)
    #         else:
    #             break
    #     search_terms = " ".join(included_kwds)
    #
    #     # get the first and second-tier keywords:
    #     first_tier_kwds = []
    #     second_tier_kwds = []
    #     for kwd in keywords:
    #         if kwd in search_terms:
    #             first_tier_kwds.append(kwd)
    #         else:
    #             second_tier_kwds.append(kwd)
    #
    #     return search_terms, new_keywords, new_scores, \
    #            first_tier_kwds, second_tier_kwds

    def get_text_from_result(self, result={}, maxwords=3000):
        try:
            text = result["abstract"].strip().lower()
            text = txtproc.filterout_gibberish(text)
            if text:
                return txtproc.limit_number_of_words(text, maxwords)
        except:
            pass
        try:
            text = result["text lines"].strip().lower()
            text = txtproc.filterout_gibberish(text)
            return txtproc.limit_number_of_words(text, maxwords)
        except:
            pass
        return ""

    def get_keywords_from_text(self, text=""):
        text = txtproc.cleanup_text(text.strip().lower())
        keywords, scores = txtproc.extract_scored_keyphrases(text)
        # sort:
        ks = zip(keywords, scores)
        scores = sorted(scores, reverse=True)
        keywords = [kph for (kph, val) in sorted(ks, reverse=True)]
        return keywords, scores

    def rotate_keywords(self, persistent_kwds=[], first_tier_kwds=[],
                        second_tier_kwds=[], removed_kwds=[],
                        locally_banned_kwds=[]):

        # persistent_kwds, first_tier_kwds, second_tier_kwds, \
        # removed_kwds, banned_kwds = kwd_groups

        # k, s = keywords_scores
        temp_banned_kwds = list(set(locally_banned_kwds[:]))
        # ban the first new_keywords to make sure that they don't come back:
        temp_banned_kwds += first_tier_kwds[:]
        filtered_second_tier = [k for k in second_tier_kwds if k not in temp_banned_kwds]
        new_first_tier = filtered_second_tier[:len(first_tier_kwds)]
        new_second_tier = filtered_second_tier[len(first_tier_kwds):]
        # for kwd in k[:new_keywords]:
        #     temp_banned_kwds.append(kwd)
            # dbs.append_iteration_list("banned keywords", kwd)

        # now get a new keywords with the ban in place:
        keywords = self.build_keywords_list(persistent_kwds, new_first_tier,
                                            removed_kwds)
        # new_keywords, new_kwd_groups = \
        #     self.group_keywords(keywords_scores, persistent_kwds,
        #                         removed_kwds, temp_banned_kwds,
        #                         new_keywords)
        # write to database so that gui could be updated:
        # p_kwds, f_tier_kwds, s_tier_kwds, \
        # r_kwds, temp_banned_kwds = new_kwd_groups

        print new_first_tier
        print "will try again with {}".format(" ".join(keywords))
        dbs.write_iteration_list("keywords", keywords)
        dbs.write_iteration_list("first-tier keywords", new_first_tier)
        dbs.write_iteration_list("second-tier keywords", new_second_tier)

        return keywords, temp_banned_kwds

        # if len(k) > new_keywords:
        #     new_keywords_scores = k[new_keywords:], s[new_keywords:]
        #     new_keywords, new_kwd_groups = \
        #         self.group_keywords(keywords_scores, persistent_kwds,
        #                             removed_kwds, banned_kwds,
        #                             new_keywords)
        #     # write to database so that gui could be updated:
        #     persistent_kwds, first_tier_kwds, second_tier_kwds, \
        #     removed_kwds, banned_kwds = new_kwd_groups
        #     print first_tier_kwds
        #     print "will try again with {}".format(" ".join(new_keywords))
        #     dbs.write_iteration_list("keywords", new_keywords)
        #     dbs.write_iteration_list("first-tier keywords",
        #                              first_tier_kwds)
        #     dbs.write_iteration_list("second-tier keywords",
        #                              second_tier_kwds)
        # return new_keywords, new_keywords_scores, new_kwd_groups

    def scale_scores(self, scores=[], text="", len_power=0.5):
        nwords = txtproc.count_words(text)#len(text.split())
        return [s*nwords**len_power for s in scores]

    # def add_negative_terms(self, search_terms='', negative_kwds=[]):
    #     new_search_terms = search_terms
    #     for neg in negative_kwds:
    #         if len(neg.split())>1:
    #             new_search_terms += ' -"' + neg + '"'
    #         else:
    #             new_search_terms += ' -' + neg
    #     return new_search_terms

#    ##### search methods:            
#    def get_links_from_keywords(self):
#        """
#        get a list of links related to current keywords (e.g., the
#        links returned by a google search). 
#        """
#        self._current_links =\
#        utils.get_links_from_keywords(self._keywords)
#        
#        
#    def get_compound_text_from_links(self):
#        """
#        Visit each link in self._search_links and extract the 
#        relevant text. 
#        During each visit, check if the website (or mother website) 
#        has been visited within the last, say, 10 seconds. If so 
#        move the link to the bottom of the list and attempt to visit 
#        the following link.
#        - Join together all the extracted text and save it in 
#        self._compound_text
#        """
#                
#        
    ####### database methods:
#    def initialize_database(self):
#        dbs.initialize_json_database(self._database)
#        
#    def read_database(self, entry_name = "stop"):
#        return dbs.read_json_entry(entry_name, self._database)
#        
#    def write_database(self, entry_name = "stop", value = False):
#        dbs.write_json_entry(entry_name, value, self._database)
#    
#    def list_database_entries(self):
#        return dbs.list_json_entries(self._database)
        
    ######## other methods:
    
    def domain_visited_recently_in_search_results(self, url, 
                                                  search_results,
                                                  dt = 15):
        domain = utils.get_url_domain(url).lower().strip()
        for r in search_results:
            r_domain = utils.get_url_domain(r["link"]).lower().strip()
            if domain == r_domain:
                if time.time() - r["time of visit"] < 15:
                    return True
        return False

    def merge_keywords_scores_tuples(self, ks_tuple_list):
        """
        for a list of, possibly overlaping, (keywords, scores) tuples,
        merge them on a single tuple (kout, sout) where kout is the union
        of all the keywords in the ks_list and sout is the list of
        corresponding scores, where the scores of overlapping keywords are
        added. Then sort according to score. Then divide the merged scores
        by the number of merged ks tuples.
        The idea is that by merging the common keywords will keep a "normal"
        score, whereas the others will whither.
        :param ks_tuple_list: list of tuples e.g., [(k1,s1),(k2,s2),(k3,s3)]
        :return: tuple of merged tuples (merged_k, merged_s)
        """
        # function that merges two keyword, scores tuples:
        def join_keywords(ks_tuple1, ks_tuple2):
            k1, s1 = ks_tuple1
            k2, s2 = ks_tuple2

            all_k_set = set(k1 + k2)
            dict1 = dict(zip(k1, s1))
            dict2 = dict(zip(k2, s2))

            k3 = []
            s3 = []
            for kph in list(all_k_set):
                k3.append(kph)
                if kph in k1 and kph in k2:
                    s3.append(dict1[kph] + dict2[kph])
                elif kph in k1:
                    s3.append(dict1[kph])
                elif kph in k2:
                    s3.append(dict2[kph])
            # sort the output:
            sk3 = zip(s3, k3)
            s3 = sorted(s3, reverse=True)
            k3 = [kph for (val, kph) in sorted(sk3, reverse=True)]

            return k3, s3
        # merge all (adding overlapping scores):
        merged_k, merged_s = reduce(join_keywords, ks_tuple_list)
        # divide the scores by the number of merged ks tuples:
        # n = float(len(ks_tuple_list))
        # merged_s = [s/n for s in merged_s]

        return merged_k, merged_s
        
#    def has_been_processed_before(self, url):
#        result = {}
#        iterations = self.read_database("iterations")
#        
#        return result
        
##    def initialize_images_variables(self):
##        root_folder = get_root_folder()
##        self.images_folder_path =\
##        make_path(root_folder, "images")
##        self.images_data_iterations = []
##        
##    def initialize_papers_variables(self):
##        self.papers_data_iterations = []
##        self.visited_paper_links = [] #list of (url, time_visited)
##        self.iterations_metrics = []
##        
##    def sort_papers_if_needed(self):
##        """
##        first find the subset of self.visited_paper_links visited 
##        at times t < self.minimum_time_delay_between_visits and 
##        then determine if there're urls in 
##        self.papers_in_current_iteration that coincide with the 
##        general form of any of the recently visited urls.
##        "general form" could be if all minus one or two of the 
##        words making up the link coincide with the recently 
##        visited url.
##        """
##        
##    def extract_abstract_from_html(self, html = ""):
##        """
##        look at the labview vi, look for tags like Abstract, 
##        abstract, etc (combinations of abstract with different 
##        cases, using re can make it even simpler).
##        now beautiful soup can be used to make easier.
##        """
##        abstract = ""
##        return abstract
##        
##    def get_top_words_from_histogram(self):
##        """
##        output the upper self.threshold_percentage words in the 
##        self.words_histogram.
##        need to check the number of occurrences of last item and 
##        extend the list to include all the words with the same 
##        number of ocurrences in histogram.
##        """
##        top_words = []
##        return top_words
#        
#        
#
####### second-tier functions and classes:
#
#def google_images_search(keywords):
#    """
#    does a google images search and outputs the links to the first 
#    N images and their corresponding websites.
#    """
#    image_links = []
#    website_links = []
#    return image_links, website_links
#
#def save_image_from_website(website_address = "http://www.google.com/imgres?imgurl=http%3A%2F%2Fanimalia-life.com%2Fdata_images%2Fcat%2Fcat1.jpg&imgrefurl=http%3A%2F%2Fanimalia-life.com%2Fcat.html&h=2196&w=2891&tbnid=_QnS9VfSCjBzHM%3A&zoom=1&docid=W0zXkc6zsgjxZM&hl=en&ei=Iax4VI2FKIPdsAThuYHYBg&tbm=isch&ved=0CDMQMygAMAA&iact=rc&uact=3&dur=10427&page=1&start=0&ndsp=4",
#                            save_in = "C:\Users\Roberto\Documents\Projects\Software projects\Meta Search Engine\in Python"):
#    """
#    """
#
#def google_scholar_search(keywords):
#    """
#    make a scholar search and extract from the html a list  
#    consisting of items of the form 
#    (title, url, abstract_snipet)
#    the abstract snipet is extracted just in case that the actual 
#    abstract can't be extacted later.
#    """
#    scholar_results = []
#    return scholar_results
#
#class new_browser():
#    """
#    if a url is given as input, will get the html in self.html 
#    and close the browser. so leave url empty when first 
#    instantiating this class to do something else (like 
#    fill a form)
#    """
#    def __init__(self, url = ""):
#        import mechanize
#        import cookielib
#        # Browser
#        br = mechanize.Browser()
#    
#        # Cookie Jar
#        cj = cookielib.LWPCookieJar()
#        br.set_cookiejar(cj)
#    
#        # Browser options
#        br.set_handle_equiv(True)
#        #br.set_handle_gzip(True)
#        br.set_handle_redirect(True)
#        br.set_handle_referer(True)
#        br.set_handle_robots(False)
#    
#        # Follows refresh 0 but not hangs on refresh > 0
#        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
#        # Want debugging messages?
#        #br.set_debug_http(True)
#        #br.set_debug_redirects(True)
#        #br.set_debug_responses(True)
#        # User-Agent (this is cheating, ok?)
#        # might consider getting a list of user agents and 
#        # randomly choosing one of them (recommended to avoid 
#        # getting caught).
#        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
#        
#        self.br = br
#        if url:
#            self.browse_to_url(url)
#        
#    def browse_to_url(self, url = "", close = True):
#        self.html = ""
#        if url:
#            try:
#                self.br.open(url)
#                self.update_browser()
#                if close:
#                    self.close_browser()
#            except:
#                print "could't open {}".format(url)
#                
#        
#    def fill_form(self, url = "", form_index = 0, 
#                  data = {}, close = True):
#        try:
#            self.br.open(url = url, close = False)
#            self.br.select_form(nr = 0)
#            for key, value in data.iteritems():
#                self.br.form[key] = value
#            self.br.submit()
#            self.update_browser()
#            if close:
#                self.close_browser()
#        except:
#            print "couldn't fill form"
#    
#    def update_browser(self):
#        self.response = self.br.response()
#        self.html = self.response.read()
#        self.url = self.response.geturl()
#    
#    def close_browser(self):
#        self.br.close()
#        
#        
########  third-tier functions:
#
#def get_website_html(url = ""):
#    html = ""
#    return html
#
#def word_histogram_from_text(text = ""):
#    """
#    - first split the text into a vector.
#    - then go through all the elements, use re to filter out 
#    non alphanumeric characters (e.g., "."). make all lowercase.
#    erase the whitespace on both sides.
#    - eliminate all the "common words" (e.g., "the", "a", "to", etc) 
#    and any empty elements (which could come up when erasing the 
#    non alphanumeric characters)
#    """
#    word_histogram = []
#    return word_histogram
#
#def sentence_to_lower_case_list(sentence = ""):
#    """
#    split text and make all the words in list lower case.
#    """
#    words_list = []
#    return words_list
#    
#def list_to_sentence(word_list = []):
#    sentence = ""
#    return sentence
#    
#def eliminate_duplicates(items_list = []):
#    return items_list
#    
#def compare_lists(list1 = [], list2 = []):
#    """
#    compare the elements of the two lists and determine the 
#    coincidences. output the number of coincidences divided by 
#    the lenght of the longest list.
#    """
#    similarity = 0
#    return similarity
#
#def get_root_folder():
#    import os
#    return os.getcwd()
#        
#def make_path(folder, file_name):
#    from os import path
#    return path.join(folder, file_name)
#
#def does_file_exist(file_path):
#    from os import path
#    return path.exists(file_path)
    
        
if __name__ == "__main__":
    kw = kwSearch()
    kw.full_search()