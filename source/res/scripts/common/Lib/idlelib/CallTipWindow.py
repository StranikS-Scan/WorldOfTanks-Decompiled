# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/CallTipWindow.py
from Tkinter import *
HIDE_VIRTUAL_EVENT_NAME = '<<calltipwindow-hide>>'
HIDE_SEQUENCES = ('<Key-Escape>', '<FocusOut>')
CHECKHIDE_VIRTUAL_EVENT_NAME = '<<calltipwindow-checkhide>>'
CHECKHIDE_SEQUENCES = ('<KeyRelease>', '<ButtonRelease>')
CHECKHIDE_TIME = 100
MARK_RIGHT = 'calltipwindowregion_right'

class CallTip:

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = self.label = None
        self.parenline = self.parencol = None
        self.lastline = None
        self.hideid = self.checkhideid = None
        self.checkhide_after_id = None
        return

    def position_window(self):
        curline = int(self.widget.index('insert').split('.')[0])
        if curline == self.lastline:
            return
        self.lastline = curline
        self.widget.see('insert')
        if curline == self.parenline:
            box = self.widget.bbox('%d.%d' % (self.parenline, self.parencol))
        else:
            box = self.widget.bbox('%d.0' % curline)
        if not box:
            box = list(self.widget.bbox('insert'))
            box[0] = 0
            box[2] = 0
        x = box[0] + self.widget.winfo_rootx() + 2
        y = box[1] + box[3] + self.widget.winfo_rooty()
        self.tipwindow.wm_geometry('+%d+%d' % (x, y))

    def showtip(self, text, parenleft, parenright):
        self.text = text
        if self.tipwindow or not self.text:
            return
        self.widget.mark_set(MARK_RIGHT, parenright)
        self.parenline, self.parencol = map(int, self.widget.index(parenleft).split('.'))
        self.tipwindow = tw = Toplevel(self.widget)
        self.position_window()
        tw.wm_overrideredirect(1)
        try:
            tw.tk.call('::tk::unsupported::MacWindowStyle', 'style', tw._w, 'help', 'noActivates')
        except TclError:
            pass

        self.label = Label(tw, text=self.text, justify=LEFT, background='#ffffe0', relief=SOLID, borderwidth=1, font=self.widget['font'])
        self.label.pack()
        self.checkhideid = self.widget.bind(CHECKHIDE_VIRTUAL_EVENT_NAME, self.checkhide_event)
        for seq in CHECKHIDE_SEQUENCES:
            self.widget.event_add(CHECKHIDE_VIRTUAL_EVENT_NAME, seq)

        self.widget.after(CHECKHIDE_TIME, self.checkhide_event)
        self.hideid = self.widget.bind(HIDE_VIRTUAL_EVENT_NAME, self.hide_event)
        for seq in HIDE_SEQUENCES:
            self.widget.event_add(HIDE_VIRTUAL_EVENT_NAME, seq)

    def checkhide_event(self, event=None):
        if not self.tipwindow:
            return
        else:
            curline, curcol = map(int, self.widget.index('insert').split('.'))
            if curline < self.parenline or curline == self.parenline and curcol <= self.parencol or self.widget.compare('insert', '>', MARK_RIGHT):
                self.hidetip()
            else:
                self.position_window()
                if self.checkhide_after_id is not None:
                    self.widget.after_cancel(self.checkhide_after_id)
                self.checkhide_after_id = self.widget.after(CHECKHIDE_TIME, self.checkhide_event)
            return

    def hide_event(self, event):
        if not self.tipwindow:
            return
        self.hidetip()

    def hidetip(self):
        if not self.tipwindow:
            return
        else:
            for seq in CHECKHIDE_SEQUENCES:
                self.widget.event_delete(CHECKHIDE_VIRTUAL_EVENT_NAME, seq)

            self.widget.unbind(CHECKHIDE_VIRTUAL_EVENT_NAME, self.checkhideid)
            self.checkhideid = None
            for seq in HIDE_SEQUENCES:
                self.widget.event_delete(HIDE_VIRTUAL_EVENT_NAME, seq)

            self.widget.unbind(HIDE_VIRTUAL_EVENT_NAME, self.hideid)
            self.hideid = None
            self.label.destroy()
            self.label = None
            self.tipwindow.destroy()
            self.tipwindow = None
            self.widget.mark_unset(MARK_RIGHT)
            self.parenline = self.parencol = self.lastline = None
            return

    def is_active(self):
        return bool(self.tipwindow)


class container:

    def __init__(self):
        root = Tk()
        text = self.text = Text(root)
        text.pack(side=LEFT, fill=BOTH, expand=1)
        text.insert('insert', 'string.split')
        root.update()
        self.calltip = CallTip(text)
        text.event_add('<<calltip-show>>', '(')
        text.event_add('<<calltip-hide>>', ')')
        text.bind('<<calltip-show>>', self.calltip_show)
        text.bind('<<calltip-hide>>', self.calltip_hide)
        text.focus_set()
        root.mainloop()

    def calltip_show(self, event):
        self.calltip.showtip('Hello world')

    def calltip_hide(self, event):
        self.calltip.hidetip()


def main():
    c = container()


if __name__ == '__main__':
    main()
