# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/command/register.py
__revision__ = '$Id$'
import urllib2
import getpass
import urlparse
from warnings import warn
from distutils.core import PyPIRCCommand
from distutils import log

class register(PyPIRCCommand):
    description = 'register the distribution with the Python package index'
    user_options = PyPIRCCommand.user_options + [('list-classifiers', None, 'list the valid Trove classifiers'), ('strict', None, 'Will stop the registering if the meta-data are not fully compliant')]
    boolean_options = PyPIRCCommand.boolean_options + ['verify', 'list-classifiers', 'strict']
    sub_commands = [('check', lambda self: True)]

    def initialize_options(self):
        PyPIRCCommand.initialize_options(self)
        self.list_classifiers = 0
        self.strict = 0

    def finalize_options(self):
        PyPIRCCommand.finalize_options(self)
        check_options = {'strict': ('register', self.strict),
         'restructuredtext': ('register', 1)}
        self.distribution.command_options['check'] = check_options

    def run(self):
        self.finalize_options()
        self._set_config()
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

        if self.dry_run:
            self.verify_metadata()
        elif self.list_classifiers:
            self.classifiers()
        else:
            self.send_metadata()

    def check_metadata(self):
        warn('distutils.command.register.check_metadata is deprecated,               use the check command instead', PendingDeprecationWarning)
        check = self.distribution.get_command_obj('check')
        check.ensure_finalized()
        check.strict = self.strict
        check.restructuredtext = 1
        check.run()

    def _set_config(self):
        config = self._read_pypirc()
        if config != {}:
            self.username = config['username']
            self.password = config['password']
            self.repository = config['repository']
            self.realm = config['realm']
            self.has_config = True
        else:
            if self.repository not in ('pypi', self.DEFAULT_REPOSITORY):
                raise ValueError('%s not found in .pypirc' % self.repository)
            if self.repository == 'pypi':
                self.repository = self.DEFAULT_REPOSITORY
            self.has_config = False

    def classifiers(self):
        response = urllib2.urlopen(self.repository + '?:action=list_classifiers')
        log.info(response.read())

    def verify_metadata(self):
        code, result = self.post_to_server(self.build_post_data('verify'))
        log.info('Server response (%s): %s' % (code, result))

    def send_metadata(self):
        if self.has_config:
            choice = '1'
            username = self.username
            password = self.password
        else:
            choice = 'x'
            username = password = ''
        choices = '1 2 3 4'.split()
        while choice not in choices:
            self.announce('We need to know who you are, so please choose either:\n 1. use your existing login,\n 2. register as a new user,\n 3. have the server generate a new password for you (and email it to you), or\n 4. quit\nYour selection [default 1]: ', log.INFO)
            choice = raw_input()
            if not choice:
                choice = '1'
            if choice not in choices:
                print 'Please choose one of the four options!'

        if choice == '1':
            while not username:
                username = raw_input('Username: ')

            while not password:
                password = getpass.getpass('Password: ')

            auth = urllib2.HTTPPasswordMgr()
            host = urlparse.urlparse(self.repository)[1]
            auth.add_password(self.realm, host, username, password)
            code, result = self.post_to_server(self.build_post_data('submit'), auth)
            self.announce('Server response (%s): %s' % (code, result), log.INFO)
            if code == 200:
                if self.has_config:
                    self.distribution.password = password
                else:
                    self.announce('I can store your PyPI login so future submissions will be faster.', log.INFO)
                    self.announce('(the login will be stored in %s)' % self._get_rc_file(), log.INFO)
                    choice = 'X'
                    while choice.lower() not in 'yn':
                        choice = raw_input('Save your login (y/N)?')
                        if not choice:
                            choice = 'n'

                    if choice.lower() == 'y':
                        self._store_pypirc(username, password)
        elif choice == '2':
            data = {':action': 'user'}
            data['name'] = data['password'] = data['email'] = ''
            data['confirm'] = None
            while not data['name']:
                data['name'] = raw_input('Username: ')

            while data['password'] != data['confirm']:
                while not data['password']:
                    data['password'] = getpass.getpass('Password: ')

                while not data['confirm']:
                    data['confirm'] = getpass.getpass(' Confirm: ')

                if data['password'] != data['confirm']:
                    data['password'] = ''
                    data['confirm'] = None
                    print "Password and confirm don't match!"

            while not data['email']:
                data['email'] = raw_input('   EMail: ')

            code, result = self.post_to_server(data)
            if code != 200:
                log.info('Server response (%s): %s' % (code, result))
            else:
                log.info('You will receive an email shortly.')
                log.info('Follow the instructions in it to complete registration.')
        elif choice == '3':
            data = {':action': 'password_reset'}
            data['email'] = ''
            while not data['email']:
                data['email'] = raw_input('Your email address: ')

            code, result = self.post_to_server(data)
            log.info('Server response (%s): %s' % (code, result))
        return

    def build_post_data(self, action):
        meta = self.distribution.metadata
        data = {':action': action,
         'metadata_version': '1.0',
         'name': meta.get_name(),
         'version': meta.get_version(),
         'summary': meta.get_description(),
         'home_page': meta.get_url(),
         'author': meta.get_contact(),
         'author_email': meta.get_contact_email(),
         'license': meta.get_licence(),
         'description': meta.get_long_description(),
         'keywords': meta.get_keywords(),
         'platform': meta.get_platforms(),
         'classifiers': meta.get_classifiers(),
         'download_url': meta.get_download_url(),
         'provides': meta.get_provides(),
         'requires': meta.get_requires(),
         'obsoletes': meta.get_obsoletes()}
        if data['provides'] or data['requires'] or data['obsoletes']:
            data['metadata_version'] = '1.1'
        return data

    def post_to_server(self, data, auth=None):
        if 'name' in data:
            self.announce('Registering %s to %s' % (data['name'], self.repository), log.INFO)
        boundary = '--------------GHSKFJDLGDS7543FJKLFHRE75642756743254'
        sep_boundary = '\n--' + boundary
        end_boundary = sep_boundary + '--'
        chunks = []
        for key, value in data.items():
            if type(value) not in (type([]), type(())):
                value = [value]
            for value in value:
                chunks.append(sep_boundary)
                chunks.append('\nContent-Disposition: form-data; name="%s"' % key)
                chunks.append('\n\n')
                chunks.append(value)
                if value and value[-1] == '\r':
                    chunks.append('\n')

        chunks.append(end_boundary)
        chunks.append('\n')
        body = []
        for chunk in chunks:
            if isinstance(chunk, unicode):
                body.append(chunk.encode('utf-8'))
            body.append(chunk)

        body = ''.join(body)
        headers = {'Content-type': 'multipart/form-data; boundary=%s; charset=utf-8' % boundary,
         'Content-length': str(len(body))}
        req = urllib2.Request(self.repository, body, headers)
        opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler(password_mgr=auth))
        data = ''
        try:
            result = opener.open(req)
        except urllib2.HTTPError as e:
            if self.show_response:
                data = e.fp.read()
            result = (e.code, e.msg)
        except urllib2.URLError as e:
            result = (500, str(e))
        else:
            if self.show_response:
                data = result.read()
            result = (200, 'OK')

        if self.show_response:
            dashes = '-' * 75
            self.announce('%s%s%s' % (dashes, data, dashes))
        return result
