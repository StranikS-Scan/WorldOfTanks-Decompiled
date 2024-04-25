# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/referral_program/referral_program_helpers.py
from gui import GUI_SETTINGS
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
REF_RPOGRAM_PDATA_KEY = 'refProgram'
RECRUITER_ID_ATTR = 'recruiterId'

def _getUrl(urlName=None):
    return getReferralProgramURL() if urlName is None else getReferralProgramURL() + GUI_SETTINGS.referralProgram.get(urlName)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def isReferralProgramEnabled(lobbyContext=None):
    return lobbyContext and lobbyContext.getServerSettings().isReferralProgramEnabled()


def getReferralProgramURL():
    return GUI_SETTINGS.referralProgram.get('baseUrl')


def getObtainVehicleURL():
    return _getUrl('getVehicle')


def getReferralShopURL():
    return _getUrl('referralShop')


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isCurrentUserRecruit(itemsCache=None):
    return bool(itemsCache.items.stats.refSystem20.get(RECRUITER_ID_ATTR, False))
