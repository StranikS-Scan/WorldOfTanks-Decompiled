# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/cgf/snowstorm_hint.py
import CGF
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from grinch.cgf import getVehicleFromGO
from grinch_common.cgf.snowstorm import GrinchSnowstormTriggerComponent
from grinch_common.grinch_constants import ARENA_BONUS_TYPE_CAPS
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.GRINCH, CGF.DomainOption.DomainClient)
class SnowstormHintManager(CGF.ComponentManager):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    @onAddedQuery(GrinchSnowstormTriggerComponent)
    def onAdded(self, grinchSnowstormTriggerComponent):
        areaTrigger = grinchSnowstormTriggerComponent.trigger()
        if not areaTrigger:
            return
        grinchSnowstormTriggerComponent.enterReactionId = areaTrigger.addEnterReaction(self.__onEnter)
        grinchSnowstormTriggerComponent.exitReactionId = areaTrigger.addExitReaction(self.__onExit)

    @onRemovedQuery(GrinchSnowstormTriggerComponent)
    def onRemoved(self, grinchSnowstormTriggerComponent):
        areaTrigger = grinchSnowstormTriggerComponent.trigger()
        if not areaTrigger:
            return
        else:
            if grinchSnowstormTriggerComponent.enterReactionId is not None:
                areaTrigger.removeEnterReaction(grinchSnowstormTriggerComponent.enterReactionId)
            if grinchSnowstormTriggerComponent.exitReactionId is not None:
                areaTrigger.removeEnterReaction(grinchSnowstormTriggerComponent.exitReactionId)
            return

    def __onEnter(self, gameObject, snowstormGO):
        vehicle = getVehicleFromGO(self.spaceID, gameObject)
        if not vehicle:
            return
        if not vehicle.isAlive():
            return
        from gui.battle_control import avatar_getter
        if vehicle.id == avatar_getter.getPlayerVehicleID():
            from gui.battle_control import battle_constants
            self.__guiSessionProvider.invalidateVehicleState(battle_constants.VEHICLE_VIEW_STATE.WARNING_ZONE, battle_constants.DestroyTimerViewState(battle_constants.VEHICLE_VIEW_STATE.WARNING_ZONE, 0.0, battle_constants.TIMER_VIEW_STATE.WARNING, startTime=0.0))

    def __onExit(self, gameObject, snowstormGO):
        vehicle = getVehicleFromGO(self.spaceID, gameObject)
        if not vehicle:
            return
        from gui.battle_control import avatar_getter
        if vehicle.id == avatar_getter.getPlayerVehicleID():
            from gui.battle_control import battle_constants
            self.__guiSessionProvider.invalidateVehicleState(battle_constants.VEHICLE_VIEW_STATE.WARNING_ZONE, battle_constants.DestroyTimerViewState.makeCloseTimerState(battle_constants.VEHICLE_VIEW_STATE.WARNING_ZONE))
