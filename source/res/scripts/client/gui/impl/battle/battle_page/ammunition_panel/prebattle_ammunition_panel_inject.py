# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/ammunition_panel/prebattle_ammunition_panel_inject.py
from constants import ARENA_PERIOD
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.Scaleform.daapi.view.meta.PrebattleAmmunitionPanelViewMeta import PrebattleAmmunitionPanelViewMeta
from gui.impl.battle.battle_page.ammunition_panel.prebattle_ammunition_panel_view import PrebattleAmmunitionPanelView
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class PrebattleAmmunitionPanelInject(PrebattleAmmunitionPanelViewMeta, IAbstractPeriodView):
    __slots__ = ('__view', '__arenaPeriod')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PrebattleAmmunitionPanelInject, self).__init__()
        self.__view = None
        self.__arenaPeriod = None
        return

    def onViewIsHidden(self):
        self._destroyInjected()

    def _onPopulate(self):
        ctrl = self.sessionProvider.shared.vehiclePostProgression
        if ctrl.postProgression.isPostProgressionEnabled:
            super(PrebattleAmmunitionPanelInject, self)._onPopulate()

    def _dispose(self):
        self.__view = None
        super(PrebattleAmmunitionPanelInject, self)._dispose()
        return

    def setPeriod(self, period):
        if self.__view and period == ARENA_PERIOD.BATTLE:
            self.__view.updateViewActive(False)
            self.as_hideS(self.__arenaPeriod is not None)
        self.__arenaPeriod = period
        return

    def _makeInjectView(self):
        self.__view = PrebattleAmmunitionPanelView()
        return self.__view
