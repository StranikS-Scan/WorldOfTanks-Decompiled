# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/CGIHTTPServer.py
__version__ = '0.4'
__all__ = ['CGIHTTPRequestHandler']
import os
import sys
import urllib
import BaseHTTPServer
import SimpleHTTPServer
import select
import copy

class CGIHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    have_fork = hasattr(os, 'fork')
    have_popen2 = hasattr(os, 'popen2')
    have_popen3 = hasattr(os, 'popen3')
    rbufsize = 0

    def do_POST(self):
        if self.is_cgi():
            self.run_cgi()
        else:
            self.send_error(501, 'Can only POST to CGI scripts')

    def send_head(self):
        if self.is_cgi():
            return self.run_cgi()
        else:
            return SimpleHTTPServer.SimpleHTTPRequestHandler.send_head(self)

    def is_cgi(self):
        collapsed_path = _url_collapse_path(self.path)
        dir_sep = collapsed_path.find('/', 1)
        head, tail = collapsed_path[:dir_sep], collapsed_path[dir_sep + 1:]
        if head in self.cgi_directories:
            self.cgi_info = (head, tail)
            return True
        return False

    cgi_directories = ['/cgi-bin', '/htbin']

    def is_executable(self, path):
        return executable(path)

    def is_python(self, path):
        head, tail = os.path.splitext(path)
        return tail.lower() in ('.py', '.pyw')

    def run_cgi(self):
        dir, rest = self.cgi_info
        path = dir + '/' + rest
        i = path.find('/', len(dir) + 1)
        while i >= 0:
            nextdir = path[:i]
            nextrest = path[i + 1:]
            scriptdir = self.translate_path(nextdir)
            if os.path.isdir(scriptdir):
                dir, rest = nextdir, nextrest
                i = path.find('/', len(dir) + 1)
            break

        rest, _, query = rest.partition('?')
        i = rest.find('/')
        if i >= 0:
            script, rest = rest[:i], rest[i:]
        else:
            script, rest = rest, ''
        scriptname = dir + '/' + script
        scriptfile = self.translate_path(scriptname)
        if not os.path.exists(scriptfile):
            self.send_error(404, 'No such CGI script (%r)' % scriptname)
            return
        elif not os.path.isfile(scriptfile):
            self.send_error(403, 'CGI script is not a plain file (%r)' % scriptname)
            return
        else:
            ispy = self.is_python(scriptname)
            if not ispy:
                if not (self.have_fork or self.have_popen2 or self.have_popen3):
                    self.send_error(403, 'CGI script is not a Python script (%r)' % scriptname)
                    return
                if not self.is_executable(scriptfile):
                    self.send_error(403, 'CGI script is not executable (%r)' % scriptname)
                    return
            env = copy.deepcopy(os.environ)
            env['SERVER_SOFTWARE'] = self.version_string()
            env['SERVER_NAME'] = self.server.server_name
            env['GATEWAY_INTERFACE'] = 'CGI/1.1'
            env['SERVER_PROTOCOL'] = self.protocol_version
            env['SERVER_PORT'] = str(self.server.server_port)
            env['REQUEST_METHOD'] = self.command
            uqrest = urllib.unquote(rest)
            env['PATH_INFO'] = uqrest
            env['PATH_TRANSLATED'] = self.translate_path(uqrest)
            env['SCRIPT_NAME'] = scriptname
            if query:
                env['QUERY_STRING'] = query
            host = self.address_string()
            if host != self.client_address[0]:
                env['REMOTE_HOST'] = host
            env['REMOTE_ADDR'] = self.client_address[0]
            authorization = self.headers.getheader('authorization')
            if authorization:
                authorization = authorization.split()
                if len(authorization) == 2:
                    import base64, binascii
                    env['AUTH_TYPE'] = authorization[0]
                    if authorization[0].lower() == 'basic':
                        try:
                            authorization = base64.decodestring(authorization[1])
                        except binascii.Error:
                            pass
                        else:
                            authorization = authorization.split(':')
                            if len(authorization) == 2:
                                env['REMOTE_USER'] = authorization[0]
            if self.headers.typeheader is None:
                env['CONTENT_TYPE'] = self.headers.type
            else:
                env['CONTENT_TYPE'] = self.headers.typeheader
            length = self.headers.getheader('content-length')
            if length:
                env['CONTENT_LENGTH'] = length
            referer = self.headers.getheader('referer')
            if referer:
                env['HTTP_REFERER'] = referer
            accept = []
            for line in self.headers.getallmatchingheaders('accept'):
                if line[:1] in '\t\n\r ':
                    accept.append(line.strip())
                accept = accept + line[7:].split(',')

            env['HTTP_ACCEPT'] = ','.join(accept)
            ua = self.headers.getheader('user-agent')
            if ua:
                env['HTTP_USER_AGENT'] = ua
            co = filter(None, self.headers.getheaders('cookie'))
            if co:
                env['HTTP_COOKIE'] = ', '.join(co)
            for k in ('QUERY_STRING', 'REMOTE_HOST', 'CONTENT_LENGTH', 'HTTP_USER_AGENT', 'HTTP_COOKIE', 'HTTP_REFERER'):
                env.setdefault(k, '')

            self.send_response(200, 'Script output follows')
            decoded_query = query.replace('+', ' ')
            if self.have_fork:
                args = [script]
                if '=' not in decoded_query:
                    args.append(decoded_query)
                nobody = nobody_uid()
                self.wfile.flush()
                pid = os.fork()
                if pid != 0:
                    pid, sts = os.waitpid(pid, 0)
                    while select.select([self.rfile], [], [], 0)[0]:
                        if not self.rfile.read(1):
                            break

                    if sts:
                        self.log_error('CGI script exit status %#x', sts)
                    return
                try:
                    try:
                        os.setuid(nobody)
                    except os.error:
                        pass

                    os.dup2(self.rfile.fileno(), 0)
                    os.dup2(self.wfile.fileno(), 1)
                    os.execve(scriptfile, args, env)
                except:
                    self.server.handle_error(self.request, self.client_address)
                    os._exit(127)

            else:
                import subprocess
                cmdline = [scriptfile]
                if self.is_python(scriptfile):
                    interp = sys.executable
                    if interp.lower().endswith('w.exe'):
                        interp = interp[:-5] + interp[-4:]
                    cmdline = [interp, '-u'] + cmdline
                if '=' not in query:
                    cmdline.append(query)
                self.log_message('command: %s', subprocess.list2cmdline(cmdline))
                try:
                    nbytes = int(length)
                except (TypeError, ValueError):
                    nbytes = 0

                p = subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
                if self.command.lower() == 'post' and nbytes > 0:
                    data = self.rfile.read(nbytes)
                else:
                    data = None
                while select.select([self.rfile._sock], [], [], 0)[0]:
                    if not self.rfile._sock.recv(1):
                        break

                stdout, stderr = p.communicate(data)
                self.wfile.write(stdout)
                if stderr:
                    self.log_error('%s', stderr)
                p.stderr.close()
                p.stdout.close()
                status = p.returncode
                if status:
                    self.log_error('CGI script exit status %#x', status)
                else:
                    self.log_message('CGI script exited OK')
            return


def _url_collapse_path(path):
    path, _, query = path.partition('?')
    path = urllib.unquote(path)
    path_parts = path.split('/')
    head_parts = []
    for part in path_parts[:-1]:
        if part == '..':
            head_parts.pop()
        if part and part != '.':
            head_parts.append(part)

    if path_parts:
        tail_part = path_parts.pop()
        if tail_part:
            if tail_part == '..':
                head_parts.pop()
                tail_part = ''
            elif tail_part == '.':
                tail_part = ''
    else:
        tail_part = ''
    if query:
        tail_part = '?'.join((tail_part, query))
    splitpath = ('/' + '/'.join(head_parts), tail_part)
    collapsed_path = '/'.join(splitpath)
    return collapsed_path


nobody = None

def nobody_uid():
    global nobody
    if nobody:
        return nobody
    try:
        import pwd
    except ImportError:
        return -1

    try:
        nobody = pwd.getpwnam('nobody')[2]
    except KeyError:
        nobody = 1 + max(map(lambda x: x[2], pwd.getpwall()))

    return nobody


def executable(path):
    try:
        st = os.stat(path)
    except os.error:
        return False

    return st.st_mode & 73 != 0


def test(HandlerClass=CGIHTTPRequestHandler, ServerClass=BaseHTTPServer.HTTPServer):
    SimpleHTTPServer.test(HandlerClass, ServerClass)


if __name__ == '__main__':
    test()
