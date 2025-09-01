# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/SMDisableShotSNComponent.py
from dyn_components_groups import groupComponent
from gui.battle_control.avatar_getter import getPlayerVehicleID
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from xml_config_specs import FloatParam
from story_mode.gui.battle_control.battle_constant import VEHICLE_VIEW_STATE

@groupComponent(duration=FloatParam())
class SMDisableShotSNComponent(DynamicScriptComponent):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(SMDisableShotSNComponent, self).__init__()
        self._updateSNTimer(self.groupComponentConfig.duration)

    def onDestroy(self):
        self._updateSNTimer(0.0)
        super(SMDisableShotSNComponent, self).onDestroy()

    def _updateSNTimer(self, duration):
        if getPlayerVehicleID() != self.entity.id:
            return
        self._sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.SCC_DISABLE_SHOT, duration)
