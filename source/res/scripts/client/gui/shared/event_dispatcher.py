# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/event_dispatcher.py
from adisp import process
from debug_utils import LOG_WARNING
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nInfoDialogMeta
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.prb_control.settings import CTRL_ENTITY_TYPE
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.utils.functions import getViewName, getUniqueViewName
from gui.shared.utils import isPopupsWindowsOpenDisabled
from CurrentVehicle import HeroTankPreviewAppearance
from helpers import dependency
from skeletons.gui.shared import IItemsCache
import constants
if constants.IS_BOOTCAMP_ENABLED:
    from bootcamp.Bootcamp import g_bootcamp

class SETTINGS_TAB_INDEX(object):
    GAME = 0
    GRAPHICS = 1
    SOUND = 2
    CONTROL = 3
    AIM = 4
    MARKERS = 5
    FEEDBACK = 6


def showBattleResultsWindow(arenaUniqueID):
    if constants.IS_BOOTCAMP_ENABLED:
        if g_bootcamp.isRunning():
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_BATTLE_RESULT, getViewName(VIEW_ALIAS.BOOTCAMP_BATTLE_RESULT, str(arenaUniqueID)), ctx={'arenaUniqueID': arenaUniqueID}), EVENT_BUS_SCOPE.LOBBY)
            return
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BATTLE_RESULTS, getViewName(VIEW_ALIAS.BATTLE_RESULTS, str(arenaUniqueID)), {'arenaUniqueID': arenaUniqueID}), EVENT_BUS_SCOPE.LOBBY)


def notifyBattleResultsPosted(arenaUniqueID):
    g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.BATTLE_RESULTS_POSTED, {'arenaUniqueID': arenaUniqueID}), EVENT_BUS_SCOPE.LOBBY)


def showRankedBattleResultsWindow(rankedResultsVO, vehicle, rankInfo):
    g_eventBus.handleEvent(events.LoadViewEvent(alias=RANKEDBATTLES_ALIASES.RANKED_BATTLES_BATTLE_RESULTS, ctx={'rankedResultsVO': rankedResultsVO,
     'vehicle': vehicle,
     'rankInfo': rankInfo}), EVENT_BUS_SCOPE.LOBBY)


def showRankedAwardWindow(rankID, showNext=True, vehicle=None):
    g_eventBus.handleEvent(events.LoadViewEvent(alias=RANKEDBATTLES_ALIASES.RANKED_BATTLES_AWARD, ctx={'rankID': rankID,
     'showNext': showNext,
     'vehicle': vehicle}), EVENT_BUS_SCOPE.LOBBY)


def showRankedPrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(alias=RANKEDBATTLES_ALIASES.RANKED_BATTLE_PRIME_TIME, ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleInfo(vehTypeCompDescr):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_INFO_WINDOW, getViewName(VIEW_ALIAS.VEHICLE_INFO_WINDOW, vehTypeCompDescr), ctx={'vehicleCompactDescr': int(vehTypeCompDescr)}), EVENT_BUS_SCOPE.LOBBY)


def showModuleInfo(itemCD, vehicleDescr):
    if constants.IS_BOOTCAMP_ENABLED:
        if g_bootcamp.isRunning():
            return
    itemCD = int(itemCD)
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.MODULE_INFO_WINDOW, getViewName(VIEW_ALIAS.MODULE_INFO_WINDOW, itemCD), {'moduleCompactDescr': itemCD,
     'vehicleDescr': vehicleDescr}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleSellDialog(vehInvID):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_SELL_DIALOG, ctx={'vehInvID': int(vehInvID)}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleBuyDialog(vehicle, isTradeIn=False):
    if constants.IS_BOOTCAMP_ENABLED:
        if g_bootcamp.isRunning():
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_VEHICLE_BUY_WINDOW, ctx={'nationID': vehicle.nationID,
             'itemID': vehicle.innationID}), EVENT_BUS_SCOPE.LOBBY)
            return
    alias = VIEW_ALIAS.VEHICLE_RESTORE_WINDOW if vehicle.isRestoreAvailable() else VIEW_ALIAS.VEHICLE_BUY_WINDOW
    g_eventBus.handleEvent(events.LoadViewEvent(alias, ctx={'nationID': vehicle.nationID,
     'itemID': vehicle.innationID,
     'isTradeIn': isTradeIn}), EVENT_BUS_SCOPE.LOBBY)


def showBattleBoosterBuyDialog(battleBoosterIntCD, install=False):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOSTER_BUY_WINDOW, ctx={'typeCompDescr': battleBoosterIntCD,
     'install': install}), EVENT_BUS_SCOPE.LOBBY)


def showResearchView(vehTypeCompDescr):
    if constants.IS_BOOTCAMP_ENABLED:
        if g_bootcamp.isRunning():
            exitEvent = events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR)
            loadEvent = events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_LOBBY_RESEARCH, ctx={'rootCD': vehTypeCompDescr,
             'exit': exitEvent})
            g_eventBus.handleEvent(loadEvent, scope=EVENT_BUS_SCOPE.LOBBY)
            return
    exitEvent = events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR)
    loadEvent = events.LoadViewEvent(VIEW_ALIAS.LOBBY_RESEARCH, ctx={'rootCD': vehTypeCompDescr,
     'exit': exitEvent})
    g_eventBus.handleEvent(loadEvent, scope=EVENT_BUS_SCOPE.LOBBY)


def showVehicleStats(vehTypeCompDescr):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_PROFILE, ctx={'itemCD': vehTypeCompDescr}), scope=EVENT_BUS_SCOPE.LOBBY)


def showHangar():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)


def showVehiclePreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, vehStrCD=None):
    from CurrentVehicle import g_currentPreviewVehicle
    if g_currentPreviewVehicle.isPresent():
        g_currentPreviewVehicle.selectVehicle(vehTypeCompDescr)
    else:
        if constants.IS_BOOTCAMP_ENABLED:
            if g_bootcamp.isRunning():
                from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
                LOG_DEBUG_DEV_BOOTCAMP('showVehiclePreview', vehTypeCompDescr, previewAlias)
                g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_VEHICLE_PREVIEW, ctx={'itemCD': vehTypeCompDescr,
                 'previewAlias': previewAlias}), scope=EVENT_BUS_SCOPE.LOBBY)
                return
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_PREVIEW, ctx={'itemCD': vehTypeCompDescr,
         'previewAlias': previewAlias,
         'vehicleStrCD': vehStrCD}), scope=EVENT_BUS_SCOPE.LOBBY)


def showSabatonVehiclePreview():
    """Show sabaton tank in preview mode
    """
    from items import sabaton_crew
    from gui.Scaleform.daapi.view.lobby.vehiclePreview.vehicle_preview_dp import SabatonVehPreviewDataProvider
    vehType = sabaton_crew.getSabatonVehType()
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_PREVIEW, ctx={'itemCD': vehType.compactDescr,
     'previewAlias': VIEW_ALIAS.LOBBY_HANGAR,
     'previewAppearance': HeroTankPreviewAppearance(),
     'previewDP': SabatonVehPreviewDataProvider()}), scope=EVENT_BUS_SCOPE.LOBBY)


def hideVehiclePreview():
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_VEHICLE_PREVIEW), scope=EVENT_BUS_SCOPE.LOBBY)


def hideBattleResults():
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_BATTLE_RESULT_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)


def hideWebBrowser(browserID=None):
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_BROWSER_WINDOW, ctx={'browserID': browserID}), scope=EVENT_BUS_SCOPE.LOBBY)


def showAwardWindow(award, isUniqueName=True):
    """
    :param award: AwardAbstract instance object
    :param isUniqueName:
    """
    if isPopupsWindowsOpenDisabled():
        LOG_WARNING('Award popup disabled', award, isUniqueName)
        return
    if isUniqueName:
        name = getUniqueViewName(VIEW_ALIAS.AWARD_WINDOW)
    else:
        name = VIEW_ALIAS.AWARD_WINDOW
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.AWARD_WINDOW, name=name, ctx={'award': award}), EVENT_BUS_SCOPE.LOBBY)


def showMissionAwardWindow(award):
    """
    Shows modal dialog with award(s) and congratulations.
    :param award: AwardAbstract instance object
    """
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.MISSION_AWARD_WINDOW, name=getUniqueViewName(VIEW_ALIAS.MISSION_AWARD_WINDOW), ctx={'award': award}), EVENT_BUS_SCOPE.LOBBY)


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
    """
    Selects vehicle and returns to hangar.
    :param itemCD: int-type compact descriptor of vehicle
    """
    from CurrentVehicle import g_currentVehicle
    itemsCache = dependency.instance(IItemsCache)
    veh = itemsCache.items.getItemByCD(int(itemCD))
    assert veh.isInInventory, 'Vehicle must be in inventory.'
    g_currentVehicle.selectVehicle(veh.invID)
    showHangar()


def showPersonalCase(tankmanInvID, tabIndex, scope=EVENT_BUS_SCOPE.DEFAULT):
    """
    Show personalCase window on current tab.
    :param tankmanInvID: int-type tankman inventory ID.
    :param tabIndex: int-type tab index
    :param scope:
    """
    from bootcamp.BootcampGarage import g_bootcampGarage
    if constants.IS_BOOTCAMP_ENABLED:
        if g_bootcamp.isRunning():
            g_bootcampGarage.closeAllPopUps()
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_PERSONAL_CASE, getViewName(VIEW_ALIAS.BOOTCAMP_PERSONAL_CASE, tankmanInvID), {'tankmanID': tankmanInvID,
             'page': tabIndex}), scope)
            return
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.PERSONAL_CASE, getViewName(VIEW_ALIAS.PERSONAL_CASE, tankmanInvID), {'tankmanID': tankmanInvID,
     'page': tabIndex}), scope)


def showPremiumWindow(arenaUniqueID=0, premiumBonusesDiff=None):
    """
    Show premium window
    """
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.PREMIUM_WINDOW, getViewName(VIEW_ALIAS.PREMIUM_WINDOW), ctx={'arenaUniqueID': arenaUniqueID,
     'premiumBonusesDiff': premiumBonusesDiff}), EVENT_BUS_SCOPE.LOBBY)


def showBoostersWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOSTERS_WINDOW), EVENT_BUS_SCOPE.LOBBY)


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


def showSettingsWindow(redefinedKeyMode=False, tabIndex=None):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.SETTINGS_WINDOW, ctx={'redefinedKeyMode': redefinedKeyMode,
     'tabIndex': tabIndex}), scope=EVENT_BUS_SCOPE.GLOBAL)


def showVehicleCompare():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_COMPARE), scope=EVENT_BUS_SCOPE.LOBBY)
