# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/progress_counter/settings_model.py
import typing
from gui.Scaleform.daapi.view.battle.pve_base.base.settings_model import BaseWidgetSettingsModel
from pve_battle_hud import ProgressCounterState

class ProgressCounterServerModel(BaseWidgetSettingsModel):
    __slots__ = ('state', 'params')

    def __init__(self, id, type, state, params):
        super(ProgressCounterServerModel, self).__init__(id, type, ProgressCounterState(state))
        self.params = params

    def __repr__(self):
        return '<ProgressCounterServerModel>: id=%s, type=%s, state=%s, params=%s' % (self.id,
         self.type,
         self.state,
         self.params)
