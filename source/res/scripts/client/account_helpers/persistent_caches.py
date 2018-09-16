# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/persistent_caches.py
import weakref
import cPickle
import os
import base64
import BigWorld
import constants
from soft_exception import SoftException

class SimpleCache(object):

    def __init__(self, cacheType, cacheName):
        self.__cacheType = cacheType
        self.__cacheName = cacheName
        self.__account = None
        self.__memcache = {}
        return

    def clear(self):
        try:
            fileName = self.getFileName()
            self.__memcache.pop(fileName, None)
            os.remove(fileName)
        except Exception:
            pass

        return

    def setAccount(self, account=None):
        self.__account = account and weakref.proxy(account)

    def getAccount(self):
        return self.__account

    def getFileName(self):
        if self.__account is None:
            raise SoftException('Account is not defined')
        return cacheFileName(self.__account, self.__cacheType, self.__cacheName)

    def get(self):
        return self.__load()

    def getDescr(self):
        return self.__load()[0]

    def getData(self):
        return self.__load()[1]

    def __load(self):
        if self.__account is not None:
            fileName = self.getFileName()
            mcacheData = self.__memcache.get(fileName, None)
            if mcacheData:
                return mcacheData
            try:
                with open(fileName, 'rb') as f:
                    descr = cPickle.load(f)
                    data = cPickle.load(f)
                    self.__memcache[fileName] = (descr, data)
                    return (descr, data)
            except IOError:
                pass
            except Exception:
                pass

        return (None, None)

    def save(self, descr, data):
        if self.__account is None:
            return
        else:
            try:
                fileName = self.getFileName()
                self.__memcache[fileName] = (descr, data)
                with open(fileName, 'wb') as f:
                    cPickle.dump(descr, f, -1)
                    cPickle.dump(data, f, -1)
                    return True
            except IOError:
                pass

            return False


def cacheFileName(account, cacheType, cacheName):
    p = os.path
    prefsFilePath = unicode(BigWorld.wg_getPreferencesFilePath(), 'utf-8', errors='ignore')
    cacheDir = p.join(p.dirname(prefsFilePath), cacheType)
    if not os.path.isdir(cacheDir):
        os.makedirs(cacheDir)
    cache = p.join(cacheDir, base64.b32encode('%s_%s_%s_%s' % (constants.AUTH_REALM,
     account.name,
     account.__class__.__name__,
     cacheName)) + '.dat')
    return cache


def readFile(filename):
    ret = None
    try:
        with open(filename, 'rb') as f:
            ret = f.read()
    except IOError:
        return

    return ret


def writeFile(filename, data):
    try:
        with open(filename, 'wb') as f:
            f.write(data)
    except IOError:
        return False

    return True
