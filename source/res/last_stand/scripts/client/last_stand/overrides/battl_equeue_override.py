# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/overrides/battl_equeue_override.py
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.Scaleform.framework.view_overrider import OverrideData
from gui.impl.gen import R
from last_stand.gui.impl.lobby.pre_battle_queue_view import PreBattleQueueView
from last_stand.skeletons.ls_controller import ILSController
from helpers import dependency

class BattleQueueOverride(OverrideData):
    lsCtrl = dependency.descriptor(ILSController)

    def __init__(self):
        super(BattleQueueOverride, self).__init__(GuiImplViewLoadParams(R.views.last_stand.mono.lobby.prebattle_queue_view(), PreBattleQueueView, ScopeTemplates.LOBBY_SUB_SCOPE))

    def checkCondition(self, *args, **kwargs):
        return self.lsCtrl.isEventHangar()
