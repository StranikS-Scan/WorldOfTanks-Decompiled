# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/battle_modifiers_panel.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.shared.system_factory import collectBattleModifiersPanel
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.game_control import IFunRandomController, IBattleModifiersController
from gui.impl.gen import R

class BattleModifiersPanelInject(InjectComponentAdaptor):
    __slots__ = ('_currentViewId',)
    __battleModifiersController = dependency.descriptor(IBattleModifiersController)
    __funRandomCtrl = dependency.descriptor(IFunRandomController)

    def __init__(self):
        super(BattleModifiersPanelInject, self).__init__()
        self._currentViewId = R.invalid()

    @nextTick
    def updateState(self):
        newViewId = BattleModifiersPanelInject._getActiveModifierPanel()
        if self._currentViewId != newViewId:
            self._currentViewId = newViewId
            self._destroyInjected()
            if newViewId != R.invalid():
                self._createInjectView(newViewId)

    def _onPopulate(self):
        self.updateState()

    def _makeInjectView(self, viewId=None):
        classView = collectBattleModifiersPanel().get(viewId)
        return classView()

    @staticmethod
    def _getActiveModifierPanel():
        entries = collectBattleModifiersPanel()
        for viewId, view in entries.iteritems():
            if view.getIsActive():
                return viewId

        return R.invalid()
