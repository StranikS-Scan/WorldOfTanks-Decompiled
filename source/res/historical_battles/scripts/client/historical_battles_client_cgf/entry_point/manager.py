# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles_client_cgf/entry_point/manager.py
import CGF
from cgf_script.managers_registrator import autoregister, onAddedQuery
from events_core_client.events_core_cgf.entry_point.component import EventNames, EventClickedComponent
from helpers import dependency
from shared_utils import nextTick

@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class HistoricalBattlesExt3dEntryPoint(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, EventClickedComponent)
    def onEventClickedAdded(self, go, clicked):
        if clicked.eventName == EventNames.HB.value:
            from historical_battles.skeletons.gui.game_event_controller import IGameEventController
            ctrl = dependency.instance(IGameEventController)
            nextTick(ctrl.switchPrb)()
            go.removeComponent(clicked)
