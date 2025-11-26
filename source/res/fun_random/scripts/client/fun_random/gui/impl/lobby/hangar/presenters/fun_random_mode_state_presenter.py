# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/presenters/fun_random_mode_state_presenter.py
from __future__ import absolute_import
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_mode_state_model import FunRandomModeStateModel
from gui.impl.pub.view_component import ViewComponent

class FunRandomModeStatePresenter(ViewComponent[FunRandomModeStateModel], FunSubModesWatcher):

    def __init__(self):
        super(FunRandomModeStatePresenter, self).__init__(model=FunRandomModeStateModel)

    @property
    def viewModel(self):
        return super(FunRandomModeStatePresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(FunRandomModeStatePresenter, self)._onLoading(*args, **kwargs)
        self.startSubSettingsListening(self.__invalidateAll, desiredOnly=True)
        self.startSubSelectionListening(self.__invalidateAll)
        self.__invalidateAll()

    def _finalize(self):
        self.stopSubSelectionListening(self.__invalidateAll)
        self.stopSubSettingsListening(self.__invalidateAll, desiredOnly=True)
        super(FunRandomModeStatePresenter, self)._finalize()

    def _getCallbacks(self):
        return super(FunRandomModeStatePresenter, self)._getCallbacks() + (('inventory.1', self.__invalidateAll),)

    @hasDesiredSubMode()
    def __invalidateAll(self, *_):
        with self.viewModel.transaction() as model:
            model.setAssetsPointer(self.getDesiredSubMode().getAssetsPointer())
            model.setHasSuitableVehicles(self.getDesiredSubMode().hasSuitableVehicles())
