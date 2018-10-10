# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/missions.py
from helpers import dependency
from personal_missions import PM_BRANCH
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.gui.game_control import IMarathonEventsController
from skeletons.gui.lobby_context import ILobbyContext
from web_client_api import w2c, W2CSchema, Field
from gui.server_events import events_dispatcher as server_events

class _PersonalMissionsSchema(W2CSchema):
    branch = Field(required=True, type=basestring, validator=lambda v, _: v in PM_BRANCH.NAME_TO_TYPE)
    operation_id = Field(required=False, type=int)


class MissionsWebApiMixin(object):

    @w2c(W2CSchema, 'missions')
    def openMissionsTab(self, cmd):
        server_events.showMissions()

    @w2c(W2CSchema, 'missions_events')
    def openMissionsEvents(self, cmd):
        if dependency.instance(IMarathonEventsController).isAnyActive():
            server_events.showMissionsMarathon()
        else:
            server_events.showMissionsGrouped()

    @w2c(W2CSchema, 'missions_for_current_vehicle')
    def openVehicleMissions(self, cmd):
        server_events.showMissionsForCurrentVehicle()

    @w2c(W2CSchema, 'missions_categories')
    def openMissionCategories(self, cmd):
        server_events.showMissionsCategories()

    @w2c(W2CSchema, 'missions_competitions')
    def openMissionsElenEvents(self, cmd):
        serverSettings = dependency.instance(ILobbyContext).getServerSettings()
        elenController = dependency.instance(IEventBoardController)
        if serverSettings.isElenEnabled() and elenController.hasEvents():
            server_events.showMissionsElen()


class PersonalMissionsWebApiMixin(object):

    @w2c(_PersonalMissionsSchema, 'personal_missions')
    def openPersonalMissions(self, cmd):
        server_events.showPersonalMissionOperationsPage(PM_BRANCH.NAME_TO_TYPE[cmd.branch], operationID=cmd.operation_id)
