# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/shared/shop_helpers.py
from gui import GUI_SETTINGS
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

def getNewYearOldCollectionRewardUrl():
    return _getNyUrl('newYearOldCollectionRewardUrl')


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _getNyUrl(urlName, lobbyContext=None):
    hostUrl = lobbyContext.getServerSettings().shop.hostUrl
    return hostUrl + GUI_SETTINGS.nyShop.get(urlName, '')
