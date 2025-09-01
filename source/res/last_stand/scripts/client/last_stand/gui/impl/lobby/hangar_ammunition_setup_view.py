# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/hangar_ammunition_setup_view.py
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.backport import TooltipData
from gui.impl.lobby.tank_setup.ammunition_setup.base_hangar import BaseHangarAmmunitionSetupView
from gui.impl.lobby.tank_setup.main_tank_setup.hangar import HangarMainTankSetupView
from gui.impl.lobby.tank_setup.tank_setup_builder import HangarTankSetupBuilder
from last_stand.gui.impl.gen.view_models.views.lobby.ext_ammo_setup_view import ExtAmmoSetupView
from last_stand.gui.sounds import playSound
from last_stand.gui.sounds.sound_constants import CONSUMABLES_VIEW_EXIT, CONSUMABLES_VIEW_ENTER
from last_stand.gui.impl.lobby.tank_setup.sub_view import LastStandSetupSubView
from last_stand.gui.impl.lobby.tank_setup.interactor import LastStandInteractor
from last_stand.gui.impl.lobby.hangar_ammunition_panel_view import LSAmmunitionPanel
from last_stand.gui.ls_gui_constants import LS_ABILITY_TOOLTIP, LS_MAIN_SHELL
from last_stand.gui.impl.lobby.ls_vehicle_params_view import LSVehicleParamsPresenter
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.tank_setup.interactors.battle_booster import BattleBoosterInteractor
from gui.impl.lobby.tank_setup.interactors.opt_device import OptDeviceInteractor
from gui.impl.lobby.tank_setup.interactors.shell import ShellInteractor
from gui.impl.lobby.tank_setup.sub_views.battle_booster_setup import BattleBoosterSetupSubView
from gui.impl.lobby.tank_setup.sub_views.opt_device_setup import OptDeviceSetupSubView
from gui.impl.lobby.tank_setup.sub_views.shell_setup import ShellSetupSubView

class LSHangarAmmunitionSetupView(BaseHangarAmmunitionSetupView):
    _VIEW_FLAG = ViewFlags.LOBBY_TOP_SUB_VIEW
    _VIEW_MODEL = ExtAmmoSetupView

    def changeGroupsPreset(self):
        self._ammunitionPanel.switchToNextPreset()

    def _createBlur(self):
        return None

    def _initialize(self, *args, **kwargs):
        self._ammunitionPanel.initialize()
        self._tankSetup.initialize()
        self._addListeners()
        playSound(CONSUMABLES_VIEW_ENTER)

    def _finalize(self):
        playSound(CONSUMABLES_VIEW_EXIT)
        super(LSHangarAmmunitionSetupView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(LSHangarAmmunitionSetupView, self)._onLoading(**kwargs)
        self._paramsView = LSVehicleParamsPresenter()
        self.setChildView(R.views.lobby.hangar.subViews.VehicleParams(), self._paramsView)

    def _addListeners(self):
        super(LSHangarAmmunitionSetupView, self)._addListeners()
        self.viewModel.onSwitch += self.changeGroupsPreset

    def _removeListeners(self):
        self.viewModel.onSwitch -= self.changeGroupsPreset
        super(LSHangarAmmunitionSetupView, self)._removeListeners()

    def _createMainTankSetup(self):
        return HangarMainTankSetupView(self.viewModel.tankSetup, self.__getTankSetupBuilder()(self._vehItem))

    def _createAmmunitionPanel(self):
        ctx = {'specializationClickable': True}
        return LSAmmunitionPanel(self.viewModel.ammunitionPanel, self._vehItem.getItem(), ctx=ctx)

    def _closeWindow(self):
        self._isClosed = True
        self.viewModel.setShow(False)
        self.destroyWindow()

    def _getBackportTooltipData(self, event):
        data = super(LSHangarAmmunitionSetupView, self)._getBackportTooltipData(event)
        if data is None:
            return
        elif data.specialAlias in (TOOLTIPS_CONSTANTS.HANGAR_MODULE, TOOLTIPS_CONSTANTS.HANGAR_CARD_MODULE):
            return TooltipData(data.tooltip, data.isSpecial, LS_ABILITY_TOOLTIP, data.specialArgs, data.isWulfTooltip)
        else:
            return TooltipData(data.tooltip, data.isSpecial, LS_MAIN_SHELL, data.specialArgs, data.isWulfTooltip) if data.specialAlias == TOOLTIPS_CONSTANTS.TECH_MAIN_SHELL else data

    def __getTankSetupBuilder(self):
        return LSTankSetupBuilder


class LSTankSetupBuilder(HangarTankSetupBuilder):
    __slots__ = ()

    def configureComponents(self, viewModel):
        components = []
        self.addComponent(components, viewModel.shellsSetup, ShellSetupSubView, ShellInteractor(self._vehItem))
        self.addComponent(components, viewModel.consumablesSetup, LastStandSetupSubView, LastStandInteractor(self._vehItem))
        self.addComponent(components, viewModel.optDevicesSetup, OptDeviceSetupSubView, OptDeviceInteractor(self._vehItem))
        self.addComponent(components, viewModel.battleBoostersSetup, BattleBoosterSetupSubView, BattleBoosterInteractor(self._vehItem))
        return components
