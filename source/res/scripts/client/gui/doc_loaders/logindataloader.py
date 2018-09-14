# Embedded file name: scripts/client/gui/doc_loaders/LoginDataLoader.py
import BigWorld
import Settings
from gui import GUI_SETTINGS
from debug_utils import LOG_CURRENT_EXCEPTION
from Event import Event
from helpers.obfuscators import PasswordObfuscator
from external_strings_utils import _PASSWORD_MAX_LENGTH
__author__ = 'd_trofimov'

class LoginDataLoader(object):
    LOGIN_TAG = 'login'
    TOKEN2_TAG = 'token2'
    PWD_SECTION = 'pwd'
    HOST_TAG = 'host'
    PASSWORD_TAG = 'password'
    REMEMBER_PWD_TAG = 'rememberPwd'

    def __init__(self):
        super(LoginDataLoader, self).__init__()
        self.__host = ''
        self.__token2 = ''
        self.__user = ''
        self.__rememberPwd = False
        self.__passLength = 0
        self.onConfigLoaded = Event()

    def get_host(self):
        return self.__host

    def set_host(self, host):
        self.__host = host

    host = property(get_host, set_host)

    def get_token2(self):
        return self.__token2

    def set_token2(self, token2):
        self.__token2 = token2

    token2 = property(get_token2, set_token2)

    def get_user(self):
        return self.__user

    def set_user(self, user):
        self.__user = user

    user = property(get_user, set_user)

    def get_rememberPwd(self):
        return self.__rememberPwd

    def set_rememberPwd(self, rememberPwd):
        self.__rememberPwd = rememberPwd

    rememberPwd = property(get_rememberPwd, set_rememberPwd)

    def get_passLength(self):
        return self.__passLength

    def set_passLength(self, passLength):
        self.__passLength = passLength

    passLength = property(get_passLength, set_passLength)

    def loadUserConfig(self):
        ds = self.__getUserLoginSection()
        isRememberPwd = GUI_SETTINGS.rememberPassVisible
        password = ''
        self.__rememberPwd = False
        if isRememberPwd:
            self.__rememberPwd = ds.readBool(self.REMEMBER_PWD_TAG, False)
        if ds:
            if GUI_SETTINGS.clearLoginValue:
                ds.writeString(self.LOGIN_TAG, '')
            self.__user = self.__getUserLoginName(ds)
            self.__host = ds.readString(self.HOST_TAG)
            decrypt = getattr(BigWorld, 'wg_ucpdata', None)
            if self.PASSWORD_TAG in ds.keys():
                password = ds.readString(self.PASSWORD_TAG)
                decrypt = PasswordObfuscator().unobfuscate
            else:
                password = ds.readString(self.PWD_SECTION)
            if not isRememberPwd:
                self.__rememberPwd = False
                password = ''
            elif len(password) > 0 and self.REMEMBER_PWD_TAG not in ds.keys():
                self.__rememberPwd = True
            else:
                self.__rememberPwd = ds.readBool(self.REMEMBER_PWD_TAG, False)
            if self.__rememberPwd and decrypt is not None:
                try:
                    password = decrypt(password)
                except (TypeError, AttributeError):
                    LOG_CURRENT_EXCEPTION()

            if self.TOKEN2_TAG in ds.keys():
                token2 = BigWorld.wg_ucpdata(ds.readString(self.TOKEN2_TAG))
                if len(token2):
                    separatorPos = token2.find(':')
                    if separatorPos > 0:
                        try:
                            self.__passLength = int(token2[:separatorPos])
                        except ValueError:
                            self.__passLength = self.DEFAULT_PASS_LENGTH

                        self.__passLength = min(self.__passLength, _PASSWORD_MAX_LENGTH)
                        self.__token2 = token2[separatorPos + 1:]
                        password = '*' * self.__passLength
                    else:
                        self.__token2 = ''
        self.onConfigLoaded(self.__user, password, self.__rememberPwd, isRememberPwd)
        return

    def saveUserConfig(self, user, host):
        li = self.__getUserLoginSection()
        li.writeString(self.LOGIN_TAG, BigWorld.wg_cpdata(user) if not GUI_SETTINGS.clearLoginValue else '')
        li.writeBool(self.REMEMBER_PWD_TAG, self.__rememberPwd if GUI_SETTINGS.rememberPassVisible else False)
        li.writeString(self.HOST_TAG, host)
        self.saveUserToken(self.__passLength, self.__token2)
        Settings.g_instance.save()

    def saveUserToken(self, passwordLength, token2):
        ds = Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO]
        rememberPwd = GUI_SETTINGS.rememberPassVisible and ds.readBool(self.REMEMBER_PWD_TAG, False)
        li = self.__getUserLoginSection()
        if len(token2):
            token2 = '%d:%s' % (passwordLength, token2)
        if self.PWD_SECTION in li.keys():
            li.deleteSection(self.PWD_SECTION)
        if GUI_SETTINGS.igrCredentialsReset and not rememberPwd:
            li.writeString(self.LOGIN_TAG, '')
        li.writeString(self.TOKEN2_TAG, BigWorld.wg_cpdata(token2) if rememberPwd else '')

    def __getUserLoginName(self, loginInfoSection):
        userLogin = ''
        if self.LOGIN_TAG in loginInfoSection.keys() and loginInfoSection.readString(self.LOGIN_TAG, ''):
            userLogin = BigWorld.wg_ucpdata(loginInfoSection.readString(self.LOGIN_TAG, ''))
        return userLogin

    def __getUserLoginSection(self):
        up = Settings.g_instance.userPrefs
        if up.has_key(Settings.KEY_LOGIN_INFO):
            return up[Settings.KEY_LOGIN_INFO]
        else:
            return up.write(Settings.KEY_LOGIN_INFO, '')
