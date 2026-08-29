# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/__init__.py
from __future__ import absolute_import
import typing
if typing.TYPE_CHECKING:
    from helpers.dependency import DependencyManager
__all__ = ('getUserMissionsConfig',)

def getUserMissionsConfig(manager):
    from gui.impl.lobby.user_missions.hangar_widget.services import IBattlePassService, IEventsService, IMissionsService, IMissionsContainerService, IUserMissionWidgetService
    from gui.impl.lobby.user_missions.hangar_widget.services.battle_pass_service import BattlePassService
    from gui.impl.lobby.user_missions.hangar_widget.services.events_service import EventsService
    from gui.impl.lobby.user_missions.hangar_widget.services.missions_service import MissionsService
    from gui.impl.lobby.user_missions.hangar_widget.services.missions_container_service import MissionsContainerService
    from gui.impl.lobby.user_missions.hangar_widget.services.user_mission_widget_service import UserMissionWidgetService
    battlePassService = BattlePassService()
    manager.addInstance(IBattlePassService, battlePassService, finalizer='finalize')
    eventsService = EventsService()
    manager.addInstance(IEventsService, eventsService, finalizer='finalize')
    missionsService = MissionsService()
    manager.addInstance(IMissionsService, missionsService, finalizer='finalize')
    missionsContainerService = MissionsContainerService()
    manager.addInstance(IMissionsContainerService, missionsContainerService, finalizer='finalize')
    userMissionWidgetService = UserMissionWidgetService()
    manager.addInstance(IUserMissionWidgetService, userMissionWidgetService, finalizer='finalize')
