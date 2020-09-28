# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/stun.py
from soft_exception import SoftException
from items import _xml
import ResMgr
_CONFIG_FILE = 'scripts/item_defs/vehicles/common/stun.xml'
g_cfg = {}

def readConfig():
    section = ResMgr.openSection(_CONFIG_FILE)
    if section is None:
        _xml.raiseWrongXml(None, _CONFIG_FILE, 'can not open or read')
    xmlCtx = (None, _CONFIG_FILE)
    c = {}
    c['baseStunDuration'] = _xml.readNonNegativeFloat(xmlCtx, section, 'baseStunDuration')
    c['guaranteedStunDuration'] = _xml.readFraction(xmlCtx, section, 'guaranteedStunDuration')
    c['damageDurationCoeff'] = _xml.readFraction(xmlCtx, section, 'damageDurationCoeff')
    c['guaranteedStunEffect'] = _xml.readFraction(xmlCtx, section, 'guaranteedStunEffect')
    c['damageEffectCoeff'] = _xml.readFraction(xmlCtx, section, 'damageEffectCoeff')
    c['minStunDuration'] = _xml.readNonNegativeFloat(xmlCtx, section, 'minStunDuration')
    c['shellEffectFactor'] = _xml.readFraction(xmlCtx, section, 'shellEffectFactor')
    c['stunFactorEnginePower'] = _xml.readFraction(xmlCtx, section, 'stunFactorEnginePower')
    c['stunFactorVehicleRotationSpeed'] = _xml.readFraction(xmlCtx, section, 'stunFactorVehicleRotationSpeed')
    c['stunFactorTurretTraverse'] = _xml.readFraction(xmlCtx, section, 'stunFactorTurretTraverse')
    c['stunFactorViewDistance'] = _xml.readFraction(xmlCtx, section, 'stunFactorViewDistance')
    c['stunFactorMaxSpeed'] = _xml.readFraction(xmlCtx, section, 'stunFactorMaxSpeed')
    c['wtStunFactorEnginePower'] = _xml.readFraction(xmlCtx, section, 'wtStunFactorEnginePower')
    c['wtStunFactorVehicleRotationSpeed'] = _xml.readFraction(xmlCtx, section, 'wtStunFactorVehicleRotationSpeed')
    c['wtStunFactorTurretTraverse'] = _xml.readFraction(xmlCtx, section, 'wtStunFactorTurretTraverse')
    c['wtStunFactorMaxSpeed'] = _xml.readFraction(xmlCtx, section, 'wtStunFactorMaxSpeed')
    c['stunFactorReloadTime'] = _xml.readPositiveFloat(xmlCtx, section, 'stunFactorReloadTime', 1.0)
    _validateValue1inf('stunFactorReloadTime', c['stunFactorReloadTime'])
    c['stunFactorAimingTime'] = _xml.readPositiveFloat(xmlCtx, section, 'stunFactorAimingTime', 1.0)
    _validateValue1inf('stunFactorAimingTime', c['stunFactorAimingTime'])
    c['stunFactorVehicleMovementShotDispersion'] = _xml.readPositiveFloat(xmlCtx, section, 'stunFactorVehicleMovementShotDispersion', 1.0)
    _validateValue1inf('stunFactorVehicleMovementShotDispersion', c['stunFactorVehicleMovementShotDispersion'])
    c['stunFactorVehicleRotationShotDispersion'] = _xml.readPositiveFloat(xmlCtx, section, 'stunFactorVehicleRotationShotDispersion', 1.0)
    _validateValue1inf('stunFactorVehicleRotationShotDispersion', c['stunFactorVehicleRotationShotDispersion'])
    c['stunFactorTurretRotationShotDispersion'] = _xml.readPositiveFloat(xmlCtx, section, 'stunFactorTurretRotationShotDispersion', 1.0)
    _validateValue1inf('stunFactorTurretRotationShotDispersion', c['stunFactorTurretRotationShotDispersion'])
    c['stunFactorMinShotDispersion'] = _xml.readPositiveFloat(xmlCtx, section, 'stunFactorMinShotDispersion', 1.0)
    _validateValue1inf('stunFactorMinShotDispersion', c['stunFactorMinShotDispersion'])
    return c


def init():
    global g_cfg
    g_cfg.update(readConfig())


def _validateValue1inf(keyName, value):
    if value < 1:
        raise SoftException('invalid value for "%s": %s (it should be in range [1, +inf])' % (keyName, value))
