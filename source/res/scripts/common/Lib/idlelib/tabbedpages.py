# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/tabbedpages.py
from Tkinter import *

class InvalidNameError(Exception):
    pass


class AlreadyExistsError(Exception):
    pass


class TabSet(Frame):

    def __init__(self, page_set, select_command, tabs=None, n_rows=1, max_tabs_per_row=5, expand_tabs=False, **kw):
        Frame.__init__(self, page_set, **kw)
        self.select_command = select_command
        self.n_rows = n_rows
        self.max_tabs_per_row = max_tabs_per_row
        self.expand_tabs = expand_tabs
        self.page_set = page_set
        self._tabs = {}
        self._tab2row = {}
        if tabs:
            self._tab_names = list(tabs)
        else:
            self._tab_names = []
        self._selected_tab = None
        self._tab_rows = []
        self.padding_frame = Frame(self, height=2, borderwidth=0, relief=FLAT, background=self.cget('background'))
        self.padding_frame.pack(side=TOP, fill=X, expand=False)
        self._arrange_tabs()
        return

    def add_tab(self, tab_name):
        if not tab_name:
            raise InvalidNameError("Invalid Tab name: '%s'" % tab_name)
        if tab_name in self._tab_names:
            raise AlreadyExistsError("Tab named '%s' already exists" % tab_name)
        self._tab_names.append(tab_name)
        self._arrange_tabs()

    def remove_tab(self, tab_name):
        if tab_name not in self._tab_names:
            raise KeyError("No such Tab: '%s" % page_name)
        self._tab_names.remove(tab_name)
        self._arrange_tabs()

    def set_selected_tab(self, tab_name):
        if tab_name == self._selected_tab:
            return
        else:
            if tab_name is not None and tab_name not in self._tabs:
                raise KeyError("No such Tab: '%s" % page_name)
            if self._selected_tab is not None:
                self._tabs[self._selected_tab].set_normal()
            self._selected_tab = None
            if tab_name is not None:
                self._selected_tab = tab_name
                tab = self._tabs[tab_name]
                tab.set_selected()
                tab_row = self._tab2row[tab]
                tab_row.pack_forget()
                tab_row.pack(side=TOP, fill=X, expand=0)
            return

    def _add_tab_row(self, tab_names, expand_tabs):
        if not tab_names:
            return
        tab_row = Frame(self)
        tab_row.pack(side=TOP, fill=X, expand=0)
        self._tab_rows.append(tab_row)
        for tab_name in tab_names:
            tab = TabSet.TabButton(tab_name, self.select_command, tab_row, self)
            if expand_tabs:
                tab.pack(side=LEFT, fill=X, expand=True)
            else:
                tab.pack(side=LEFT)
            self._tabs[tab_name] = tab
            self._tab2row[tab] = tab_row

        tab.is_last_in_row = True

    def _reset_tab_rows(self):
        while self._tab_rows:
            tab_row = self._tab_rows.pop()
            tab_row.destroy()

        self._tab2row = {}

    def _arrange_tabs(self):
        for tab_name in self._tabs.keys():
            self._tabs.pop(tab_name).destroy()

        self._reset_tab_rows()
        if not self._tab_names:
            return
        else:
            if self.n_rows is not None and self.n_rows > 0:
                n_rows = self.n_rows
            else:
                n_rows = (len(self._tab_names) - 1) // self.max_tabs_per_row + 1
            expand_tabs = self.expand_tabs or n_rows > 1
            i = 0
            for row_index in xrange(n_rows):
                n_tabs = (len(self._tab_names) - i - 1) // (n_rows - row_index) + 1
                tab_names = self._tab_names[i:i + n_tabs]
                i += n_tabs
                self._add_tab_row(tab_names, expand_tabs)

            selected = self._selected_tab
            self.set_selected_tab(None)
            if selected in self._tab_names:
                self.set_selected_tab(selected)
            return

    class TabButton(Frame):
        bw = 2

        def __init__(self, name, select_command, tab_row, tab_set):
            Frame.__init__(self, tab_row, borderwidth=self.bw, relief=RAISED)
            self.name = name
            self.select_command = select_command
            self.tab_set = tab_set
            self.is_last_in_row = False
            self.button = Radiobutton(self, text=name, command=self._select_event, padx=5, pady=1, takefocus=FALSE, indicatoron=FALSE, highlightthickness=0, selectcolor='', borderwidth=0)
            self.button.pack(side=LEFT, fill=X, expand=True)
            self._init_masks()
            self.set_normal()

        def _select_event(self, *args):
            self.select_command(self.name)

        def set_selected(self):
            self._place_masks(selected=True)

        def set_normal(self):
            self._place_masks(selected=False)

        def _init_masks(self):
            page_set = self.tab_set.page_set
            background = page_set.pages_frame.cget('background')
            self.mask = Frame(page_set, borderwidth=0, relief=FLAT, background=background)
            self.mskl = Frame(page_set, borderwidth=0, relief=FLAT, background=background)
            self.mskl.ml = Frame(self.mskl, borderwidth=self.bw, relief=RAISED)
            self.mskl.ml.place(x=0, y=-self.bw, width=2 * self.bw, height=self.bw * 4)
            self.mskr = Frame(page_set, borderwidth=0, relief=FLAT, background=background)
            self.mskr.mr = Frame(self.mskr, borderwidth=self.bw, relief=RAISED)

        def _place_masks(self, selected=False):
            height = self.bw
            if selected:
                height += self.bw
            self.mask.place(in_=self, relx=0.0, x=0, rely=1.0, y=0, relwidth=1.0, width=0, relheight=0.0, height=height)
            self.mskl.place(in_=self, relx=0.0, x=-self.bw, rely=1.0, y=0, relwidth=0.0, width=self.bw, relheight=0.0, height=height)
            page_set = self.tab_set.page_set
            if selected and (not self.is_last_in_row or self.winfo_rootx() + self.winfo_width() < page_set.winfo_rootx() + page_set.winfo_width()):
                height -= self.bw
            self.mskr.place(in_=self, relx=1.0, x=0, rely=1.0, y=0, relwidth=0.0, width=self.bw, relheight=0.0, height=height)
            self.mskr.mr.place(x=-self.bw, y=-self.bw, width=2 * self.bw, height=height + self.bw * 2)
            self.tab_set.lower()


class TabbedPageSet(Frame):

    class Page(object):
        uses_grid = False

        def __init__(self, page_set):
            self.frame = Frame(page_set, borderwidth=2, relief=RAISED)

        def _show(self):
            raise NotImplementedError

        def _hide(self):
            raise NotImplementedError

    class PageRemove(Page):
        uses_grid = True

        def _show(self):
            self.frame.grid(row=0, column=0, sticky=NSEW)

        def _hide(self):
            self.frame.grid_remove()

    class PageLift(Page):
        uses_grid = True

        def __init__(self, page_set):
            super(TabbedPageSet.PageLift, self).__init__(page_set)
            self.frame.grid(row=0, column=0, sticky=NSEW)
            self.frame.lower()

        def _show(self):
            self.frame.lift()

        def _hide(self):
            self.frame.lower()

    class PagePackForget(Page):

        def _show(self):
            self.frame.pack(fill=BOTH, expand=True)

        def _hide(self):
            self.frame.pack_forget()

    def __init__(self, parent, page_names=None, page_class=PageLift, n_rows=1, max_tabs_per_row=5, expand_tabs=False, **kw):
        Frame.__init__(self, parent, **kw)
        self.page_class = page_class
        self.pages = {}
        self._pages_order = []
        self._current_page = None
        self._default_page = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.pages_frame = Frame(self)
        self.pages_frame.grid(row=1, column=0, sticky=NSEW)
        if self.page_class.uses_grid:
            self.pages_frame.columnconfigure(0, weight=1)
            self.pages_frame.rowconfigure(0, weight=1)
        self._tab_set = TabSet(self, self.change_page, n_rows=n_rows, max_tabs_per_row=max_tabs_per_row, expand_tabs=expand_tabs)
        if page_names:
            for name in page_names:
                self.add_page(name)

        self._tab_set.grid(row=0, column=0, sticky=NSEW)
        self.change_page(self._default_page)
        return

    def add_page(self, page_name):
        if not page_name:
            raise InvalidNameError("Invalid TabPage name: '%s'" % page_name)
        if page_name in self.pages:
            raise AlreadyExistsError("TabPage named '%s' already exists" % page_name)
        self.pages[page_name] = self.page_class(self.pages_frame)
        self._pages_order.append(page_name)
        self._tab_set.add_tab(page_name)
        if len(self.pages) == 1:
            self._default_page = page_name
            self.change_page(page_name)

    def remove_page(self, page_name):
        if page_name not in self.pages:
            raise KeyError("No such TabPage: '%s" % page_name)
        self._pages_order.remove(page_name)
        if len(self._pages_order) > 0:
            if page_name == self._default_page:
                self._default_page = self._pages_order[0]
        else:
            self._default_page = None
        if page_name == self._current_page:
            self.change_page(self._default_page)
        self._tab_set.remove_tab(page_name)
        page = self.pages.pop(page_name)
        page.frame.destroy()
        return

    def change_page(self, page_name):
        if self._current_page == page_name:
            return
        else:
            if page_name is not None and page_name not in self.pages:
                raise KeyError("No such TabPage: '%s'" % page_name)
            if self._current_page is not None:
                self.pages[self._current_page]._hide()
            self._current_page = None
            if page_name is not None:
                self._current_page = page_name
                self.pages[page_name]._show()
            self._tab_set.set_selected_tab(page_name)
            return


if __name__ == '__main__':
    root = Tk()
    tabPage = TabbedPageSet(root, page_names=['Foobar', 'Baz'], n_rows=0, expand_tabs=False)
    tabPage.pack(side=TOP, expand=TRUE, fill=BOTH)
    Label(tabPage.pages['Foobar'].frame, text='Foo', pady=20).pack()
    Label(tabPage.pages['Foobar'].frame, text='Bar', pady=20).pack()
    Label(tabPage.pages['Baz'].frame, text='Baz').pack()
    entryPgName = Entry(root)
    buttonAdd = Button(root, text='Add Page', command=lambda : tabPage.add_page(entryPgName.get()))
    buttonRemove = Button(root, text='Remove Page', command=lambda : tabPage.remove_page(entryPgName.get()))
    labelPgName = Label(root, text='name of page to add/remove:')
    buttonAdd.pack(padx=5, pady=5)
    buttonRemove.pack(padx=5, pady=5)
    labelPgName.pack(padx=5)
    entryPgName.pack(padx=5)
    root.mainloop()
