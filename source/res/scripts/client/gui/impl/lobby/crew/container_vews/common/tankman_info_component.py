# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/common/tankman_info_component.py
import typing
import BigWorld
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import createAndLoadBackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.container_views.base.components import ComponentBase
from gui.impl.lobby.crew.tooltips.perk_available_tooltip import PerkAvailableTooltip
from gui.impl.lobby.crew.tooltips.premium_vehicle_tooltip import PremiumVehicleTooltip
from gui.impl.lobby.crew.utils import convertMoneyToTuple, playRecruitVoiceover, VEHICLE_TAGS_FILTER
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from uilogging.crew.loggers import CrewTankmanInfoLogger
from uilogging.crew.logging_constants import CrewPersonalFileKeys
if typing.TYPE_CHECKING:
    from typing import Any, Callable, Tuple
    from gui.impl.gen.view_models.views.lobby.crew.common.tankman_info_model import TankmanInfoModel

class TankmanInfoComponent(ComponentBase):
    _itemsCache = dependency.descriptor(IItemsCache)
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, key, parent, logUIEvents=False):
        self._toolTipMgr = self._appLoader.getApp().getToolTipMgr()
        self._uiLogger = CrewTankmanInfoLogger(logUIEvents)
        super(TankmanInfoComponent, self).__init__(key, parent)

    def _getViewModel(self, vm):
        return vm.tankmanInfo

    def _getEvents(self):
        return super(TankmanInfoComponent, self)._getEvents() + ((self.viewModel.onPlayUniqueVoice, self._onPlayUniqueVoice), (self.viewModel.onChangeVehicle, self._onChangeVehicle), (self.viewModel.onRetrain, self._onRetrain))

    def _fillViewModel(self, vm):
        self._setTankmanInfo(vm)
        self._setVehicleInfo(vm)

    def _setTankmanInfo(self, vm):
        vm.setInvId(self.context.tankman.invID)
        vm.setIconName(self.context.tankman.getExtensionLessIconWithSkin())
        vm.setFullName(self.context.tankman.getFullUserNameWithSkin())
        vm.setDescription(self.context.tankman.getDescription())
        vm.setRole(self.context.tankman.role)
        vm.setSkillsEfficiency(self.context.tankman.currentVehicleSkillsEfficiency)
        vm.setIsInSkin(self.context.tankman.isInSkin)
        vm.setIsFemale(self.context.tankman.isFemale)
        vm.setIsCrewLocked(self.context.tankmanCurrentVehicle and self.context.tankmanCurrentVehicle.isCrewLocked)
        vm.setHasPostProgression(not bool(self.context.tankman.descriptor.needXpForVeteran))
        vm.setIsPostProgressionAnimated(BigWorld.player().crewAccountController.getTankmanVeteranAnimanion(self.context.tankman.invID))
        vm.setHasUniqueSound(self.context.voiceoverParams is not None)
        vm.setHasRetrainDiscount(self.context.retrainPrice.isActionPrice())
        return

    def _setVehicleInfo(self, vm):
        if self.context.tankmanCurrentVehicle:
            fillVehicleModel(vm.currentVehicle, self.context.tankmanCurrentVehicle, VEHICLE_TAGS_FILTER)
            vm.currentVehicle.setIsPremium(self.context.tankmanCurrentVehicle.isPremium)
        if self.context.tankmanNativeVehicle:
            fillVehicleModel(vm.nativeVehicle, self.context.tankmanNativeVehicle, VEHICLE_TAGS_FILTER)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            posX, posY = event.mouse.positionX, event.mouse.positionY
            parent = self.parent.getParentWindow()
            self._uiLogger.onBeforeTooltipOpened(tooltipId)
            if tooltipId == TooltipConstants.SKILL:
                args = [str(event.getArgument('skillName')),
                 self.context.tankmanID,
                 None,
                 False,
                 True,
                 event.getArgument('isBonus')]
                self._toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_PERK_GF, args, posX, posY, parent)
                return TOOLTIPS_CONSTANTS.CREW_PERK_GF
            if tooltipId == TOOLTIPS_CONSTANTS.COMMANDER_BONUS:
                args = (self.context.tankman.invID,)
                self._toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.COMMANDER_BONUS, args, posX, posY, parent)
                return TOOLTIPS_CONSTANTS.COMMANDER_BONUS
            if tooltipId == TOOLTIPS_CONSTANTS.CREW_SKILL_UNTRAINED:
                args = ()
                self._toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_SKILL_UNTRAINED, args, posX, posY, parent)
                return TOOLTIPS_CONSTANTS.CREW_SKILL_UNTRAINED
            if tooltipId == TooltipConstants.TANKMAN:
                args = (self.context.tankman.invID,)
                self._toolTipMgr.onCreateWulfTooltip(TooltipConstants.TANKMAN, args, posX, posY, parent)
                return TooltipConstants.TANKMAN
            if tooltipId == TooltipConstants.SKILLS_EFFICIENCY:
                args = (event.getArgument('tankmanID'),)
                self._toolTipMgr.onCreateWulfTooltip(tooltipId, args, posX, posY, parent)
                return tooltipId
            if tooltipId == TOOLTIPS_CONSTANTS.ACTION_PRICE:
                specialArgs = (None,
                 None,
                 convertMoneyToTuple(self.context.retrainPrice.price),
                 convertMoneyToTuple(self.context.retrainPrice.defPrice),
                 True,
                 False,
                 None,
                 True)
                return createAndLoadBackportTooltipWindow(self.parent.getParentWindow(), isSpecial=True, tooltipId=TOOLTIPS_CONSTANTS.ACTION_PRICE, specialArgs=specialArgs)
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.crew.tooltips.PerkAvailableTooltip():
            return PerkAvailableTooltip(self.context.tankmanID)
        if contentID == R.views.lobby.crew.tooltips.PremiumVehicleTooltip():
            return PremiumVehicleTooltip(vehicleCD=self.context.tankman.vehicleNativeDescr.type.compactDescr)
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)

    def _onRetrain(self):
        self._uiLogger.logClick(CrewPersonalFileKeys.RETRAIN_BUTTON)
        self.events.onRetrainClick(self.parent.viewKey)

    def _onChangeVehicle(self):
        self._uiLogger.logClick(CrewPersonalFileKeys.CHANGE_SPECIALIZATION_BUTTON)
        self.events.onChangeVehicleClick(tankmanInvID=self.context.tankman.invID)

    def _onPlayUniqueVoice(self):
        if self.context.voiceoverParams is None:
            return
        else:
            self.__sound = playRecruitVoiceover(self.context.voiceoverParams)
            self._uiLogger.logClick(CrewPersonalFileKeys.VOICEOVER_BUTTON)
            return
