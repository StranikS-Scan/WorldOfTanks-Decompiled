# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/armor/penetration_utils.py
from __future__ import absolute_import, division
import math
import typing
from builtins import round
from collections import namedtuple
import armor_inspector
import math_utils
from account_helpers.settings_core import settings_constants
from constants import SHELL_TYPES, SHELL_MECHANICS_TYPE
from gui.impl.lobby.vehicle_hub.sub_presenters.armor.utils import colorInt2Str, applyNormalizationForArmor
from helpers import dependency
from gui.impl.lobby.vehicle_hub.sub_presenters.armor.config import getConfig
from gui.shared.utils.functions import getShellImpactParams
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_model import DCCType
from items.components.component_constants import MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS, MODERN_HE_DAMAGE_ABSORPTION_FACTOR
from skeletons.account_helpers.settings_core import ISettingsCore
if typing.TYPE_CHECKING:
    from Vehicle import SegmentCollisionResultExt
    from items.components.gun_components import GunShot
ShellParams = namedtuple('ShellParams', ('shellCaliber', 'shellPiercingFull', 'shellPiercingMin', 'shellPiercingMax', 'shellPiercingPowerRandomization', 'normalizationAngle', 'ricochetAngleCos', 'shellJetLossPPByDist', 'shellMayRicochet', 'shellCheckCaliberForRicochet', 'shieldPenetration', 'shellTypeMaxDamage', 'useHEShell'))
PenetrationInfo = namedtuple('PenetrationInfo', ('chance', 'color', 'resultType'))
_EPS = 1e-05
_HALF_PI = math.pi * 0.5
_MM_TO_M = 0.001
_PEN_SIGMA = 0.33
_INV_SQRT2 = 1.0 / math.sqrt(2.0)

def setShellParamsFromVehicle(shot, spaceID):
    shell = shot.shell
    ricochetAngleCos, normalizationAngle, _, _ = getShellImpactParams(shell.type)
    fullPiercingPower = shot.piercingPower[0]
    minPP = 100.0 * (1.0 - shell.piercingPowerRandomization)
    maxPP = 100.0 * (shell.piercingPowerRandomization + 1.0)
    shellJetLossPPByDist = 0.0
    if shell.kind in (SHELL_TYPES.ARMOR_PIERCING, SHELL_TYPES.ARMOR_PIERCING_CR):
        shellMayRicochet = True
        checkCaliberForRicochet = True
    elif shell.kind == SHELL_TYPES.ARMOR_PIERCING_HE:
        shellMayRicochet = True
        checkCaliberForRicochet = True
    elif shell.kind == SHELL_TYPES.HOLLOW_CHARGE:
        shellMayRicochet = True
        checkCaliberForRicochet = False
    else:
        shellMayRicochet = False
        checkCaliberForRicochet = False
    if hasattr(shell.type, 'piercingPowerLossFactorByDistance'):
        shellJetLossPPByDist = shell.type.piercingPowerLossFactorByDistance
    shieldPenetration = 0.0
    shellTypeMaxDamage = 0.0
    useHEShell = shell.kind == SHELL_TYPES.HIGH_EXPLOSIVE and shell.type.mechanics == SHELL_MECHANICS_TYPE.MODERN
    if shell.kind == SHELL_TYPES.HIGH_EXPLOSIVE:
        if shell.type.shieldPenetration is not None:
            shieldPenetration = float(shell.type.shieldPenetration)
        if shell.type.maxDamage is not None:
            shellTypeMaxDamage = float(shell.type.maxDamage)
    shellParams = ShellParams(shellCaliber=float(shell.caliber), shellPiercingPowerRandomization=float(shell.piercingPowerRandomization), shellPiercingFull=float(fullPiercingPower), shellPiercingMin=float(minPP), shellPiercingMax=float(maxPP), normalizationAngle=float(normalizationAngle), ricochetAngleCos=float(ricochetAngleCos), shellJetLossPPByDist=float(shellJetLossPPByDist), shellMayRicochet=bool(shellMayRicochet), shellCheckCaliberForRicochet=bool(checkCaliberForRicochet), shieldPenetration=float(shieldPenetration), shellTypeMaxDamage=float(shellTypeMaxDamage), useHEShell=bool(useHEShell))
    armor_inspector.setShellParams(spaceID, shellParams.shellCaliber, shellParams.shellPiercingFull, shellParams.shellPiercingMin, shellParams.shellPiercingMax, shellParams.normalizationAngle, shellParams.ricochetAngleCos, shellParams.shellJetLossPPByDist, shellParams.shellMayRicochet, shellParams.shellCheckCaliberForRicochet, shellParams.shieldPenetration, shellParams.shellTypeMaxDamage, shellParams.useHEShell)
    return shellParams


def calculatePenetrationInfo(shellParams, collisions):
    params = shellParams
    if params is None or params.shellPiercingFull <= _EPS:
        return
    else:
        parts = collisions
        if not parts:
            return
        settingsCore = dependency.instance(ISettingsCore)
        isColorBlind = settingsCore.getSetting(settings_constants.GRAPHICS.COLOR_BLIND)
        colorPalette = getConfig().getActualColorList(isColorBlind)
        ricochetColor = colorPalette.ricochet
        noDamageColor = colorPalette.noDamage
        firstDistance = parts[0].dist
        remainingShellPen = params.shellPiercingFull
        ignoredMaterials = set()
        isJet = False
        jetStartDist = 0.0
        explosionDamageAbsorption = 0.0
        for collision in parts:
            matInfo = collision.matInfo
            if matInfo is None or matInfo.armor is None:
                continue
            matKey = (collision.compName, matInfo.kind)
            if matKey in ignoredMaterials:
                continue
            hitAngleCos = abs(collision.hitAngleCos) if matInfo.useHitAngle else 1.0
            hitAngleCos = math_utils.clamp(0.0, 1.0, hitAngleCos)
            if _shouldHitRicochet(matInfo, hitAngleCos, params) and not isJet:
                return PenetrationInfo(0, ricochetColor, DCCType.RICOCHET)
            collisionDistance = collision.dist - firstDistance + 0.1
            if isJet:
                jetDist = collisionDistance - jetStartDist
                if jetDist > 0.0:
                    lossFactor = 1.0 - jetDist * params.shellJetLossPPByDist
                    remainingShellPen *= max(lossFactor, 0.0)
            armorValue = float(matInfo.armor or 0.0)
            if matInfo.useHitAngle:
                hitAngleCos = applyNormalizationForArmor(hitAngleCos, armorValue, matInfo, params.normalizationAngle, params.shellCaliber)
                hitAngleCos = max(hitAngleCos, _EPS)
                penArmor = armorValue / hitAngleCos if hitAngleCos > _EPS else armorValue
            else:
                penArmor = armorValue
            if matInfo.vehicleDamageFactor and matInfo.vehicleDamageFactor > _EPS:
                result = _buildPenetrationResult(remainingShellPen, penArmor, params)
                return result
            if params.useHEShell:
                if params.shieldPenetration > 0.0:
                    remainingShellPen -= penArmor * MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS
                    explosionDamageAbsorption += penArmor * MODERN_HE_DAMAGE_ABSORPTION_FACTOR
                    if explosionDamageAbsorption >= params.shellTypeMaxDamage:
                        remainingShellPen = 0.0
                else:
                    remainingShellPen = 0.0
            else:
                remainingShellPen -= penArmor
            if matInfo.collideOnceOnly:
                ignoredMaterials.add(matKey)
            if params.shellJetLossPPByDist > 0.0:
                isJet = True
                jetStartDist = collisionDistance + armorValue * _MM_TO_M
            isJet = False

        return PenetrationInfo(0, noDamageColor, DCCType.NO_DAMAGE)


def _shouldHitRicochet(matInfo, hitAngleCos, params):
    if not getattr(matInfo, 'mayRicochet', False):
        return False
    armor = float(matInfo.armor or 0.0)
    if armor <= _EPS:
        return False
    if hitAngleCos > params.ricochetAngleCos:
        return False
    if not getattr(matInfo, 'checkCaliberForRicochet', False):
        return True
    return True if not params.shellCheckCaliberForRicochet else armor * 3.0 >= params.shellCaliber


def _buildPenetrationResult(remainingShellPen, penArmor, params):
    piercingRatio = (remainingShellPen - penArmor) / params.shellPiercingFull + 1.0
    randomization = params.shellPiercingPowerRandomization
    fraction = math_utils.clamp(0.0, 1.0, (piercingRatio + randomization - 1) / randomization / 2)
    chance = _computePenetrationChance(piercingRatio, randomization)
    color = colorInt2Str(armor_inspector.getPenColor(fraction))
    return PenetrationInfo(chance, color, DCCType.PENETRATION)


def _computePenetrationChance(piercingRatio, randomization):
    normalized = (piercingRatio - 1.0) / randomization / _PEN_SIGMA
    cdf = 0.5 * (1.0 + math.erf(normalized * _INV_SQRT2))
    return int(round(math_utils.clamp(0.0, 100.0, cdf * 100.0)))
