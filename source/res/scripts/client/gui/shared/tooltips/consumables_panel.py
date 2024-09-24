# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/consumables_panel.py
from typing import TYPE_CHECKING
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
from post_progression_common import TankSetupLayouts, TankSetupGroupsId
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
if TYPE_CHECKING:
    from typing import Tuple, Optional
    from items.vehicle_items import Shell
    from gui.battle_control.controllers.consumables.ammo_ctrl import _GunSettings
    from gui.battle_control.arena_info.interfaces import IPrebattleSetupsController
ASTERISK = '*'
TOOLTIP_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}\n/{{BODY}}{1:>s}{{/BODY}}'
TOOLTIP_NO_BODY_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}'

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext, battleSessionProvider=IBattleSessionProvider)
def makeShellTooltip(intCD, lobbyContext=None, battleSessionProvider=None):
    gunSettings = battleSessionProvider.shared.ammo.getGunSettings()
    descriptor = gunSettings.getShellDescriptor(intCD)
    piercingPower = int(round(gunSettings.getPiercingPower(intCD)))
    shotSpeed = gunSettings.getShotSpeed(intCD)
    kind = descriptor.kind
    projSpeedFactor = vehicles.g_cache.commonConfig['miscParams']['projectileSpeedFactor']
    header = backport.text(R.strings.item_types.shell.kinds.dyn(kind)())
    body = ''
    fmt = TOOLTIP_NO_BODY_FORMAT
    if GUI_SETTINGS.technicalInfo:
        vehicle = battleSessionProvider.shared.vehicleState.getControllingVehicle()
        vehicleDescriptor = vehicle.typeDescriptor if vehicle else None
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
        params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.shotSpeed(), value=backport.getIntegralFormat(int(round(shotSpeed / projSpeedFactor)))))
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
    item = None
    layout, group = GROUP_AND_LAYOUT.get(slotType, (None, None))
    if layout and group:
        intCD = preBattleSetups.getSlotItem(layout, group, slotId)
        if intCD:
            item = vehicles.getItemByCompactDescr(intCD)
    return getEquipmentTooltipContent(item) if item else ('', '')


def getEquipmentTooltipContent(item):
    body = stripColorTagDescrTags(item.shortDescriptionSpecial)
    if isinstance(item, Equipment):
        if item.cooldownSeconds:
            tooltipStr = R.strings.ingame_gui.consumables_panel.equipment.cooldownSeconds()
            cooldownStr = backport.text(tooltipStr, cooldownSeconds=str(int(item.cooldownSeconds)))
            body = '\n\n'.join((body, cooldownStr))
    return (item.userString, body)
