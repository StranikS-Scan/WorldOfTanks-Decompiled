# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/consumables_panel.py
from __future__ import absolute_import, division
from past.utils import old_div
from typing import TYPE_CHECKING
from battle_modifiers_common import BattleParams
from constants import DAMAGE_INTERPOLATION_DIST_FIRST, DAMAGE_INTERPOLATION_DIST_LAST
from constants import SHELL_TYPES
from gui import GUI_SETTINGS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.shared.formatters import text_styles
from gui.shared.items_parameters import NO_DATA
from gui.shared.items_parameters.params import ShellParams
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
    from typing import Tuple, Optional
    from items.vehicle_items import Shell
    from gui.battle_control.controllers.consumables.ammo_ctrl import _GunSettings
    from gui.battle_control.arena_info.interfaces import IPrebattleSetupsController
    from battle_modifiers_common import BattleModifiers
ASTERISK = '*'
TOOLTIP_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}\n/{{BODY}}{1:>s}{{/BODY}}'
TOOLTIP_NO_BODY_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}'
BULLET = backport.text(R.strings.common.common.bullet())
SPEC_PARAM_TEMPLATE = BULLET + ' ' + '%s'

def _formatPairOfValues(value1, value2, formattingFunc=backport.getNiceNumberFormat):
    return '%s / %s' % (formattingFunc(value1), formattingFunc(value2))


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext, battleSessionProvider=IBattleSessionProvider)
def makeShellTooltip(intCD, lobbyContext=None, battleSessionProvider=None):
    gunSettings = battleSessionProvider.shared.ammo.getGunSettings()
    descriptor = gunSettings.getShellDescriptor(intCD)
    piercingPower = round_py2_style_int(gunSettings.getPiercingPower(intCD))
    shotSpeed = gunSettings.getShotSpeed(intCD)
    kind = descriptor.kind
    projSpeedFactor = vehicles.g_cache.commonConfig['miscParams']['projectileSpeedFactor']
    header = backport.text(R.strings.item_types.shell.kinds.dyn(kind)())
    body = ''
    fmt = TOOLTIP_NO_BODY_FORMAT
    if GUI_SETTINGS.technicalInfo:
        vehicle = battleSessionProvider.shared.vehicleState.getControllingVehicle()
        vehicleDescriptor = vehicle.typeDescriptor if vehicle else None
        if hasVehicleDescrMechanic(vehicleDescriptor, VehicleMechanic.LOW_CHARGE_SHOT):
            params = getLowChargeShotParams(descriptor, vehicleDescriptor)
        else:
            shellParams = ShellParams(descriptor, vehicleDescriptor)
            piercingPowerTable = shellParams.piercingPowerTable
            isDistanceDependent = piercingPowerTable is not None
            damageValue = backport.getNiceNumberFormat(shellParams.avgDamage)
            note = ''
            showDistanceAsterisk = False
            footNotes = []
            if descriptor.isDamageMutable:
                showDistanceAsterisk = True
                damageValue = '{}-{}'.format(backport.getNiceNumberFormat(shellParams.avgMutableDamage[0]), backport.getNiceNumberFormat(shellParams.avgMutableDamage[1]))
                note = ASTERISK
                footNotes.append(ASTERISK + backport.text(R.strings.menu.moduleInfo.params.piercingDistance.footnote(), minDist=int(DAMAGE_INTERPOLATION_DIST_FIRST), maxDist=int(min(vehicleDescriptor.shot.maxDistance, DAMAGE_INTERPOLATION_DIST_LAST))))
            params = [backport.text(R.strings.ingame_gui.shells_kinds.params.damage(), value=damageValue) + note]
            if piercingPower != 0:
                value = backport.getNiceNumberFormat(piercingPower)
                if piercingPowerTable != NO_DATA and isDistanceDependent:
                    note = ASTERISK
                    value = '{}-{}'.format(backport.getNiceNumberFormat(piercingPowerTable[0][1]), backport.getNiceNumberFormat(piercingPowerTable[-1][1]))
                    if not showDistanceAsterisk:
                        footNotes.append(note + backport.text(R.strings.menu.moduleInfo.params.piercingDistance.footnote(), minDist=backport.getNiceNumberFormat(piercingPowerTable[0][0]), maxDist=backport.getNiceNumberFormat(piercingPowerTable[-1][0])))
                else:
                    note = ASTERISK if not showDistanceAsterisk else ASTERISK * 2
                    footNotes.append(note + backport.text(R.strings.menu.moduleInfo.params.noPiercingDistance.footnote()))
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.piercingPower(), value=value) + note)
            params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.shotSpeed(), value=backport.getIntegralFormat(round_py2_style_int(old_div(shotSpeed, projSpeedFactor)))))
            if kind == SHELL_TYPES.HIGH_EXPLOSIVE and descriptor.type.explosionRadius > 0.0:
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.explosionRadius(), value=backport.getNiceNumberFormat(descriptor.type.explosionRadius)))
            if descriptor.hasStun and lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
                stun = descriptor.stun
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.stunDuration(), minValue=backport.getNiceNumberFormat(stun.guaranteedStunDuration * stun.stunDuration), maxValue=backport.getNiceNumberFormat(stun.stunDuration)))
            for footNote in footNotes:
                params.append('\n' + footNote)

        body = text_styles.concatStylesToMultiLine(*params)
        fmt = TOOLTIP_FORMAT
    return (header, body, fmt)


GROUP_AND_LAYOUT = {TankSetupConstants.CONSUMABLES: (TankSetupLayouts.EQUIPMENT, TankSetupGroupsId.EQUIPMENT_AND_SHELLS),
 TankSetupConstants.OPT_DEVICES: (TankSetupLayouts.OPTIONAL_DEVICES, TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS),
 TankSetupConstants.BATTLE_BOOSTERS: (TankSetupLayouts.BATTLE_BOOSTERS, TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS)}

@dependency.replace_none_kwargs(battleSessionProvider=IBattleSessionProvider)
def buildEquipmentSlotTooltipTextBySlotInfo(slotType, slotId, battleSessionProvider=None):
    preBattleSetups = battleSessionProvider.shared.prebattleSetups
    modifiers = battleSessionProvider.arenaVisitor.getArenaModifiers()
    item = None
    layout, group = GROUP_AND_LAYOUT.get(slotType, (None, None))
    if layout and group:
        intCD = preBattleSetups.getSlotItem(layout, group, slotId)
        if intCD:
            item = vehicles.getItemByCompactDescr(intCD)
    return getEquipmentTooltipContent(item, modifiers) if item else ('', '')


def getEquipmentTooltipContent(item, modifiers):
    body = stripColorTagDescrTags(item.shortDescriptionSpecial)
    if isinstance(item, Equipment):
        if item.cooldownSeconds:
            cooldown = modifiers(BattleParams.EQUIPMENT_COOLDOWN, item.cooldownSeconds)
            tooltipStr = R.strings.ingame_gui.consumables_panel.equipment.cooldownSeconds()
            cooldownStr = backport.text(tooltipStr, cooldownSeconds=str(int(cooldown)))
            body = '\n\n'.join((body, cooldownStr))
    return (item.userString, body)


def getLowChargeShotParams(shellDescr, vDescr, vehAttrs=None):
    params = [backport.text(R.strings.ingame_gui.shells_kinds.params.header())]
    vDescrWithoutMechanics = getVehicleDescriptorWithoutMechanics(vDescr, VehicleMechanic.LOW_CHARGE_SHOT.value)
    basicShellparams = ShellParams(shellDescr, vDescrWithoutMechanics)
    specShellParams = ShellParams(shellDescr, vDescr)
    damage = _formatPairOfValues(basicShellparams.avgDamage, specShellParams.avgDamage)
    params.append(SPEC_PARAM_TEMPLATE % backport.text(R.strings.ingame_gui.shells_kinds.params.damage(), value=damage))
    piercingPowerTable = specShellParams.piercingPowerTable
    piercingNote = ''
    if piercingPowerTable is not None and piercingPowerTable != NO_DATA:
        basicPiercing = '%s-%s' % (backport.getNiceNumberFormat(basicShellparams.piercingPowerTable[0][1]), backport.getNiceNumberFormat(basicShellparams.piercingPowerTable[-1][1]))
        specPiercing = '%s-%s' % (backport.getNiceNumberFormat(piercingPowerTable[0][1]), backport.getNiceNumberFormat(piercingPowerTable[-1][1]))
        piercing = '%s / %s' % (basicPiercing, specPiercing)
        params.append(SPEC_PARAM_TEMPLATE % backport.text(R.strings.ingame_gui.shells_kinds.params.piercingPower(), value=piercing) + ASTERISK)
        piercingNote = backport.text(R.strings.menu.moduleInfo.params.piercingDistance.footnote(), minDist=backport.getNiceNumberFormat(piercingPowerTable[0][0]), maxDist=backport.getNiceNumberFormat(piercingPowerTable[-1][0]))
    elif specShellParams.avgPiercingPower:
        piercing = _formatPairOfValues(basicShellparams.avgPiercingPower, specShellParams.avgPiercingPower)
        params.append(SPEC_PARAM_TEMPLATE % backport.text(R.strings.ingame_gui.shells_kinds.params.piercingPower(), value=piercing) + ASTERISK)
        piercingNote = backport.text(R.strings.menu.moduleInfo.params.noPiercingDistance.footnote())
    if vehAttrs is not None:
        factorName = '{}/gunShotsSpeed'.format(VehicleMechanic.LOW_CHARGE_SHOT.value)
        basicShotSpeed, _ = getVehicleShotSpeedByFactors(vehAttrs, basicShellparams.shotSpeed, factorName=factorName)
        specShotSpeed, _ = getVehicleShotSpeedByFactors(vehAttrs, specShellParams.shotSpeed, factorName=factorName)
    else:
        basicShotSpeed = basicShellparams.shotSpeed
        specShotSpeed = specShellParams.shotSpeed
    shotSpeed = _formatPairOfValues(int(round_py2_style_int(basicShotSpeed)), int(round_py2_style_int(specShotSpeed)), backport.getIntegralFormat)
    params.append(SPEC_PARAM_TEMPLATE % backport.text(R.strings.ingame_gui.shells_kinds.params.shotSpeed(), value=shotSpeed))
    if specShellParams.explosionRadius:
        explosionRadius = _formatPairOfValues(basicShellparams.explosionRadius, specShellParams.explosionRadius)
        params.append(SPEC_PARAM_TEMPLATE % backport.text(R.strings.ingame_gui.shells_kinds.params.explosionRadius(), value=explosionRadius))
    if piercingNote:
        params.append('\n' + ASTERISK + piercingNote)
    return params
