# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/webbrowser.py
import os
import shlex
import sys
import stat
import subprocess
import time
__all__ = ['Error',
 'open',
 'open_new',
 'open_new_tab',
 'get',
 'register']

class Error(Exception):
    pass


_browsers = {}
_tryorder = []

def register(name, klass, instance=None, update_tryorder=1):
    _browsers[name.lower()] = [klass, instance]
    if update_tryorder > 0:
        _tryorder.append(name)
    elif update_tryorder < 0:
        _tryorder.insert(0, name)


def get(using=None):
    if using is not None:
        alternatives = [using]
    else:
        alternatives = _tryorder
    for browser in alternatives:
        if '%s' in browser:
            browser = shlex.split(browser)
            if browser[-1] == '&':
                return BackgroundBrowser(browser[:-1])
            else:
                return GenericBrowser(browser)
        try:
            command = _browsers[browser.lower()]
        except KeyError:
            command = _synthesize(browser)

        if command[1] is not None:
            return command[1]
        if command[0] is not None:
            return command[0]()

    raise Error('could not locate runnable browser')
    return


def open(url, new=0, autoraise=True):
    for name in _tryorder:
        browser = get(name)
        if browser.open(url, new, autoraise):
            return True

    return False


def open_new(url):
    return open(url, 1)


def open_new_tab(url):
    return open(url, 2)


def _synthesize(browser, update_tryorder=1):
    cmd = browser.split()[0]
    if not _iscommand(cmd):
        return [None, None]
    name = os.path.basename(cmd)
    try:
        command = _browsers[name.lower()]
    except KeyError:
        return [None, None]

    controller = command[1]
    if controller and name.lower() == controller.basename:
        import copy
        controller = copy.copy(controller)
        controller.name = browser
        controller.basename = os.path.basename(browser)
        register(browser, None, controller, update_tryorder)
        return [None, controller]
    else:
        return [None, None]


if sys.platform[:3] == 'win':

    def _isexecutable(cmd):
        cmd = cmd.lower()
        if os.path.isfile(cmd) and cmd.endswith(('.exe', '.bat')):
            return True
        for ext in ('.exe', '.bat'):
            if os.path.isfile(cmd + ext):
                return True

        return False


else:

    def _isexecutable(cmd):
        if os.path.isfile(cmd):
            mode = os.stat(cmd)[stat.ST_MODE]
            if mode & stat.S_IXUSR or mode & stat.S_IXGRP or mode & stat.S_IXOTH:
                return True
        return False


def _iscommand(cmd):
    if _isexecutable(cmd):
        return True
    path = os.environ.get('PATH')
    if not path:
        return False
    for d in path.split(os.pathsep):
        exe = os.path.join(d, cmd)
        if _isexecutable(exe):
            return True

    return False


class BaseBrowser(object):
    args = ['%s']

    def __init__(self, name=''):
        self.name = name
        self.basename = name

    def open(self, url, new=0, autoraise=True):
        raise NotImplementedError

    def open_new(self, url):
        return self.open(url, 1)

    def open_new_tab(self, url):
        return self.open(url, 2)


class GenericBrowser(BaseBrowser):

    def __init__(self, name):
        if isinstance(name, basestring):
            self.name = name
            self.args = ['%s']
        else:
            self.name = name[0]
            self.args = name[1:]
        self.basename = os.path.basename(self.name)

    def open(self, url, new=0, autoraise=True):
        cmdline = [self.name] + [ arg.replace('%s', url) for arg in self.args ]
        try:
            if sys.platform[:3] == 'win':
                p = subprocess.Popen(cmdline)
            else:
                p = subprocess.Popen(cmdline, close_fds=True)
            return not p.wait()
        except OSError:
            return False


class BackgroundBrowser(GenericBrowser):

    def open(self, url, new=0, autoraise=True):
        cmdline = [self.name] + [ arg.replace('%s', url) for arg in self.args ]
        try:
            if sys.platform[:3] == 'win':
                p = subprocess.Popen(cmdline)
            else:
                setsid = getattr(os, 'setsid', None)
                if not setsid:
                    setsid = getattr(os, 'setpgrp', None)
                p = subprocess.Popen(cmdline, close_fds=True, preexec_fn=setsid)
            return p.poll() is None
        except OSError:
            return False

        return


class UnixBrowser(BaseBrowser):
    raise_opts = None
    remote_args = ['%action', '%s']
    remote_action = None
    remote_action_newwin = None
    remote_action_newtab = None
    background = False
    redirect_stdout = True

    def _invoke(self, args, remote, autoraise):
        raise_opt = []
        if remote and self.raise_opts:
            autoraise = int(autoraise)
            opt = self.raise_opts[autoraise]
            if opt:
                raise_opt = [opt]
        cmdline = [self.name] + raise_opt + args
        if remote or self.background:
            inout = file(os.devnull, 'r+')
        else:
            inout = None
        setsid = getattr(os, 'setsid', None)
        if not setsid:
            setsid = getattr(os, 'setpgrp', None)
        p = subprocess.Popen(cmdline, close_fds=True, stdin=inout, stdout=self.redirect_stdout and inout or None, stderr=inout, preexec_fn=setsid)
        if remote:
            time.sleep(1)
            rc = p.poll()
            if rc is None:
                time.sleep(4)
                rc = p.poll()
                if rc is None:
                    return True
            return not rc
        else:
            if self.background:
                if p.poll() is None:
                    return True
                else:
                    return False
            else:
                return not p.wait()
            return

    def open(self, url, new=0, autoraise=True):
        if new == 0:
            action = self.remote_action
        elif new == 1:
            action = self.remote_action_newwin
        elif new == 2:
            if self.remote_action_newtab is None:
                action = self.remote_action_newwin
            else:
                action = self.remote_action_newtab
        else:
            raise Error("Bad 'new' parameter to open(); " + 'expected 0, 1, or 2, got %s' % new)
        args = [ arg.replace('%s', url).replace('%action', action) for arg in self.remote_args ]
        success = self._invoke(args, True, autoraise)
        if not success:
            args = [ arg.replace('%s', url) for arg in self.args ]
            return self._invoke(args, False, False)
        else:
            return True
            return


class Mozilla(UnixBrowser):
    raise_opts = ['-noraise', '-raise']
    remote_args = ['-remote', 'openURL(%s%action)']
    remote_action = ''
    remote_action_newwin = ',new-window'
    remote_action_newtab = ',new-tab'
    background = True


Netscape = Mozilla

class Galeon(UnixBrowser):
    raise_opts = ['-noraise', '']
    remote_args = ['%action', '%s']
    remote_action = '-n'
    remote_action_newwin = '-w'
    background = True


class Chrome(UnixBrowser):
    remote_args = ['%action', '%s']
    remote_action = ''
    remote_action_newwin = '--new-window'
    remote_action_newtab = ''
    background = True


Chromium = Chrome

class Opera(UnixBrowser):
    remote_args = ['%action', '%s']
    remote_action = ''
    remote_action_newwin = '--new-window'
    remote_action_newtab = ''
    background = True


class Elinks(UnixBrowser):
    remote_args = ['-remote', 'openURL(%s%action)']
    remote_action = ''
    remote_action_newwin = ',new-window'
    remote_action_newtab = ',new-tab'
    background = False
    redirect_stdout = False


class Konqueror(BaseBrowser):

    def open(self, url, new=0, autoraise=True):
        if new == 2:
            action = 'newTab'
        else:
            action = 'openURL'
        devnull = file(os.devnull, 'r+')
        setsid = getattr(os, 'setsid', None)
        if not setsid:
            setsid = getattr(os, 'setpgrp', None)
        try:
            p = subprocess.Popen(['kfmclient', action, url], close_fds=True, stdin=devnull, stdout=devnull, stderr=devnull)
        except OSError:
            pass
        else:
            p.wait()
            return True

        try:
            p = subprocess.Popen(['konqueror', '--silent', url], close_fds=True, stdin=devnull, stdout=devnull, stderr=devnull, preexec_fn=setsid)
        except OSError:
            pass
        else:
            if p.poll() is None:
                return True

        try:
            p = subprocess.Popen(['kfm', '-d', url], close_fds=True, stdin=devnull, stdout=devnull, stderr=devnull, preexec_fn=setsid)
        except OSError:
            return False

        return p.poll() is None
        return


class Grail(BaseBrowser):

    def _find_grail_rc(self):
        import glob
        import pwd
        import socket
        import tempfile
        tempdir = os.path.join(tempfile.gettempdir(), '.grail-unix')
        user = pwd.getpwuid(os.getuid())[0]
        filename = os.path.join(tempdir, user + '-*')
        maybes = glob.glob(filename)
        if not maybes:
            return
        else:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            for fn in maybes:
                try:
                    s.connect(fn)
                except socket.error:
                    try:
                        os.unlink(fn)
                    except IOError:
                        pass

                else:
                    return s

            return

    def _remote(self, action):
        s = self._find_grail_rc()
        if not s:
            return 0
        s.send(action)
        s.close()

    def open(self, url, new=0, autoraise=True):
        if new:
            ok = self._remote('LOADNEW ' + url)
        else:
            ok = self._remote('LOAD ' + url)
        return ok


def register_X_browsers():
    if _iscommand('xdg-open'):
        register('xdg-open', None, BackgroundBrowser('xdg-open'))
    if 'GNOME_DESKTOP_SESSION_ID' in os.environ and _iscommand('gvfs-open'):
        register('gvfs-open', None, BackgroundBrowser('gvfs-open'))
    if 'GNOME_DESKTOP_SESSION_ID' in os.environ and _iscommand('gnome-open'):
        register('gnome-open', None, BackgroundBrowser('gnome-open'))
    if 'KDE_FULL_SESSION' in os.environ and _iscommand('kfmclient'):
        register('kfmclient', Konqueror, Konqueror('kfmclient'))
    if _iscommand('x-www-browser'):
        register('x-www-browser', None, BackgroundBrowser('x-www-browser'))
    for browser in ('mozilla-firefox', 'firefox', 'mozilla-firebird', 'firebird', 'iceweasel', 'iceape', 'seamonkey', 'mozilla', 'netscape'):
        if _iscommand(browser):
            register(browser, None, Mozilla(browser))

    if _iscommand('kfm'):
        register('kfm', Konqueror, Konqueror('kfm'))
    elif _iscommand('konqueror'):
        register('konqueror', Konqueror, Konqueror('konqueror'))
    for browser in ('galeon', 'epiphany'):
        if _iscommand(browser):
            register(browser, None, Galeon(browser))

    if _iscommand('skipstone'):
        register('skipstone', None, BackgroundBrowser('skipstone'))
    for browser in ('google-chrome', 'chrome', 'chromium', 'chromium-browser'):
        if _iscommand(browser):
            register(browser, None, Chrome(browser))

    if _iscommand('opera'):
        register('opera', None, Opera('opera'))
    if _iscommand('mosaic'):
        register('mosaic', None, BackgroundBrowser('mosaic'))
    if _iscommand('grail'):
        register('grail', Grail, None)
    return


if os.environ.get('DISPLAY'):
    register_X_browsers()
if os.environ.get('TERM'):
    if _iscommand('www-browser'):
        register('www-browser', None, GenericBrowser('www-browser'))
    if _iscommand('links'):
        register('links', None, GenericBrowser('links'))
    if _iscommand('elinks'):
        register('elinks', None, Elinks('elinks'))
    if _iscommand('lynx'):
        register('lynx', None, GenericBrowser('lynx'))
    if _iscommand('w3m'):
        register('w3m', None, GenericBrowser('w3m'))
if sys.platform[:3] == 'win':

    class WindowsDefault(BaseBrowser):

        def open(self, url, new=0, autoraise=True):
            try:
                os.startfile(url)
            except WindowsError:
                return False

            return True


    _tryorder = []
    _browsers = {}
    register('windows-default', WindowsDefault)
    iexplore = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Internet Explorer\\IEXPLORE.EXE')
    for browser in ('firefox',
     'firebird',
     'seamonkey',
     'mozilla',
     'netscape',
     'opera',
     iexplore):
        if _iscommand(browser):
            register(browser, None, BackgroundBrowser(browser))

if sys.platform == 'darwin':

    class MacOSX(BaseBrowser):

        def __init__(self, name):
            self.name = name

        def open(self, url, new=0, autoraise=True):
            if ':' not in url:
                url = 'file:' + url
            new = int(bool(new))
            if self.name == 'default':
                script = 'open location "%s"' % url.replace('"', '%22')
            else:
                if self.name == 'OmniWeb':
                    toWindow = ''
                else:
                    toWindow = 'toWindow %d' % (new - 1)
                cmd = 'OpenURL "%s"' % url.replace('"', '%22')
                script = 'tell application "%s"\n                                activate\n                                %s %s\n                            end tell' % (self.name, cmd, toWindow)
            osapipe = os.popen('osascript', 'w')
            if osapipe is None:
                return False
            else:
                osapipe.write(script)
                rc = osapipe.close()
                return not rc


    class MacOSXOSAScript(BaseBrowser):

        def __init__(self, name):
            self._name = name

        def open(self, url, new=0, autoraise=True):
            if self._name == 'default':
                script = 'open location "%s"' % url.replace('"', '%22')
            else:
                script = '\n                   tell application "%s"\n                       activate\n                       open location "%s"\n                   end\n                   ' % (self._name, url.replace('"', '%22'))
            osapipe = os.popen('osascript', 'w')
            if osapipe is None:
                return False
            else:
                osapipe.write(script)
                rc = osapipe.close()
                return not rc


    register('safari', None, MacOSXOSAScript('safari'), -1)
    register('firefox', None, MacOSXOSAScript('firefox'), -1)
    register('chrome', None, MacOSXOSAScript('chrome'), -1)
    register('MacOSX', None, MacOSXOSAScript('default'), -1)
if sys.platform[:3] == 'os2' and _iscommand('netscape'):
    _tryorder = []
    _browsers = {}
    register('os2netscape', None, GenericBrowser(['start', 'netscape', '%s']), -1)
if 'BROWSER' in os.environ:
    _userchoices = os.environ['BROWSER'].split(os.pathsep)
    _userchoices.reverse()
    for cmdline in _userchoices:
        if cmdline != '':
            cmd = _synthesize(cmdline, -1)
            if cmd[1] is None:
                register(cmdline, None, GenericBrowser(cmdline), -1)

    cmdline = None
    del cmdline
    del _userchoices

def main():
    import getopt
    usage = 'Usage: %s [-n | -t] url\n    -n: open new window\n    -t: open new tab' % sys.argv[0]
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ntd')
    except getopt.error as msg:
        print >> sys.stderr, msg
        print >> sys.stderr, usage
        sys.exit(1)

    new_win = 0
    for o, a in opts:
        if o == '-n':
            new_win = 1
        if o == '-t':
            new_win = 2

    if len(args) != 1:
        print >> sys.stderr, usage
        sys.exit(1)
    url = args[0]
    open(url, new_win)
    print '\x07'


if __name__ == '__main__':
    main()
