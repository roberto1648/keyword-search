# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 15:34:28 2016

@author: roberto
"""
import mechanize
import cookielib
from bs4 import BeautifulSoup
from urlparse import urlparse
import re
import os, sys

####### >>> Policies


class GoogleSearch():
    def __init__(self,
                 search_terms="ultrafast lasers",
                 debug_mode=False):
        """
        Search google scholar for the given keywords.

        Inputs:

        search_terms: a string with the search terms separated by spaces.
        debug_mode: boolean determining whether or not to raise any errors. if
        False (Defalult) will return empty outputs.

        Output:

        results: 1D array of dictionaries with keys:
            'links': link to the scholar search result.
            'text': small text returned for each link.
            'html': the raw html of the result tag.
        """
        self._debug_mode = debug_mode
        self._search_terms = search_terms

    def run(self):
        html = self.get_html()
        return self.extract_info_from_html(html)
        # return self._search_results

    def get_html(self):
        """
        Search google scholar for the given _search_terms using a
        MechanizeBrowser().

        self._search_terms should be a string with the search
        terms separated by spaces.
        if self._debug_mode is True will raise any errors, if
        False (Defalult) will return an empty html string.

        produces:

        self._html: the raw html returned from the search.
        """
        html = ""
        try:
            # address = "https://scholar.google.com/schhp?hl=en&as_sdt=0,31"
            address = "https://www.google.com/#hl=en"
            # address = "https://www.google.com/?ion=1&espv=2&client=ubuntu#"
            br = MechanizeBrowser()
            br.browse_to_webpage(address)
            br.select_form(index=0)
            br.fill_form_item('q', self._search_terms)
            br.submit_form()
            html = br.get_html()  # ;print br.list_links()
            br.close()
        except:
            if self._debug_mode:
                raise
        # self._html = html
        return html

    def extract_info_from_html(self, html):
        """
        From inspecting the scholar html, the results are:
        - contained in "div" tags of class="gs_ri".
        - the result header (as seen on the webpage) is then
        inside a "h3" tag of class="gs_rt".
        - the h3 tag text is the result title.
        - inside the h3 is an "a" tag, whose "href" attribute is
        the link to the page that contains the paper abstract. of
        all the extractable information this link should be the
        only indispensable one.
        - The authors, journal, year, and publisher are in a "div" tag of
        class="gs_a" (direct child of the parent "div", sibling of the
        "h3") and are contained in the tag's text. The tag also has an
        "a" subtag with a "href" link attribute to the citations, but
        it's a google link so it'd require more steps to get that.
        - A few lines from the abstract are given in another "div" tag
        of class="gs_rs" (direct child of parent "div"). If needed could
        use this text to validate the actual abstract later (e.g., can
        go through the words one by one and see if they are included in
        the text one suspects to be the abstract.)
        """
        soup = BeautifulSoup(html)#self._html)
        tags = soup.find_all(name="div", class_="g")

        g_results = []
        for tag in tags:
            info = self.extract_item_info(tag)
            if info["link"]:
                g_results.append(info)

        # self._search_results = gs_results
        return g_results

    def extract_item_info(self, tag):
        info = {"title": "",
                "link": "",
                "text lines": ""}

        h3_tag = tag.find("h3", class_="r")
        try:
            info["title"] = h3_tag.text
        except:
            pass
        try:
            link = tag.find("cite").text
            if "..." in link:
                link = h3_tag.find("a")
                link = link["href"][7:]
                link = link[:link.find("&sa=")]
            info["link"] = link
        except:
            pass
        try:
            info["text lines"] = \
                tag.find("span", class_="st").text
        except:
            pass
        return info


class GoogleScholarSearch():
    def __init__(self, 
                 search_terms = "ultrafast lasers", 
                 debug_mode = False):
        """
        Search google scholar for the given keywords.
        
        Inputs:
        
        search_terms: a string with the search terms separated by spaces.
        debug_mode: boolean determining whether or not to raise any errors. if 
        False (Defalult) will return empty outputs.
        
        Output:
        
        results: 1D array of dictionaries with keys:
            'links': link to the scholar search result.
            'text': small text returned for each link.
            'html': the raw html of the result tag.
        """
        self._debug_mode = debug_mode
        self._search_terms = search_terms
        
    def run(self):
        self.get_html()
        self.extract_info_from_html()        
        return self._search_results
    
    def get_html(self):
        """
        Search google scholar for the given _search_terms using a 
        MechanizeBrowser().
        
        self._search_terms should be a string with the search 
        terms separated by spaces.
        if self._debug_mode is True will raise any errors, if 
        False (Defalult) will return an empty html string.
        
        produces:
        
        self._html: the raw html returned from the search.
        """
        html = ""
        try:
            address = "https://scholar.google.com/schhp?hl=en&as_sdt=0,31"
            br = MechanizeBrowser()
            br.browse_to_webpage(address)
            br.select_form(index = 0)
            br.fill_form_item('q', self._search_terms)
            br.submit_form()    
            html = br.get_html()#;print br.list_links()
            br.close()
        except:
            if self._debug_mode:
                raise
        self._html = html
        
    def extract_info_from_html(self):
        """
        From inspecting the scholar html, the results are: 
        - contained in "div" tags of class="gs_ri".
        - the result header (as seen on the webpage) is then 
        inside a "h3" tag of class="gs_rt".
        - the h3 tag text is the result title.
        - inside the h3 is an "a" tag, whose "href" attribute is 
        the link to the page that contains the paper abstract. of 
        all the extractable information this link should be the 
        only indispensable one.
        - The authors, journal, year, and publisher are in a "div" tag of 
        class="gs_a" (direct child of the parent "div", sibling of the 
        "h3") and are contained in the tag's text. The tag also has an 
        "a" subtag with a "href" link attribute to the citations, but 
        it's a google link so it'd require more steps to get that.
        - A few lines from the abstract are given in another "div" tag 
        of class="gs_rs" (direct child of parent "div"). If needed could 
        use this text to validate the actual abstract later (e.g., can 
        go through the words one by one and see if they are included in 
        the text one suspects to be the abstract.)
        """
        soup = BeautifulSoup(self._html)
        tags = soup.find_all(name = "div", class_ = "gs_ri")
        
        gs_results = []
        for tag in tags:
            info = self.extract_paper_info(tag)
            if info["link"]:
                gs_results.append(info)
                
        self._search_results = gs_results
        
    def extract_paper_info(self, tag_soup):
        info = {"title": "",
                "link": "",
                "authors, year, journal": "",
                "abstract lines": ""}
        
        h3_tag = tag_soup.find("h3", class_ = "gs_rt")
        try:
            info["title"] = h3_tag.text
        except:
            pass
        try:
            info["link"] = h3_tag.find("a")["href"]
        except:
            pass
        try:
            info["authors, year, journal"] =\
            tag_soup.find("div", "gs_a").text
        except:
            pass
        try:
            info["abstract lines"] =\
            tag_soup.find("div", class_ = "gs_rs").text
        except:
            pass
        return info
        

class GoogleImagesSearch():
    def __init__(self, 
                 search_terms = "ultrafast lasers", 
                 debug_mode = False):
        """
        Search google images for the given keywords.
        
        Inputs:
        
        search_terms: a string with the search terms separated by spaces.
        
        debug_mode: boolean determining whether or not to raise any errors. if 
        False (Defalult) will return empty outputs.
        
        Output:
        
        results: 1D array of dictionaries with keys:
            'thumbnail link': link to the small image produced by google.
            'image url': link to the image's original website.
            'html': the raw html of the result tag.
        """
        self._debug_mode = debug_mode
        self._search_terms = search_terms
        
    def run(self):
        html = self.get_html()
        results = self.extract_results(html)
        return results
    
    def get_html(self):
        """
        Search google images for the given _search_terms using a 
        MechanizeBrowser().
        
        self._search_terms should be a string with the search 
        terms separated by spaces.
        if self._debug_mode is True will raise any errors, if 
        False (Defalult) will return an empty html string on error.
        
        produces:
        
        self._html: the raw html returned from the search.
        """
        html = ""
        try:
            address = "https://www.google.com/search?tbm=isch&hl=en"
            br = MechanizeBrowser()
            br.browse_to_webpage(address)
            br.select_form(index = 0)
            br.fill_form_item('q', self._search_terms)
            br.submit_form()    
            html = br.get_html()#;print br.list_links()
            br.close()
        except:
            if self._debug_mode:
                raise
        self._html = html
        return html
        
    def extract_results(self, html):
        """
        
        """
        soup = BeautifulSoup(html)
        # Should extract <a href="/url?q=
        results = soup.findAll('a', href=re.compile("^/url\?q="))
        
        proc_results = []
        for result in results:
            info = self.extract_result(result)
            if info["thumbnail url"]:
                proc_results.append(info)
                
        self._search_results = proc_results
        return proc_results
        
    def extract_result(self, result):
        info = {"thumbnail url": "",
                "image url": ""}
        
        imgtags = result.findAll('img')
        if len(imgtags) > 0:
            try:
                info["thumbnail url"] = imgtags[0]['src']
            except:
                pass
        try:
            s = result['href'][7:]
            info["image url"] = s[:s.find("&sa=")]
            # info["image url"] = result['href'][7:]
        except:
            pass
        return info
        
    def set_search_terms(self, search_terms = ""):
        if search_terms:
            self._search_terms = search_terms
            
    def set_debug_mode(self, debug_mode = True):
        self._debug_mode = debug_mode
        
    def download_thumbnails(self, results = [],
                            savein = ""):
        # save in a default directory if none given:
        if savein:
            folder = os.path.join(savein, "")#making sure it ends with / or \.
        else:
#            folder = os.path.join(os.getcwd(), "google_images_thumbnails")
            folder = os.path.join("google_images_thumbnails", "")
        # create folder if it doesn't exist:
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        br = MechanizeBrowser()
        k = 0
        for result in results:
            try:
                fname = folder + "thumbnail " + str(k)
                br.download_file(result["thumbnail url"], fname)
                if self._debug_mode:
                    print "saved at " + fname
                k += 1
            except:
                if self._debug_mode:
                    raise
                else:
                    pass


class WebsiteScrapper():
    def __init__(self,
                 address="",
                 debug_mode=False,
                 maxmemsize=0.5e9):
        """
        Visit the address to extract info.
        """
        self._address = address
        self._debug_mode = debug_mode
        self.maxmemsize = maxmemsize # in bytes

    def get_visible_text(self, separator=u" ", strip = True):
        html = self.get_html()
        soup = self.get_soup(html)
        [s.extract() for s in soup(['href', 'style', 'script',
                                    '[document]', 'head', 'title'])]
        return soup.getText(separator=separator, strip=strip)

    def get_meaningful_visible_text(self, min_words=50):
        """
        Weed out text candidates that have less words than min_words.
        @param min_words
        @:param maxmemsize: float. megabytes of memory.
        @return: string. Concatenated meaningful text separated by "\n".
        """
        visible_text = self.get_visible_text(separator="$separator$",
                                             strip=True)
        txt_list = visible_text.split("$separator$")

        meaningful_txt = []
        for txt in txt_list:
            nwords = len(txt.split())
            if nwords > min_words:
                meaningful_txt.append(txt)

        return "\n".join(meaningful_txt)

    def get_html(self):
        html = get_webpage_html(self._address, self._debug_mode);print sys.getsizeof(html)
        # make sure that the html is not too big:
        if sys.getsizeof(html) > self.maxmemsize:
            print "html size in memory is bigger than maximum allowed ({} GB)".format(self.maxmemsize/1e9)
            print "if needed increase maxmemsize in WebsiteScrapper"
            return ""
        return html

    def get_soup(self, html):
        return BeautifulSoup(html)
        # html = get_webpage_html(self._address, self._debug_mode);print sys.getsizeof(html)
        # # make sure that the file file is an string and not too big:
        # if sys.getsizeof(html)<maxmemsize*1e6:
        #     soup = self.soup = BeautifulSoup(html)
        # else:
        #     soup = BeautifulSoup("")
        # return soup


class PaperWebsiteScrapper():
    def __init__(self, 
                 address = "", 
                 debug_mode = False):
        """
        Visit the address to extract paper info (at least the abstract).
        """
        self._address = address
        self._debug_mode = debug_mode
        
    def run(self):
        """
        There's no general way to find the abstract on all journal pages 
        so here one tries to find it in likely ways (e.g., look for an 
        "abstract" header) but no step is assumed to work and things are 
        tried for a number of times before giving up and going to the 
        next step.
        """
        self.get_soup()
        self.look_for_abstract_headers()
        self.look_for_the_abstract()
        return self._abstract
        
    def get_soup(self):
        html = get_webpage_html(self._address, self._debug_mode)
        self._soup = BeautifulSoup(html)        
        
    def look_for_abstract_headers(self):
        """
        Find any tags beggining with h that contain "abstract" in 
        its text and whose lenght is not too long.
        
        if no tags begging with h are good, then try without the h.(REMOVED)
        """
        self._possible_abstract_header_tags =\
        self._soup.find_all(self.could_be_abstract_header)
        
    def look_for_the_abstract(self):
        """
        start with the first abstract header suspect, go to its parent, 
        and look for the abstract text. The text to be valid should be 
        within a minimum and maximum number of words. If this fails go 
        up to the parent of the parent and repeat. This can be repeated 
        for Ntries, after which go to the next abstract header suspect 
        on the list. If this doesn't work for all abstract suspects, 
        simply make a search in the whole soup with the text validation 
        mentioned above.
        """
        self._abstract = ""
        max_tries = 3
        n_try = 0
        header_index = 0
        headers = self._possible_abstract_header_tags[:]
        if headers:
            Nheaders = len(headers)
            stop = False
            header = headers[0]
        else:
            stop = True
        
        while not stop:
            parent = header.parent
            abs_tags = parent.find_all(self.is_abstract_tag)
            if abs_tags:
                self._abstract = abs_tags[0].text
                stop = True
            elif n_try + 1 < max_tries:
                n_try += 1
                header = parent
                continue
            elif header_index + 1 < Nheaders:
                header_index += 1
                header = headers[header_index]
                continue
            else:
                stop = True                            
                
        
    def could_be_abstract_header(self, tag):
        could_be = False
        if tag.name[0] == "h":
            if "abstract" in tag.text.lower():
                Nwords = len(tag.text.split(" "))
                if Nwords < 4:#10:
                    could_be = True            
        return could_be
        
    def could_be_non_h_abstract_header(self, tag):
        could_be = False
        if "abstract" in tag.text.lower():
            Nwords = len(tag.text.split(" "))
            if Nwords < 4:#10:
                could_be = True
        return could_be
        
    def is_abstract_tag(self, tag):
        t = tag.text
        t = t.replace(".", " ")
        t = t.replace("\n", " ")
        tl = t.split(" ")
        Nwords = len(tl)
        return (Nwords > 100) and (Nwords < 600)

####### >>>> Mechanisms

class MechanizeBrowser():
    """
    Mechanize can simulate the use of a browser (e.g., fill 
    and submit forms) but there's no documentation that i know 
    of so here is the result of a collection of recipes i 
    found for common actions such as: finding out the number 
    of links or forms, filling forms, clicking links, etc.
    """
    def __init__(self, timeout = 20):
        self._timeout = timeout
        br = mechanize.Browser()
        # Cookie Jar
        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)
        # Browser options
        br.set_handle_equiv(True)
        #br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
    
        # Follows refresh 0 but not hangs on refresh > 0
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), 
                              max_time=1)
        # Want debugging messages?
        #br.set_debug_http(True)
        #br.set_debug_redirects(True)
        #br.set_debug_responses(True)
                              
#        # Explicitly configure proxies (Browser will attempt to set good defaults).
#        # Note the userinfo ("joe:password@") and port number (":3128") are optional.
#        br.set_proxies({"http": "joe:password@myproxy.example.com:3128",
#                        "ftp": "proxy.example.com",
#                        })
#        # Add HTTP Basic/Digest auth username and password for HTTP proxy access.
#        # (equivalent to using "joe:password@..." form above)
#        br.add_proxy_password("joe", "password")
                              
        # User-Agent (this is cheating, ok?)
        br.addheaders =\
        [('User-agent', 
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        self._br = br
    
    def close(self):
        """
        not much to say, just close the mechanize
        object so that its memory allocation can 
        be freed.
        """
        self._br.close()

    def browse_to_webpage(self, address):
        self._br.open(address, timeout=self._timeout)

    def list_form_names(self):
        return [form.name for form in self._br.forms()]
        
    def select_form(self,
                    name = "",
                    index = 0):
        if name:
            self._br.select_form(name = name)
        else:
            self._br.select_form(nr = index)
            
    def list_form_controls(self):
        br = self._br
        controls = []
        for control in br.form.controls:
            n = control.name
            t = control.type
            v = br[n]
            descr =\
            "name: {}, type: {}, value: {}".format(n, t, v)
            controls.append(descr)
        return controls
    
    def fill_form_item(self, 
                       item_name = "",
                       value = "",
                       item_index = 0):
        if item_name:
            self._br.form[item_name] = value
        else:
            control = self._br.form.controls[item_index]
            control.value = value
        
    def submit_form(self):
        self._br.submit()
    
    def get_url(self):
        return self._br.geturl()
        
    def get_html(self):
        r = self._br.response()
        return r.read().decode("utf-8", "ignore")
#        return r.read()
        
    def back(self):
        self._br.back()
    
    def forward(self):
        self._br.forward()
        
    def list_links(self):
        d = {}
        num = 0
        for link in self._br.links():
            if hasattr(link, "text"):
                key = link.text
            else:
                key = num
            num += 1
            d[key] = link.url
        return d
        
    def click_on_link(self, text = "", index = 0):
        if text:
            link = self._br.find_link(text = text)
        else:
            link = list(self._br.links())[index]
        self._br.follow_link(link)
        
    def download_file(self, url, 
                      save_as = 'temp_br_download'):
        self._br.retrieve(fullurl = url,
                          filename = save_as)[0]
        

def get_webpage_html(address,
                     debug_mode = False):
    br = MechanizeBrowser()
    try:
        br.browse_to_webpage(address)
        html = br.get_html()
        br.close()
        return html
    except:
        br.close()
        if debug_mode:
            print "error in get_webpage_html"
            print "couldn't open: {}".format(address)
            raise
        else:
            return ""
            
def open_webpage_in_browser(address, 
                            debug_mode = False):
    """
    opens the website on an actual web browser.
    """
    import webbrowser
    try:
        webbrowser.open(address)
    except:
        if debug_mode:
            raise
            
def get_url_domain(url = "http://www.example.com/hi"):
#    from urlparse import urlparse
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return domain