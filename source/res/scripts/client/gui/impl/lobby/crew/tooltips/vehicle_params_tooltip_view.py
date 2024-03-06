# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/vehicle_params_tooltip_view.py
import collections
from functools import partial
from typing import TYPE_CHECKING
import constants
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.vehicle_params_category import VehicleParamsCategory
from gui.impl.gen.view_models.views.lobby.crew.tooltips.vehicle_params_item import VehicleParamsItem, ValueStyleEnum
from gui.impl.gen.view_models.views.lobby.crew.tooltips.vehicle_params_note import VehicleParamsNote, NoteThemeEnum
from gui.impl.gen.view_models.views.lobby.crew.tooltips.vehicle_params_tooltip_view_model import VehicleParamsTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import KPI
from gui.shared.items_parameters import formatters as param_formatter
from gui.shared.items_parameters.bonus_helper import isSituationalBonus, CREW_MASTERY_BONUSES
from gui.shared.items_parameters.comparator import PARAM_STATE
from gui.shared.items_parameters.formatters import isRelativeParameter
from gui.shared.items_parameters.param_name_helper import getVehicleParameterText
from gui.shared.items_parameters.params import PIERCING_DISTANCES
from gui.shared.utils import CHASSIS_REPAIR_TIME, SHOT_DISPERSION_ANGLE, DUAL_ACCURACY_COOLING_DELAY, isRomanNumberForbidden
from helpers import i18n
from items import perks, vehicles, tankmen, parseIntCompactDescr
from post_progression_common import ACTION_TYPES
from shared_utils import first
if TYPE_CHECKING:
    from typing import Optional
    from gui.shared.gui_items import Vehicle
    from gui.shared.tooltips.contexts import HangarParamContext
_BONUS_TYPES_ORDER = {constants.BonusTypes.EXTRA: 6,
 constants.BonusTypes.SKILL: 5,
 constants.BonusTypes.ROLE: 5,
 constants.BonusTypes.PERK: 5,
 constants.BonusTypes.OPTIONAL_DEVICE: 4,
 constants.BonusTypes.EQUIPMENT: 3,
 constants.BonusTypes.BATTLE_BOOSTER: 2,
 constants.BonusTypes.PAIR_MODIFICATION: 1,
 constants.BonusTypes.BASE_MODIFICATION: 0}
_CREW_TYPES = (constants.BonusTypes.PERK, constants.BonusTypes.SKILL)
_MULTI_KPI_PARAMS = frozenset(['vehicleRepairSpeed',
 'vehicleRamOrExplosionDamageResistance',
 'vehicleGunShotDispersion',
 'crewHitChance',
 'crewRepeatedStunDuration',
 'vehicleChassisStrength',
 'vehicleChassisFallDamage',
 'vehicleChassisRepairSpeed',
 'vehicleAmmoBayEngineFuelStrength',
 'vehicleFireChance',
 'demaskFoliageFactor',
 'demaskMovingFactor',
 'crewStunDuration',
 'damageEnemiesByRamming',
 'vehPenaltyForDamageEngineAndCombat',
 'vehicleGunShotDispersionAfterShot',
 'vehicleGunShotDispersionChassisMovement',
 'vehicleGunShotDispersionChassisRotation',
 'vehicleGunShotDispersionTurretRotation',
 'vehicleGunShotDispersionWhileGunDamaged',
 'vehicleRamDamageResistance',
 'vehicleSpeedGain',
 'aimingTime',
 'autoReloadTime',
 'avgDamagePerMinute',
 'avgPiercingPower',
 'chargeTime',
 'chassisRepairTime',
 'chassisRotationSpeed',
 'circularVisionRadius',
 'clipFireRate',
 'enginePower',
 'enginePowerPerTon',
 'invisibilityMovingFactor',
 'invisibilityStillFactor',
 'maxHealth',
 'radioDistance',
 'reloadTime',
 'reloadTimeSecs',
 'shotDispersionAngle',
 'turboshaftEnginePower',
 'turboshaftInvisibilityMovingFactor',
 'turboshaftInvisibilityStillFactor',
 'turretRotationSpeed',
 'rocketAccelerationEnginePower',
 'vehicleEnemySpottingTime',
 DUAL_ACCURACY_COOLING_DELAY])
AUTORELOAD_TIME = 'autoReloadTime'
_PARAMS_WITH_AGGREGATED_PENALTIES = {DUAL_ACCURACY_COOLING_DELAY}
_CREW_ICON = 'all'

def _optDeviceCmp(x, y):

    def _getTypePriority(itemName):
        item = vehicles.g_cache.getOptionalDeviceByName(itemName)
        if item.isDeluxe:
            return 1
        if item.isTrophy:
            return 2
        return 3 if item.isModernized else 0

    return cmp(_getTypePriority(x), _getTypePriority(y))


_TYPE_ITEMS_COMPARATORS = {constants.BonusTypes.OPTIONAL_DEVICE: _optDeviceCmp}

def _bonusCmp(x, y):
    return cmp(_BONUS_TYPES_ORDER.get(y[1], 0), _BONUS_TYPES_ORDER.get(x[1], 0)) or cmp(x[1], y[1]) or _TYPE_ITEMS_COMPARATORS.get(x[1], lambda _, __: 0)(x[0], y[0]) or cmp(x[0], y[0])


def _getBonusID(bnsType, bnsId):
    if bnsType == constants.BonusTypes.OPTIONAL_DEVICE:
        return bnsId.split('_tier')[0]
    elif bnsType in (constants.BonusTypes.PAIR_MODIFICATION, constants.BonusTypes.BASE_MODIFICATION):
        mod = vehicles.g_cache.postProgression().getModificationByName(bnsId)
        if mod is not None:
            return mod.locName
        return bnsId
    else:
        return bnsId


def _getBonusName(bnsType, bnsId, enabled=True, archetype=None):
    itemStr = ''
    useArchetypeLocale = archetype is not None and enabled is False
    if bnsType in (constants.BonusTypes.EQUIPMENT, constants.BonusTypes.OPTIONAL_DEVICE):
        if useArchetypeLocale:
            bnsR = R.strings.artefacts.archetype.dyn(archetype)
            noTplStrR = bnsR and bnsR.name.dyn('noTemplate')
            if noTplStrR:
                itemStr = backport.text(noTplStrR())
            else:
                itemStr = backport.text(R.strings.artefacts.archetype.template(), name=backport.text(bnsR.name()) if bnsR else '')
        else:
            bnsR = R.strings.artefacts.dyn(bnsId)
            if bnsR:
                itemStr = backport.text(bnsR.name())
    elif bnsType == constants.BonusTypes.SKILL:
        itemStr = backport.text(R.strings.tooltips.vehicleParams.bonus.skill.template(), name=backport.text(R.strings.crew_perks.dyn(bnsId).name()), type=backport.text(R.strings.tooltips.vehicleParams.skill.name()))
    elif bnsType == constants.BonusTypes.PERK:
        perkItem = perks.g_cache.perks[int(bnsId)]
        itemStr = backport.text(R.strings.tooltips.vehicleParams.bonus.perk.template(), name=perkItem.name, type=backport.text(R.strings.tooltips.vehicleParams.skill.name()))
    elif bnsType == constants.BonusTypes.ROLE:
        bnsR = R.strings.tooltips.vehicleParams.bonus.tankmanLevel.dyn(bnsId)
        if bnsR.exists():
            itemStr = backport.text(R.strings.tooltips.vehicleParams.bonus.role.template(), name=backport.text(bnsR()))
    elif bnsType == constants.BonusTypes.EXTRA:
        bnsR = R.strings.tooltips.vehicleParams.bonus.extra.dyn(bnsId)
        if bnsR.exists():
            itemStr = backport.text(R.strings.tooltips.vehicleParams.bonus.role.template(), name=backport.text(bnsR()))
    elif bnsType == constants.BonusTypes.BATTLE_BOOSTER:
        bnsR = R.strings.artefacts.dyn(bnsId)
        if bnsR:
            itemStr = backport.text(R.strings.tooltips.vehicleParams.bonus.battleBooster.template(), name=backport.text(bnsR.name()))
    elif bnsType == constants.BonusTypes.PAIR_MODIFICATION:
        bnsR = R.strings.artefacts.dyn(bnsId)
        if bnsR:
            itemStr = backport.text(R.strings.tooltips.vehicleParams.bonus.vehPostProgressionPairModification.template(), name=backport.text(bnsR.name()))
    elif bnsType == constants.BonusTypes.BASE_MODIFICATION:
        bnsR = R.strings.artefacts.dyn(bnsId)
        if bnsR:
            itemStr = backport.text(R.strings.tooltips.vehicleParams.bonus.vehPostProgressionBaseModification.template(), name=backport.text(bnsR.name()))
    return itemStr


def _getNumNotNullPenaltyTankman(penalties):
    nullPenaltyTypes = []
    actualPenalties = []
    for penalty in penalties:
        if penalty.value != 0:
            actualPenalties.append(penalty)
        nullPenaltyTypes.append(penalty.roleName)

    return (actualPenalties, nullPenaltyTypes)


def _formatValueChange(paramName, value, colorScheme):
    if not param_formatter.isRelativeParameter(paramName):
        if isinstance(value, collections.Sized):
            state = zip([PARAM_STATE.WORSE] * len(value), value)
        else:
            state = (PARAM_STATE.WORSE, value)
        valueStr = param_formatter.formatParameter(paramName, value, state, colorScheme=colorScheme, formatSettings=param_formatter.DELTA_PARAMS_SETTING, allowSmartRound=False)
        return valueStr or ''
    else:
        return ''


def _isUpgradedInstanceOfInstalled(installedDevices, deviceDescr):
    if not deviceDescr.isUpgradable:
        return False
    _, __, upgradedID = parseIntCompactDescr(deviceDescr.upgradeInfo.upgradedCompDescr)
    upgradedDescr = vehicles.g_cache.optionalDevices().get(upgradedID)
    return True if upgradedDescr.name in installedDevices else _isUpgradedInstanceOfInstalled(installedDevices, upgradedDescr)


def _isDowngradedInstanceOfInstalled(installedDevices, deviceDescr):
    if not (deviceDescr.isUpgradable or deviceDescr.isUpgraded) or deviceDescr.downgradeInfo is None:
        return False
    else:
        _, __, downgradedID = parseIntCompactDescr(deviceDescr.downgradeInfo.downgradedCompDescr)
        downgradedDescr = vehicles.g_cache.optionalDevices().get(downgradedID)
        return True if downgradedDescr.name in installedDevices else _isDowngradedInstanceOfInstalled(installedDevices, downgradedDescr)


class BaseVehicleParamsTooltipView(ViewImpl):
    __slots__ = ('_paramName', '_context', '_supportAdvanced', '_extendedData', '_hasPerksBonuses')

    def __init__(self, paramName, context, supportAdvanced):
        settings = ViewSettings(R.views.lobby.crew.tooltips.VehicleParamsTooltipView(), model=VehicleParamsTooltipViewModel())
        super(BaseVehicleParamsTooltipView, self).__init__(settings)
        self._paramName = paramName
        self._context = context
        self._supportAdvanced = supportAdvanced
        self._paramName = paramName

    @property
    def vehicle(self):
        return self._context.buildItem()

    @property
    def viewModel(self):
        return super(BaseVehicleParamsTooltipView, self).getViewModel()

    @staticmethod
    def _formatValueText(style, text):
        return '%({0}_open)s{1}%({0}_close)s'.format(style.value, text.replace('&lt;', '<'))

    def _onLoading(self, *args, **kwargs):
        super(BaseVehicleParamsTooltipView, self)._onLoading(*args, **kwargs)
        comparator = self._context.getComparator()
        self._extendedData = comparator.getExtendedData(self._paramName)
        self._hasPerksBonuses = comparator.hasBonusOfType(constants.BonusTypes.PERK)
        with self.viewModel.transaction() as tx:
            self._fillModel(tx)

    def _fillModel(self, model):
        pass


class BaseVehicleAdvancedParamsTooltipView(BaseVehicleParamsTooltipView):

    def _fillModel(self, model):
        vehicle = self.vehicle
        isExtraParam = KPI.Name.hasValue(self._paramName)
        model.setIsAdvanced(self._supportAdvanced)
        if isExtraParam:
            title = backport.text(R.strings.menu.extraParams.header(), paramName=backport.text(getVehicleParameterText(self._paramName, isPositive=True)))
            desc = backport.text(R.strings.menu.extraParams.name.dyn(self._paramName, R.strings.menu.extraParams.desc)())
        else:
            titleParamName = param_formatter.getTitleParamName(vehicle, self._paramName)
            measureParamName = param_formatter.getMeasureParamName(vehicle, self._paramName)
            title = self.__getTitleStr(titleParamName)
            measureUnitLoc = param_formatter.MEASURE_UNITS.get(measureParamName, '')
            model.setUnitOfMeasurement(i18n.makeString(measureUnitLoc) if i18n.isValidKey(measureUnitLoc) else '')
            if self._paramName == AUTORELOAD_TIME and self._hasExtendedInfo():
                desc = self._getAutoReloadTimeDescription()
            elif self._paramName == CHASSIS_REPAIR_TIME and vehicle and vehicle.isTrackWithinTrack:
                desc = backport.text(R.strings.tooltips.tank_params.desc.chassisRepairTimeYoh())
            elif self._paramName == SHOT_DISPERSION_ANGLE and vehicle and vehicle.descriptor.hasDualAccuracy:
                desc = backport.text(R.strings.tooltips.tank_params.desc.shotDispersionAngle.withDualAccuracy())
            else:
                desc = backport.text(R.strings.tooltips.tank_params.desc.dyn(self._paramName)())
        if isRelativeParameter(self._paramName) and self._context.isApproximately:
            approxImgRes = R.images.gui.maps.icons.vehPostProgression.tooltips.dyn(self._extendedData.state[0])
            if approxImgRes.exists():
                notes = model.getHeaderNotes()
                note = VehicleParamsNote()
                note.setIcon(approxImgRes())
                note.setTitle(backport.text(R.strings.veh_post_progression.tooltips.ttc.approximately()))
                note.setTheme(NoteThemeEnum.CONTENT)
                notes.addViewModel(note)
        model.setTitle(title)
        model.setDescription(str(desc))
        paramIcon = R.images.gui.maps.icons.vehParams.big.dyn(self._paramName)
        if paramIcon.isValid():
            model.setIcon(paramIcon())
        if self._paramName == AUTORELOAD_TIME and self._hasExtendedInfo():
            notes = model.getFooterNotes()
            note = VehicleParamsNote()
            note.setIcon(R.images.gui.maps.icons.modules.autoLoaderGunBoost())
            note.setTitle(self._getAutoReloadTimeExtendedDescription())
            note.setTheme(NoteThemeEnum.AUTORELOADTIME)
            notes.addViewModel(note)

    def _hasExtendedInfo(self):
        return True

    def _getAutoReloadTimeDescription(self):
        return backport.text(R.strings.tooltips.tank_params.desc.autoReloadTime())

    def _getAutoReloadTimeExtendedDescription(self):
        return backport.text(R.strings.tooltips.tank_params.desc.autoReloadTime.boost.shortDescription())

    def __getTitleStr(self, titleParamName):
        strRootPath = R.strings.menu.tank_params.dyn(titleParamName)
        strPath = strRootPath.extendedTitle if strRootPath.dyn('extendedTitle').exists() else strRootPath
        return backport.text(strPath())


class VehicleAdvancedParamsTooltipView(BaseVehicleAdvancedParamsTooltipView):

    def _fillModel(self, model):
        super(VehicleAdvancedParamsTooltipView, self)._fillModel(model)
        hasSituational = self._fillBonuses(model)
        if self.vehicle:
            self._fillPenalties(model)
            self._fillFootNotes(model, hasSituational)

    def _fillBonuses(self, model):
        result = collections.defaultdict(list)
        vehicle = self.vehicle
        situationalScheme = (partial(self._formatValueText, ValueStyleEnum.RED), partial(self._formatValueText, ValueStyleEnum.WHITEORANGE), partial(self._formatValueText, ValueStyleEnum.YELLOW))
        extractedBonusScheme = (partial(self._formatValueText, ValueStyleEnum.RED), partial(self._formatValueText, ValueStyleEnum.GREENBRIGHT), partial(self._formatValueText, ValueStyleEnum.GREENBRIGHT))
        vehPostProgressionBonusLevels = {step.action.getTechName():step.getLevel() for step in vehicle.postProgression.iterUnorderedSteps() if step.action.actionType == ACTION_TYPES.MODIFICATION}
        bonuses = sorted(self._extendedData.bonuses, cmp=_bonusCmp)
        bonusExtractor = self._context.getBonusExtractor(vehicle, bonuses, self._paramName)
        hasSituational = False
        appliedOptDeviceBonuses = []
        installedArchetypes = set()
        for bnsType, bnsId, pInfo in bonusExtractor.getBonusInfo():
            diff = pInfo.getParamDiff()
            tooltipSection, archetype = self._getTooltipGroupingForBonus(bnsType, bnsId)
            if archetype is not None:
                installedArchetypes.add(archetype)
            formattedBnsID = _getBonusID(bnsType, bnsId)
            isSituational = isSituationalBonus(formattedBnsID, bnsType, pInfo.name)
            scheme = situationalScheme if isSituational else extractedBonusScheme
            valueStr = param_formatter.formatParameterDelta(pInfo, scheme)
            if isSituational and bnsId in CREW_MASTERY_BONUSES:
                if diff == 0.0 or isinstance(diff, (list, tuple)) and not filter(None, diff):
                    valueStr = ''
            if valueStr is not None:
                hasSituational = hasSituational or isSituational
                bonusName = _getBonusName(bnsType, formattedBnsID)
                itemModel = VehicleParamsItem()
                itemModel.setIsEnabled(True)
                itemModel.setValue(valueStr)
                itemModel.setTitle(bonusName)
                if isSituational:
                    itemModel.setAsteriskIcon(R.images.gui.maps.icons.tooltip.asterisk_optional())
                levelIcon = self.__getLevelIcon(bnsId, bnsType, vehPostProgressionBonusLevels)
                itemModel.setIcon(param_formatter.getBonusIconRes(formattedBnsID, bnsType) if levelIcon is None else levelIcon)
                appliedOptDeviceBonuses.append(bnsId)
                result[tooltipSection].append(itemModel)

        for bnsId, bnsType in sorted(self._extendedData.possibleBonuses, cmp=_bonusCmp):
            if bnsType == constants.BonusTypes.PERK and not self._hasPerksBonuses:
                continue
            if bnsType == constants.BonusTypes.EQUIPMENT:
                if not vehicle.consumables.layoutCapacity:
                    continue
            if bnsType == constants.BonusTypes.BATTLE_BOOSTER:
                if not vehicle.battleBoosters.layoutCapacity:
                    continue
            if bnsType == constants.BonusTypes.OPTIONAL_DEVICE:
                if not vehicle.optDevices.layoutCapacity:
                    continue
                device = vehicles.g_cache.getOptionalDeviceByName(bnsId)
                if device.isModernized or device.isTrophy:
                    if device.downgradeInfo is not None or device.isUpgraded:
                        continue
                    elif _isUpgradedInstanceOfInstalled(appliedOptDeviceBonuses, device) or _isDowngradedInstanceOfInstalled(appliedOptDeviceBonuses, device):
                        continue
            tooltipSection, archetype = self._getTooltipGroupingForBonus(bnsType, bnsId)
            if archetype is not None and archetype in installedArchetypes:
                continue
            isInactive = False
            if (bnsId, bnsType) in self._extendedData.inactiveBonuses.keys():
                isInactive = True
            formattedBnsID = _getBonusID(bnsType, bnsId)
            isEnabled = (formattedBnsID, bnsType) in bonuses if bnsType in _CREW_TYPES else False
            itemModel = VehicleParamsItem()
            if isInactive and bnsType != constants.BonusTypes.BATTLE_BOOSTER:
                itemModel.setAsteriskIcon(R.images.gui.maps.icons.tooltip.asterisk_red())
            itemModel.setIsEnabled(False)
            bnsArchetype = None if isInactive else archetype
            itemModel.setTitle(_getBonusName(bnsType, formattedBnsID, enabled=isEnabled, archetype=bnsArchetype))
            levelIcon = self.__getLevelIcon(bnsId, bnsType, vehPostProgressionBonusLevels)
            itemModel.setIcon(levelIcon if levelIcon else param_formatter.getBonusIconRes(formattedBnsID, bnsType, bnsArchetype))
            result[tooltipSection].append(itemModel)
            if archetype is not None:
                installedArchetypes.add(archetype)

        categories = model.getCategories()
        for section in constants.TTC_TOOLTIP_SECTIONS.ALL:
            bonuses = result[section]
            if bonuses:
                sectionTitle = R.strings.tooltips.vehicleParams.bonuses.title.dyn(section)()
                category = VehicleParamsCategory()
                category.setTitle(backport.text(sectionTitle))
                categoryBonuses = category.getItems()
                for bonus in bonuses:
                    categoryBonuses.addViewModel(bonus)

                categories.addViewModel(category)

        return hasSituational

    def _fillPenalties(self, model):
        baseColorScheme = (partial(self._formatValueText, ValueStyleEnum.RED), partial(self._formatValueText, ValueStyleEnum.WHITESPANISH), partial(self._formatValueText, ValueStyleEnum.GREENBRIGHT))
        modelPenalties = model.getPenalties()
        penalties = self._extendedData.penalties
        actualPenalties, _ = _getNumNotNullPenaltyTankman(penalties)
        penaltiesLen = len(penalties)
        numNotNullPenaltyTankman = len(actualPenalties)
        if penaltiesLen > numNotNullPenaltyTankman:
            model.setIsNotFullCrew(True)
            penaltyModel = VehicleParamsItem()
            penaltyModel.setTitle(backport.text(R.strings.tooltips.vehicleParams.penalty.crewNotFull.template()))
            penaltyModel.setIcon(R.images.gui.maps.icons.vehParams.tooltips.penalties.all())
            modelPenalties.addViewModel(penaltyModel)
        if numNotNullPenaltyTankman > 0:
            if self._paramName in _PARAMS_WITH_AGGREGATED_PENALTIES:
                self.__fillAggregatedNotNullPenalties(penalties, modelPenalties, baseColorScheme)
            else:
                self.__fillNotNullPenaltyTankmen(penalties, modelPenalties, baseColorScheme)

    def _fillFootNotes(self, model, hasSituational):
        notes = model.getFooterNotes()
        result = []
        if len(self._extendedData.bonuses) > 1 and self._paramName in _MULTI_KPI_PARAMS:
            result.append((backport.text(R.strings.menu.extraParams.multiDesc()), None, NoteThemeEnum.TEXTONLY))
        if hasSituational:
            result.append((backport.text(R.strings.tooltips.vehicleParams.bonus.situational()), R.images.gui.maps.icons.tooltip.asterisk_optional(), NoteThemeEnum.WARNING))
        if self._extendedData.inactiveBonuses:
            conditionsToActivate = set(self._extendedData.inactiveBonuses.values())
            conditionsToActivate = [ backport.text(R.strings.crew_perks.dyn(bnsID).name()) for bnsID, _ in conditionsToActivate if R.strings.crew_perks.dyn(bnsID).isValid() ]
            if conditionsToActivate:
                result.append((backport.text(R.strings.tooltips.vehicleParams.bonus.inactiveDescription(), skillName=', '.join(conditionsToActivate)), R.images.gui.maps.icons.tooltip.asterisk_red(), NoteThemeEnum.WARNING))
        for title, icon, theme in result:
            note = VehicleParamsNote()
            note.setTitle(title)
            note.setTheme(theme)
            if icon is not None:
                note.setIcon(icon)
            notes.addViewModel(note)

        return

    def _getTooltipGroupingForBonus(self, bonusType, bonusName):
        if bonusType == constants.BonusTypes.EXTRA:
            return (constants.TTC_TOOLTIP_SECTIONS.EQUIPMENT, None)
        else:
            if bonusType == constants.BonusTypes.OPTIONAL_DEVICE:
                artifact = vehicles.g_cache.getOptionalDeviceByName(bonusName)
            elif bonusType == constants.BonusTypes.SKILL:
                artifact = tankmen.getSkillsConfig().getSkill(bonusName)
            elif bonusType in (constants.BonusTypes.BASE_MODIFICATION, constants.BonusTypes.PAIR_MODIFICATION):
                artifact = vehicles.g_cache.postProgression().getModificationByName(bonusName)
            else:
                artifact = vehicles.g_cache.getEquipmentByName(bonusName)
            return (artifact.tooltipSection, getattr(artifact, 'archetype', None))

    def _hasExtendedInfo(self):
        if g_currentPreviewVehicle.isPresent():
            item = g_currentPreviewVehicle.item
        else:
            item = g_currentVehicle.item if g_currentVehicle else None
        return item and item.descriptor.gun.autoreloadHasBoost or not item

    def _getAutoReloadTimeDescription(self):
        return backport.text(R.strings.tooltips.tank_params.desc.autoReloadTime.boost())

    def _getAutoReloadTimeExtendedDescription(self):
        return backport.text(R.strings.tooltips.tank_params.desc.autoReloadTime.boost.description())

    def __fillAggregatedNotNullPenalties(self, penalties, model, baseColorScheme):
        rootStr = R.strings.tooltips.vehicleParams.penalty
        notNativeTankmenPenalties, otherPenalties = [], []
        for penalty in penalties:
            if penalty.vehicleIsNotNative:
                notNativeTankmenPenalties.append(penalty)
            if penalty.value != 0:
                otherPenalties.append(penalty)

        self.__fillGroupPenalties(model, otherPenalties, rootStr.tankmanLevel, rootStr.crewLevel, baseColorScheme)
        self.__fillGroupPenalties(model, notNativeTankmenPenalties, rootStr.tankmanDifferentVehicle, rootStr.crewDifferentVehicle, baseColorScheme)

    def __fillGroupPenalties(self, modelPenalties, penalties, templateStr, crewStr, baseColorScheme):
        if not penalties:
            return
        if len(penalties) == 1:
            penaltyItem = first(penalties)
            roleName = penaltyItem.roleName
            title = backport.text(templateStr.template(), tankmanType=backport.text(R.strings.item_types.tankman.roles.dyn(roleName)()))
            valueStr = _formatValueChange(self._extendedData.name, penaltyItem.value, baseColorScheme)
            model = self.__createPenaltyModel(valueStr, title, roleName)
        else:
            value = sum((penalty.value for penalty in penalties))
            valueStr = _formatValueChange(self._extendedData.name, value, baseColorScheme)
            model = self.__createPenaltyModel(valueStr, backport.text(crewStr()), _CREW_ICON)
        modelPenalties.addViewModel(model)

    def __fillNotNullPenaltyTankmen(self, penalties, modelPenalties, baseColorScheme):
        for penalty in penalties:
            valueStr = _formatValueChange(self._extendedData.name, penalty.value, baseColorScheme)
            if valueStr:
                if penalty.vehicleIsNotNative:
                    template = R.strings.tooltips.vehicleParams.penalty.tankmanDifferentVehicle.template()
                else:
                    template = R.strings.tooltips.vehicleParams.penalty.tankmanLevel.template()
                penaltyStr = backport.text(template, tankmanType=backport.text(R.strings.item_types.tankman.roles.dyn(penalty.roleName)()))
                penaltyModel = self.__createPenaltyModel(valueStr, penaltyStr, penalty.roleName)
                modelPenalties.addViewModel(penaltyModel)

    @staticmethod
    def __createPenaltyModel(value, title, iconName):
        penaltyModel = VehicleParamsItem()
        penaltyModel.setValue(value)
        penaltyModel.setTitle(title)
        penaltyModel.setIcon(param_formatter.getPenaltyIconRes(iconName))
        return penaltyModel

    @staticmethod
    def __getLevelIcon(bnsID, bnsType, vehPostProgressionBonusLevels):
        if bnsType == constants.BonusTypes.BASE_MODIFICATION:
            level = vehPostProgressionBonusLevels.get(bnsID, None)
            numberFormat = 'arabic_number_{}' if isRomanNumberForbidden() else 'roman_number_{}'
            if level is not None:
                return R.images.gui.maps.icons.vehPostProgression.stepLevels.c_24x24.dyn(numberFormat.format(level))()
        return


class VehicleAvgParamsTooltipView(BaseVehicleAdvancedParamsTooltipView):
    _AVG_TO_RANGE_PARAMETER_NAME = {'avgDamage': 'damage',
     'avgPiercingPower': 'piercingPower'}

    def _fillModel(self, model):
        super(VehicleAvgParamsTooltipView, self)._fillModel(model)
        rangeParamNames = [self._AVG_TO_RANGE_PARAMETER_NAME[self._paramName]]
        shell = self.vehicle.descriptor.shot.shell
        if self._paramName == 'avgPiercingPower' and shell.isPiercingDistanceDependent:
            rangeParamNames = ['maxPiercingPower', 'minPiercingPower']
        elif self._paramName == 'avgDamage' and shell.isDamageMutable:
            rangeParamNames = ['maxMutableDamage', 'minMutableDamage']
        categories = model.getCategories()
        category = VehicleParamsCategory()
        items = category.getItems()
        for rangeParamName in rangeParamNames:
            value = self._context.getComparator().getExtendedData(rangeParamName).value
            fmtValue = param_formatter.formatParameter(rangeParamName, value)
            args = {'units': i18n.makeString(param_formatter.MEASURE_UNITS.get(rangeParamName))}
            if rangeParamName in ('minPiercingPower', 'minMutableDamage'):
                args['distance'] = int(min(self.vehicle.descriptor.shot.maxDistance, PIERCING_DISTANCES[1]))
            title = backport.text(R.strings.tooltips.tank_params.avgParamComment.dyn(rangeParamName)(), **args)
            avgItem = VehicleParamsItem()
            avgItem.setValue(self._formatValueText(ValueStyleEnum.WHITESPANISH, fmtValue))
            avgItem.setTitle(title)
            items.addViewModel(avgItem)

        categories.addViewModel(category)
