# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/stun.py
from soft_exception import SoftException
from items import _xml
import ResMgr
_CONFIG_FILE = 'scripts/item_defs/vehicles/common/stun.xml'
g_cfg = {}

def readConfig():
    reader = ResMgr.openSection(_CONFIG_FILE)
    if reader is None:
        _xml.raiseWrongXml(None, _CONFIG_FILE, 'can not open or read')
    xmlCtx = (None, _CONFIG_FILE)
    c = {}
    section = reader['DEFAULT']
    if section is None:
        _xml.raiseWrongXml(xmlCtx, reader.name, "'DEFAULT' subsection is missed")
    readStunType(c, xmlCtx, section)
    section = reader['stunTypes']
    if section is not None:
        xmlCtx = (xmlCtx, section.name)
        for stunType, stunData in section.items():
            readStunType(c, xmlCtx, stunData, c['DEFAULT'])

    return c


def readStunType(config, xmlCtx, section, default=None):
    if section.name in config:
        _xml.raiseWrongXml(xmlCtx, section.name, 'duplicate stun type name')
    xmlCtx = (xmlCtx, section.name)
    config[section.name] = stunType = {}
    stunType['baseStunDuration'] = _xml.readNonNegativeFloat(xmlCtx, section, 'baseStunDuration', 0 if default is None else default['baseStunDuration'])
    stunType['shellEffectFactor'] = _xml.readFraction(xmlCtx, section, 'shellEffectFactor', 0 if default is None else default['shellEffectFactor'])
    factors = ('stunFactorEnginePower', 'stunFactorVehicleRotationSpeed', 'stunFactorTurretTraverse', 'stunFactorViewDistance', 'stunFactorMaxSpeed')
    for factor in factors:
        stunType[factor] = _xml.readFraction(xmlCtx, section, factor, 0.0 if default is None else default[factor])

    factors = ('stunFactorReloadTime', 'stunFactorAimingTime', 'stunFactorVehicleMovementShotDispersion', 'stunFactorVehicleRotationShotDispersion', 'stunFactorTurretRotationShotDispersion', 'stunFactorMinShotDispersion')
    for factor in factors:
        stunType[factor] = _xml.readPositiveFloat(xmlCtx, section, factor, 1.0 if default is None else default[factor])
        _validateValue1inf(factor, stunType[factor])

    return


def init():
    global g_cfg
    g_cfg.update(readConfig())


def _validateValue1inf(keyName, value):
    if value < 1:
        raise SoftException('invalid value for "%s": %s (it should be in range [1, +inf])' % (keyName, value))
