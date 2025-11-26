# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/presenters/header_presenter.py
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.shared import IItemsCache
from battle_royale.gui.constants import BattleRoyaleModeState
from battle_royale.gui.impl.gen.view_models.views.lobby.views.header_model import HeaderModel, ModeStatus

class HeaderPresenter(ViewComponent[HeaderModel], IGlobalListener):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(HeaderPresenter, self).__init__(model=HeaderModel)

    @property
    def viewModel(self):
        return super(HeaderPresenter, self).getViewModel()

    def onPrbEntitySwitched(self):
        self.__update()

    def _getEvents(self):
        return super(HeaderPresenter, self)._getEvents() + ((self.__battleRoyaleController.onPrimeTimeStatusUpdated, self.__update),)

    def _onLoading(self, *args, **kwargs):
        super(HeaderPresenter, self)._onLoading(*args, **kwargs)
        self.startGlobalListening()
        self.__update()

    def _finalize(self):
        self.stopGlobalListening()
        return super(HeaderPresenter, self)._finalize()

    def __update(self, *_):
        isAlert = self.__battleRoyaleController.getModeState() != BattleRoyaleModeState.Regular
        if isAlert:
            modeStatus = ModeStatus.ALERT
        else:
            modeStatus = ModeStatus.BATTLESELECTOR
        self.viewModel.setModeStatus(modeStatus)
