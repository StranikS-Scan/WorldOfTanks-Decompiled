# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/robotparser.py
import urlparse
import urllib
__all__ = ['RobotFileParser']

class RobotFileParser:

    def __init__(self, url=''):
        self.entries = []
        self.default_entry = None
        self.disallow_all = False
        self.allow_all = False
        self.set_url(url)
        self.last_checked = 0
        return

    def mtime(self):
        return self.last_checked

    def modified(self):
        import time
        self.last_checked = time.time()

    def set_url(self, url):
        self.url = url
        self.host, self.path = urlparse.urlparse(url)[1:3]

    def read(self):
        opener = URLopener()
        f = opener.open(self.url)
        lines = [ line.strip() for line in f ]
        f.close()
        self.errcode = opener.errcode
        if self.errcode in (401, 403):
            self.disallow_all = True
        elif self.errcode >= 400 and self.errcode < 500:
            self.allow_all = True
        elif self.errcode == 200 and lines:
            self.parse(lines)

    def _add_entry(self, entry):
        if '*' in entry.useragents:
            if self.default_entry is None:
                self.default_entry = entry
        else:
            self.entries.append(entry)
        return

    def parse(self, lines):
        state = 0
        linenumber = 0
        entry = Entry()
        self.modified()
        for line in lines:
            linenumber += 1
            if not line:
                if state == 1:
                    entry = Entry()
                    state = 0
                elif state == 2:
                    self._add_entry(entry)
                    entry = Entry()
                    state = 0
            i = line.find('#')
            if i >= 0:
                line = line[:i]
            line = line.strip()
            if not line:
                continue
            line = line.split(':', 1)
            if len(line) == 2:
                line[0] = line[0].strip().lower()
                line[1] = urllib.unquote(line[1].strip())
                if line[0] == 'user-agent':
                    if state == 2:
                        self._add_entry(entry)
                        entry = Entry()
                    entry.useragents.append(line[1])
                    state = 1
                elif line[0] == 'disallow':
                    if state != 0:
                        entry.rulelines.append(RuleLine(line[1], False))
                        state = 2
                elif line[0] == 'allow':
                    if state != 0:
                        entry.rulelines.append(RuleLine(line[1], True))
                        state = 2

        if state == 2:
            self._add_entry(entry)

    def can_fetch(self, useragent, url):
        if self.disallow_all:
            return False
        if self.allow_all:
            return True
        if not self.last_checked:
            return False
        parsed_url = urlparse.urlparse(urllib.unquote(url))
        url = urlparse.urlunparse(('',
         '',
         parsed_url.path,
         parsed_url.params,
         parsed_url.query,
         parsed_url.fragment))
        url = urllib.quote(url)
        if not url:
            url = '/'
        for entry in self.entries:
            if entry.applies_to(useragent):
                return entry.allowance(url)

        return self.default_entry.allowance(url) if self.default_entry else True

    def __str__(self):
        entries = self.entries
        if self.default_entry is not None:
            entries = entries + [self.default_entry]
        return '\n'.join(map(str, entries)) + '\n'


class RuleLine:

    def __init__(self, path, allowance):
        if path == '' and not allowance:
            allowance = True
        path = urlparse.urlunparse(urlparse.urlparse(path))
        self.path = urllib.quote(path)
        self.allowance = allowance

    def applies_to(self, filename):
        return self.path == '*' or filename.startswith(self.path)

    def __str__(self):
        return (self.allowance and 'Allow' or 'Disallow') + ': ' + self.path


class Entry:

    def __init__(self):
        self.useragents = []
        self.rulelines = []

    def __str__(self):
        ret = []
        for agent in self.useragents:
            ret.extend(['User-agent: ', agent, '\n'])

        for line in self.rulelines:
            ret.extend([str(line), '\n'])

        return ''.join(ret)

    def applies_to(self, useragent):
        useragent = useragent.split('/')[0].lower()
        for agent in self.useragents:
            if agent == '*':
                return True
            agent = agent.lower()
            if agent in useragent:
                return True

        return False

    def allowance(self, filename):
        for line in self.rulelines:
            if line.applies_to(filename):
                return line.allowance

        return True


class URLopener(urllib.FancyURLopener):

    def __init__(self, *args):
        urllib.FancyURLopener.__init__(self, *args)
        self.errcode = 200

    def prompt_user_passwd(self, host, realm):
        return (None, None)

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        self.errcode = errcode
        return urllib.FancyURLopener.http_error_default(self, url, fp, errcode, errmsg, headers)
