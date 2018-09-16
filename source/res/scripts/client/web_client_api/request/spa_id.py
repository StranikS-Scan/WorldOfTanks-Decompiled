# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/request/spa_id.py
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from web_client_api import w2c, W2CSchema

class SpaIdWebApiMixin(object):
    connectionMgr = dependency.descriptor(IConnectionManager)

    @w2c(W2CSchema, 'spa_id')
    def spaId(self, cmd):
        if self.connectionMgr is not None:
            yield {'spa_id': str(self.connectionMgr.databaseID)}
        else:
            yield {'error': 'Unable to obtain spa id'}
        return
