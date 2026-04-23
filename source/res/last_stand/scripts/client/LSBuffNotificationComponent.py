# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSBuffNotificationComponent.py
from __future__ import absolute_import
from dyn_components_groups import groupComponent
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID
from xml_config_specs import StrParam, ListParam, ObjParam, FloatParam

@groupComponent(buffKey=StrParam(), params=ListParam(valueParam=ObjParam(key=StrParam(), value=FloatParam())))
class LSBuffNotificationComponent(DynamicScriptComponent):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(LSBuffNotificationComponent, self).__init__()
        self._buffKey = self.groupComponentConfig.buffKey
        self._params = self.groupComponentConfig.params

    @property
    def lsBattleGuiCtrl(self):
        return self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)

    @property
    def buffKey(self):
        return self._buffKey

    @property
    def params(self):
        return [ (item.key, item.value) for item in self._params ]

    def _onAvatarReady(self):
        super(LSBuffNotificationComponent, self)._onAvatarReady()
        self.lsBattleGuiCtrl.applyBuff((self.buffKey, self.params), self.entity.id)

    def onDestroy(self):
        self.lsBattleGuiCtrl.unApplyBuff((self.buffKey, self.params))
        super(LSBuffNotificationComponent, self).onDestroy()
