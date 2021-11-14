# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/wgnp/demo_account/request.py
from constants import WG_GAMES
from gui.platform.base.request import Params, ContentType
from gui.platform.wgnp.demo_account.response import WGNPDemoAccCredentialsAddResponse, WGNPDemoAccCredentialsConfirmResponse, WGNPDemoAccChangeNicknameResponse, WGNPDemoAccValidateNicknameResponse

class CredentialsStatusParams(Params):
    url = './personal/api/v2/account/credentials/basic/create/'
    method = 'GET'


class AddCredentialsParams(Params):
    response = WGNPDemoAccCredentialsAddResponse
    url = './personal/api/v2/account/credentials/basic/create/'
    headers = {'Content-Type': ContentType.FORM_URLENCODED.value}
    proofOfWorkURL = './personal/api/v2/account/credentials/basic/create/challenge/?type=pow'
    method = 'POST'
    queryParams = {'type': 'pow'}
    postData = {'game': WG_GAMES.TANKS}

    def __init__(self, urlHost, login, password):
        super(AddCredentialsParams, self).__init__(urlHost)
        self.postData['login'] = login
        self.postData['password'] = password


class ConfirmCredentialsParams(Params):
    response = WGNPDemoAccCredentialsConfirmResponse
    url = './personal/api/v2/account/credentials/basic/activate/'
    headers = {'Content-Type': ContentType.FORM_URLENCODED.value}
    method = 'POST'
    postData = {'game': WG_GAMES.TANKS}

    def __init__(self, urlHost, code):
        super(ConfirmCredentialsParams, self).__init__(urlHost)
        self.postData['code'] = code


class NicknameStatusParams(Params):
    url = './personal/api/v2/account/name/update/state/'
    method = 'POST'


class ValidateNicknameParams(Params):
    response = WGNPDemoAccValidateNicknameResponse
    headers = {'Content-Type': ContentType.FORM_URLENCODED.value}
    url = './personal/account/nicknames/{nickname}/'
    postData = {'suggestions': 1,
     'use_pattern': 1}
    method = 'POST'
    auth = False
    addUserAgentHeader = False

    def __init__(self, urlHost, nickname):
        super(ValidateNicknameParams, self).__init__(urlHost)
        self.url = self.url.format(nickname=nickname)


class ChangeNicknameParams(Params):
    response = WGNPDemoAccChangeNicknameResponse
    url = './personal/api/v2/account/name/update/'
    headers = {'Content-Type': ContentType.FORM_URLENCODED.value}
    method = 'POST'
    postData = {'game': WG_GAMES.TANKS,
     'via': WG_GAMES.TANKS}

    def __init__(self, urlHost, nickname, cost):
        super(ChangeNicknameParams, self).__init__(urlHost)
        self.postData['name'] = nickname
        self.postData['cost'] = cost
