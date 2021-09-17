# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/missions.py
from helpers import dependency
from gui.battle_pass.battle_pass_helpers import BattlePassProgressionSubTabs
from gui.marathon.marathon_event_controller import getMarathons
from personal_missions import PM_BRANCH
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.gui.game_control import IMarathonEventsController
from skeletons.gui.lobby_context import ILobbyContext
from web.web_client_api import w2c, W2CSchema, Field
from gui.server_events import events_dispatcher as server_events

class _MissionsSchema(W2CSchema):
    tab = Field(required=False, type=basestring, default=None)
    missionID = Field(required=False, type=basestring, default=None)
    groupID = Field(required=False, type=basestring, default=None)
    marathonPrefix = Field(required=False, type=basestring, default=None)
    anchor = Field(required=False, type=basestring, default=None)
    showDetails = Field(required=False, type=bool, default=True)
    subTab = Field(required=False, type=int, default=0)


class _PersonalMissionsSchema(W2CSchema):
    branch = Field(required=True, type=basestring, validator=lambda v, _: v in PM_BRANCH.NAME_TO_TYPE)
    operation_id = Field(required=False, type=int)


class _MarathonMissionsSchema(W2CSchema):
    prefix = Field(required=True, type=basestring, validator=lambda v, _: v in {m.prefix for m in getMarathons()})


class _MissionsCategoriesSchema(W2CSchema):
    group_id = Field(required=False, type=basestring, default=None)


class MissionsWebApiMixin(object):

    @w2c(_MissionsSchema, 'missions')
    def openMissionsTab(self, cmd):
        server_events.showMissions(tab=cmd.tab, missionID=cmd.missionID, groupID=cmd.groupID, marathonPrefix=cmd.marathonPrefix, anchor=cmd.anchor, showDetails=cmd.showDetails, subTab=cmd.subTab)

    @w2c(W2CSchema, 'missions_events')
    def openMissionsEvents(self, cmd):
        if dependency.instance(IMarathonEventsController).isAnyActive():
            server_events.showMissionsMarathon()
        else:
            server_events.showMissionsGrouped()

    @w2c(W2CSchema, 'missions_for_current_vehicle')
    def openVehicleMissions(self, cmd):
        server_events.showMissionsForCurrentVehicle()

    @w2c(_MissionsCategoriesSchema, 'missions_categories')
    def openMissionCategories(self, cmd):
        server_events.showMissionsCategories(groupID=cmd.group_id)

    @w2c(W2CSchema, 'missions_competitions')
    def openMissionsElenEvents(self, cmd):
        serverSettings = dependency.instance(ILobbyContext).getServerSettings()
        elenController = dependency.instance(IEventBoardController)
        if serverSettings.isElenEnabled() and elenController.hasEvents():
            server_events.showMissionsElen()

    @w2c(_MarathonMissionsSchema, 'missions_marathon')
    def openMissionMarathon(self, cmd):
        server_events.showMissionsMarathon(cmd.prefix)

    @w2c(W2CSchema, 'battle_pass_common')
    def openBattlePassMainProgression(self, _):
        server_events.showMissionsBattlePassCommonProgression()

    @w2c(W2CSchema, 'battle_pass_buy:')
    def openBattlePassMainWithBuy(self, _):
        server_events.showMissionsBattlePassCommonProgression(subTab=BattlePassProgressionSubTabs.BUY_TAB_FOR_SHOP)

    @w2c(W2CSchema, 'battle_pass_levels_buy:')
    def openBattlePassMainWithBuyLevels(self, _):
        server_events.showMissionsBattlePassCommonProgression(subTab=BattlePassProgressionSubTabs.BUY_LEVELS_TAB_FROM_SHOP)


class PersonalMissionsWebApiMixin(object):

    @w2c(_PersonalMissionsSchema, 'personal_missions')
    def openPersonalMissions(self, cmd):
        server_events.showPersonalMissionOperationsPage(PM_BRANCH.NAME_TO_TYPE[cmd.branch], operationID=cmd.operation_id)
