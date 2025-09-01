# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/__init__.py
from __future__ import absolute_import
from gui.impl.gen import R
from gui.impl.lobby.gf_notifications import GFNotificationTemplates
from gui.impl.lobby.veh_skill_tree.notifications.perk_available_notification import PerkAvailableNotification
from gui.impl.lobby.vehicle_hub.states import OverviewState, ModulesState, StatsState, ArmorState, VehSkillTreeState, VehSkillTreeInitialState, VehSkillTreePrestigeState, VehSkillTreeProgressionState
from gui.impl.lobby.vehicle_hub.vehicle_hub_main_view import VehicleHubCtx
from gui.shared.system_factory import registerGamefaceNotifications
__all__ = ('OverviewState', 'ModulesState', 'StatsState', 'ArmorState', 'VehSkillTreeState', 'VehSkillTreeInitialState', 'VehSkillTreePrestigeState', 'VehSkillTreeProgressionState', 'VehicleHubCtx')

def getStateMachineRegistrators():
    from gui.impl.lobby.vehicle_hub.states import registerStates, registerTransitions
    return (registerStates, registerTransitions)


def getContextMenuHandlers():
    pass


def getViewSettings():
    pass


def getBusinessHandlers():
    pass


registerGamefaceNotifications({GFNotificationTemplates.SKILL_TREE_PERK_AVAILABLE_NOTIFICATION: (R.views.mono.lobby.veh_skill_tree.notifications.perk_available(), PerkAvailableNotification)})
