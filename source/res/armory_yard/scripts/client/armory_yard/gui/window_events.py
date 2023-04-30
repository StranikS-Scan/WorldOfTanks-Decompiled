# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/window_events.py
import logging
import typing
from CurrentVehicle import HeroTankPreviewAppearance
from frameworks.wulf import WindowFlags, WindowLayer, ViewFlags
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shop import showBuyGoldWebOverlay, Source
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController
from skeletons.gui.impl import INotificationWindowController
if typing.TYPE_CHECKING:
    from gui.shared.gui_items import Vehicle
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showArmoryYardRewardWindow(bonuses, state, stage=0, closeCallback=None, showImmediately=True, notificationMgr=None):
    from armory_yard.gui.impl.lobby.feature.armory_yard_rewards_view import ArmoryYardRewardsWindow
    window = ArmoryYardRewardsWindow(bonuses, state, stage, closeCallback)
    if showImmediately:
        window.load()
    else:
        notificationMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(armoryYard=IArmoryYardController)
def showArmoryYardBuyWindow(armoryYard=None, parent=None, isBlurEnabled=False, onLoadedCallback=None):
    from armory_yard.gui.impl.lobby.feature.armory_yard_buy_view import ArmoryYardBuyWindow
    if armoryYard.isActive():
        window = ArmoryYardBuyWindow(parent=parent, isBlurEnabled=isBlurEnabled, onLoadedCallback=onLoadedCallback)
        window.load()


def showArmoryYardVideoRewardWindow(vehicle):
    from armory_yard.gui.impl.lobby.feature.armory_yard_video_reward_view import ArmoryYardVideoRewardWindow
    if vehicle is None:
        _logger.error("Armory yard reward video isn't shown. Vehicle is None")
    else:
        window = ArmoryYardVideoRewardWindow(vehicle)
        window.load()
    return


@dependency.replace_none_kwargs(armoryYard=IArmoryYardController)
def showArmoryYardIntroWindow(closeCallback=None, parent=None, armoryYard=None, loadedCallback=None):
    from armory_yard.gui.impl.lobby.feature.armory_yard_intro_view import ArmoryYardIntroWindow
    finalRewardVehicle = armoryYard.getFinalRewardVehicle()
    if finalRewardVehicle:
        window = ArmoryYardIntroWindow(finalRewardVehicle, closeCallback, parent=parent, loadedCallback=loadedCallback)
        window.load()
    else:
        _logger.error("Final reward isn't found. Please check reward config")


def showBuyGoldForArmoryYard(goldPrice):
    params = {'reason': '',
     'goldPrice': goldPrice,
     'source': Source.EXTERNAL}
    showBuyGoldWebOverlay(params)


def showArmoryYardVehiclePreview(vehTypeCompDescr, showHeroTankText=False, backToHangar=False, isHeroTank=False, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, previewBackCb=None, backBtnLabel=None):
    previewAppearance = None
    if backToHangar:
        previewAppearance = HeroTankPreviewAppearance()
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(HANGAR_ALIASES.ARMORY_YARD_VEHICLE_PREVIEW), ctx={'itemCD': vehTypeCompDescr,
     'previewAppearance': previewAppearance,
     'previewBackCb': previewBackCb,
     'backBtnLabel': backBtnLabel,
     'previewAlias': previewAlias,
     'showHeroTankText': showHeroTankText,
     'isHeroTank': isHeroTank}), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def _createArmoryYardBrowserView(url, viewFlags, returnClb=None):
    from gui.impl.lobby.common.browser_view import BrowserView, makeSettings
    from web.web_client_api import webApiCollection, ui, sound, request
    webHandlers = webApiCollection(request.RequestWebApi, ui.OpenWindowWebApi, ui.CloseWindowWebApi, ui.OpenTabWebApi, ui.UtilWebApi, sound.SoundWebApi, sound.HangarSoundWebApi)
    settings = makeSettings(url=url, webHandlers=webHandlers, viewFlags=viewFlags, restoreBackground=True, returnClb=returnClb)
    return BrowserView(R.views.lobby.common.BrowserView(), settings)


@dependency.replace_none_kwargs(armoryYard=IArmoryYardController)
def showArmoryYardIntroVideo(parent=None, armoryYard=None):
    window = LobbyWindow(content=_createArmoryYardBrowserView(url=armoryYard.serverSettings.getModeSettings().introVideoLink, viewFlags=ViewFlags.VIEW), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, parent=parent, layer=WindowLayer.OVERLAY)
    window.load()


@dependency.replace_none_kwargs(armoryYard=IArmoryYardController)
def showArmoryYardInfoPage(parent=None, closeCallback=None, armoryYard=None):
    window = LobbyWindow(content=_createArmoryYardBrowserView(url=armoryYard.serverSettings.getModeSettings().infoPageLink, viewFlags=ViewFlags.LOBBY_TOP_SUB_VIEW, returnClb=closeCallback), wndFlags=WindowFlags.WINDOW, parent=parent, layer=WindowLayer.TOP_SUB_VIEW)
    window.load()


def showArmoryYardWaiting():
    if not Waiting.isOpened('loadArmoryYard'):
        Waiting.show('loadArmoryYard', showSparks=False, isSingle=True, backgroundImage=backport.image(R.images.gui.maps.icons.lobby.ay_loading_bg()))


def hideArmoryYardWaiting():
    if Waiting.isOpened('loadArmoryYard'):
        Waiting.hide('loadArmoryYard')
