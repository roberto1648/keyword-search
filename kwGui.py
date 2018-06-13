# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 17:12:33 2014

@author: Roberto
"""
import kivy
#kivy.require('1.8.0')

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivy.uix.image import AsyncImage
from kivy.app import App
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, ListProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock

from threading import Thread
import random
import os
import time

from kwSearch import kwSearch
import DatabaseFunctions as dbs
import kwImages
import SearchUtils

kwsearch_database = "kwSearchDB.json"
        

############ >>>>> Mechanisms 
    
######## gui mechanisms

class EntryField(BoxLayout):
    field_label = StringProperty()
    user_input = StringProperty()
    def __init__(self, **kwargs):
        super(EntryField, self).__init__(**kwargs)
        

class Lbl(Label):
    def __init__(self, **kwargs):
        super(Lbl, self).__init__(**kwargs)
    
class RedLbl(Label):
    label_text = StringProperty()
    def __init__(self, **kwargs):
        super(RedLbl, self).__init__(**kwargs)        

class BlackBtn(Button):
    def __init__(self, **kwargs):
        super(BlackBtn, self).__init__(**kwargs)
        
class Btn(Button):
    def __init__(self, **kwargs):
        super(Btn, self).__init__(**kwargs)
        
class DraggableWidget(RelativeLayout):
    def __init__(self,  **kwargs):
        super(DraggableWidget, self).__init__(**kwargs)
        self.selected = None

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.select()
            return True
        return super(DraggableWidget, self).on_touch_down(touch)

    def select(self):
        if not self.selected:
            self.ix = self.center_x
            self.iy = self.center_y
            self.selected = True
#            with self.canvas:
#                self.selected = Line(rectangle=(0,0,self.width,self.height), dash_offset=2)

    def on_touch_move(self, touch):
        (x,y) = self.parent.to_parent(touch.x, touch.y)
        if self.selected and self.parent.collide_point(x - self.width/2, y -self.height/2):
            self.translate(touch.x-self.ix,touch.y-self.iy)
            return True
        return super(DraggableWidget, self).on_touch_move(touch)

    def translate(self, x, y):
        self.center_x = self.ix = self.ix + x
        self.center_y = self.iy = self.iy + y

    def on_touch_up(self, touch):
        if self.selected:
            self.unselect()
            return True
        return super(DraggableWidget, self).on_touch_up(touch)

    def unselect(self):
        if self.selected:
            self.selected = False
#            self.canvas.remove(self.selected)
#            self.selected = None
        
########### >>>>>> Policies

class RootWindow(FloatLayout):
    def __init__(self, **kwargs):
        super(RootWindow, self).__init__(**kwargs)
        self.clear_widgets()
        self.history = []
        self.add_widget(MainForm())


class MainForm(BoxLayout):    
    def __init__(self, **kwargs):
        super(MainForm, self).__init__(**kwargs)
        
        keywords = []
        kwd_panel = self.ids.keyword_panel#;print kwd_panel.my_size
        kwd_panel.populate_panel(persistent_keywords = [],
                                 firsttier_keywords = keywords,
                                 secontier_keywords = [])
        dbs.create_ipc_directory()
        self._last_dbs_read = dbs.ipc_folder_last_modified_on()

        #initial focus on the text input:
        self.ids.search_box.ids.input_from_user.focus = True

        # initial buttons state:
        self.ids.search_box.reset()
        self.ids.navigation_controls.reset()

        Clock.schedule_interval(self.update, 1.0)
                                 
    def update(self, dt):
        # check if the database has been modified since last checked:
        tlast = self._last_dbs_read
        tmod = dbs.ipc_folder_last_modified_on()
        # tmod = dbs.database_last_modified_on()
        if tmod > tlast:
            self._last_dbs_read = tmod        
            running = dbs.check_running()#dbs.read_database("running")
            pause = dbs.check_pause()#dbs.read_database("pause")
            if running:
                if not pause:
                    self.ids.keyword_panel.update()
                    self.ids.search_box.update()
                    self.ids.images_panel.update()
                self.ids.navigation_controls.update()
            else:
                self.ids.search_box.reset()
                self.ids.navigation_controls.reset()

        if int(time.time())%4 == 0:
            if not dbs.check_pause():
                self.ids.images_panel.show_new_thumbnails()
        
        
class FloatingKeyword(DraggableWidget):
    def __init__(self, **kwargs):
        super(FloatingKeyword, self).__init__(**kwargs)
        
    def on_touch_down(self, touch):

        if self.collide_point(touch.x, touch.y):
            self.select()
            self.touch_down_y = touch.y
            # pause (i.e., prevent going into the following iteration of 
            # kwSearch) while moving the widget:
            self._already_paused = dbs.check_pause()#dbs.read_database("pause")
            if not self._already_paused:
                dbs.pause_on()
                # dbs.write_database("pause", True)
            return True
        return super(DraggableWidget, self).on_touch_down(touch)
        
    def on_touch_move(self, touch):
        (x,y) = self.parent.to_parent(touch.x, touch.y)
        if self.selected and self.parent.collide_point(x - self.width/2, y -self.height/2):
            self.translate(touch.x-self.ix,touch.y-self.iy)
            # make the trashcan appear when widget gets close to the sides,
            # dissapear when moving away from the edge.
            if self.parent.trashcan:
                if x < self.parent.width and x>0:
                    self.parent.remove_widget(self.parent.trashcan)
                    self.parent.trashcan = None
            else:
                if x - self.width < 0:
                    t = TrashCan(side='left')
                    self.parent.add_widget(t)
                    self.parent.trashcan = t
            return True

        return super(DraggableWidget, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.selected:
            self.unselect()
            parent = self.parent
            # erase widget if dropped in trashcan area:
            kw = self.text
            if parent.trashcan:
                parent.remove_widget(self.parent.trashcan)
                parent.trashcan = None
                parent.remove_widget(self)
                #add here code to blacklist corresponding keyword:
                self.new_removed_keyword(kw)
            else:
                touch_up_y = touch.y#self.parent.to_local(touch.x, touch.y)[1]
                self.promote_demote_keyword(kw, touch_up_y)
                
            # un-pause:
            if not self._already_paused:
                dbs.pause_off()
                
            return True

        return super(DraggableWidget, self).on_touch_up(touch)
        
    def new_removed_keyword(self, keyword = "bye keyword"):
        already_paused = dbs.check_pause()
        if not already_paused:
            dbs.pause_on()

        removed_kwds = dbs.read_iteration_list("removed keywords")
        notkeyword = '-"' + keyword + '"'
        keywords = dbs.read_iteration_list("keywords")

        if removed_kwds:
            if keyword not in removed_kwds:
                dbs.append_iteration_list("removed keywords", keyword)
                dbs.remove_duplicates_from_iteration_list("removed keywords")
                dbs.remove_from_iteration_list("keywords", keyword)
                if notkeyword not in keywords:
                    dbs.append_iteration_list("keywords", notkeyword)
        else:
            dbs.append_iteration_list("removed keywords", keyword)
            dbs.remove_from_iteration_list("keywords", keyword)
            if notkeyword not in keywords:
                dbs.append_iteration_list("keywords", notkeyword)

        dbs.remove_from_iteration_list("persistent keywords", keyword)
        dbs.remove_from_iteration_list("first-tier keywords", keyword)
        dbs.remove_from_iteration_list("second-tier keywords", keyword)

        if not already_paused:
            dbs.pause_off()
 
            
    def promote_demote_keyword(self, keyword = "keyword 1", 
                               touch_up_y = 100):
        """
        Move the keyword up or down the hierarchy according to where it was 
        dropped. Since the keywords are redrawn every time there's a change 
        in the database (see the update method in main form), it suffices to 
        see in which area it was dropped (i.e., permanent, first-tier, or 
        second-tier areas) and then where in relation to the other present 
        keywords within the area to insert the keyword in the appropriate 
        place (and delete it from the other two lists).
        """
        #TODO: review:
        # border should be y3, words drop over it become permanent.
        # demoted permanent words are just removed from the permanent list
        # (not banned)
        # only ban demoted first- and second-tier keywords.
        # thus just add an if checking whether the demoted keywords was
        # a permanent one.
        already_paused = dbs.check_pause()
        if not already_paused:
            dbs.pause_on()

        # iteration = dbs.read_database("iterations")[-1]

        keyword = keyword.replace("banned: ", "")

        # start by removing the keyword from the 3 lists:
        dbs.remove_from_iteration_list("persistent keywords", keyword)
        dbs.remove_from_iteration_list("first-tier keywords", keyword)
        dbs.remove_from_iteration_list("second-tier keywords", keyword)
        dbs.remove_from_iteration_list("second-tier keywords",
                                       "banned: " + keyword)
        dbs.remove_from_iteration_list("banned keywords", keyword)

        # now insert the keyword at the appropriate list:
        y1, y2, y3, y4 = self.parent._panel_border_heights
        touch_down_y = self.touch_down_y
        if touch_up_y > y3:
            dbs.insert_to_iteration_list("persistent keywords", keyword, 0)
        else:#ban kwd unless it was a permanent kwd
            if (touch_up_y<touch_down_y) and (touch_down_y<y2):
                dbs.insert_to_iteration_list("second-tier keywords",
                                             "banned: "+keyword, 5)
                dbs.append_iteration_list("banned keywords", keyword)
                dbs.remove_duplicates_from_iteration_list("banned keywords")
            else:
                dbs.insert_to_iteration_list("second-tier keywords", keyword)

        if not already_paused:
            dbs.pause_off()


class ThumbnailImage(AsyncImage):
    def __init__(self, thumbnail_url,
                 image_website_url,
                 **kwargs):
        super(ThumbnailImage, self).__init__(**kwargs)
        self.thumbnail_url = self.source = thumbnail_url
        self.image_website_url = image_website_url
        self.allow_stretch = True
        self.timeout = 1

    def on_touch_down(self, touch):

        if self.collide_point(touch.x, touch.y):
            SearchUtils.open_webpage_in_browser(self.image_website_url)
            self.open_popup()
            # self.scrape_image_url()
            # pause
            already_paused = dbs.check_pause()  # dbs.read_database("pause")
            if not already_paused:
                dbs.pause_on()
                # dbs.write_database("pause", True)
            return True
        return super(AsyncImage, self).on_touch_down(touch)

    def scrape_image_url(self, *args):
        """
        use kwImages to get the html from the image webpage, take relevant text and
        add it to the database for consideration in kwSearch.
        might have to wait one second or so, since the same website is being opened
        in a browser.
        @return:
        """
        kwImages.add_url_text_to_database(self.image_website_url)
        dbs.pause_off()

    def pause_off(self, *args):
        dbs.pause_off()

    def open_popup(self):
        content = BoxLayout(orientation="vertical")
        content.add_widget(Label(text="Was the website info useful?"))
        no = Button(text="no")
        yes = Button(text="yes")
        buttons = BoxLayout()
        buttons.add_widget(no)
        buttons.add_widget(yes)
        content.add_widget(buttons)
        popup = Popup(title='Welcome back',
                      content=content,
                      size_hint=(0.5, 0.5),
                      auto_dismiss=False)
        yes.bind(on_press=popup.dismiss)
        yes.bind(on_press=self.scrape_image_url)
        no.bind(on_press=popup.dismiss)
        no.bind(on_press=self.pause_off)
        popup.open()

        
class TrashCan(BoxLayout):
    img_size = 50
    def __init__(self, side = "right", **kwargs):
        super(TrashCan, self).__init__(**kwargs)
        self.opacity = 0.5
        if side == "top":
            self.size_hint = 1, None
            self.height = self.img_size
            self.pos_hint = {"x":0, "y":1}
        elif side == "bottom":
            self.size_hint = 1, None
            self.height = self.img_size
            self.pos_hint = {"x":0, "y":0}
        elif side == "right":
            self.orientation = "vertical"
            self.size_hint = None, 1
            self.width = self.img_size
            self.pos_hint = {"x":1, "y":0}
        elif side == "left":
            self.orientation = "vertical"
            self.size_hint = None, 1
            self.width = self.img_size
            self.pos_hint = {"x":0, "y":0}
        b1 = BoxLayout()
        img = Image(source = "trashcan.png")
        img.size = self.img_size, self.img_size
        img.size_hint = None, None
        b2 = BoxLayout()
        self.add_widget(b1)
        self.add_widget(img)
        self.add_widget(b2)

        
class KeywordPanel(RelativeLayout):
    """
    A container for the displayed keywords which can be moved 
    around by the user to force a keyword to be relatively more
    or less important than others, or to remove a keyword from 
    the panel to put it on a blacklist for the search.
    
    Needed to implement here on_size() and on_pos() because 
    relative and float layouts are special in not repositioning 
    their children unless pos_hint's are given for them (but when 
    a pos_hint is given, then the child won't respond to dragging). 
    This still wouldn't be a problem in mobile devices but for the 
    fact that even there there's one resizing (and posibly 
    repositioning) when the widgets are rendered on the screen, 
    at which point the size goes from whatever was written here 
    (or the default) to the stretching/compression required by 
    the parent layout.
    """
    def __init__(self, **kwargs):
        super(KeywordPanel, self).__init__(**kwargs)
        self.trashcan = None
        self._max_keywords = 10
        
    def update(self):
        pers = dbs.read_iteration_list("persistent keywords")
        firsttier = dbs.read_iteration_list("first-tier keywords")
        secondtier = dbs.read_iteration_list("second-tier keywords")

        self.populate_panel(pers, firsttier, secondtier)
        
    def add_keyword_widget(self, keyword = "keyword",
                           pos = (0.5, 0.5)):
        kw = FloatingKeyword()
        kw.text = keyword
#        kw.pos = pos
        kw.x = pos[0]#center_x = pos[0]
        kw.y = pos[1]
        self.add_widget(kw)
        
        w, h = self.size
        kw.proportional_x = kw.center_x/w#;print kw.prop_x
        kw.proportional_y = kw.center_y/h
        return kw
        
    def remove_all_children(self):
        self.clear_widgets()
    
    def populate_panel(self,
                       persistent_keywords = [],
                       firsttier_keywords = [],
                       secontier_keywords = []):
        self.remove_all_children()
        y1 = 0.95*self.height
        y2 = self.place_keywords(persistent_keywords, y1, (0,1,0,1))
        y3 = self.place_keywords(firsttier_keywords, y2, (1,1,1,1))
        y4 = self.place_keywords(secontier_keywords, y3, (1,1,1,0.5))
        self.old_size = self.size[:]
        
        # transform to absolute (window) coordinates and store in attribute:
        panel_heights = []
        for y in [y1, y2, y3, y4]:
            panel_heights.append( self.to_window(0, y)[1] )
        self._panel_border_heights = panel_heights
        
    def place_keywords(self, keywords = [],
                       upper_y = 100,
                       font_color = (1,0,0,1)):
        """
        """
        keywords_list = keywords[:]
#        x0, y0 = lower_left
#        x1, y1 = upper_right
        W, H = self.size
#        x0 *= W
#        x1 *= W
#        y0 *= H
#        y1 *= H
        x = 0#0.5*W
        y = upper_y
#        if keywords_list:
#            Nkw = float(len(keywords_list))
#        else:
#            Nkw = 1.
#        dy = (y1-y0)/Nkw
        for kw in keywords_list:
            kw_wid = self.add_keyword_widget(kw, (x,y))
            kw_wid.color = font_color
            # the following doesn't work for some reason (size=0,0)
#            w, h = kw_wid.size#; print kw_wid.pos, kw_wid.size
#            if y + h > y1:
#                kw_wid.pos[1] = y1 - h
#            elif y < y0:
#                kw_wid.pos[1] = y0
#            if x - w/2. < x0:
#                kw_wid.pos[0] = x0 + w/2.
#            elif x + w/2. > x1:
#                kw_wid.pos[0] = x1 - w/2.
            
            #next x,y:
            x = 0.3*(W-kw_wid.right)*random.random()#0
            # x = ( 0.1 + 0.6*random.random() )*W#x0 + (x1 - x0)*random.random()
            #y -= dy
            y -= kw_wid.font_size
        return y
    
    def on_size(self, *args):
        self.reposition_children()
        
    def on_pos(self, *args):
        self.reposition_children()
            
    def reposition_children(self):
        children = self.children#self.curr_kw_wdgts
        if hasattr(self, "old_size"):
            old_w, old_h = self.old_size[:]
        else:
            old_w, old_h = self.size[:]
        new_w, new_h = self.size[:]
        for kw in children:
            if old_w > 0:
                r = kw.center_x/float(old_w)#;print r
                if r <= 1 :#in strange cases sizes go over 1, ignore.
                    kw.proportional_x = r
            if old_h > 0:
                r = kw.center_y/float(old_h)
                if r <= 1:
                    kw.proportional_y = r
            kw.center_x = float(new_w)*kw.proportional_x
            kw.center_y = float(new_h)*kw.proportional_y
        self.old_size = self.size[:]


class ImagesPanel(BoxLayout):
    def __init__(self, **kwargs):
        super(ImagesPanel, self).__init__(**kwargs)

    def populate_panel(self):
        try:
            grid = GridLayout(rows=2)
            thumbnails = self.get_current_thumbnails_info()
            for k in range(4):
                thumbnail = random.choice(thumbnails)
                thb_url = thumbnail["thumbnail url"]
                img_url = thumbnail["image url"]
                img = ThumbnailImage(thb_url, img_url)
                grid.add_widget(img)
            self.clear_widgets()
            self.add_widget(grid)
        except:
            pass


    def update(self):
        kwi = kwImages.Search()
        results = kwi.run()
        if results:
            kwi.save_results(results)
            self.populate_panel()

    def show_new_thumbnails(self):
        self.populate_panel()

    def get_current_thumbnails_info(self):
        thumbnails = []
        # if "iterations" in dbs.list_database_entries():
        try:
            iteration = dbs.read_database("iterations")[-1]
            thumbnails = iteration["thumbnails"]["thumbnails info"]
        except:
            pass
        return thumbnails

    def on_size(self, *args):
        self.populate_panel()

    def on_pos(self, *args):
        self.populate_panel()

    # def thumbnail_pressed(self, touch):
    #     print touch.x, touch.y


        
class SearchBox(BoxLayout):
    def __init__(self, **kwargs):
        super(SearchBox, self).__init__(**kwargs)
        
    def update(self):
        kwds_list = dbs.read_iteration_list("keywords")
        kwds = " ".join(kwds_list)
        self.ids.input_from_user.text = kwds

        # iterations = dbs.read_database("iterations")
        # if iterations:
        #     iteration = iterations[-1]
        #     kwds = " ".join( iteration["keywords"] )
        #     self.ids.input_from_user.text = kwds
        
    def reset(self):
        btn = self.ids.search_button
        btn.disabled = False
        btn.text = "Search"
        
    def button_pressed(self):
        btn = self.ids.search_button
        txt_inp = self.ids.input_from_user
        already_paused = dbs.check_pause()
        if not already_paused:
            dbs.pause_on()
        if btn.text == "Search":
            kw_panel = self.parent.ids.keyword_panel
            keywords = self.ids.input_from_user.text
            kw_list = self.keywords_to_list(keywords)
            kw_panel.populate_panel(kw_list)
            # self.old_text = txt_inp.text
            btn.text = "Reset"
            btn.disabled = True
            # start the kw search:
            t = Thread(target=kwSearch(kw_list).run, args=[])
            t.start()
        if btn.text == "Reset":
            for word in txt_inp.text.split(" "):
                keywords = dbs.read_iteration_list("keywords")
                if word not in keywords:
                    # new_word = "new:" + word
                    # txt_inp.text = txt_inp.text.replace(word, new_word)
                    if word.startswith("-"):
                        dbs.append_iteration_list("removed keywords", word)
                    else:
                        if word not in dbs.read_iteration_list("persistent keywords"):
                            dbs.append_iteration_list("persistent keywords", word)
                    btn.disabled = True
            # self.old_text = txt_inp.text
        if not already_paused:
            dbs.pause_off()
            
    def on_touch_down(self, touch):
        if self.parent:
            kw_input = self.ids.input_from_user#search_keywords
            if kw_input.collide_point(touch.x, touch.y):
                kw_input.on_touch_down(touch)#otherwise input doesn't work..
                self.ids.search_button.disabled = False
                return True
        return super(SearchBox, self).on_touch_down(touch)
        
    def keywords_to_list(self, keywords):
        """
        Splits the given keywords into a list. Multiword keywords must be 
        enclosed in quotes "".
        """
        kwlist = []
        compound_kw = ""
        for w in keywords.strip().split():
            kw = w.strip()            
            if kw.startswith('"') and kw.endswith('"'):
                kwlist.append(kw)
            elif kw.startswith('"'):
                compound_kw = kw
            elif kw.endswith('"'):
                compound_kw += " " + kw
                kwlist.append(compound_kw)
                compound_kw = ""
            elif compound_kw:
                compound_kw += " " + kw
            else:
                kwlist.append(kw)
        return kwlist

        
class NavigationControls(BoxLayout):
    def __init__(self, **kwargs):
        super(NavigationControls, self).__init__(**kwargs)
        
    def toggle_stop(self):
        stop = not dbs.check_stop()#dbs.read_database("stop")
        # dbs.write_database("stop", stop)
        if stop:
            dbs.stop()
        else:
            dbs.unstop()
        btn = self.ids.stop_button
        if stop:
            btn.background_color = (0,1,0,1)
        else:
            btn.background_color = (1,0,0,1)
            
    def toggle_pause(self):
        pause = not dbs.check_pause()#dbs.read_database("pause")
        if pause:
            dbs.pause_on()
        else:
            dbs.pause_off()
        # dbs.write_database("pause", pause)
        btn = self.ids.pause_button
        if pause:
            btn.background_color = (0,1,0,1)
        else:
            btn.background_color = (1,0,0,1)
            
    def reset(self):
        stp_btn = self.ids.stop_button
        stp_btn.background_color = (1,0,0,1)
        stp_btn.disabled = True

        pause_btn = self.ids.pause_button
        pause_btn.background_color = (1,0,0,1)
        pause_btn.disabled = True
   
    def update(self):
        pause_btn = self.ids.pause_button
        pause_btn.disabled = False
        pause = dbs.check_pause()
        if pause:
            pause_btn.background_color = (0,1,0,1)
        else:
            pause_btn.background_color = (1,0,0,1)

        stp_btn = self.ids.stop_button
        stp_btn.disabled = False

        
############ app
class KwGUI(App):
    def build(self):
        return RootWindow()
        
    
if __name__=="__main__":
    KwGUI().run()
