# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/__init__.py
import constants
DISABLE_TEST_MODE = False
TEST_REALM = 'kis10'

def getKafkaHost():
    return 'https://wotuilog-%s.wgtest.net/ui/log/' % (TEST_REALM,) if not DISABLE_TEST_MODE and constants.IS_DEVELOPMENT else 'https://wotuilog.%s.wargaming.net/ui/log/' % (constants.CURRENT_REALM.lower(),)


def getAPIHost():
    return 'https://api-wotuilog-%s.wgtest.net/api/features/' % (TEST_REALM,) if not DISABLE_TEST_MODE and constants.IS_DEVELOPMENT else 'https://api.wotuilog.%s.wargaming.net/api/features/' % (constants.CURRENT_REALM.lower(),)


class Settings(object):

    def __init__(self):
        self.requestTimeout = 30
        self.httpMethod = 'POST'
        self.host = getKafkaHost()
        self.apiHost = getAPIHost()
        self.testMode = not DISABLE_TEST_MODE and constants.IS_DEVELOPMENT
        self.realm = constants.CURRENT_REALM
        self.headers = {'Content-Type': 'application/json'}


loggingSettings = Settings()
