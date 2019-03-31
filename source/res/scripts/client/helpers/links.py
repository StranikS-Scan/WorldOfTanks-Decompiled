# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/links.py
# Compiled at: 2019-03-14 16:45:53
import BigWorld
import ResMgr
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR

def getPaymentWebsiteURL():
    pass


def openPaymentWebsite():
    try:
        url = getPaymentWebsiteURL()
        if len(url) > 0:
            BigWorld.wg_openWebBrowser(url)
        else:
            LOG_ERROR('Payment website url is empty.Check tag <paymentURL> in the "text/settings.xml".')
    except Exception:
        LOG_CURRENT_EXCEPTION()


def openFinPasswordWebsite():
    try:
        url = 'http://game.worldoftanks.ru/'
        ds = ResMgr.openSection('text/settings.xml')
        if ds is not None:
            url = ds.readString('finPasswordURL')
        BigWorld.wg_openWebBrowser(url)
    except Exception:
        LOG_CURRENT_EXCEPTION()

    return


def openMigrationWebsite(login):
    try:
        url = 'http://game.worldoftanks.ru/migration/%s'
        ds = ResMgr.openSection('text/settings.xml')
        if ds is not None:
            url = ds.readString('migrationURL')
        BigWorld.wg_openWebBrowser(url % login)
    except Exception:
        LOG_CURRENT_EXCEPTION()

    return
