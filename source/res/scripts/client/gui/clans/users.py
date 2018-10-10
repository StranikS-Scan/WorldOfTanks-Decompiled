# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/users.py
import weakref
from adisp import async, process
from gui.wgcg.clan.contexts import AccountClanRatingsCtx

class UserCache(object):

    def __init__(self, clanCtrl):
        super(UserCache, self).__init__()
        self.__cache = dict()
        self.__clanCtrl = weakref.proxy(clanCtrl)

    @async
    @process
    def requestUsers(self, dbIDs, callback):
        status = True
        missingUser = [ usrID for usrID in dbIDs if usrID not in self.__cache ]
        if missingUser:
            usrCtx = AccountClanRatingsCtx(missingUser)
            result = yield self.__clanCtrl.sendRequest(usrCtx, allowDelay=True)
            if result.isSuccess():
                ratingsData = usrCtx.getDataObj(result.data)
                for key, item in ratingsData.iteritems():
                    self.__cache[key] = item

            else:
                status = False
        users = dict(((usrID, self.__cache[usrID]) for usrID in dbIDs if usrID in self.__cache))
        callback((status, users))
