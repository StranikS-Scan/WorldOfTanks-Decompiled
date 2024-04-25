# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/commander_cmp.py
from frameworks.wulf import ViewFlags, ViewSettings
from CurrentVehicle import g_currentVehicle
from gui.impl.backport.backport_tooltip import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle_royale.commander_cmp_perk_model import CommanderCmpPerkModel
from gui.impl.gen.view_models.views.battle_royale.commander_cmp_view_model import CommanderCmpViewModel
from gui.impl.gen.view_models.views.battle_royale.commander_cmp_tooltips import CommanderCmpTooltips
from gui.impl.pub import ViewImpl
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import isIncorrectVehicle
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.app_loader import IAppLoader
_R_SKILLS_ICONS = R.images.gui.maps.icons.tankmen.skills.big
_IGNORED_SKILL_NAMES = ('commander_sixthSense',)

class CommanderComponent(InjectComponentAdaptor):

    def _makeInjectView(self):
        return CommanderView(R.views.lobby.battle_royale.CommanderView())


class CommanderView(ViewImpl):
    _RU_REALM_TAG = 'cis'
    __brControl = dependency.descriptor(IBattleRoyaleController)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, viewKey, viewModelClazz=CommanderCmpViewModel):
        settings = ViewSettings(viewKey)
        settings.flags = ViewFlags.VIEW
        settings.model = viewModelClazz()
        self.__toolTipMgr = self.__appLoader.getApp().getToolTipMgr()
        super(CommanderView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CommanderView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            else:
                commanderID = self.__getCommanderID()
                if commanderID is None:
                    return
                if tooltipId == CommanderCmpTooltips.TOOLTIP_TANKMAN:
                    tipData = self.__getTooltipData(commanderID)
                    window = BackportTooltipWindow(tipData, self.getParentWindow()) if tipData is not None else None
                    if window is not None:
                        window.load()
                    return window
                args = (tooltipId,
                 commanderID,
                 None,
                 None,
                 False)
                self.__toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_PERK_GF, args, event.mouse.positionX, event.mouse.positionY)
                return TOOLTIPS_CONSTANTS.CREW_PERK_GF
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

    def __removeListeners(self):
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged

    def __onCurrentVehicleChanged(self):
        self.__updateModel()

    def __updateModel(self):
        vehicle = g_currentVehicle.item
        if isIncorrectVehicle(vehicle):
            return
        with self.viewModel.transaction() as model:
            model.setNation(vehicle.nationName)
            perkList = model.getPerkList()
            perkList.clear()
            commanderSkills = self.__brControl.getBrCommanderSkills()
            for skill in commanderSkills:
                skillName = skill.name
                if skillName in _IGNORED_SKILL_NAMES:
                    continue
                perkModel = CommanderCmpPerkModel()
                perkModel.setIcon(_R_SKILLS_ICONS.dyn(skillName)())
                perkModel.setTooltipID(skillName)
                perkList.addViewModel(perkModel)
                perkList.invalidate()

    def __getTooltipData(self, commanderID):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_ROYALE_TANKMAN, specialArgs=(commanderID, False))

    @staticmethod
    def __getCommanderID():
        vehicle = g_currentVehicle.item
        if vehicle is None:
            return
        else:
            crew = vehicle.crew
            return None if crew is None else crew[0][1].invID
