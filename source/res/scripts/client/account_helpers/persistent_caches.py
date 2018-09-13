# Embedded file name: scripts/client/account_helpers/persistent_caches.py
import BigWorld
import cPickle
import os
import base64
import constants

class SimpleCache(object):

    def __init__(self, cacheType, cacheName, accountName = None):
        self.__cacheType = cacheType
        self.__cacheName = cacheName
        self.__accountName = accountName

    def clear(self):
        try:
            os.remove(self.getFileName())
        except:
            pass

    def setAccount(self, account = None):
        self.__accountName = account.name if account is not None else None
        return

    def setAccountName(self, accountName = None):
        self.__accountName = accountName

    def getAccountName(self):
        return self.__accountName

    def getFileName(self):
        raise self.__accountName is not None or AssertionError
        return cacheFileName(self.__accountName, self.__cacheType, self.__cacheName)

    def get(self):
        return self.__load()

    def getDescr(self):
        return self.__load()[0]

    def getData(self):
        return self.__load()[1]

    def __load(self):
        if self.__accountName is not None:
            try:
                with open(self.getFileName(), 'rb') as f:
                    descr = cPickle.load(f)
                    data = cPickle.load(f)
                    return (descr, data)
            except IOError:
                pass
            except Exception:
                pass

        return (None, None)

    def save(self, descr, data):
        if not self.__accountName is not None:
            raise AssertionError
            return self.__accountName is None and None
        else:
            try:
                with open(self.getFileName(), 'wb') as f:
                    cPickle.dump(descr, f, -1)
                    cPickle.dump(data, f, -1)
                    return True
            except IOError:
                pass

            return False


def cacheFileName(accountName, cacheType, cacheName):
    p = os.path
    prefsFilePath = unicode(BigWorld.wg_getPreferencesFilePath(), 'utf-8', errors='ignore')
    cacheDir = p.join(p.dirname(prefsFilePath), cacheType)
    if not os.path.isdir(cacheDir):
        os.makedirs(cacheDir)
    cacheFileName = p.join(cacheDir, base64.b32encode('%s:%s:%s' % (constants.AUTH_REALM, accountName, cacheName)) + '.dat')
    return cacheFileName


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
