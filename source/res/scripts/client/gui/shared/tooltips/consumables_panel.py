# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/consumables_panel.py
from __future__ import absolute_import, division
from typing import TYPE_CHECKING
from battle_modifiers_common import BattleParams
from constants import DAMAGE_INTERPOLATION_DIST_FIRST, DAMAGE_INTERPOLATION_DIST_LAST
from constants import SHELL_TYPES
from gui import GUI_SETTINGS
from gui.battle_control.components_states.ammo.constants import ShellMode
from gui.battle_control.gui_vehicle_builder import VehicleBuilder
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.shared.formatters import text_styles
from gui.shared.gui_items import KPI
from gui.shared.items_parameters.functions import aggregateKpi, getBustleFeedModifiedShells, getShellCalibrationShells, getShellParamsSwitcherModifiedShells, kpiFromCrewSkills
from gui.shared.items_parameters import getShellDescriptors, NO_DATA
from gui.shared.items_parameters.shell_params import ShellParams
from gui.shared.items_parameters.formatters import CRITICAL_HIT_CHANCE_TYPE_DYN_PATH
from gui.shared.utils.functions import stripColorTagDescrTags
from helpers import dependency
from items import vehicles
from items.artefacts import Equipment, Artefact
from items.utils import getVehicleShotSpeedByFactors, getVehicleDescriptorWithoutMechanics
from math_common import round_py2_style_int
from post_progression_common import TankSetupLayouts, TankSetupGroupsId
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import hasVehicleDescrMechanic
if TYPE_CHECKING:
    from typing import Tuple, Optional, Type
    from items.vehicle_items import Shell
    from items.vehicles import VehicleDescriptor
    from gui.battle_control.controllers.consumables.ammo_ctrl import _GunSettings
    from gui.battle_control.arena_info.interfaces import IPrebattleSetupsController
    from battle_modifiers_common import BattleModifiers
ASTERISK = '*'
TOOLTIP_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}\n/{{BODY}}{1:>s}{{/BODY}}'
TOOLTIP_NO_BODY_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}'
BULLET = backport.text(R.strings.common.common.bullet())
LIST_PREFIX = BULLET + ' '
GROUP_AND_LAYOUT = {TankSetupConstants.CONSUMABLES: (TankSetupLayouts.EQUIPMENT, TankSetupGroupsId.EQUIPMENT_AND_SHELLS),
 TankSetupConstants.OPT_DEVICES: (TankSetupLayouts.OPTIONAL_DEVICES, TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS),
 TankSetupConstants.BATTLE_BOOSTERS: (TankSetupLayouts.BATTLE_BOOSTERS, TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS)}

@dependency.replace_none_kwargs(battleSessionProvider=IBattleSessionProvider)
def buildEquipmentSlotTooltipTextBySlotInfo(slotType, slotId, battleSessionProvider=None):
    preBattleSetups = battleSessionProvider.shared.prebattleSetups
    item = None
    layout, group = GROUP_AND_LAYOUT.get(slotType, (None, None))
    if layout and group:
        intCD = preBattleSetups.getSlotItem(layout, group, slotId)
        if intCD:
            item = vehicles.getItemByCompactDescr(intCD)
    if item:
        modifiers = battleSessionProvider.arenaVisitor.getArenaModifiers()
        return _getEquipmentTooltipContent(item, modifiers)
    else:
        return ('', '')


def _getEquipmentTooltipContent(item, modifiers):
    body = stripColorTagDescrTags(item.shortDescriptionSpecial)
    if isinstance(item, Equipment):
        if item.cooldownSeconds:
            cooldown = modifiers(BattleParams.EQUIPMENT_COOLDOWN, item.cooldownSeconds)
            tooltipStr = R.strings.ingame_gui.consumables_panel.equipment.cooldownSeconds()
            cooldownStr = backport.text(tooltipStr, cooldownSeconds=str(int(cooldown)))
            body = '\n\n'.join((body, cooldownStr))
    return (item.userString, body)


@dependency.replace_none_kwargs(sessionProvider=IBattleSessionProvider)
def makeShellTooltip(intCD, sessionProvider=None):
    gunSettings = sessionProvider.shared.ammo.getGunSettings()
    descriptor = gunSettings.getShellDescriptor(intCD)
    kind = descriptor.kind
    header = backport.text(R.strings.item_types.shell.kinds.dyn(kind)())
    body = ''
    fmt = TOOLTIP_NO_BODY_FORMAT
    if GUI_SETTINGS.technicalInfo:
        vehicle = sessionProvider.shared.vehicleState.getControllingVehicle()
        vehicleDescriptor = vehicle.typeDescriptor if vehicle is not None else None
        if vehicleDescriptor is None:
            return (header, body, fmt)
        mechanic = _getShellMechanic(descriptor, vehicleDescriptor)
        paramsBuilder = getShellTooltipsParamBuilderByMechanic(mechanic)()
        params = paramsBuilder.build(descriptor, vehicleDescriptor, gunSettings)
        body = text_styles.concatStylesToMultiLine(*params)
        fmt = TOOLTIP_FORMAT
    return (header, body, fmt)


@dependency.replace_none_kwargs(sessionProvider=IBattleSessionProvider)
def applyBoundFactors(value, sessionProvider=None):
    vStateCtrl = sessionProvider.shared.vehicleState
    vehicleEntity = vStateCtrl.getControllingVehicle() if vStateCtrl else None
    if vehicleEntity is None:
        return value
    else:
        builder = VehicleBuilder()
        builder.setStrCD(vehicleEntity.typeDescriptor.makeCompactDescr())
        builder.setCrew(vehicleEntity.crewCompactDescrs)
        kpiFactors = aggregateKpi(kpiFromCrewSkills(builder.getResult()))
        lowerBoundFactor = kpiFactors.getFactor(KPI.Name.DAMAGE_AND_PIERCING_DISTRIBUTION_LOWER_BOUND)
        upperBoundFactor = kpiFactors.getFactor(KPI.Name.DAMAGE_AND_PIERCING_DISTRIBUTION_UPPER_BOUND)
        totalFactor = (lowerBoundFactor + upperBoundFactor) / 100.0
        return round_py2_style_int(value * (1.0 + totalFactor / 2)) if totalFactor else value


def getShellTooltipsParamBuilder(shellMode):
    return _PARAM_BUILDERS.get(shellMode, _StandardShellParamsBuilder)


def getShellTooltipsParamBuilderByMechanic(mechanic):
    return _PARAM_BUILDERS_BY_MECHANIC.get(mechanic, _StandardShellParamsBuilder)


class IShellParamsBuilder(object):

    def build(self, shellDescr, vDescr, gunSettings):
        raise NotImplementedError


class _StandardShellParamsBuilder(IShellParamsBuilder):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def build(self, shellDescr, vDescr, gunSettings):
        shellParams = ShellParams(shellDescr, vDescr)
        params = []
        footnotes = _FootnoteCollector()
        self._appendDamage(params, shellDescr, vDescr, shellParams, footnotes)
        self._appendDamagePerSec(params, shellDescr, vDescr)
        self._appendPiercingPower(params, shellDescr, gunSettings, shellParams, footnotes)
        self._appendShotSpeed(params, shellDescr, gunSettings)
        self._appendExplosionRadius(params, shellDescr)
        self._appendStunDuration(params, shellDescr)
        params.extend(footnotes.collectNotes())
        return params

    def _appendDamage(self, params, shellDescr, vDescr, shellParams, footnotes):
        damageValue = backport.getIntegralFormat(applyBoundFactors(shellParams.avgDamage))
        note = ''
        if shellDescr.isDamageMutable:
            damageValue = '%s-%s' % (backport.getIntegralFormat(applyBoundFactors(shellParams.avgMutableDamage[0])), backport.getIntegralFormat(applyBoundFactors(shellParams.avgMutableDamage[1])))
            note = footnotes.addDistanceNote(minDist=int(DAMAGE_INTERPOLATION_DIST_FIRST), maxDist=int(min(vDescr.shot.maxDistance, DAMAGE_INTERPOLATION_DIST_LAST)))
        params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.damage(), value=damageValue) + note)

    def _appendDamagePerSec(self, params, shellDescr, vDescr):
        if vDescr is not None and vDescr.isAutoShootGunVehicle:
            params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.damagePerSecond(), value=backport.getIntegralFormat(round_py2_style_int(shellDescr.armorDamage[0] / vDescr.gun.clip[1]))))
        return

    def _appendPiercingPower(self, params, shellDescr, gunSettings, shellParams, footnotes):
        piercingPower = gunSettings.getPiercingPower(shellDescr.compactDescr)
        if piercingPower == 0:
            return
        else:
            piercingPower = applyBoundFactors(piercingPower)
            value = backport.getNiceNumberFormat(piercingPower)
            piercingPowerTable = shellParams.piercingPowerTable
            if piercingPowerTable is not None and piercingPowerTable != NO_DATA:
                value = '%s-%s' % (backport.getIntegralFormat(applyBoundFactors(piercingPowerTable[0][1])), backport.getIntegralFormat(applyBoundFactors(piercingPowerTable[-1][1])))
                note = footnotes.addDistanceNote(minDist=backport.getIntegralFormat(piercingPowerTable[0][0]), maxDist=backport.getIntegralFormat(piercingPowerTable[-1][0]))
            else:
                note = footnotes.addNoDistanceNote()
            params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.piercingPower(), value=value) + note)
            return

    def _appendShotSpeed(self, params, shellDescr, gunSettings):
        intCD = shellDescr.compactDescr
        shotSpeed = gunSettings.getShotSpeed(intCD)
        vehAttrs = self._sessionProvider.shared.feedback.getVehicleAttrs()
        shotSpeed, _ = getVehicleShotSpeedByFactors(vehAttrs, shotSpeed)
        projSpeedFactor = vehicles.g_cache.commonConfig['miscParams']['projectileSpeedFactor']
        params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.shotSpeed(), value=backport.getIntegralFormat(round_py2_style_int(shotSpeed / projSpeedFactor))))

    def _appendExplosionRadius(self, params, shellDescr):
        if shellDescr.kind == SHELL_TYPES.HIGH_EXPLOSIVE and shellDescr.type.explosionRadius > 0.0:
            params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.explosionRadius(), value=backport.getNiceNumberFormat(shellDescr.type.explosionRadius)))

    def _appendStunDuration(self, params, shellDescr):
        if shellDescr.hasStun and self._lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
            stun = shellDescr.stun
            params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.stunDuration(), minValue=backport.getNiceNumberFormat(stun.guaranteedStunDuration * stun.stunDuration), maxValue=backport.getNiceNumberFormat(stun.stunDuration)))


class _ComplexMechanicParamsBuilder(IShellParamsBuilder):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _mechanic = None

    def build(self, shellDescr, vDescr, gunSettings):
        basicVDescr, specVDescr = self._getDescriptors(vDescr)
        footnotes = _FootnoteCollector()
        params = self._getBaseParams(shellDescr, basicVDescr, specVDescr, footnotes)
        params.extend(self._getExtendedParams(shellDescr, basicVDescr, specVDescr))
        params.extend(footnotes.collectNotes())
        return [self._getLabel()] + params

    def _getLabel(self):
        return backport.text(R.strings.ingame_gui.shells_kinds.params.header.dyn(self._mechanic.value)()) if self._mechanic is not None else ''

    def _getDescriptors(self, vDescr):
        return (vDescr, vDescr)

    def _getBaseParams(self, shellDescr, basicVDescr, specVDescr, footnotes):
        params = []
        basicShellParams = ShellParams(shellDescr, basicVDescr)
        specShellParams = ShellParams(shellDescr, specVDescr)
        damage = _formatPairOfValues(applyBoundFactors(basicShellParams.avgDamage), applyBoundFactors(specShellParams.avgDamage), backport.getIntegralFormat)
        params.append(LIST_PREFIX + backport.text(R.strings.ingame_gui.shells_kinds.params.damage(), value=damage))
        piercingPowerTable = specShellParams.piercingPowerTable
        if piercingPowerTable is not None and piercingPowerTable != NO_DATA:
            basicPiercing = '%s-%s' % (backport.getIntegralFormat(applyBoundFactors(basicShellParams.piercingPowerTable[0][1])), backport.getIntegralFormat(applyBoundFactors(basicShellParams.piercingPowerTable[-1][1])))
            specPiercing = '%s-%s' % (backport.getIntegralFormat(applyBoundFactors(piercingPowerTable[0][1])), backport.getIntegralFormat(applyBoundFactors(piercingPowerTable[-1][1])))
            piercing = '%s / %s' % (basicPiercing, specPiercing)
            note = footnotes.addDistanceNote(minDist=backport.getIntegralFormat(piercingPowerTable[0][0]), maxDist=backport.getIntegralFormat(piercingPowerTable[-1][0]))
            params.append(LIST_PREFIX + backport.text(R.strings.ingame_gui.shells_kinds.params.piercingPower(), value=piercing) + note)
        elif specShellParams.avgPiercingPower:
            piercing = _formatPairOfValues(applyBoundFactors(basicShellParams.avgPiercingPower), applyBoundFactors(specShellParams.avgPiercingPower), backport.getIntegralFormat)
            note = footnotes.addNoDistanceNote()
            params.append(LIST_PREFIX + backport.text(R.strings.ingame_gui.shells_kinds.params.piercingPower(), value=piercing) + note)
        vehAttrs = self._sessionProvider.shared.feedback.getVehicleAttrs()
        basicShotSpeed, _ = getVehicleShotSpeedByFactors(vehAttrs, basicShellParams.shotSpeed)
        specShotSpeed, _ = getVehicleShotSpeedByFactors(vehAttrs, specShellParams.shotSpeed)
        shotSpeed = _formatPairOfValues(round_py2_style_int(basicShotSpeed), round_py2_style_int(specShotSpeed), backport.getIntegralFormat)
        params.append(LIST_PREFIX + backport.text(R.strings.ingame_gui.shells_kinds.params.shotSpeed(), value=shotSpeed))
        if specShellParams.explosionRadius:
            explosionRadius = _formatPairOfValues(basicShellParams.explosionRadius, specShellParams.explosionRadius)
            params.append(LIST_PREFIX + backport.text(R.strings.ingame_gui.shells_kinds.params.explosionRadius(), value=explosionRadius))
        return params

    def _getExtendedParams(self, shellDescr, basicVDescr, specVDescr):
        return []


class _LowChargeShotParamsBuilder(_ComplexMechanicParamsBuilder):
    _mechanic = VehicleMechanic.LOW_CHARGE_SHOT

    def _getDescriptors(self, vDescr):
        return (vDescr.defaultVehicleDescr, vDescr.siegeVehicleDescr)


class _ShellCalibrationParamsBuilder(_ComplexMechanicParamsBuilder):
    _mechanic = VehicleMechanic.SHELL_CALIBRATION

    def _getDescriptors(self, vDescr):
        return (getVehicleDescriptorWithoutMechanics(vDescr, self._mechanic.value), vDescr)


class _ShellParamsSwitcherParamsBuilder(_ComplexMechanicParamsBuilder):
    _mechanic = VehicleMechanic.SHELL_PARAMS_SWITCHER

    def _getDescriptors(self, vDescr):
        return (vDescr.defaultVehicleDescr, vDescr.siegeVehicleDescr)

    def _getExtendedParams(self, shellDescr, basicVDescr, specVDescr):
        params = []
        basicShell = getShellDescriptors(shellDescr, basicVDescr)[0].shell
        specShell = getShellDescriptors(shellDescr, specVDescr)[0].shell
        basicShellParams = ShellParams(shellDescr, basicVDescr)
        specShellParams = ShellParams(shellDescr, specVDescr)
        if shellDescr.isArmorPercingType:
            if basicShell.type.normalizationAngle != specShell.type.normalizationAngle:
                params.append(_getNormalizationAngleBlock(basicShellParams, specShellParams))
            if basicShell.type.ricochetAngleCos != specShell.type.ricochetAngleCos:
                params.append(_getRicochetAngleBlock(basicShellParams, specShellParams))
            criticalHitChanceBlock = _getCriticalHitChanceBlock(basicShellParams, specShellParams)
            if criticalHitChanceBlock is not None:
                params.append(criticalHitChanceBlock)
        elif shellDescr.kind == SHELL_TYPES.HOLLOW_CHARGE:
            if basicShell.type.ricochetAngleCos != specShell.type.ricochetAngleCos:
                params.append(_getRicochetAngleBlock(basicShellParams, specShellParams))
            if basicShell.type.piercingPowerLossFactorByDistance != specShell.type.piercingPowerLossFactorByDistance:
                params.append(_getPenetrationLossBlock(basicShellParams, specShellParams))
        return params


class _BustleFeedParamsBuilder(_ComplexMechanicParamsBuilder):
    _mechanic = VehicleMechanic.BUSTLE_FEED

    def _getDescriptors(self, vDescr):
        if vDescr.hasSiegeMode:
            vDescr = vDescr.defaultVehicleDescr
        return (getVehicleDescriptorWithoutMechanics(vDescr, self._mechanic.value), vDescr)


_PARAM_BUILDERS = {ShellMode.LOW_CHARGE_SHOT: _LowChargeShotParamsBuilder,
 ShellMode.SHELL_PARAMS_SWITCHER: _ShellParamsSwitcherParamsBuilder,
 ShellMode.SHELL_CALIBRATION: _ShellCalibrationParamsBuilder,
 ShellMode.BUSTLE_FEED: _BustleFeedParamsBuilder}
_PARAM_BUILDERS_BY_MECHANIC = {VehicleMechanic.LOW_CHARGE_SHOT: _LowChargeShotParamsBuilder,
 VehicleMechanic.SHELL_PARAMS_SWITCHER: _ShellParamsSwitcherParamsBuilder,
 VehicleMechanic.SHELL_CALIBRATION: _ShellCalibrationParamsBuilder,
 VehicleMechanic.BUSTLE_FEED: _BustleFeedParamsBuilder}

class _FootnoteCollector(object):

    def __init__(self):
        self.__notes = []
        self.__distanceNoteMarker = None
        return

    def addNote(self, text):
        marker = ASTERISK * (len(self.__notes) + 1)
        self.__notes.append('\n' + marker + text)
        return marker

    def addDistanceNote(self, minDist, maxDist):
        if self.__distanceNoteMarker is not None:
            return self.__distanceNoteMarker
        else:
            text = backport.text(R.strings.menu.moduleInfo.params.footnote.piercingDistance(), minDist=minDist, maxDist=maxDist)
            self.__distanceNoteMarker = self.addNote(text)
            return self.__distanceNoteMarker

    def addNoDistanceNote(self):
        return self.addNote(backport.text(R.strings.menu.moduleInfo.params.footnote.noPiercingDistance()))

    def collectNotes(self):
        return self.__notes


def _getShellMechanic(descriptor, vehicleDescriptor):
    if hasVehicleDescrMechanic(vehicleDescriptor, VehicleMechanic.LOW_CHARGE_SHOT):
        return VehicleMechanic.LOW_CHARGE_SHOT
    elif descriptor.compactDescr in getShellCalibrationShells(vehicleDescriptor):
        return VehicleMechanic.SHELL_CALIBRATION
    elif descriptor.compactDescr in getShellParamsSwitcherModifiedShells(vehicleDescriptor):
        return VehicleMechanic.SHELL_PARAMS_SWITCHER
    else:
        return VehicleMechanic.BUSTLE_FEED if descriptor.compactDescr in getBustleFeedModifiedShells(vehicleDescriptor) else None


def _formatPairOfValues(value1, value2, formattingFunc=backport.getNiceNumberFormat):
    return '%s / %s' % (formattingFunc(value1), formattingFunc(value2))


def _formatPairOfValuesByTemplate(value1, value2, template, formattingFunc=backport.getNiceNumberFormat):
    return '%s / %s' % (backport.text(template, value=formattingFunc(value1)), backport.text(template, value=formattingFunc(value2)))


def _getNormalizationAngleBlock(basicShellParams, specShellParams):
    normalization = _formatPairOfValues(basicShellParams.normalizationAngle, specShellParams.normalizationAngle, backport.getIntegralFormat)
    return LIST_PREFIX + backport.text(R.strings.ingame_gui.shells_kinds.params.normalizationAngle(), value=normalization)


def _getRicochetAngleBlock(basicShellParams, specShellParams):
    ricochetAngle = _formatPairOfValues(basicShellParams.ricochetAngle, specShellParams.ricochetAngle, backport.getIntegralFormat)
    return LIST_PREFIX + backport.text(R.strings.ingame_gui.shells_kinds.params.ricochetAngle(), value=ricochetAngle)


def _getCriticalHitChanceBlock(basicShellParams, specShellParams):
    basicShellCriticalHitChance = basicShellParams.criticalHitChance
    specShellCriticalHitChance = specShellParams.criticalHitChance
    if basicShellCriticalHitChance != specShellCriticalHitChance:
        criticalHitChanceR = R.strings.ingame_gui.shells_kinds.params.criticalHitChance

        def getCriticalHitChanceStr(chanceType):
            return backport.text(criticalHitChanceR.dyn(CRITICAL_HIT_CHANCE_TYPE_DYN_PATH[chanceType])())

        criticalHitChance = _formatPairOfValues(basicShellCriticalHitChance, specShellCriticalHitChance, getCriticalHitChanceStr)
        return LIST_PREFIX + backport.text(criticalHitChanceR(), value=criticalHitChance)
    else:
        return None


def _getPenetrationLossBlock(basicShellParams, specShellParams):
    penetrationLossR = R.strings.ingame_gui.shells_kinds.params
    penetrationLoss = _formatPairOfValuesByTemplate(basicShellParams.penetrationLoss, specShellParams.penetrationLoss, penetrationLossR.penetrationLossValueTemplate(), backport.getIntegralFormat)
    return LIST_PREFIX + backport.text(penetrationLossR.penetrationLoss(), value=penetrationLoss)
