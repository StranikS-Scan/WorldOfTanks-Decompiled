# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/commander_cmp.py
from frameworks.wulf import ViewFlags
from CurrentVehicle import g_currentVehicle
from gui.impl.backport.backport_tooltip import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle_royale.commander_cmp_view_model import CommanderCmpViewModel
from gui.impl.gen.view_models.views.battle_royale.commander_cmp_tooltips import CommanderCmpTooltips
from gui.impl.pub import ViewImpl
from gui.Scaleform.daapi.view.common.battle_royale_helpers import isIncorrectVehicle
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

class CommanderComponent(InjectComponentAdaptor):

    def _makeInjectView(self):
        return CommanderView()


class CommanderView(ViewImpl):
    _RU_REALM_TAG = 'cis'
    __brControl = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, *args, **kwargs):
        super(CommanderView, self).__init__(R.views.lobby.battleRoyale.commander_cmp.CommanderCmp(), ViewFlags.COMPONENT, CommanderCmpViewModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(CommanderView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(CommanderView, self).createToolTip(event)

    def _initialize(self):
        super(CommanderView, self)._initialize()
        self.__addListeners()
        self.__updateModel()

    def _finalize(self):
        self.__removeListeners()
        super(CommanderView, self)._finalize()

    def __addListeners(self):
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self.viewModel.onToggleSound += self.__onToggleSound

    def __removeListeners(self):
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        self.viewModel.onToggleSound -= self.__onToggleSound

    def __onCurrentVehicleChanged(self):
        self.__updateModel()

    def __updateModel(self):
        vehicle = g_currentVehicle.item
        if isIncorrectVehicle(vehicle):
            return
        with self.getViewModel().transaction() as model:
            isRuRealm = self.__brControl.voiceoverController.isRuRealm
            model.setNation(self._RU_REALM_TAG if isRuRealm else vehicle.nationName)
            model.setIsRuRealm(isRuRealm)
            model.setIsRuVoEnabled(self.__brControl.voiceoverController.isEnabled)

    def __getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        commanderID = self.__getCommanderID()
        if commanderID is None:
            return
        elif tooltipId in (CommanderCmpTooltips.TOOLTIP_SIXTH_SENSE_SKILL, CommanderCmpTooltips.TOOLTIP_EXPERT_SKILL):
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_SKILL, specialArgs=(tooltipId, commanderID))
        else:
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_ROYALE_TANKMAN, specialArgs=(commanderID, False)) if tooltipId == CommanderCmpTooltips.TOOLTIP_TANKMAN else None

    def __onToggleSound(self):
        voControl = self.__brControl.voiceoverController
        voControl.setEnabled(not voControl.isEnabled)
        self.__updateModel()

    @staticmethod
    def __getCommanderID():
        vehicle = g_currentVehicle.item
        if vehicle is None:
            return
        else:
            crew = vehicle.crew
            return None if crew is None else crew[0][1].invID
