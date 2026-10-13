# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/persistent_caches.py
from __future__ import absolute_import
import weakref
import os
from future.moves import pickle
import BigWorld
import constants
from external_strings_utils import unicode_from_utf8
from py2to3.compat import base64compat
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
                    descr = pickle.load(f)
                    data = pickle.load(f)
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
                    pickle.dump(descr, f, -1)
                    pickle.dump(data, f, -1)
                    return True
            except IOError:
                pass

            return False


def cacheFileName(account, cacheType, cacheName):
    p = os.path
    prefsFilePath = unicode_from_utf8(BigWorld.wg_getPreferencesFilePath())[1]
    cacheDir = p.join(p.dirname(prefsFilePath), cacheType)
    if not os.path.isdir(cacheDir):
        os.makedirs(cacheDir)
    uniquePath = '%s_%s_%s_%s' % (constants.AUTH_REALM,
     account.name,
     account.__class__.__name__,
     cacheName)
    cache = p.join(cacheDir, base64compat.b32encode(uniquePath) + '.dat')
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
