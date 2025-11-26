# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/presenters/dynamic_economics_presenter.py
from __future__ import absolute_import
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _CAPS
from BonusCaps import BonusCapsConst
from constants import Configs
from gui.impl.gen.view_models.views.lobby.common.dynamic_economics_model import DynamicEconomicsModel
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency, server_settings
from skeletons.gui.game_control import IHangarGuiController
from skeletons.gui.lobby_context import ILobbyContext

class DynamicEconomicsPresenter(ViewComponent[DynamicEconomicsModel], IGlobalListener):
    __hangarGuiCtrl = dependency.descriptor(IHangarGuiController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(DynamicEconomicsPresenter, self).__init__(model=DynamicEconomicsModel)

    @property
    def viewModel(self):
        return super(DynamicEconomicsPresenter, self).getViewModel()

    def onPrbEntitySwitched(self):
        self.__updateModel()

    def _getEvents(self):
        return ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),)

    def _getListeners(self):
        return ((events.LobbyHeaderMenuEvent.UPDATE_PREBATTLE_CONTROLS, self.__updateModel, EVENT_BUS_SCOPE.LOBBY),)

    def _onLoading(self, *args, **kwargs):
        super(DynamicEconomicsPresenter, self)._onLoading(*args, **kwargs)
        self.__updateModel()
        self.startGlobalListening()

    def _finalize(self):
        self.stopGlobalListening()
        super(DynamicEconomicsPresenter, self)._finalize()

    def __updateModel(self, *_):
        with self.viewModel.transaction() as model:
            dynamicEconomics = self.__hangarGuiCtrl.dynamicEconomics
            model.setIsCrystalEarnEnabled(dynamicEconomics.checkCurrentCrystalRewards(default=True))
            model.setIsDailyMultipliedXpEnabled(dynamicEconomics.checkCurrentBonusCaps(_CAPS.DAILY_MULTIPLIED_XP, default=True))

    @server_settings.serverSettingsChangeListener(BonusCapsConst.CONFIG_NAME, Configs.CRYSTAL_REWARDS_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        self.__updateModel()
