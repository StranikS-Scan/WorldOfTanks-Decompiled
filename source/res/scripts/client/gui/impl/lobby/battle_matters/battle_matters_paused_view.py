# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_matters/battle_matters_paused_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_matters.battle_matters_paused_view_model import BattleMattersPausedViewModel
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showBattleMatters
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from skeletons.gui.battle_matters import IBattleMattersController

class BattleMattersPausedView(ViewImpl):
    __slots__ = ()
    __battleMattersController = dependency.descriptor(IBattleMattersController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_matters.BattleMattersPausedView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = BattleMattersPausedViewModel()
        super(BattleMattersPausedView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleMattersPausedView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.gotoHangar, self.__gotoHangar), (self.__battleMattersController.onStateChanged, self.__onStateChanged))

    @staticmethod
    def __gotoHangar():
        showHangar()

    def __onStateChanged(self):
        if self.__battleMattersController.isEnabled():
            if not self.__battleMattersController.isPaused():
                showBattleMatters()
        else:
            showHangar()
