# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/lobby/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.framework import ComponentSettings, ScopeTemplates, ViewSettings, GroupedViewSettings
from gui.Scaleform.framework import getSwfExtensionUrl
from gui.impl import backport
from gui.impl.gen import R
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_HANGAR_ALIASES import WHITE_TIGER_HANGAR_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from white_tiger.gui.Scaleform.daapi.view.lobby.hangar.carousel.tank_carousel import WhiteTigerTankCarousel
    from white_tiger.gui.Scaleform.daapi.view.lobby.hangar.prime_time.white_tiger_prime_time_view import WhiteTigerPrimeTimeView
    from white_tiger.gui.Scaleform.daapi.view.lobby.battle_queue import BattleQueue
    from white_tiger.gui.Scaleform.daapi.view.common.settings.settings_window import WhiteTigerSettingsWindow
    from white_tiger.gui.impl.lobby.hangar_view import HangarWindow
    from white_tiger.gui.impl.lobby.feature.white_tiger_battle_results_view import WhiteTigerBattleResultsWindow
    return (ViewSettings(WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_HANGAR, HangarWindow, '', WindowLayer.SUB_VIEW, WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_HANGAR, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_PRIME_TIME_ALIAS, WhiteTigerPrimeTimeView, getSwfExtensionUrl('white_tiger', WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_PRIME_TIME), WindowLayer.TOP_SUB_VIEW, WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_PRIME_TIME_ALIAS, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),
     ViewSettings(WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_QUEUE_SCREEN, BattleQueue, getSwfExtensionUrl('white_tiger', 'whiteTigerBattleQueue.swf'), WindowLayer.TOP_SUB_VIEW, WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_QUEUE_SCREEN, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_TANK_CAROUSEL, WhiteTigerTankCarousel, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_SETTINGS_WINDOW, WhiteTigerSettingsWindow, getSwfExtensionUrl('white_tiger', 'whiteTigerSettingsWindow.swf'), WindowLayer.TOP_WINDOW, WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_SETTINGS_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     ViewSettings(WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_BATTLE_RESULT, WhiteTigerBattleResultsWindow, '', WindowLayer.SUB_VIEW, WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_BATTLE_RESULT, ScopeTemplates.LOBBY_SUB_SCOPE))


def getBusinessHandlers():
    return (WhiteTigerPackageBusinessHandler(), WhiteTigerPackageGlobalBusinessHandler())


class WhiteTigerPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_HANGAR, self.loadViewByCtxEvent), (WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_QUEUE_SCREEN, self.loadViewByCtxEvent), (WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_BATTLE_RESULT, self.loadView))
        super(WhiteTigerPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)


class WhiteTigerPackageGlobalBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_SETTINGS_WINDOW, self.loadViewByCtxEvent),)
        super(WhiteTigerPackageGlobalBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.GLOBAL)


def getTypeBigWtIconRPath(vTypeName):
    resImgId = R.images.gui.maps.icons.vehicleTypes.big
    return _getVehicleTypeImage(resImgId, vTypeName)


def getTypeWhiteWtIconRPath(vTypeName):
    resImgId = R.images.gui.maps.icons.vehicleTypes.white
    return _getVehicleTypeImage(resImgId, vTypeName)


def _getVehicleTypeImage(resImgId, vTypeName):
    imgId = resImgId.dyn(vTypeName)()
    return backport.image(imgId).replace('img://gui/', '../') if imgId != -1 else ''
