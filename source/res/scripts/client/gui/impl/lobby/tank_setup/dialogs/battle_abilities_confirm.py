# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/battle_abilities_confirm.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.fitting_types import FittingTypes
from gui.impl.gen.view_models.views.lobby.common.buy_and_exchange_bottom_content_type import BuyAndExchangeBottomContentType
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.ammunition_buy_model import AmmunitionBuyModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.confirm_bottom_content_type import ConfirmBottomContentType
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.impl.lobby.tank_setup.dialogs.main_content.main_contents import AmmunitionBuyMainContent
from uilogging.epic_battle.constants import EpicBattleLogKeys, EpicBattleLogActions, EpicBattleLogButtons
from uilogging.epic_battle.loggers import EpicBattleLogger

class BattleAbilitiesSetupConfirm(FullScreenDialogView):
    __slots__ = ('__items', '_mainContent', '__rollBack', '__withInstall', '__uiEpicBattleLogger')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.tanksetup.dialogs.Confirm(), model=AmmunitionBuyModel())
        settings.args = args
        settings.kwargs = kwargs
        self.__items = kwargs.pop('items', tuple())
        self._mainContent = None
        self.__rollBack = False
        self.__withInstall = kwargs.pop('withInstall', False)
        self.__uiEpicBattleLogger = EpicBattleLogger()
        super(BattleAbilitiesSetupConfirm, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattleAbilitiesSetupConfirm, self)._onLoading(*args, **kwargs)
        if self.__withInstall:
            self.viewModel.setBottomContentType(BuyAndExchangeBottomContentType.DEAL_PANEL)
        else:
            self.viewModel.setBottomContentType(ConfirmBottomContentType.SAVE_SLOTS_CONTENT)
        self.viewModel.setVehicleType(kwargs.get('vehicleType', ''))
        self.viewModel.setApplyForAllVehiclesByType(kwargs.get('applyForAllVehiclesByType', False))
        self._mainContent = AmmunitionBuyMainContent(viewModel=self.viewModel.mainContent, items=self.__items, itemsType=FittingTypes.BATTLE_ABILITY)
        self._mainContent.onLoading()
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.OPEN.value, item=EpicBattleLogKeys.ABILITIES_CONFIRM.value, parentScreen=EpicBattleLogKeys.SETUP_VIEW.value)

    def _initialize(self, *args, **kwargs):
        super(BattleAbilitiesSetupConfirm, self)._initialize()
        if self._mainContent is not None:
            self._mainContent.initialize()
        return

    def _finalize(self):
        if self._mainContent is not None:
            self._mainContent.finalize()
        super(BattleAbilitiesSetupConfirm, self)._finalize()
        return

    def _getAdditionalData(self):
        return {'rollBack': self.__rollBack}

    def _onCancelClicked(self):
        self.__rollBack = True
        self._onCancel()
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, item=EpicBattleLogButtons.NOT_INSTALL.value, parentScreen=EpicBattleLogKeys.ABILITIES_CONFIRM.value)

    def _onAcceptClicked(self):
        super(BattleAbilitiesSetupConfirm, self)._onAcceptClicked()
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, item=EpicBattleLogButtons.INSTALL.value, parentScreen=EpicBattleLogKeys.ABILITIES_CONFIRM.value)

    def _onExitClicked(self):
        super(BattleAbilitiesSetupConfirm, self)._onExitClicked()
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, item=EpicBattleLogButtons.CLOSE.value, parentScreen=EpicBattleLogKeys.ABILITIES_CONFIRM.value)
