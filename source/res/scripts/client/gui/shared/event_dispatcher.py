# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/event_dispatcher.py
import urlparse
from adisp import process
from debug_utils import LOG_WARNING
from gui import SystemMessages
from CurrentVehicle import HeroTankPreviewAppearance
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.app_loader import g_appLoader
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nInfoDialogMeta
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import getWebShopURL, isIngameShopEnabled
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.prb_control.settings import CTRL_ENTITY_TYPE
from gui.shared import events, g_eventBus
from gui.shared.money import MONEY_UNDEFINED
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import isPopupsWindowsOpenDisabled
from gui.shared.utils.functions import getViewName, getUniqueViewName
from helpers import dependency
from helpers.aop import pointcutable
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IHeroTankController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from soft_exception import SoftException

class SETTINGS_TAB_INDEX(object):
    GAME = 0
    GRAPHICS = 1
    SOUND = 2
    CONTROL = 3
    AIM = 4
    MARKERS = 5
    FEEDBACK = 6


def showBattleResultsWindow(arenaUniqueID):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BATTLE_RESULTS, getViewName(VIEW_ALIAS.BATTLE_RESULTS, str(arenaUniqueID)), {'arenaUniqueID': arenaUniqueID}), EVENT_BUS_SCOPE.LOBBY)


def notifyBattleResultsPosted(arenaUniqueID):
    g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.BATTLE_RESULTS_POSTED, {'arenaUniqueID': arenaUniqueID}), EVENT_BUS_SCOPE.LOBBY)


def showRankedBattleResultsWindow(rankedResultsVO, vehicle, rankInfo, questsProgress):
    g_eventBus.handleEvent(events.LoadViewEvent(alias=RANKEDBATTLES_ALIASES.RANKED_BATTLES_BATTLE_RESULTS, ctx={'rankedResultsVO': rankedResultsVO,
     'vehicle': vehicle,
     'rankInfo': rankInfo,
     'questsProgress': questsProgress}), EVENT_BUS_SCOPE.LOBBY)


def showRankedAwardWindow(rankID, vehicle=None, awards=None):
    g_eventBus.handleEvent(events.LoadViewEvent(alias=RANKEDBATTLES_ALIASES.RANKED_BATTLES_AWARD, ctx={'rankID': rankID,
     'vehicle': vehicle,
     'awards': awards}), EVENT_BUS_SCOPE.LOBBY)


def showRankedPrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(alias=RANKEDBATTLES_ALIASES.RANKED_BATTLE_PRIME_TIME, ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showEpicBattlesPrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(alias=EPICBATTLES_ALIASES.EPIC_BATTLES_PRIME_TIME_ALIAS, ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showEpicBattlesAfterBattleWindow(reusableInfo):
    g_eventBus.handleEvent(events.LoadViewEvent(alias=EPICBATTLES_ALIASES.EPIC_BATTLES_AFTER_BATTLE_ALIAS, ctx={'reusableInfo': reusableInfo}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleInfo(vehTypeCompDescr):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_INFO_WINDOW, getViewName(VIEW_ALIAS.VEHICLE_INFO_WINDOW, int(vehTypeCompDescr)), ctx={'vehicleCompactDescr': int(vehTypeCompDescr)}), EVENT_BUS_SCOPE.LOBBY)


def showModuleInfo(itemCD, vehicleDescr):
    itemCD = int(itemCD)
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.MODULE_INFO_WINDOW, getViewName(VIEW_ALIAS.MODULE_INFO_WINDOW, itemCD), {'moduleCompactDescr': itemCD,
     'vehicleDescr': vehicleDescr}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleSellDialog(vehInvID):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_SELL_DIALOG, ctx={'vehInvID': int(vehInvID)}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleBuyDialog(vehicle, isTradeIn=False, previousAlias=None):
    from gui.impl.views.lobby.buy_vehicle_view import BuyVehicleWindow
    ctx = {'nationID': vehicle.nationID,
     'itemID': vehicle.innationID,
     'isTradeIn': isTradeIn,
     'previousAlias': previousAlias}
    window = BuyVehicleWindow(ctx=ctx)
    window.load()


def showBattleBoosterBuyDialog(battleBoosterIntCD, install=False):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOSTER_BUY_WINDOW, ctx={'typeCompDescr': battleBoosterIntCD,
     'install': install}), EVENT_BUS_SCOPE.LOBBY)


def showResearchView(vehTypeCompDescr, exitEvent=None):
    exitEvent = exitEvent or events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR)
    loadEvent = events.LoadViewEvent(VIEW_ALIAS.LOBBY_RESEARCH, ctx={'rootCD': vehTypeCompDescr,
     'exit': exitEvent})
    g_eventBus.handleEvent(loadEvent, scope=EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def showTechTree(vehTypeCompDescr=None, itemsCache=None):
    vehicle = itemsCache.items.getItemByCD(vehTypeCompDescr)
    nation = vehicle.nationName
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_TECHTREE, ctx={'nation': nation}), scope=EVENT_BUS_SCOPE.LOBBY)


def showVehicleStats(vehTypeCompDescr):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_PROFILE, ctx={'itemCD': vehTypeCompDescr}), scope=EVENT_BUS_SCOPE.LOBBY)


def showHangar():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)


def showBarracks():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_BARRACKS), scope=EVENT_BUS_SCOPE.LOBBY)


def showBadges():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BADGES_PAGE), scope=EVENT_BUS_SCOPE.LOBBY)


def showStrongholds():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_STRONGHOLD), scope=EVENT_BUS_SCOPE.LOBBY)


def openManualPage(chapterIndex):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.MANUAL_CHAPTER_VIEW, ctx={'chapterIndex': chapterIndex}), EVENT_BUS_SCOPE.LOBBY)


def showWebShop(url=None, customPath=None):
    app = g_appLoader.getApp()
    if url is None:
        url = getWebShopURL()
        if customPath is not None:
            url = urlparse.urljoin(url, customPath)
    if app is not None and app.containerManager is not None:
        viewKey = ViewKey(VIEW_ALIAS.LOBBY_STORE)
        browserWindow = app.containerManager.getViewByKey(viewKey)
        if browserWindow is not None:
            browserWindow.destroy()
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_STORE, ctx={'url': url}), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def showOldShop(ctx=None):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_STORE_OLD, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def showStorage(defaultSection=STORAGE_CONSTANTS.FOR_SELL):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_STORAGE, ctx={'defaultSection': defaultSection}), scope=EVENT_BUS_SCOPE.LOBBY)


def showOldVehiclePreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, vehStrCD=None, previewBackCb=None):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_PREVIEW, ctx={'itemCD': vehTypeCompDescr,
     'previewAlias': previewAlias,
     'vehicleStrCD': vehStrCD,
     'previewBackCb': previewBackCb}), scope=EVENT_BUS_SCOPE.LOBBY)


def showVehiclePreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, vehStrCD=None, previewBackCb=None, itemsPack=None, price=MONEY_UNDEFINED, oldPrice=None, title='', endTime=None, buyParams=None):
    heroTankCtrl = dependency.instance(IHeroTankController)
    heroTankCD = heroTankCtrl.getCurrentTankCD()
    if heroTankCD and heroTankCD == vehTypeCompDescr:
        goToHeroTankOnScene(vehTypeCompDescr, previewAlias)
    else:
        lobbyContext = dependency.instance(ILobbyContext)
        if lobbyContext.getServerSettings().isIngamePreviewEnabled():
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_PREVIEW_20, ctx={'itemCD': vehTypeCompDescr,
             'previewAlias': previewAlias,
             'vehicleStrCD': vehStrCD,
             'previewBackCb': previewBackCb,
             'itemsPack': itemsPack,
             'price': price,
             'oldPrice': oldPrice,
             'title': title,
             'endTime': endTime,
             'buyParams': buyParams}), scope=EVENT_BUS_SCOPE.LOBBY)
        elif itemsPack:
            SystemMessages.pushMessage(text=_ms(MESSENGER.CLIENT_ERROR_SHARED_TRY_LATER), type=SystemMessages.SM_TYPE.Error, priority=NotificationPriorityLevel.MEDIUM)
        else:
            showOldVehiclePreview(vehTypeCompDescr, previewAlias, vehStrCD, previewBackCb)


def goToHeroTankOnScene(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR):
    import BigWorld
    from HeroTank import HeroTank
    from ClientSelectableCameraObject import ClientSelectableCameraObject
    for entity in BigWorld.entities.values():
        if entity and isinstance(entity, HeroTank):
            ClientSelectableCameraObject.switchCamera(entity)
            showHeroTankPreview(vehTypeCompDescr, previewAlias=previewAlias, previousBackAlias=None, objectSelectionEnabled=False)
            break

    return


def showHeroTankPreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, previousBackAlias=None, objectSelectionEnabled=True):
    lobbyContext = dependency.instance(ILobbyContext)
    if lobbyContext.getServerSettings().isIngamePreviewEnabled():
        alias = VIEW_ALIAS.HERO_VEHICLE_PREVIEW_20
    else:
        alias = VIEW_ALIAS.HERO_VEHICLE_PREVIEW
    g_eventBus.handleEvent(events.LoadViewEvent(alias, ctx={'itemCD': vehTypeCompDescr,
     'previewAlias': previewAlias,
     'previewAppearance': HeroTankPreviewAppearance(),
     'isHeroTank': True,
     'previousBackAlias': previousBackAlias,
     'objectSelectionEnabled': objectSelectionEnabled}), scope=EVENT_BUS_SCOPE.LOBBY)


def hideVehiclePreview():
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_VEHICLE_PREVIEW), scope=EVENT_BUS_SCOPE.LOBBY)


def hideBattleResults():
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_BATTLE_RESULT_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)


def hideWebBrowser(browserID=None):
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_BROWSER_WINDOW, ctx={'browserID': browserID}), scope=EVENT_BUS_SCOPE.LOBBY)


def showAwardWindow(award, isUniqueName=True):
    if isPopupsWindowsOpenDisabled():
        LOG_WARNING('Award popup disabled', award, isUniqueName)
        return
    if isUniqueName:
        name = getUniqueViewName(VIEW_ALIAS.AWARD_WINDOW)
    else:
        name = VIEW_ALIAS.AWARD_WINDOW
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.AWARD_WINDOW, name=name, ctx={'award': award}), EVENT_BUS_SCOPE.LOBBY)


def showMissionAwardWindow(award):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.MISSION_AWARD_WINDOW, name=getUniqueViewName(VIEW_ALIAS.MISSION_AWARD_WINDOW), ctx={'award': award}), EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionsQuestAwardScreen(quest, ctx, proxyEvent):
    alias = PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_QUEST_AWARD_SCREEN_ALIAS
    g_eventBus.handleEvent(events.LoadViewEvent(alias, name=getUniqueViewName(alias), ctx={'quest': quest,
     'ctxData': ctx,
     'proxyEvent': proxyEvent}), EVENT_BUS_SCOPE.LOBBY)


def showProfileWindow(databaseID, userName):
    alias = VIEW_ALIAS.PROFILE_WINDOW
    g_eventBus.handleEvent(events.LoadViewEvent(alias, getViewName(alias, databaseID), ctx={'userName': userName,
     'databaseID': databaseID}), EVENT_BUS_SCOPE.LOBBY)


def showClanProfileWindow(clanDbID, clanAbbrev):
    alias = CLANS_ALIASES.CLAN_PROFILE_MAIN_WINDOW_PY
    g_eventBus.handleEvent(events.LoadViewEvent(alias, getViewName(alias, clanDbID), ctx={'clanDbID': clanDbID,
     'clanAbbrev': clanAbbrev}), EVENT_BUS_SCOPE.LOBBY)


def showClanSearchWindow():
    alias = CLANS_ALIASES.CLAN_SEARCH_WINDOW_PY
    g_eventBus.handleEvent(events.LoadViewEvent(alias, alias, ctx=None), EVENT_BUS_SCOPE.LOBBY)
    return


def showClanInvitesWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(CLANS_ALIASES.CLAN_PROFILE_INVITES_WINDOW_PY), EVENT_BUS_SCOPE.LOBBY)


def showClanSendInviteWindow(clanDbID):
    alias = CLANS_ALIASES.CLAN_PROFILE_SEND_INVITES_WINDOW_PY
    g_eventBus.handleEvent(events.LoadViewEvent(alias, getViewName(alias, clanDbID), ctx={'clanDbID': clanDbID,
     'ctrlType': CTRL_ENTITY_TYPE.UNIT}), scope=EVENT_BUS_SCOPE.LOBBY)


def selectVehicleInHangar(itemCD):
    from CurrentVehicle import g_currentVehicle
    itemsCache = dependency.instance(IItemsCache)
    veh = itemsCache.items.getItemByCD(int(itemCD))
    if not veh.isInInventory:
        raise SoftException('Vehicle (itemCD={}) must be in inventory.'.format(itemCD))
    g_currentVehicle.selectVehicle(veh.invID)
    showHangar()


def showPersonalCase(tankmanInvID, tabIndex, scope=EVENT_BUS_SCOPE.DEFAULT):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.PERSONAL_CASE, getViewName(VIEW_ALIAS.PERSONAL_CASE, tankmanInvID), {'tankmanID': tankmanInvID,
     'page': tabIndex}), scope)


def showPremiumWindow(arenaUniqueID=0, premiumBonusesDiff=None):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.PREMIUM_WINDOW, getViewName(VIEW_ALIAS.PREMIUM_WINDOW), ctx={'arenaUniqueID': arenaUniqueID,
     'premiumBonusesDiff': premiumBonusesDiff}), EVENT_BUS_SCOPE.LOBBY)


def showBoostersWindow(tabID=None):
    if isIngameShopEnabled():
        showStorage(STORAGE_CONSTANTS.PERSONAL_RESERVES)
    else:
        ctx = {'tabID': tabID} if tabID is not None else {}
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOSTERS_WINDOW, ctx=ctx), EVENT_BUS_SCOPE.LOBBY)
    return


def stopTutorial():
    g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.STOP_TRAINING), scope=EVENT_BUS_SCOPE.GLOBAL)


def runTutorialChain(chapterID):
    g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.START_TRAINING, settingsID='TRIGGERS_CHAINS', initialChapter=chapterID, restoreIfRun=True))


def runSalesChain(chapterID):
    g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.START_TRAINING, settingsID='SALES_TRIGGERS', initialChapter=chapterID, restoreIfRun=True))


def changeAppResolution(width, height, scale):
    g_eventBus.handleEvent(events.GameEvent(events.GameEvent.CHANGE_APP_RESOLUTION, ctx={'width': width,
     'height': height,
     'scale': scale}), scope=EVENT_BUS_SCOPE.GLOBAL)


@process
def requestProfile(databaseID, userName, successCallback):
    itemsCache = dependency.instance(IItemsCache)
    userDossier, _, isHidden = yield itemsCache.items.requestUserDossier(databaseID)
    if userDossier is None:
        if isHidden:
            key = 'messenger/userInfoHidden'
        else:
            key = 'messenger/userInfoNotAvailable'
        from gui import DialogsInterface
        DialogsInterface.showI18nInfoDialog(key, lambda result: None, I18nInfoDialogMeta(key, messageCtx={'userName': userName}))
    else:
        successCallback(databaseID, userName)
    return


def showSettingsWindow(redefinedKeyMode=False, tabIndex=None, isBattleSettings=False):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.SETTINGS_WINDOW, ctx={'redefinedKeyMode': redefinedKeyMode,
     'tabIndex': tabIndex,
     'isBattleSettings': isBattleSettings}), scope=EVENT_BUS_SCOPE.GLOBAL)


def showVehicleCompare():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_COMPARE), scope=EVENT_BUS_SCOPE.LOBBY)


def showEpicBattleSkillView():
    g_eventBus.handleEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_SKILL_ALIAS), scope=EVENT_BUS_SCOPE.LOBBY)


@pointcutable
def showCrystalWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.CRYSTALS_PROMO_WINDOW), EVENT_BUS_SCOPE.LOBBY)


@pointcutable
def openPaymentLink():
    g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.PAYMENT))


@pointcutable
def showExchangeCurrencyWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.EXCHANGE_WINDOW), EVENT_BUS_SCOPE.LOBBY)


@pointcutable
def showExchangeXPWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.EXCHANGE_XP_WINDOW), EVENT_BUS_SCOPE.LOBBY)


def showBubbleTooltip(msg):
    g_eventBus.handleEvent(events.BubbleTooltipEvent(events.BubbleTooltipEvent.SHOW, msg), scope=EVENT_BUS_SCOPE.LOBBY)
