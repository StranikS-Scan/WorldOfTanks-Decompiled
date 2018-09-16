# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib-tk/Tkdnd.py
import Tkinter

def dnd_start(source, event):
    h = DndHandler(source, event)
    if h.root:
        return h
    else:
        return None
        return None


class DndHandler:
    root = None

    def __init__(self, source, event):
        if event.num > 5:
            return
        else:
            root = event.widget._root()
            try:
                root.__dnd
                return
            except AttributeError:
                root.__dnd = self
                self.root = root

            self.source = source
            self.target = None
            self.initial_button = button = event.num
            self.initial_widget = widget = event.widget
            self.release_pattern = '<B%d-ButtonRelease-%d>' % (button, button)
            self.save_cursor = widget['cursor'] or ''
            widget.bind(self.release_pattern, self.on_release)
            widget.bind('<Motion>', self.on_motion)
            widget['cursor'] = 'hand2'
            return

    def __del__(self):
        root = self.root
        self.root = None
        if root:
            try:
                del root.__dnd
            except AttributeError:
                pass

        return

    def on_motion(self, event):
        x, y = event.x_root, event.y_root
        target_widget = self.initial_widget.winfo_containing(x, y)
        source = self.source
        new_target = None
        while target_widget:
            try:
                attr = target_widget.dnd_accept
            except AttributeError:
                pass
            else:
                new_target = attr(source, event)
                if new_target:
                    break

            target_widget = target_widget.master

        old_target = self.target
        if old_target is new_target:
            if old_target:
                old_target.dnd_motion(source, event)
        else:
            if old_target:
                self.target = None
                old_target.dnd_leave(source, event)
            if new_target:
                new_target.dnd_enter(source, event)
                self.target = new_target
        return

    def on_release(self, event):
        self.finish(event, 1)

    def cancel(self, event=None):
        self.finish(event, 0)

    def finish(self, event, commit=0):
        target = self.target
        source = self.source
        widget = self.initial_widget
        root = self.root
        try:
            del root.__dnd
            self.initial_widget.unbind(self.release_pattern)
            self.initial_widget.unbind('<Motion>')
            widget['cursor'] = self.save_cursor
            self.target = self.source = self.initial_widget = self.root = None
            if target:
                if commit:
                    target.dnd_commit(source, event)
                else:
                    target.dnd_leave(source, event)
        finally:
            source.dnd_end(target, event)

        return


class Icon:

    def __init__(self, name):
        self.name = name
        self.canvas = self.label = self.id = None
        return

    def attach(self, canvas, x=10, y=10):
        if canvas is self.canvas:
            self.canvas.coords(self.id, x, y)
            return
        if self.canvas:
            self.detach()
        if not canvas:
            return
        label = Tkinter.Label(canvas, text=self.name, borderwidth=2, relief='raised')
        id = canvas.create_window(x, y, window=label, anchor='nw')
        self.canvas = canvas
        self.label = label
        self.id = id
        label.bind('<ButtonPress>', self.press)

    def detach(self):
        canvas = self.canvas
        if not canvas:
            return
        else:
            id = self.id
            label = self.label
            self.canvas = self.label = self.id = None
            canvas.delete(id)
            label.destroy()
            return

    def press(self, event):
        if dnd_start(self, event):
            self.x_off = event.x
            self.y_off = event.y
            self.x_orig, self.y_orig = self.canvas.coords(self.id)

    def move(self, event):
        x, y = self.where(self.canvas, event)
        self.canvas.coords(self.id, x, y)

    def putback(self):
        self.canvas.coords(self.id, self.x_orig, self.y_orig)

    def where(self, canvas, event):
        x_org = canvas.winfo_rootx()
        y_org = canvas.winfo_rooty()
        x = event.x_root - x_org
        y = event.y_root - y_org
        return (x - self.x_off, y - self.y_off)

    def dnd_end(self, target, event):
        pass


class Tester:

    def __init__(self, root):
        self.top = Tkinter.Toplevel(root)
        self.canvas = Tkinter.Canvas(self.top, width=100, height=100)
        self.canvas.pack(fill='both', expand=1)
        self.canvas.dnd_accept = self.dnd_accept

    def dnd_accept(self, source, event):
        return self

    def dnd_enter(self, source, event):
        self.canvas.focus_set()
        x, y = source.where(self.canvas, event)
        x1, y1, x2, y2 = source.canvas.bbox(source.id)
        dx, dy = x2 - x1, y2 - y1
        self.dndid = self.canvas.create_rectangle(x, y, x + dx, y + dy)
        self.dnd_motion(source, event)

    def dnd_motion(self, source, event):
        x, y = source.where(self.canvas, event)
        x1, y1, x2, y2 = self.canvas.bbox(self.dndid)
        self.canvas.move(self.dndid, x - x1, y - y1)

    def dnd_leave(self, source, event):
        self.top.focus_set()
        self.canvas.delete(self.dndid)
        self.dndid = None
        return

    def dnd_commit(self, source, event):
        self.dnd_leave(source, event)
        x, y = source.where(self.canvas, event)
        source.attach(self.canvas, x, y)


def test():
    root = Tkinter.Tk()
    root.geometry('+1+1')
    Tkinter.Button(command=root.quit, text='Quit').pack()
    t1 = Tester(root)
    t1.top.geometry('+1+60')
    t2 = Tester(root)
    t2.top.geometry('+120+60')
    t3 = Tester(root)
    t3.top.geometry('+240+60')
    i1 = Icon('ICON1')
    i2 = Icon('ICON2')
    i3 = Icon('ICON3')
    i1.attach(t1.canvas)
    i2.attach(t2.canvas)
    i3.attach(t3.canvas)
    root.mainloop()


if __name__ == '__main__':
    test()
