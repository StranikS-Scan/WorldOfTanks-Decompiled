# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/__init__.py
import typing
if typing.TYPE_CHECKING:
    from helpers.dependency import DependencyManager
__all__ = ('getUserMissionsConfig',)

def getUserMissionsConfig(manager):
    from gui.impl.lobby.user_missions.hangar_widget.services import IBattlePassService, IEventsService, IMissionsService, ICampaignService
    from gui.impl.lobby.user_missions.hangar_widget.services.battle_pass_service import BattlePassService
    from gui.impl.lobby.user_missions.hangar_widget.services.events_service import EventsService
    from gui.impl.lobby.user_missions.hangar_widget.services.missions_service import MissionsService
    from gui.impl.lobby.user_missions.hangar_widget.services.campaign_service import CampaignService
    battlePassService = BattlePassService()
    manager.addInstance(IBattlePassService, battlePassService, finalizer='finalize')
    eventsService = EventsService()
    manager.addInstance(IEventsService, eventsService, finalizer='finalize')
    missionsService = MissionsService()
    manager.addInstance(IMissionsService, missionsService, finalizer='finalize')
    campaignService = CampaignService()
    manager.addInstance(ICampaignService, campaignService, finalizer='finalize')
