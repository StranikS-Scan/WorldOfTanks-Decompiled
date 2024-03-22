# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/primary_objective/settings_model.py
import typing
from gui.Scaleform.daapi.view.battle.pve_base.base.settings_model import BaseWidgetSettingsModel
from pve_battle_hud import PrimaryObjectiveState

class PrimaryObjectiveServerModel(BaseWidgetSettingsModel):
    __slots__ = ('state', 'timer', 'finishTime', 'progresses', 'params')

    def __init__(self, id, type, state, timer, finishTime, progresses, params):
        super(PrimaryObjectiveServerModel, self).__init__(id, type, PrimaryObjectiveState(state))
        self.timer = timer
        self.finishTime = finishTime
        self.progresses = progresses
        self.params = params

    def __repr__(self):
        return '<PrimaryObjectiveServerModel>: id=%s, type=%s, state=%s, timer=%s, finishTime=%s, progresses=%s, params=%s' % (self.id,
         self.type,
         self.state,
         self.timer,
         self.finishTime,
         self.progresses,
         self.params)
