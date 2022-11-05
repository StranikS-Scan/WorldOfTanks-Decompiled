# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/events_dispatcher.py
import constants
from battle_pass_common import BattlePassConsts
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.customization.progression_helpers import parseEventID
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getMissionInfoData
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.impl.lobby.reward_window import GiveAwayRewardWindow, PiggyBankRewardWindow, TwitchRewardWindow
from gui.impl.pub.notification_commands import WindowNotificationCommand, EventNotificationCommand, NotificationEvent
from gui.prb_control.dispatcher import g_prbLoader
from gui.server_events import anniversary_helper, awards, events_helpers, recruit_helper
from gui.server_events.events_helpers import getLootboxesFromBonuses, isC11nQuest
from gui.shared import EVENT_BUS_SCOPE, event_dispatcher as shared_events, events, g_eventBus
from gui.shared.event_dispatcher import showProgressiveItemsView, hideWebBrowserOverlay, showBrowserOverlayView
from gui.shared.events import PersonalMissionsEvent
from helpers import dependency
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IMarathonEventsController
from skeletons.gui.impl import INotificationWindowController, IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
OPERATIONS = {PERSONAL_MISSIONS_ALIASES.PERONAL_MISSIONS_OPERATIONS_SEASON_1_ID: PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_OPERATIONS_PAGE_ALIAS,
 PERSONAL_MISSIONS_ALIASES.PERONAL_MISSIONS_OPERATIONS_SEASON_2_ID: PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS2_OPERATIONS_PAGE_ALIAS}
_EVENTS_REWARD_WINDOW = {recruit_helper.RecruitSourceID.TWITCH_0: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_1: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_2: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_3: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_4: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_5: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_6: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_7: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_8: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_9: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_10: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_11: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_12: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_13: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_14: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_15: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_16: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_17: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_18: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_19: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_20: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_21: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_22: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_23: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_24: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_25: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_26: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_27: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_28: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_29: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_30: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_31: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_32: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_33: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_34: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.COMMANDER_MARINA: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.COMMANDER_PATRICK: TwitchRewardWindow,
 anniversary_helper.ANNIVERSARY_EVENT_PREFIX: GiveAwayRewardWindow}
_PIGGY_BANK_EVENT_NAME = 'piggyBank'

def showPQSeasonAwardsWindow(questsType):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.QUESTS_SEASON_AWARDS_WINDOW), ctx={'questsType': questsType}), EVENT_BUS_SCOPE.LOBBY)


def canOpenPMPage(branchID=None, operationID=None, missionID=None):
    serverSettings = dependency.instance(ILobbyContext).getServerSettings()
    eventsCache = dependency.instance(IEventsCache)
    disabledOperationsIds = serverSettings.getDisabledPMOperations()
    disabledMissionsIds = serverSettings.getDisabledPersonalMissions()

    def checkBranch(idx):
        return serverSettings.isPersonalMissionsEnabled(int(idx))

    def checkOperation(idx):
        return int(idx) not in disabledOperationsIds

    def checkMission(idx):
        return int(idx) not in disabledMissionsIds

    if missionID is not None:
        mission = eventsCache.getPersonalMissions().getAllQuests()[int(missionID)]
        operationID = mission.getOperationID()
        branchID = mission.getPMType().branch
        return checkBranch(branchID) and checkOperation(operationID) and checkMission(missionID)
    elif operationID is not None:
        operation = eventsCache.getPersonalMissions().getAllOperations()[int(operationID)]
        return checkBranch(operation.getBranch()) and checkOperation(operationID)
    else:
        return checkBranch(branchID) if branchID is not None else False


def showPersonalMission(missionID=None):
    if not canOpenPMPage(missionID=missionID):
        return
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS), ctx={'eventID': missionID}), EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionsChain(operationID, chainID):
    if not canOpenPMPage(operationID=operationID):
        return
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS), ctx={'operationID': operationID,
     'chainID': chainID}), EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionOperationsPage(branchID, operationID):
    if not canOpenPMPage(branchID, operationID):
        showPersonalMissionsOperationsMap()
        return
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS), ctx={'branch': branchID,
     'operationID': operationID}), EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionsOperationsMap():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_OPERATIONS)), EVENT_BUS_SCOPE.LOBBY)


def showMissionsGrouped(missionID=None, groupID=None, anchor=None):
    showMissions(tab=QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS, missionID=missionID, groupID=groupID, anchor=anchor)


def showMissionsMarathon(marathonPrefix=None):
    if not marathonPrefix:
        marathonPrefix = dependency.instance(IMarathonEventsController).getPrimaryMarathon()
    showMissions(tab=QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS, marathonPrefix=marathonPrefix)


def showMissionsCategories(missionID=None, groupID=None, anchor=None):
    showMissions(tab=QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS, missionID=missionID, groupID=groupID, anchor=anchor)


def showMissionsForCurrentVehicle(missionID=None, groupID=None, anchor=None):
    showMissions(tab=QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_PY_ALIAS, missionID=missionID, groupID=groupID, anchor=anchor)


def showMissionsElen(eventQuestsID=None):
    showMissions(tab=QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS, missionID=eventQuestsID, groupID=eventQuestsID, showDetails=False)


def showMissionsLinkedSet():
    showMissions(tab=QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS)


def showDailyQuests(subTab):
    showMissions(tab=QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS, subTab=subTab)


def showMissionsMapboxProgression():
    showMissions(tab=QUESTS_ALIASES.MAPBOX_VIEW_PY_ALIAS)


def showBattleMatters():
    _showMissions(tab=QUESTS_ALIASES.BATTLE_MATTERS_VIEW_PY_ALIAS, openMainRewardView=False)


def showBattleMattersMainView():
    _showMissions(tab=QUESTS_ALIASES.BATTLE_MATTERS_VIEW_PY_ALIAS, openMainView=True)


def showBattleMattersMainReward():
    _showMissions(tab=QUESTS_ALIASES.BATTLE_MATTERS_VIEW_PY_ALIAS, openMainRewardView=True)


def showMissionsBattlePass(layoutID=None, chapterID=0):

    def __battleQueueViewPredicate(window):
        return window.content is not None and getattr(window.content, 'alias', None) == VIEW_ALIAS.BATTLE_QUEUE

    guiLoader = dependency.instance(IGuiLoader)
    if guiLoader.windowsManager.findWindows(__battleQueueViewPredicate):
        return
    _showMissions(tab=QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS, layoutID=layoutID, chapterID=chapterID)


def showMissions(tab=None, missionID=None, groupID=None, marathonPrefix=None, anchor=None, showDetails=True, subTab=None):
    _showMissions(**{'tab': tab,
     'subTab': subTab,
     'eventID': missionID,
     'groupID': groupID,
     'marathonPrefix': marathonPrefix,
     'anchor': anchor,
     'showMissionDetails': showDetails})


def showMissionDetails(missionID, groupID):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MISSION_DETAILS), ctx={'eventID': missionID,
     'groupID': groupID}), scope=EVENT_BUS_SCOPE.LOBBY)


def hideMissionDetails():
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_MISSION_DETAILS_VIEW), EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionDetails(missionID):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_PERSONAL_MISSION_DETAILS), ctx={'eventID': missionID}), scope=EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionAwards():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_AWARDS_VIEW_ALIAS)), scope=EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionStartPage():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS)), scope=EVENT_BUS_SCOPE.LOBBY)


def hidePersonalMissionDetails():
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_PERSONAL_MISSION_DETAILS_VIEW), EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionBrowserView(ctx):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.PERSONAL_MISSIONS_BROWSER_VIEW), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def showProgressiveItemsBrowserView(ctx):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.PROGRESSIVE_ITEMS_BROWSER_VIEW), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def showMission(eventID, eventType=None):
    from gui.impl.lobby.missions.daily_quests_view import DailyTabs
    if eventType == constants.EVENT_TYPE.C11N_PROGRESSION:
        itemIntCD, vehicleIntCD = parseEventID(eventID)
        service = dependency.instance(ICustomizationService)
        vehicle = service.getItemByCD(vehicleIntCD)
        service.showCustomization(vehicle.invID, lambda : showProgressiveItemsView(itemIntCD))
        return
    elif isC11nQuest(eventID):
        service = dependency.instance(ICustomizationService)
        from gui.customization.constants import CustomizationModes
        service.showCustomization(modeId=CustomizationModes.STYLED)
        return
    else:
        eventsCache = dependency.instance(IEventsCache)
        quests = eventsCache.getAllQuests()
        quest = quests.get(eventID)
        if eventID == BattlePassConsts.FAKE_QUEST_ID:
            hideWebBrowserOverlay()
            showMissionsBattlePass()
            return
        if quest is None or quest.isHidden():
            prefix = events_helpers.getMarathonPrefix(eventID)
            if prefix is not None:
                return showMissionsMarathon(marathonPrefix=prefix)
        if eventType is not None and eventType == constants.EVENT_TYPE.PERSONAL_MISSION:
            showPersonalMission(eventID)
        elif quest is not None and quest.showMissionAction() is not None:
            quest.showMissionAction()()
        elif quest is not None and not quest.isHidden():
            if events_helpers.isMarathon(quest.getGroupID()):
                groups = eventsCache.getGroups()
                group = groups.get(quest.getGroupID())
                groupContent = group.getGroupContent(quests)
                mainQuest = group.getMainQuest(groupContent)
                if mainQuest and quest.getID() != mainQuest.getID():
                    showMissionsGrouped(missionID=quest.getID(), groupID=group.getID(), anchor=group.getID())
                else:
                    showMissionsGrouped(anchor=group.getID())
            elif events_helpers.isBattleMattersQuestID(quest.getID()):
                showMissionsLinkedSet()
            elif events_helpers.isDailyQuest(quest.getID()):
                showDailyQuests(subTab=DailyTabs.QUESTS)
            elif events_helpers.isPremium(quest.getID()):
                showDailyQuests(subTab=DailyTabs.PREMIUM_MISSIONS)
            else:
                showMissionsCategories(missionID=quest.getID(), groupID=quest.getGroupID(), anchor=quest.getGroupID())
        return


def showAchievementsAward(achievements):
    shared_events.showAwardWindow(awards.AchievementsAward(achievements))


def showMotiveAward(quest):
    shared_events.showAwardWindow(awards.MotiveQuestAward(quest, showMission))


def showTankwomanAward(questID, tankmanData):
    ctx = {'isFemale': tankmanData.isFemale,
     'questID': questID}
    shared_events.showTankwomanRecruitAwardDialog(ctx)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def showRecruitWindow(recruitID, eventsCache=None):
    recruitData = recruit_helper.getRecruitInfo(recruitID)
    if recruitData.getSourceID() == recruit_helper.RecruitSourceID.TANKWOMAN:
        quest = eventsCache.getPersonalMissions().getAllQuests()[int(recruitID)]
        bonus = quest.getTankmanBonus()
        needToGetTankman = quest.needToGetAddReward() and not bonus.isMain or quest.needToGetMainReward() and bonus.isMain
        if needToGetTankman and bonus.tankman is not None:
            showTankwomanAward(quest.getID(), first(bonus.tankman.getTankmenData()))
    else:
        shared_events.showTokenRecruitDialog({'tokenName': recruitID,
         'tokenData': recruitData})
    return


def showMissionAward(quest, ctx):

    def handleEvent():
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is not None and prbDispatcher.getFunctionalState().isNavigationDisabled():
            SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error)
            return False
        else:
            showMissionsCategories()
            return True

    eventName = recruit_helper.getSourceIdFromQuest(quest.getID()) or anniversary_helper.getEventNameByQuest(quest)
    if eventName in _EVENTS_REWARD_WINDOW:
        ctx['quest'] = quest
        ctx['eventName'] = eventName
        rewardWindow = _EVENTS_REWARD_WINDOW[eventName](ctx)
        rewardWindow.load()
    else:
        bonuses = getMissionInfoData(quest).getSubstituteBonuses()
        if bonuses:
            lootboxes = getLootboxesFromBonuses(bonuses)
            if lootboxes:
                for lootboxId, lootboxInfo in lootboxes.iteritems():
                    showLootboxesAward(lootboxId=lootboxId, lootboxCount=lootboxInfo['count'], isFree=lootboxInfo['isFree'])

            else:
                missionAward = awards.MissionAward(quest, ctx, handleEvent)
                if missionAward.getAwards():
                    shared_events.showMissionAwardWindow(missionAward)


def showLootboxesAward(lootboxId, lootboxCount, isFree):
    pass


def showPiggyBankRewardWindow(creditsValue, isPremActive):
    ctx = {'eventName': _PIGGY_BANK_EVENT_NAME,
     'credits': creditsValue,
     'isPremActive': isPremActive}
    rewardWindow = PiggyBankRewardWindow(ctx)
    rewardWindow.load()


def showMetaBonusOverlayView(url, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB, forcedSkipEscape=False, browserParams=None):
    notificationMgr = dependency.instance(INotificationWindowController)
    event = NotificationEvent(method=showBrowserOverlayView, url=url, alias=alias, forcedSkipEscape=forcedSkipEscape, browserParams=browserParams)
    notificationMgr.append(EventNotificationCommand(event))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showCurrencyReserveAwardWindow(creditsValue, goldValue, notificationMgr=None):
    from gui.impl.lobby.currency_reserves.reserves_award_view import ReservesAwardWindow
    notificationMgr.append(WindowNotificationCommand(ReservesAwardWindow(creditsValue, goldValue)))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showSubscriptionAwardWindow(notificationMgr=None):
    from gui.impl.lobby.subscription.subscription_award_view import SubscriptionAwardWindow
    notificationMgr.append(WindowNotificationCommand(SubscriptionAwardWindow()))


def showPersonalMissionAward(quest, ctx):
    shared_events.showPersonalMissionsQuestAwardScreen(quest, ctx, showPersonalMission)


def showOperationUnlockedAward(quest, ctx):
    shared_events.showAwardWindow(awards.OperationUnlockedAward(quest, ctx, showPersonalMissionsChain))


def showPersonalMissionsOperationAwardsScreen(ctx):
    alias = PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_OPERATION_AWARDS_SCREEN_ALIAS
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def updatePersonalMissionAward(context):
    g_eventBus.handleEvent(events.PersonalMissionsEvent(PersonalMissionsEvent.UPDATE_AWARD_SCREEN, ctx=context), EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionFirstEntryAwardView(ctx):
    alias = PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_FIRST_ENTRY_AWARD_VIEW_ALIAS
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def showActions(tab=None, anchor=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_STORE), ctx={'tab': tab,
     'anchor': anchor}), scope=EVENT_BUS_SCOPE.LOBBY)


def _showMissions(**kwargs):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MISSIONS), ctx=kwargs), scope=EVENT_BUS_SCOPE.LOBBY)
