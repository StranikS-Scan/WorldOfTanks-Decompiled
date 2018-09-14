# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/event_dispatcher.py
from adisp import process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nInfoDialogMeta
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.battle_results import data_providers
from gui.prb_control.settings import CTRL_ENTITY_TYPE
from gui.shared import events, g_eventBus
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.utils.functions import getViewName, getUniqueViewName

class SETTINGS_TAB_INDEX(object):
    GAME = 0
    GRAPHICS = 1
    SOUND = 2
    CONTROL = 3
    AIM = 4
    MARKERS = 5
    FEEDBACK = 6


def _showBattleResults(arenaUniqueID, dataProvider):
    """
    :param arenaUniqueID: long, arena unique id
    :param dataProvider: gui.battle_results.data_providers.* instance
    """
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BATTLE_RESULTS, getViewName(VIEW_ALIAS.BATTLE_RESULTS, str(arenaUniqueID)), ctx={'dataProvider': dataProvider}), EVENT_BUS_SCOPE.LOBBY)


def showBattleResultsFromData(battleResultsData):
    """
    :param battleResultsData: dict, gotten battle results
    """
    arenaUniqueID = battleResultsData['arenaUniqueID']
    return _showBattleResults(arenaUniqueID, data_providers.DirectDataProvider(arenaUniqueID, battleResultsData))


def showMyBattleResults(arenaUniqueID):
    """
    :param arenaUniqueID: long, arena unique id
    """
    return _showBattleResults(arenaUniqueID, data_providers.OwnResultsDataProvider(arenaUniqueID))


def showUserBattleResults(arenaUniqueID, svrPackedData):
    """
    :param arenaUniqueID: long, arena unique id
    :param svrPackedData: str or None, used to show other user post-battle results
    """
    return _showBattleResults(arenaUniqueID, data_providers.UserResultsDataProvider(arenaUniqueID, svrPackedData))


def showVehicleInfo(vehTypeCompDescr):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_INFO_WINDOW, getViewName(VIEW_ALIAS.VEHICLE_INFO_WINDOW, vehTypeCompDescr), ctx={'vehicleCompactDescr': int(vehTypeCompDescr)}), EVENT_BUS_SCOPE.LOBBY)


def showModuleInfo(itemCD, vehicleDescr):
    itemCD = int(itemCD)
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.MODULE_INFO_WINDOW, getViewName(VIEW_ALIAS.MODULE_INFO_WINDOW, itemCD), {'moduleCompactDescr': itemCD,
     'vehicleDescr': vehicleDescr}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleSellDialog(vehInvID):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_SELL_DIALOG, ctx={'vehInvID': int(vehInvID)}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleBuyDialog(vehicle):
    alias = VIEW_ALIAS.VEHICLE_RESTORE_WINDOW if vehicle.isRestoreAvailable() else VIEW_ALIAS.VEHICLE_BUY_WINDOW
    g_eventBus.handleEvent(events.LoadViewEvent(alias, ctx={'nationID': vehicle.nationID,
     'itemID': vehicle.innationID}), EVENT_BUS_SCOPE.LOBBY)


def showResearchView(vehTypeCompDescr):
    exitEvent = events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR)
    loadEvent = events.LoadViewEvent(VIEW_ALIAS.LOBBY_RESEARCH, ctx={'rootCD': vehTypeCompDescr,
     'exit': exitEvent})
    g_eventBus.handleEvent(loadEvent, scope=EVENT_BUS_SCOPE.LOBBY)


def showVehicleStats(vehTypeCompDescr):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_PROFILE, ctx={'itemCD': vehTypeCompDescr}), scope=EVENT_BUS_SCOPE.LOBBY)


def showHangar():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)


def showVehiclePreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR):
    from CurrentVehicle import g_currentPreviewVehicle
    if g_currentPreviewVehicle.isPresent():
        g_currentPreviewVehicle.selectVehicle(vehTypeCompDescr)
    else:
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_PREVIEW, ctx={'itemCD': vehTypeCompDescr,
         'previewAlias': previewAlias}), scope=EVENT_BUS_SCOPE.LOBBY)


def hideBattleResults():
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_BATTLE_RESULT_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)


def showAwardWindow(award, isUniqueName=True, viewAlias=VIEW_ALIAS.AWARD_WINDOW):
    """
    :param award: AwardAbstract instance object
    :param isUniqueName:
    """
    if isUniqueName:
        name = getUniqueViewName(viewAlias)
    else:
        name = viewAlias
    g_eventBus.handleEvent(events.LoadViewEvent(viewAlias, name=name, ctx={'award': award}), EVENT_BUS_SCOPE.LOBBY)


def showMissionAwardWindow(award):
    name = getUniqueViewName(VIEW_ALIAS.MISSION_AWARD_WINDOW)
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
    veh = g_itemsCache.items.getItemByCD(int(itemCD))
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


def showChangeDivisionWindow(division):
    g_eventBus.handleEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW, ctx={'isInChangeDivisionMode': True,
     'division': division}), scope=EVENT_BUS_SCOPE.LOBBY)


def stopTutorial():
    g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.STOP_TRAINING), scope=EVENT_BUS_SCOPE.GLOBAL)


def runTutorialChain(chapterID):
    g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.START_TRAINING, settingsID='TRIGGERS_CHAINS', initialChapter=chapterID, restoreIfRun=True))


def changeAppResolution(width, height, scale):
    g_eventBus.handleEvent(events.GameEvent(events.GameEvent.CHANGE_APP_RESOLUTION, ctx={'width': width,
     'height': height,
     'scale': scale}), scope=EVENT_BUS_SCOPE.GLOBAL)


@process
def requestProfile(databaseID, userName, successCallback):
    userDossier, _, isHidden = yield g_itemsCache.items.requestUserDossier(databaseID)
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
