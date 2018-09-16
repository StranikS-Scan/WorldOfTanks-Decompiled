# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/config.py
import os
from ConfigParser import ConfigParser
from distutils.cmd import Command
DEFAULT_PYPIRC = '[distutils]\nindex-servers =\n    pypi\n\n[pypi]\nusername:%s\npassword:%s\n'

class PyPIRCCommand(Command):
    DEFAULT_REPOSITORY = 'https://pypi.python.org/pypi'
    DEFAULT_REALM = 'pypi'
    repository = None
    realm = None
    user_options = [('repository=', 'r', 'url of repository [default: %s]' % DEFAULT_REPOSITORY), ('show-response', None, 'display full response text from server')]
    boolean_options = ['show-response']

    def _get_rc_file(self):
        return os.path.join(os.path.expanduser('~'), '.pypirc')

    def _store_pypirc(self, username, password):
        rc = self._get_rc_file()
        f = os.fdopen(os.open(rc, os.O_CREAT | os.O_WRONLY, 384), 'w')
        try:
            f.write(DEFAULT_PYPIRC % (username, password))
        finally:
            f.close()

    def _read_pypirc(self):
        rc = self._get_rc_file()
        if os.path.exists(rc):
            self.announce('Using PyPI login from %s' % rc)
            repository = self.repository or self.DEFAULT_REPOSITORY
            config = ConfigParser()
            config.read(rc)
            sections = config.sections()
            if 'distutils' in sections:
                index_servers = config.get('distutils', 'index-servers')
                _servers = [ server.strip() for server in index_servers.split('\n') if server.strip() != '' ]
                if _servers == []:
                    if 'pypi' in sections:
                        _servers = ['pypi']
                    else:
                        return {}
                for server in _servers:
                    current = {'server': server}
                    current['username'] = config.get(server, 'username')
                    for key, default in (('repository', self.DEFAULT_REPOSITORY), ('realm', self.DEFAULT_REALM), ('password', None)):
                        if config.has_option(server, key):
                            current[key] = config.get(server, key)
                        current[key] = default

                    if current['server'] == repository or current['repository'] == repository:
                        return current

            elif 'server-login' in sections:
                server = 'server-login'
                if config.has_option(server, 'repository'):
                    repository = config.get(server, 'repository')
                else:
                    repository = self.DEFAULT_REPOSITORY
                return {'username': config.get(server, 'username'),
                 'password': config.get(server, 'password'),
                 'repository': repository,
                 'server': server,
                 'realm': self.DEFAULT_REALM}
        return {}

    def initialize_options(self):
        self.repository = None
        self.realm = None
        self.show_response = 0
        return

    def finalize_options(self):
        if self.repository is None:
            self.repository = self.DEFAULT_REPOSITORY
        if self.realm is None:
            self.realm = self.DEFAULT_REALM
        return
