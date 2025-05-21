# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSBuffVehicleIconComponent.py
from dyn_components_groups import groupComponent
from script_component.DynamicScriptComponent import DynamicScriptComponent
from xml_config_specs import StrParam
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID

@groupComponent(icon=StrParam())
class LSBuffVehicleIconComponent(DynamicScriptComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(LSBuffVehicleIconComponent, self).__init__()
        self._icon = self.groupComponentConfig.icon

    def _onAvatarReady(self):
        lsBattleGuiCtrl = self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)
        if lsBattleGuiCtrl:
            lsBattleGuiCtrl.addVehicleMarkerIcon(self.entity.id, self._icon)

    def onDestroy(self):
        lsBattleGuiCtrl = self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)
        if lsBattleGuiCtrl:
            lsBattleGuiCtrl.removeVehicleMarkerIcon(self.entity.id, self._icon)
        super(LSBuffVehicleIconComponent, self).onDestroy()

    @property
    def icon(self):
        return self._icon
