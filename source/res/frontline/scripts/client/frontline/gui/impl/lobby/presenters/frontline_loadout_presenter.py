# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/presenters/frontline_loadout_presenter.py
import typing
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen import R
from gui.impl.lobby.hangar.presenters.consumables_presenter import ConsumablesPresenter
from gui.impl.lobby.hangar.presenters.equipments_presenter import EquipmentsPresenter
from gui.impl.lobby.hangar.presenters.instructions_presenter import InstructionsPresenter
from frontline.gui.impl.lobby.presenters.frontline_ability_presenter import FrontlineAbilityPresenter
from gui.impl.lobby.hangar.presenters.loadout_presenter import LoadoutPresenter, _LoadoutStatesObserver
from gui.impl.lobby.hangar.presenters.shells_presenter import ShellsPresenter
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_const import FrontlineConst
from frontline.gui.impl.lobby.presenters.fl_hangar_ammunition_groups_controller import FLHangarAmmunitionGroupsController
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
if typing.TYPE_CHECKING:
    from gui.impl.pub.view_component import ViewComponent

class _FrontlineLoadoutStatesObserver(_LoadoutStatesObserver):
    _GROUP_SECTIONS_NAMES = [[TankSetupConstants.OPT_DEVICES, TankSetupConstants.BATTLE_BOOSTERS, FrontlineConst.BATTLE_ABILITIES], [TankSetupConstants.SHELLS, TankSetupConstants.CONSUMABLES]]

    @property
    def _stateID(self):
        from frontline.gui.impl.lobby.states import FrontlineLoadoutState
        return FrontlineLoadoutState.STATE_ID


class FrontlineLoadoutPresenter(LoadoutPresenter):
    _STATES_OBSERVER = _FrontlineLoadoutStatesObserver
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        self._toolTipMgr = self._appLoader.getApp().getToolTipMgr()
        super(FrontlineLoadoutPresenter, self).__init__()

    def createToolTip(self, event):
        if event.contentID == R.views.frontline.mono.lobby.tooltips.battle_ability_tooltip():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == FrontlineConst.BATTLE_ABILITIES:
                intCD = event.getArgument('intCD')
                self._toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.FRONTLINE_BATTLE_ABILITY, (intCD,), event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
            return tooltipId
        return super(FrontlineLoadoutPresenter, self).createToolTip(event)

    def _getChildComponents(self):
        hangar = R.aliases.hangar.shared
        frontline = R.aliases.frontline
        return {hangar.Equipments(): lambda : EquipmentsPresenter(self._vehInteractingItem),
         hangar.Instructions(): lambda : InstructionsPresenter(self._vehInteractingItem),
         hangar.Shells(): lambda : FrontlineShellsPresenter(self._vehInteractingItem),
         hangar.Consumables(): lambda : ConsumablesPresenter(self._vehInteractingItem),
         frontline.loadout.BattleAbilities(): lambda : FrontlineAbilityPresenter(self._vehInteractingItem, self.getSlotSelectionObserver())}

    def __updateAmmunitionGroupsController(self, recreate=False, sectionName=None):
        if not g_currentVehicle.isPresent():
            return
        vehicle = self._vehInteractingItem.getItem()
        if self.__ammunitionGroupsController:
            self.__ammunitionGroupsController.updateVehicle(vehicle)
        else:
            self.__ammunitionGroupsController = FLHangarAmmunitionGroupsController(vehicle)
        self.__updateModel(recreate, sectionName)


class FrontlineShellsPresenter(ShellsPresenter):

    @property
    def isShellState(self):
        from frontline.gui.impl.lobby.states import FrontlineShellsLoadoutState
        lsm = getLobbyStateMachine()
        return lsm.getStateByCls(FrontlineShellsLoadoutState).isEntered()
