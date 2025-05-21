# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/overrides/hangar_override.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.Scaleform.framework.view_overrider import OverrideData
from gui.impl.gen import R
from last_stand.gui.impl.lobby.hangar_view import HangarView
from last_stand.skeletons.ls_controller import ILSController
from helpers import dependency

class HangarOverride(OverrideData):
    lsCtrl = dependency.descriptor(ILSController)

    def __init__(self):
        super(HangarOverride, self).__init__(GuiImplViewLoadParams(R.views.last_stand.mono.lobby.hangar(), HangarView, ScopeTemplates.LOBBY_SUB_SCOPE))

    def checkCondition(self, *args, **kwargs):
        return self.lsCtrl.isEventHangar() and self.lsCtrl.isAvailable()

    def getFadeCtx(self):
        return {'layer': WindowLayer.OVERLAY,
         'waitForLayoutReady': R.views.last_stand.mono.lobby.hangar()}
