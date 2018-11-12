# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/browser/ingameshop_helpers.py
from gui import GUI_SETTINGS, DialogsInterface
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _getUrl(urlName=None, lobbyContext=None):
    return lobbyContext.getServerSettings().ingameShop.hostUrl if urlName is None else lobbyContext.getServerSettings().ingameShop.hostUrl + GUI_SETTINGS.ingameshop.get(urlName)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isIngameShopEnabled(itemsCache=None):
    return itemsCache.items.stats.isIngameShopEnabled


def getWebShopURL():
    return _getUrl()


def getBuyMoreGoldUrl():
    return _getUrl('buyMoreGoldUrl')


def getBuyGoldUrl():
    return _getUrl('buyGoldUrl')


def getBuyPremiumUrl():
    return _getUrl('buyPremiumUrl')


def getBuyBoostersUrl():
    return _getUrl('buyBoosters')


def getBuyBattleBoostersUrl():
    return _getUrl('buyBattleBoosters')


def getBuyEquipmentUrl():
    return _getUrl('buyEquipment')


def getBuyOptionalDevicesUrl():
    return _getUrl('buyOptionalDevices')


def getBuyVehiclesUrl():
    return _getUrl('buyVehiclesUrl')


def getVehicleUrl():
    return _getUrl('buyVehicle')


def getBonsUrl():
    return _getUrl('bonsUrl')


def showDisabledDialog():
    DialogsInterface.showI18nInfoDialog('ingameShopDisabled', None)
    return
