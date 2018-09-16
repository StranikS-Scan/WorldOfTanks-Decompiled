# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/curses/textpad.py
import curses
import curses.ascii

def rectangle(win, uly, ulx, lry, lrx):
    win.vline(uly + 1, ulx, curses.ACS_VLINE, lry - uly - 1)
    win.hline(uly, ulx + 1, curses.ACS_HLINE, lrx - ulx - 1)
    win.hline(lry, ulx + 1, curses.ACS_HLINE, lrx - ulx - 1)
    win.vline(uly + 1, lrx, curses.ACS_VLINE, lry - uly - 1)
    win.addch(uly, ulx, curses.ACS_ULCORNER)
    win.addch(uly, lrx, curses.ACS_URCORNER)
    win.addch(lry, lrx, curses.ACS_LRCORNER)
    win.addch(lry, ulx, curses.ACS_LLCORNER)


class Textbox:

    def __init__(self, win, insert_mode=False):
        self.win = win
        self.insert_mode = insert_mode
        self.maxy, self.maxx = win.getmaxyx()
        self.maxy = self.maxy - 1
        self.maxx = self.maxx - 1
        self.stripspaces = 1
        self.lastcmd = None
        win.keypad(1)
        return

    def _end_of_line(self, y):
        last = self.maxx
        while True:
            if curses.ascii.ascii(self.win.inch(y, last)) != curses.ascii.SP:
                last = min(self.maxx, last + 1)
                break
            elif last == 0:
                break
            last = last - 1

        return last

    def _insert_printable_char(self, ch):
        y, x = self.win.getyx()
        if y < self.maxy or x < self.maxx:
            if self.insert_mode:
                oldch = self.win.inch()
            try:
                self.win.addch(ch)
            except curses.error:
                pass

            if self.insert_mode:
                backy, backx = self.win.getyx()
                if curses.ascii.isprint(oldch):
                    self._insert_printable_char(oldch)
                    self.win.move(backy, backx)

    def do_command(self, ch):
        y, x = self.win.getyx()
        self.lastcmd = ch
        if curses.ascii.isprint(ch):
            if y < self.maxy or x < self.maxx:
                self._insert_printable_char(ch)
        elif ch == curses.ascii.SOH:
            self.win.move(y, 0)
        elif ch in (curses.ascii.STX,
         curses.KEY_LEFT,
         curses.ascii.BS,
         curses.KEY_BACKSPACE):
            if x > 0:
                self.win.move(y, x - 1)
            elif y == 0:
                pass
            elif self.stripspaces:
                self.win.move(y - 1, self._end_of_line(y - 1))
            else:
                self.win.move(y - 1, self.maxx)
            if ch in (curses.ascii.BS, curses.KEY_BACKSPACE):
                self.win.delch()
        elif ch == curses.ascii.EOT:
            self.win.delch()
        elif ch == curses.ascii.ENQ:
            if self.stripspaces:
                self.win.move(y, self._end_of_line(y))
            else:
                self.win.move(y, self.maxx)
        elif ch in (curses.ascii.ACK, curses.KEY_RIGHT):
            if x < self.maxx:
                self.win.move(y, x + 1)
            elif y == self.maxy:
                pass
            else:
                self.win.move(y + 1, 0)
        else:
            if ch == curses.ascii.BEL:
                return 0
            if ch == curses.ascii.NL:
                if self.maxy == 0:
                    return 0
                if y < self.maxy:
                    self.win.move(y + 1, 0)
            elif ch == curses.ascii.VT:
                if x == 0 and self._end_of_line(y) == 0:
                    self.win.deleteln()
                else:
                    self.win.move(y, x)
                    self.win.clrtoeol()
            elif ch == curses.ascii.FF:
                self.win.refresh()
            elif ch in (curses.ascii.SO, curses.KEY_DOWN):
                if y < self.maxy:
                    self.win.move(y + 1, x)
                    if x > self._end_of_line(y + 1):
                        self.win.move(y + 1, self._end_of_line(y + 1))
            elif ch == curses.ascii.SI:
                self.win.insertln()
            elif ch in (curses.ascii.DLE, curses.KEY_UP):
                if y > 0:
                    self.win.move(y - 1, x)
                    if x > self._end_of_line(y - 1):
                        self.win.move(y - 1, self._end_of_line(y - 1))

    def gather(self):
        result = ''
        for y in range(self.maxy + 1):
            self.win.move(y, 0)
            stop = self._end_of_line(y)
            if stop == 0 and self.stripspaces:
                continue
            for x in range(self.maxx + 1):
                if self.stripspaces and x > stop:
                    break
                result = result + chr(curses.ascii.ascii(self.win.inch(y, x)))

            if self.maxy > 0:
                result = result + '\n'

        return result

    def edit(self, validate=None):
        while 1:
            ch = self.win.getch()
            if validate:
                ch = validate(ch)
            if not ch:
                continue
            if not self.do_command(ch):
                break
            self.win.refresh()

        return self.gather()


if __name__ == '__main__':

    def test_editbox(stdscr):
        ncols, nlines = (9, 4)
        uly, ulx = (15, 20)
        stdscr.addstr(uly - 2, ulx, 'Use Ctrl-G to end editing.')
        win = curses.newwin(nlines, ncols, uly, ulx)
        rectangle(stdscr, uly - 1, ulx - 1, uly + nlines, ulx + ncols)
        stdscr.refresh()
        return Textbox(win).edit()


    str = curses.wrapper(test_editbox)
    print 'Contents of text box:', repr(str)
