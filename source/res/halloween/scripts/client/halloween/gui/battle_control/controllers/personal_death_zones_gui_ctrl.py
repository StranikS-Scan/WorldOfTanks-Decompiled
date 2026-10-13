# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/battle_control/controllers/personal_death_zones_gui_ctrl.py
from __future__ import absolute_import
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency
from gui.battle_control.controllers.personal_death_zones_gui_ctrl import PersonalDeathZonesGUIController
from halloween.gui.battle_control.halloween_battle_constants import VEHICLE_VIEW_STATE

class HWPersonalDeathZonesGUIController(PersonalDeathZonesGUIController):
    _guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    _ZONE_TO_STATE = {'ignite_deathzone_aoe_hw': VEHICLE_VIEW_STATE.HW_PERSONAL_DEATH_ZONE_IGNITE,
     'ignite_deathzone_overtime_aoe_hw': VEHICLE_VIEW_STATE.HW_PERSONAL_DEATH_ZONE_IGNITE,
     'stun_deathzone_aoe_hw': VEHICLE_VIEW_STATE.HW_PERSONAL_DEATH_ZONE_STUN,
     'interval_deathzone_aoe_hw': VEHICLE_VIEW_STATE.HW_PERSONAL_DEATH_ZONE_INTERVAL}

    def _updateWarningNotification(self, zone, visible):
        groupName = zone._equipment.groupName
        if groupName in self._ZONE_TO_STATE:
            self._guiSessionProvider.invalidateVehicleState(self._ZONE_TO_STATE[groupName], (visible, zone.delay if visible else 0, zone.launchTime if visible else 0))
        else:
            super(HWPersonalDeathZonesGUIController, self)._updateWarningNotification(zone, visible)
