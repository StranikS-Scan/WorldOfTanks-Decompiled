# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/event_dispatcher.py
from operator import attrgetter
from CurrentVehicle import HeroTankPreviewAppearance
from adisp import process
from debug_utils import LOG_WARNING
from gui import SystemMessages, DialogsInterface
from gui.Scaleform import MENU
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nInfoDialogMeta, I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import getWebShopURL, isIngameShopEnabled
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.genConsts.VEHICLE_SELECTOR_CONSTANTS import VEHICLE_SELECTOR_CONSTANTS
from gui.Scaleform.genConsts.NEWYEAR_ALIASES import NEWYEAR_ALIASES
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.app_loader import g_appLoader
from gui.game_control.links import URLMacros
from gui.prb_control.settings import CTRL_ENTITY_TYPE
from gui.shared import events, g_eventBus, money
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.processors.goodies import BoosterActivator
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import isPopupsWindowsOpenDisabled
from gui.shared.utils.functions import getViewName, getUniqueViewName
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IHeroTankController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from soft_exception import SoftException
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME as _VCN

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


def showStorageModuleInfo(intCD):
    intCD = int(intCD)
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.MODULE_INFO_WINDOW, getViewName(VIEW_ALIAS.MODULE_INFO_WINDOW, intCD), {'moduleCompactDescr': intCD,
     'isAdditionalInfoShow': _ms(MENU.MODULEINFO_ADDITIONALINFO)}), EVENT_BUS_SCOPE.LOBBY)


def showStorageBoosterInfo(boosterID):
    boosterID = int(boosterID)
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOSTER_INFO_WINDOW, getViewName(VIEW_ALIAS.BOOSTER_INFO_WINDOW, boosterID), {'boosterID': boosterID}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleSellDialog(vehInvID):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_SELL_DIALOG, ctx={'vehInvID': int(vehInvID)}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleBuyDialog(vehicle, isTradeIn=False, previousAlias=None):
    from gui.impl.lobby.buy_vehicle_view import BuyVehicleWindow
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


@process
def showWebShop(url='', path='', params=None):
    parse = URLMacros().parse
    if path:
        path = yield parse(path, params)
        if url:
            url = yield parse(url)
        else:
            url = getWebShopURL()
    else:
        path = ''
        if url:
            url = yield parse(url, params)
        else:
            url = getWebShopURL()
    url = '/'.join((node.strip('/') for node in (url, path)))
    app = g_appLoader.getApp()
    if app is not None and app.containerManager is not None:
        viewKey = ViewKey(VIEW_ALIAS.LOBBY_STORE)
        browserWindow = app.containerManager.getViewByKey(viewKey)
        if browserWindow is not None:
            browser = browserWindow.getBrowser()
            browser.navigate(url)
            return
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_STORE, ctx={'url': url}), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def showOldShop(ctx=None):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_STORE_OLD, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def showStorage(defaultSection=STORAGE_CONSTANTS.FOR_SELL, tabId=None):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_STORAGE, ctx={'defaultSection': defaultSection,
     'defaultTab': tabId}), scope=EVENT_BUS_SCOPE.LOBBY)


def showOldVehiclePreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, vehStrCD=None, previewBackCb=None):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_PREVIEW, ctx={'itemCD': vehTypeCompDescr,
     'previewAlias': previewAlias,
     'vehicleStrCD': vehStrCD,
     'previewBackCb': previewBackCb}), scope=EVENT_BUS_SCOPE.LOBBY)


def showVehiclePreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, vehStrCD=None, previewBackCb=None, itemsPack=None, price=money.MONEY_UNDEFINED, oldPrice=None, title='', endTime=None, buyParams=None, vehParams=None):
    lobbyContext = dependency.instance(ILobbyContext)
    newPreviewEnabled = lobbyContext.getServerSettings().isIngamePreviewEnabled()
    heroTankController = dependency.instance(IHeroTankController)
    heroTankCD = heroTankController.getCurrentTankCD()
    isHeroTank = heroTankCD and heroTankCD == vehTypeCompDescr
    if isHeroTank and not itemsPack:
        goToHeroTankOnScene(vehTypeCompDescr, previewAlias)
    elif newPreviewEnabled:
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_PREVIEW_20, ctx={'itemCD': vehTypeCompDescr,
         'previewAlias': previewAlias,
         'vehicleStrCD': vehStrCD,
         'previewBackCb': previewBackCb,
         'itemsPack': itemsPack,
         'price': price,
         'oldPrice': oldPrice,
         'title': title,
         'endTime': endTime,
         'buyParams': buyParams,
         'vehParams': vehParams}), scope=EVENT_BUS_SCOPE.LOBBY)
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
            showHeroTankPreview(vehTypeCompDescr, previewAlias=previewAlias, previousBackAlias=None)
            break

    return


def showHeroTankPreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, previousBackAlias=None):
    lobbyContext = dependency.instance(ILobbyContext)
    if lobbyContext.getServerSettings().isIngamePreviewEnabled():
        alias = VIEW_ALIAS.HERO_VEHICLE_PREVIEW_20
    else:
        alias = VIEW_ALIAS.HERO_VEHICLE_PREVIEW
    g_eventBus.handleEvent(events.LoadViewEvent(alias, ctx={'itemCD': vehTypeCompDescr,
     'previewAlias': previewAlias,
     'previewAppearance': HeroTankPreviewAppearance(),
     'isHeroTank': True,
     'previousBackAlias': previousBackAlias}), scope=EVENT_BUS_SCOPE.LOBBY)


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


@process
@dependency.replace_none_kwargs(goodiesCache=IGoodiesCache)
def showBoosterActivateDialog(boosterIntCD, goodiesCache=None):
    newBooster = goodiesCache.getBooster(boosterIntCD)
    criteria = REQ_CRITERIA.BOOSTER.ACTIVE | REQ_CRITERIA.BOOSTER.BOOSTER_TYPES([newBooster.boosterType])
    activeBoosters = goodiesCache.getBoosters(criteria=criteria).values()
    curBooster = max(activeBoosters, key=attrgetter('effectValue')) if activeBoosters else None
    messageCtx = {'newBoosterName': text_styles.middleTitle(newBooster.description)}
    if curBooster is None:
        key = BOOSTER_CONSTANTS.BOOSTER_ACTIVATION_CONFORMATION_TEXT_KEY
    else:
        key = BOOSTER_CONSTANTS.BOOSTER_REPLACE_CONFORMATION_TEXT_KEY
        messageCtx['curBoosterName'] = text_styles.middleTitle(curBooster.description)
    shouldActivate = yield DialogsInterface.showDialog(I18nConfirmDialogMeta(key=key, messageCtx=messageCtx, focusedID=DIALOG_BUTTON_ID.CLOSE))
    if shouldActivate:
        result = yield BoosterActivator(newBooster).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
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


def showEpicBattleSkillView(previousPageAlias=VIEW_ALIAS.LOBBY_HANGAR, showBackButton=False):
    g_eventBus.handleEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_SKILL_ALIAS, ctx={'showBackButton': showBackButton,
     'previousPage': previousPageAlias}), scope=EVENT_BUS_SCOPE.LOBBY)


def showCrystalWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.CRYSTALS_PROMO_WINDOW), EVENT_BUS_SCOPE.LOBBY)


def openPaymentLink():
    g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.PAYMENT))


def showExchangeCurrencyWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.EXCHANGE_WINDOW), EVENT_BUS_SCOPE.LOBBY)


def showExchangeXPWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.EXCHANGE_XP_WINDOW), EVENT_BUS_SCOPE.LOBBY)


def showBubbleTooltip(msg):
    g_eventBus.handleEvent(events.BubbleTooltipEvent(events.BubbleTooltipEvent.SHOW, msg), scope=EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext, nyCtrl=INewYearController)
def showLootBoxEntry(lootBoxType=NewYearLootBoxes.PREMIUM, lobbyCtx=None, nyCtrl=None):
    enabled = lobbyCtx.getServerSettings().isLootBoxesEnabled() and nyCtrl.isEnabled()
    if not enabled:
        from gui.impl.lobby.loot_box.loot_box_helper import showRestrictedSysMessage
        showRestrictedSysMessage()
        return
    from gui.impl.lobby.loot_box.loot_box_entry_view import LootBoxEntryWindow
    window = LootBoxEntryWindow(lootBoxType)
    window.load()


def showLootBoxBuyWindow():
    g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.LOOT_BOX_URL))


def showLootBoxGiftWindow():
    g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.LOOT_BOX_GIFT_URL))


def showNewYearApplyVehicleDiscount(level):
    g_eventBus.handleEvent(events.LoadViewEvent(NEWYEAR_ALIASES.NEW_YEAR_VEHICLE_SELECTOR_ALIAS, ctx={'isMultiSelect': False,
     'section': 'ny_vehicle_discount_activation',
     'vehicleTypes': (_VCN.LIGHT_TANK, _VCN.MEDIUM_TANK, _VCN.HEAVY_TANK),
     'filterVisibility': VEHICLE_SELECTOR_CONSTANTS.VISIBLE_NATION | VEHICLE_SELECTOR_CONSTANTS.VISIBLE_VEHICLE_TYPE | VEHICLE_SELECTOR_CONSTANTS.VISIBLE_COMPATIBLE_ONLY,
     'level': level}), scope=EVENT_BUS_SCOPE.LOBBY)


def showLootBoxAutoOpenWindow(rewards):
    from gui.impl.lobby.loot_box.loot_box_auto_open_view import LootBoxAutoOpenWindow
    window = LootBoxAutoOpenWindow(rewards)
    window.load()


def showNYLevelUpWindow(context):
    from gui.impl.new_year.views.new_year_level_up_view import NewYearLevelUpWindow
    window = NewYearLevelUpWindow(context)
    window.load()
