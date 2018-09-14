# Embedded file name: scripts/client/gui/login/Preferences.py
import json
from predefined_hosts import AUTO_LOGIN_QUERY_URL
import BigWorld
import Settings
from debug_utils import LOG_DEBUG, LOG_WARNING

class Preferences(dict):

    def __init__(self):
        dict.__init__(self)
        self.__oldFormat = False
        preferences = Settings.g_instance.userPrefs
        if not preferences.has_key(Settings.KEY_LOGIN_INFO):
            preferences.write(Settings.KEY_LOGIN_INFO, '')
        elif preferences[Settings.KEY_LOGIN_INFO].readString('login', ''):
            self.__oldFormat = True
            self.__readOldPreferencesFormat(preferences[Settings.KEY_LOGIN_INFO])
            LOG_DEBUG('Read old format preferences: {0}'.format(self))
        else:
            try:
                loginInfo = json.loads(BigWorld.wg_ucpdata(preferences[Settings.KEY_LOGIN_INFO].readString('data', '')), encoding='utf-8')
                self.update(loginInfo)
                LOG_DEBUG('Read login info from preferences.xml: {0}'.format(self))
            except ValueError:
                LOG_WARNING('Ignoring login info from preferences.xml')

    def writeLoginInfo(self):
        LOG_DEBUG('Wrote login info into preferences.xml: {0}'.format(self))
        if self.__oldFormat:
            Settings.g_instance.userPrefs.deleteSection(Settings.KEY_LOGIN_INFO)
            Settings.g_instance.userPrefs.write(Settings.KEY_LOGIN_INFO, '')
            self.__oldFormat = False
        Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO].writeString('data', BigWorld.wg_cpdata(json.dumps(dict(self), encoding='utf-8')))

    def __readOldPreferencesFormat(self, loginInfo):
        self['login'] = BigWorld.wg_ucpdata(loginInfo.readString('login', ''))
        self['remember_user'] = loginInfo.readBool('rememberPwd', False)
        if self['remember_user']:
            pwdLengthToken2 = BigWorld.wg_ucpdata(loginInfo.readString('token2'))
            if pwdLengthToken2:
                self['password_length'] = int(pwdLengthToken2.split(':')[0])
                self['token2'] = pwdLengthToken2.split(':', 1)[1]
        lastLoginType = loginInfo.readString('lastLoginType', 'basic')
        if lastLoginType == 'basic':
            lastLoginType = 'credentials'
        self['login_type'] = lastLoginType
        self['session'] = BigWorld.wg_cpsalt(loginInfo.readString('salt', ''))
        self['name'] = loginInfo.readString('user', '')

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            if key == 'remember_user':
                return False
            elif key == 'server_name':
                return AUTO_LOGIN_QUERY_URL
            elif key == 'login_type':
                return 'credentials'
            elif key == 'password_length':
                return 0
            else:
                return ''
