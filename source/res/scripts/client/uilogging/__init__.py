# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/__init__.py
import constants
DISABLE_TEST_MODE = False
TEST_REALM = 'kis10'

def getKafkaHost():
    if not DISABLE_TEST_MODE and constants.IS_DEVELOPMENT:
        return 'https://wotuilog-%s.wgtest.net/ui/log/' % (TEST_REALM,)
    elif constants.IS_KOREA:
        return None
    elif constants.CURRENT_REALM not in constants.REGIONAL_REALMS:
        return None
    else:
        return 'https://wotuilog-cn.wggames.cn/ui/log/' if constants.IS_CHINA else 'https://wotuilog-%s.wargaming.net/ui/log/' % (constants.CURRENT_REALM.lower(),)


def getAPIHost():
    if not DISABLE_TEST_MODE and constants.IS_DEVELOPMENT:
        return 'https://api-wotuilog-%s.wgtest.net/api/features/' % (TEST_REALM,)
    elif constants.IS_KOREA:
        return None
    elif constants.CURRENT_REALM not in constants.REGIONAL_REALMS:
        return None
    else:
        return 'https://api-wotuilog-cn.wggames.cn/api/features/' if constants.IS_CHINA else 'https://api-wotuilog-%s.wargaming.net/api/features/' % (constants.CURRENT_REALM.lower(),)


class Settings(object):

    def __init__(self):
        self.requestTimeout = 10
        self.httpMethod = 'POST'
        self.host = getKafkaHost()
        self.apiHost = getAPIHost()
        self.testMode = not DISABLE_TEST_MODE and constants.IS_DEVELOPMENT
        self.realm = constants.CURRENT_REALM
        self.headers = {'Content-Type': 'application/json'}

    @property
    def hostsDefined(self):
        return self.host is not None and self.apiHost is not None


loggingSettings = Settings()
