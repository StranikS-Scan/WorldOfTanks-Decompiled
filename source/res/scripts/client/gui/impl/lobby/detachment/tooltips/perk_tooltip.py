# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/perk_tooltip.py
from enum import IntEnum
import logging
from typing import TYPE_CHECKING, Dict, Optional
from items import perks
from items.components.perks_constants import PerksValueType
from crew2 import settings_globals
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.backport import getNiceNumberFormat
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.perk_veh_param_model import PerkVehParamModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.perk_bonus_model import PerkBonusModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.perk_tooltip_model import PerkTooltipModel
from gui.impl.pub import ViewImpl
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from gui.shared.gui_items.perk import PerkGUI
from gui.shared.items_parameters import MAX_RELATIVE_VALUE
from gui.shared.items_parameters.params import VehicleParams
from gui.shared.items_parameters.comparator import BACKWARD_QUALITY_PARAMS
from helpers import dependency
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.loggers import DynamicGroupTooltipLogger
from constants import AbilitySystemScopeNames
if TYPE_CHECKING:
    from gui.detachment.detachment_cache import DetachmentCache
    from gui.shared.gui_items.detachment import Detachment
    from gui.shared.items_cache import ItemsCache
_logger = logging.getLogger(__name__)
RELATIVE_BAR_PARAMS_FOR_TOOLTIP = {102: 'relativeVisibility',
 301: 'relativeCamouflage'}

class VehicleKey(IntEnum):
    CURRENT = 0
    NO_PERK = 1
    MAX_PERK = 2


class PerkTooltip(ViewImpl):
    _detachmentCache = dependency.descriptor(IDetachmentCache)
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('_perkID', '_detachmentInvID', '_instructorInvID', '_tooltipType', '_vehParams', '_showCurrentParam', '_showMaxParam', '_totalPerkLvl', '_detachment', '_matrixPerk', '_vehIntCD', '_tempPoints')
    uiLogger = DynamicGroupTooltipLogger()

    def __init__(self, perkID, detachmentInvID=None, instructorInvID=None, tooltipType=PerkTooltipModel.DETACHMENT_PERK_TOOLTIP, vehIntCD=None, tempPoints=None):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.PerkTooltip())
        settings.model = PerkTooltipModel()
        super(PerkTooltip, self).__init__(settings)
        self._perkID = int(perkID)
        self._detachmentInvID = detachmentInvID
        self._instructorInvID = instructorInvID
        self._tooltipType = tooltipType
        self._vehIntCD = vehIntCD
        self._vehParams = {}
        self._showCurrentParam = False
        self._showMaxParam = False
        self._totalPerkLvl = 0
        self._detachment = None
        self._tempPoints = tempPoints
        return

    @property
    def viewModel(self):
        return super(PerkTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PerkTooltip, self)._onLoading()
        self._fillModel()

    def _initialize(self, *args, **kwargs):
        super(PerkTooltip, self)._initialize()
        self.uiLogger.tooltipOpened()

    def _finalize(self):
        self.uiLogger.tooltipClosed(self.__class__.__name__)
        self.uiLogger.reset()
        g_detachmentTankSetupVehicle.restoreCompareVehicle()
        super(PerkTooltip, self)._finalize()

    def _fillModel(self):
        self._fillMainInfo()

    def _fillMainInfo(self):
        perkID = self._perkID
        self._detachment = detachment = self._detachmentCache.getDetachment(self._detachmentInvID)
        instructor = self._detachmentCache.getInstructor(self._instructorInvID)
        detPerkLvl = 0
        _defaultMatrixID = 1
        matrix = settings_globals.g_perkSettings.matrices.getMatrix(_defaultMatrixID)
        perkInstructorInfluence = []
        perkBoosterInfluence = []
        vehicle = None
        isOvercapped = False
        if detachment is not None:
            detPerkLvl = detachment.build.get(perkID, 0)
            matrix = detachment.getDescriptor().getPerksMatrix()
            if self._vehIntCD:
                vehicle = self._itemsCache.items.getItemByCD(self._vehIntCD)
            else:
                vehicle = self._itemsCache.items.getVehicle(detachment.vehInvID) if detachment.isInTank else None
        bonusPerks = {perkID: self._tempPoints - detPerkLvl if self._tempPoints is not None else 0}
        totalInstrPoints = boosterPoints = 0
        if detachment is not None:
            perkInstructorInfluence = detachment.getPerkInstructorInfluence(perkID, bonusPerks=bonusPerks, vehicle=vehicle)
            perkBoosterInfluence = detachment.getPerkBoosterInfluence(perkID, bonusPerks=bonusPerks, vehicle=vehicle)
            totalInstrPoints = sum((p for _, p, _ in perkInstructorInfluence))
            boosterPoints = sum((p for _, p, _ in perkBoosterInfluence))
            isOvercapped = any((overcap for _, _, overcap in perkBoosterInfluence + perkInstructorInfluence))
        elif instructor is not None:
            for _perkID, pointsCount, overcap in instructor.getPerksInfluence():
                if perkID == _perkID:
                    totalInstrPoints = pointsCount
                    isOvercapped = overcap != 0
                    break

        self._matrixPerk = matrixPerk = matrix.perks[perkID]
        branchID = matrixPerk.branch
        branch = matrix.branches[branchID]
        baseLevel = self._tempPoints if self._tempPoints is not None else detPerkLvl
        self._totalPerkLvl = baseLevel + totalInstrPoints + boosterPoints
        self._showCurrentParam = not matrixPerk.ultimate and self._totalPerkLvl > 0
        self._showMaxParam = matrixPerk.ultimate or self._totalPerkLvl < matrixPerk.max_points
        with self.viewModel.transaction() as model:
            perk = PerkGUI(perkID, self._totalPerkLvl)
            model.setId(perkID)
            model.setIconName(perk.icon)
            model.setName(perk.name)
            model.setIsOvercapped(isOvercapped)
            if self._tempPoints > 0 and self._tempPoints != detPerkLvl:
                model.setTempPoints(self._tempPoints)
            else:
                model.setPoints(baseLevel)
            model.setMaxPoints(matrixPerk.max_points)
            model.setInstructorPoints(totalInstrPoints)
            model.setInstructorsAmount(len(perkInstructorInfluence))
            model.setBoosterPoints(boosterPoints)
            model.setBranchName(R.strings.item_types.abilities.dyn(branch.name)())
            model.setBranchIconName(branch.icon)
            model.setIsUltimate(matrixPerk.ultimate)
            model.setIsPermanent(not perk.situational)
            model.setDescription(perk.getFormattedDescriptionBasedOnLvl())
            model.setType(self._tooltipType)
            instructorsBonuses = model.getInstructorsBonuses()
            for invID, points, overcap in perkInstructorInfluence:
                instructorItem = self._detachmentCache.getInstructor(invID)
                bonus = PerkBonusModel()
                bonus.setBonus(points)
                bonus.setName(instructorItem.getFullName())
                bonus.setIsOvercapped(overcap > 0)
                instructorsBonuses.addViewModel(bonus)

            instructorsBonuses.invalidate()
            if vehicle:
                boostersBonuses = model.getBoostersBonuses()
                for intCD, points, overcap in perkBoosterInfluence:
                    battleBooster = self._itemsCache.items.getItemByCD(intCD)
                    bonus = PerkBonusModel()
                    bonus.setBonus(points)
                    bonus.setName(battleBooster.userName)
                    bonus.setIsOvercapped(overcap > 0)
                    boostersBonuses.addViewModel(bonus)

                boostersBonuses.invalidate()
            if self._tooltipType != PerkTooltipModel.TTC_PERK_TOOLTIP:
                self._fillPerLevelBonuses()
        return

    def _fillRelativeBarParams(self):
        if self._detachment is not None and self._detachment.isInTank and (self._showCurrentParam or self._showMaxParam) and self._perkID in RELATIVE_BAR_PARAMS_FOR_TOOLTIP:
            self._calcCurrentParams()
        return

    def _calcCurrentParams(self):
        _logger.debug('Current vehicle stats')
        deltaLvl = self._totalPerkLvl - self._detachment.build.get(self._perkID, 0)
        g_detachmentTankSetupVehicle.setVehicleBonusPerks({self._perkID: deltaLvl}, callback=self._calcDefaultParams)

    def _fillPerLevelBonuses(self):
        perk = perks.g_cache.perks().perks[self._perkID]
        with self.viewModel.transaction() as model:
            vehParams = model.getVehParams()
            for paramName, argument in perk.defaultBlockSettings.iteritems():
                paramBonus = PerkVehParamModel()
                uiSettings = perk.defaultBlockSettings[paramName].UISettings
                value, formattedValue = _formatBonusValues(self._perkID, argument.value, uiSettings)
                paramBonus.setBonus(formattedValue)
                situationalArg = uiSettings.situationalArg
                paramBonus.setIsPermanent(not situationalArg)
                isPenalty = (value >= 0) == (paramName in BACKWARD_QUALITY_PARAMS)
                if not situationalArg:
                    paramBonus.setIsPenalty(isPenalty)
                if uiSettings.icon is not None:
                    paramBonus.setIcon(R.images.gui.maps.icons.vehParams.small.dyn(uiSettings.icon)())
                else:
                    paramBonus.setIcon(R.images.gui.maps.icons.vehParams.small.dyn(paramName)())
                if uiSettings.perkTooltipBonus:
                    paramBonus.setDescription(backport.text(R.strings.tank_setup.tooltip.perk.bonus.dyn(paramName)()))
                else:
                    defaultTitleAccessor = R.strings.tank_setup.kpi.bonus.dyn(paramName)
                    resource = R.strings.tank_setup.kpi.bonus.ttc
                    if isPenalty:
                        resource = R.strings.tank_setup.kpi.bonus.ttc.reverted
                    paramBonus.setDescription(backport.text(resource.dyn(paramName, defaultTitleAccessor)()))
                vehParams.addViewModel(paramBonus)

            vehParams.invalidate()
        return

    def _calcDefaultParams(self):
        vehicleCurrentParams = VehicleParams(g_detachmentTankSetupVehicle.vehicleToCompare)
        self._saveParams(VehicleKey.CURRENT, vehicleCurrentParams)
        perksController = g_detachmentTankSetupVehicle.vehicleToCompare.getPerksController()
        perksController.deactivatePerk(AbilitySystemScopeNames.DETACHMENT, self._perkID)
        vehicleParamsNoPerk = VehicleParams(g_detachmentTankSetupVehicle.vehicleToCompare)
        _logger.debug('Current vehicle stats without perk %s', self._perkID)
        self._saveParams(VehicleKey.NO_PERK, vehicleParamsNoPerk)
        perksController.restore(reloadPlans=False)
        _logger.debug('Vehicle stats with %s points in perk %s', self._matrixPerk.max_points, self._perkID)
        detPerkLvl = self._detachment.build.get(self._perkID, 0) if self._detachment else 0
        bonusPerkCount = self._matrixPerk.max_points - detPerkLvl
        g_detachmentTankSetupVehicle.setVehicleBonusPerks({self._perkID: bonusPerkCount}, callback=self._updateParams)

    def _updateParams(self):
        _logger.debug('_updateParams')
        vehParamsMaxPerk = VehicleParams(g_detachmentTankSetupVehicle.vehicleToCompare)
        self._saveParams(VehicleKey.MAX_PERK, vehParamsMaxPerk)
        g_detachmentTankSetupVehicle.restoreCompareVehicle()
        affectedParam = self._findAffectedParam(VehicleKey.NO_PERK, VehicleKey.MAX_PERK)
        if affectedParam is None:
            return
        else:
            with self.viewModel.transaction() as model:
                noPerkValue = self._vehParams[VehicleKey.NO_PERK][affectedParam]
                paramNameResID = R.strings.menu.tank_params.dyn(affectedParam)()
                if self._showCurrentParam:
                    currentValue = self._vehParams[VehicleKey.CURRENT][affectedParam]
                    self.__fillProgress(name=paramNameResID, model=model.progress, level=self._totalPerkLvl, points=noPerkValue, markPoints=noPerkValue, maxPoints=MAX_RELATIVE_VALUE, bonus=currentValue - noPerkValue)
                if self._showMaxParam:
                    maxPerkValue = self._vehParams[VehicleKey.MAX_PERK][affectedParam]
                    self.__fillProgress(name=paramNameResID, model=model.progressMax, level=self._matrixPerk.max_points, points=noPerkValue, markPoints=noPerkValue, maxPoints=MAX_RELATIVE_VALUE, bonus=maxPerkValue - noPerkValue)
            return

    def _findAffectedParam(self, vehKey0, vehKey1):
        vehParams0 = self._vehParams[vehKey0]
        vehParams1 = self._vehParams[vehKey1]
        paramName = RELATIVE_BAR_PARAMS_FOR_TOOLTIP.get(self._perkID)
        if not paramName:
            return None
        elif paramName in vehParams0 and paramName in vehParams1 and vehParams0[paramName] != vehParams1[paramName]:
            _logger.debug('Affected param = %s for perkID = %d', paramName, self._perkID)
            return paramName
        else:
            return None

    def _saveParams(self, vehKey, vehParams):
        paramName = RELATIVE_BAR_PARAMS_FOR_TOOLTIP.get(self._perkID)
        if paramName:
            paramValue = getattr(vehParams, paramName)
            self._vehParams.setdefault(vehKey, {})[paramName] = paramValue
            _logger.debug('\t%s = %s', paramName, paramValue)

    @classmethod
    def __fillProgress(cls, model, name, level, points, markPoints, maxPoints, bonus):
        model.setVehParamName(name)
        model.setLevel(level)
        model.setPoints(points)
        model.setMarkPoints(markPoints)
        model.setMaxPoints(maxPoints)
        model.setBonusPoints(bonus)


def _formatBonusValues(perkID, value, uiSettings):
    perk = PerkGUI(perkID, 1)
    if uiSettings.equipmentCooldown is not None:
        value = perk.getSpecialFormattedValue(uiSettings, value)
    if uiSettings.type == PerksValueType.SECONDS:
        ending = backport.text(R.strings.menu.tank_params.no_brackets.s())
    else:
        value *= 100
        ending = '%'
    if uiSettings.revert:
        value *= -1
    return (value, ('+' if value > 0 else '') + getNiceNumberFormat(value) + ending)
