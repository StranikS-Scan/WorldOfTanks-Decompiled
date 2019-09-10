# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/request/wgni_token.py
from constants import TOKEN_TYPE
from gui.shared.utils.requesters import getTokenRequester
from web.web_client_api import w2c, W2CSchema

class WgniTokenWebApiMixin(object):

    @w2c(W2CSchema, 'token1')
    def wgniToken(self, cmd):
        tokenRqs = getTokenRequester(TOKEN_TYPE.WGNI)
        if not tokenRqs.isInProcess():
            response = yield tokenRqs.request(timeout=10.0)
        else:
            response = None
        if response and response.isValid():
            yield {'request_id': 'token1',
             'spa_id': str(response.getDatabaseID()),
             'token': response.getToken()}
        else:
            coolDownExpiration = tokenRqs.getReqCoolDown() - tokenRqs.lastResponseDelta()
            yield {'request_id': 'token1',
             'error': 'Unable to obtain token.',
             'cooldown': coolDownExpiration if coolDownExpiration > 0 else tokenRqs.getReqCoolDown()}
        return
