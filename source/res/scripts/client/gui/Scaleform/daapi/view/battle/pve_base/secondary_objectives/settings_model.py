# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/secondary_objectives/settings_model.py
import typing
from gui.Scaleform.daapi.view.battle.pve_base.base.settings_model import BaseWidgetSettingsModel
from pve_battle_hud import SecondaryObjectiveState

class SecondaryObjectiveServerModel(BaseWidgetSettingsModel):
    __slots__ = ('state', 'timer', 'finishTime', 'progress', 'params')

    def __init__(self, id, type, state, timer, finishTime, progress, params):
        super(SecondaryObjectiveServerModel, self).__init__(id, type, SecondaryObjectiveState(state))
        self.timer = timer
        self.finishTime = finishTime
        self.progress = progress
        self.params = params

    def __repr__(self):
        return '<SecondaryObjectiveServerModel>: id=%s, type=%s, state=%s, timer=%s, finishTime=%s, progress=%s, params=%s' % (self.id,
         self.type,
         self.state,
         self.timer,
         self.finishTime,
         self.progress,
         self.params)
