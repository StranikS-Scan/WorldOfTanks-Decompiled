# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/IOBinding.py
import os
import types
import pipes
import sys
import codecs
import tempfile
import tkFileDialog
import tkMessageBox
import re
from Tkinter import *
from SimpleDialog import SimpleDialog
from idlelib.configHandler import idleConf
try:
    from codecs import BOM_UTF8
except ImportError:
    BOM_UTF8 = '\xef\xbb\xbf'

try:
    import locale
    locale.setlocale(locale.LC_CTYPE, '')
except (ImportError, locale.Error):
    pass

filesystemencoding = sys.getfilesystemencoding()
encoding = 'ascii'
if sys.platform == 'win32':
    try:
        encoding = locale.getdefaultlocale()[1]
        codecs.lookup(encoding)
    except LookupError:
        pass

else:
    try:
        encoding = locale.nl_langinfo(locale.CODESET)
        if encoding is None or encoding is '':
            encoding = 'ascii'
        codecs.lookup(encoding)
    except (NameError, AttributeError, LookupError):
        try:
            encoding = locale.getdefaultlocale()[1]
            if encoding is None or encoding is '':
                encoding = 'ascii'
            codecs.lookup(encoding)
        except (ValueError, LookupError):
            pass

encoding = encoding.lower()
coding_re = re.compile('^[ \\t\\f]*#.*coding[:=][ \\t]*([-\\w.]+)')

class EncodingMessage(SimpleDialog):

    def __init__(self, master, enc):
        self.should_edit = False
        self.root = top = Toplevel(master)
        top.bind('<Return>', self.return_event)
        top.bind('<Escape>', self.do_ok)
        top.protocol('WM_DELETE_WINDOW', self.wm_delete_window)
        top.wm_title('I/O Warning')
        top.wm_iconname('I/O Warning')
        self.top = top
        l1 = Label(top, text='Non-ASCII found, yet no encoding declared. Add a line like')
        l1.pack(side=TOP, anchor=W)
        l2 = Entry(top, font='courier')
        l2.insert(0, '# -*- coding: %s -*-' % enc)
        l2.pack(side=TOP, anchor=W, fill=X)
        l3 = Label(top, text='to your file\nChoose OK to save this file as %s\nEdit your general options to silence this warning' % enc)
        l3.pack(side=TOP, anchor=W)
        buttons = Frame(top)
        buttons.pack(side=TOP, fill=X)
        self.default = self.cancel = 0
        b1 = Button(buttons, text='Ok', default='active', command=self.do_ok)
        b1.pack(side=LEFT, fill=BOTH, expand=1)
        b2 = Button(buttons, text='Edit my file', command=self.do_edit)
        b2.pack(side=LEFT, fill=BOTH, expand=1)
        self._set_transient(master)

    def do_ok(self):
        self.done(0)

    def do_edit(self):
        self.done(1)


def coding_spec(str):
    lst = str.split('\n', 2)[:2]
    for line in lst:
        match = coding_re.match(line)
        if match is not None:
            break
    else:
        return

    name = match.group(1)
    import codecs
    try:
        codecs.lookup(name)
    except LookupError:
        raise LookupError, 'Unknown encoding ' + name

    return name


class IOBinding():

    def __init__(self, editwin):
        self.editwin = editwin
        self.text = editwin.text
        self.__id_open = self.text.bind('<<open-window-from-file>>', self.open)
        self.__id_save = self.text.bind('<<save-window>>', self.save)
        self.__id_saveas = self.text.bind('<<save-window-as-file>>', self.save_as)
        self.__id_savecopy = self.text.bind('<<save-copy-of-window-as-file>>', self.save_a_copy)
        self.fileencoding = None
        self.__id_print = self.text.bind('<<print-window>>', self.print_window)
        return

    def close(self):
        self.text.unbind('<<open-window-from-file>>', self.__id_open)
        self.text.unbind('<<save-window>>', self.__id_save)
        self.text.unbind('<<save-window-as-file>>', self.__id_saveas)
        self.text.unbind('<<save-copy-of-window-as-file>>', self.__id_savecopy)
        self.text.unbind('<<print-window>>', self.__id_print)
        self.editwin = None
        self.text = None
        self.filename_change_hook = None
        return

    def get_saved(self):
        return self.editwin.get_saved()

    def set_saved(self, flag):
        self.editwin.set_saved(flag)

    def reset_undo(self):
        self.editwin.reset_undo()

    filename_change_hook = None

    def set_filename_change_hook(self, hook):
        self.filename_change_hook = hook

    filename = None
    dirname = None

    def set_filename(self, filename):
        if filename and os.path.isdir(filename):
            self.filename = None
            self.dirname = filename
        else:
            self.filename = filename
            self.dirname = None
            self.set_saved(1)
            if self.filename_change_hook:
                self.filename_change_hook()
        return

    def open(self, event=None, editFile=None):
        flist = self.editwin.flist
        if flist:
            if not editFile:
                filename = self.askopenfile()
            else:
                filename = editFile
            if filename:
                if self.editwin and not getattr(self.editwin, 'interp', None) and not self.filename and self.get_saved():
                    flist.open(filename, self.loadfile)
                else:
                    flist.open(filename)
            elif self.text:
                self.text.focus_set()
            return 'break'
        else:
            if self.get_saved():
                reply = self.maybesave()
                if reply == 'cancel':
                    self.text.focus_set()
                    return 'break'
            if not editFile:
                filename = self.askopenfile()
            else:
                filename = editFile
            if filename:
                self.loadfile(filename)
            else:
                self.text.focus_set()
            return 'break'

    eol = '(\\r\\n)|\\n|\\r'
    eol_re = re.compile(eol)
    eol_convention = os.linesep

    def loadfile(self, filename):
        try:
            with open(filename, 'rb') as f:
                chars = f.read()
        except IOError as msg:
            tkMessageBox.showerror('I/O Error', str(msg), master=self.text)
            return False

        chars = self.decode(chars)
        firsteol = self.eol_re.search(chars)
        if firsteol:
            self.eol_convention = firsteol.group(0)
            if isinstance(self.eol_convention, unicode):
                self.eol_convention = self.eol_convention.encode('ascii')
            chars = self.eol_re.sub('\\n', chars)
        self.text.delete('1.0', 'end')
        self.set_filename(None)
        self.text.insert('1.0', chars)
        self.reset_undo()
        self.set_filename(filename)
        self.text.mark_set('insert', '1.0')
        self.text.yview('insert')
        self.updaterecentfileslist(filename)
        return True

    def decode(self, chars):
        if chars.startswith(BOM_UTF8):
            try:
                chars = chars[3:].decode('utf-8')
            except UnicodeError:
                return chars

            self.fileencoding = BOM_UTF8
            return chars
        try:
            enc = coding_spec(chars)
        except LookupError as name:
            tkMessageBox.showerror(title='Error loading the file', message="The encoding '%s' is not known to this Python installation. The file may not display correctly" % name, master=self.text)
            enc = None

        if enc:
            try:
                return unicode(chars, enc)
            except UnicodeError:
                pass

        try:
            return unicode(chars, 'ascii')
        except UnicodeError:
            pass

        try:
            chars = unicode(chars, encoding)
            self.fileencoding = encoding
        except UnicodeError:
            pass

        return chars

    def maybesave(self):
        if self.get_saved():
            return 'yes'
        else:
            message = 'Do you want to save %s before closing?' % (self.filename or 'this untitled document')
            confirm = tkMessageBox.askyesnocancel(title='Save On Close', message=message, default=tkMessageBox.YES, master=self.text)
            if confirm:
                reply = 'yes'
                self.save(None)
                if not self.get_saved():
                    reply = 'cancel'
            elif confirm is None:
                reply = 'cancel'
            else:
                reply = 'no'
            self.text.focus_set()
            return reply

    def save(self, event):
        if not self.filename:
            self.save_as(event)
        elif self.writefile(self.filename):
            self.set_saved(True)
            try:
                self.editwin.store_file_breaks()
            except AttributeError:
                pass

        self.text.focus_set()

    def save_as(self, event):
        filename = self.asksavefile()
        if filename:
            if self.writefile(filename):
                self.set_filename(filename)
                self.set_saved(1)
                try:
                    self.editwin.store_file_breaks()
                except AttributeError:
                    pass

        self.text.focus_set()
        self.updaterecentfileslist(filename)

    def save_a_copy(self, event):
        filename = self.asksavefile()
        if filename:
            self.writefile(filename)
        self.text.focus_set()
        self.updaterecentfileslist(filename)

    def writefile(self, filename):
        self.fixlastline()
        chars = self.encode(self.text.get('1.0', 'end-1c'))
        if self.eol_convention != '\n':
            chars = chars.replace('\n', self.eol_convention)
        try:
            with open(filename, 'wb') as f:
                f.write(chars)
            return True
        except IOError as msg:
            tkMessageBox.showerror('I/O Error', str(msg), master=self.text)
            return False

    def encode(self, chars):
        if isinstance(chars, types.StringType):
            return chars
        try:
            return chars.encode('ascii')
        except UnicodeError:
            pass

        try:
            enc = coding_spec(chars)
            failed = None
        except LookupError as msg:
            failed = msg
            enc = None

        if enc:
            try:
                return chars.encode(enc)
            except UnicodeError:
                failed = "Invalid encoding '%s'" % enc

        if failed:
            tkMessageBox.showerror('I/O Error', '%s. Saving as UTF-8' % failed, master=self.text)
        if self.fileencoding == BOM_UTF8 or failed:
            return BOM_UTF8 + chars.encode('utf-8')
        if self.fileencoding:
            try:
                return chars.encode(self.fileencoding)
            except UnicodeError:
                tkMessageBox.showerror('I/O Error', "Cannot save this as '%s' anymore. Saving as UTF-8" % self.fileencoding, master=self.text)
                return BOM_UTF8 + chars.encode('utf-8')

        config_encoding = idleConf.GetOption('main', 'EditorWindow', 'encoding')
        if config_encoding == 'utf-8':
            return BOM_UTF8 + chars.encode('utf-8')
        ask_user = True
        try:
            chars = chars.encode(encoding)
            enc = encoding
            if config_encoding == 'locale':
                ask_user = False
        except UnicodeError:
            chars = BOM_UTF8 + chars.encode('utf-8')
            enc = 'utf-8'

        if not ask_user:
            return chars
        dialog = EncodingMessage(self.editwin.top, enc)
        dialog.go()
        if dialog.num == 1:
            encline = '# -*- coding: %s -*-\n' % enc
            firstline = self.text.get('1.0', '2.0')
            if firstline.startswith('#!'):
                self.text.insert('2.0', encline)
            else:
                self.text.insert('1.0', encline)
            return self.encode(self.text.get('1.0', 'end-1c'))
        else:
            return chars

    def fixlastline(self):
        c = self.text.get('end-2c')
        if c != '\n':
            self.text.insert('end-1c', '\n')

    def print_window(self, event):
        confirm = tkMessageBox.askokcancel(title='Print', message='Print to Default Printer', default=tkMessageBox.OK, master=self.text)
        if not confirm:
            self.text.focus_set()
            return 'break'
        else:
            tempfilename = None
            saved = self.get_saved()
            if saved:
                filename = self.filename
            if not saved or filename is None:
                tfd, tempfilename = tempfile.mkstemp(prefix='IDLE_tmp_')
                filename = tempfilename
                os.close(tfd)
                if not self.writefile(tempfilename):
                    os.unlink(tempfilename)
                    return 'break'
            platform = os.name
            printPlatform = True
            if platform == 'posix':
                command = idleConf.GetOption('main', 'General', 'print-command-posix')
                command = command + ' 2>&1'
            elif platform == 'nt':
                command = idleConf.GetOption('main', 'General', 'print-command-win')
            else:
                printPlatform = False
            if printPlatform:
                command = command % pipes.quote(filename)
                pipe = os.popen(command, 'r')
                output = pipe.read().strip()
                status = pipe.close()
                if status:
                    output = 'Printing failed (exit status 0x%x)\n' % status + output
                if output:
                    output = 'Printing command: %s\n' % repr(command) + output
                    tkMessageBox.showerror('Print status', output, master=self.text)
            else:
                message = 'Printing is not enabled for this platform: %s' % platform
                tkMessageBox.showinfo('Print status', message, master=self.text)
            if tempfilename:
                os.unlink(tempfilename)
            return 'break'

    opendialog = None
    savedialog = None
    filetypes = [('Python files', '*.py *.pyw', 'TEXT'), ('Text files', '*.txt', 'TEXT'), ('All files', '*')]

    def askopenfile(self):
        dir, base = self.defaultfilename('open')
        if not self.opendialog:
            self.opendialog = tkFileDialog.Open(master=self.text, filetypes=self.filetypes)
        filename = self.opendialog.show(initialdir=dir, initialfile=base)
        if isinstance(filename, unicode):
            filename = filename.encode(filesystemencoding)
        return filename

    def defaultfilename(self, mode='open'):
        if self.filename:
            return os.path.split(self.filename)
        elif self.dirname:
            return (self.dirname, '')
        else:
            try:
                pwd = os.getcwd()
            except os.error:
                pwd = ''

            return (pwd, '')

    def asksavefile(self):
        dir, base = self.defaultfilename('save')
        if not self.savedialog:
            self.savedialog = tkFileDialog.SaveAs(master=self.text, filetypes=self.filetypes)
        filename = self.savedialog.show(initialdir=dir, initialfile=base)
        if isinstance(filename, unicode):
            filename = filename.encode(filesystemencoding)
        return filename

    def updaterecentfileslist(self, filename):
        self.editwin.update_recent_files_list(filename)


def test():
    root = Tk()

    class MyEditWin:

        def __init__(self, text):
            self.text = text
            self.flist = None
            self.text.bind('<Control-o>', self.open)
            self.text.bind('<Control-s>', self.save)
            self.text.bind('<Alt-s>', self.save_as)
            self.text.bind('<Alt-z>', self.save_a_copy)
            return

        def get_saved(self):
            pass

        def set_saved(self, flag):
            pass

        def reset_undo(self):
            pass

        def open(self, event):
            self.text.event_generate('<<open-window-from-file>>')

        def save(self, event):
            self.text.event_generate('<<save-window>>')

        def save_as(self, event):
            self.text.event_generate('<<save-window-as-file>>')

        def save_a_copy(self, event):
            self.text.event_generate('<<save-copy-of-window-as-file>>')

    text = Text(root)
    text.pack()
    text.focus_set()
    editwin = MyEditWin(text)
    io = IOBinding(editwin)
    root.mainloop()


if __name__ == '__main__':
    test()
