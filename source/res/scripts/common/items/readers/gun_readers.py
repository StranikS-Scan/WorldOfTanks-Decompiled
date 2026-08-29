# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/gun_readers.py
from __future__ import absolute_import
from typing import TYPE_CHECKING, Tuple, Optional
import ResMgr
from items import _xml
from items.components import component_constants
from items.components import gun_components
from items.components.shell_components import Stun
from items.stun import g_cfg as stunConfig
from items.readers import shared_readers
from constants import IS_EDITOR
if TYPE_CHECKING:
    from items.vehicles import Cache

def readRecoilEffect(xmlCtx, section, cache):
    if not section.has_key('recoil'):
        return
    else:
        effName = _xml.readStringOrNone(xmlCtx, section, 'recoil/recoilEffect')
        if effName is not None:
            recoilEff = cache.getGunRecoilEffects(effName)
            if recoilEff is not None:
                backoffTime = recoilEff[0]
                returnTime = recoilEff[1]
            else:
                backoffTime = component_constants.ZERO_FLOAT
                returnTime = component_constants.ZERO_FLOAT
        else:
            backoffTime = _xml.readNonNegativeFloat(xmlCtx, section, 'recoil/backoffTime')
            returnTime = _xml.readNonNegativeFloat(xmlCtx, section, 'recoil/returnTime')
        recoil = gun_components.RecoilEffect(lodDist=shared_readers.readLodDist(xmlCtx, section, 'recoil/lodDist', cache), amplitude=_xml.readNonNegativeFloat(xmlCtx, section, 'recoil/amplitude'), backoffTime=backoffTime, returnTime=returnTime)
        if IS_EDITOR:
            recoil.effectName = effName
        return recoil


def readStunParams(section, xmlCtx=None, useDefaults=False):
    if not section.readBool('hasStun', False):
        return {}
    stunParams = {}
    if section.has_key('stunRadius'):
        stunParams['stunRadius'] = _xml.readPositiveFloat(xmlCtx, section, 'stunRadius')
    if section.has_key('stunDuration'):
        stunParams['stunDuration'] = _xml.readPositiveFloat(xmlCtx, section, 'stunDuration')
    elif useDefaults:
        stunParams['stunDuration'] = stunConfig.get('baseStunDuration', 30)
    if section.has_key('stunFactor'):
        stunFactor = _xml.readPositiveFloat(xmlCtx, section, 'stunFactor')
        if stunFactor > 1:
            _xml.raiseWrongXml(xmlCtx, 'stunFactor', 'stun factor cannot exceed 1')
        stunParams['stunFactor'] = stunFactor
    elif useDefaults:
        stunParams['stunFactor'] = 1.0
    if section.has_key('guaranteedStunDuration'):
        stunParams['guaranteedStunDuration'] = _xml.readFraction(xmlCtx, section, 'guaranteedStunDuration')
    elif useDefaults:
        stunParams['guaranteedStunDuration'] = stunConfig['guaranteedStunDuration']
    if section.has_key('damageDurationCoeff'):
        stunParams['damageDurationCoeff'] = _xml.readFraction(xmlCtx, section, 'damageDurationCoeff')
    elif useDefaults:
        stunParams['damageDurationCoeff'] = stunConfig['damageDurationCoeff']
    if section.has_key('guaranteedStunEffect'):
        stunParams['guaranteedStunEffect'] = _xml.readFraction(xmlCtx, section, 'guaranteedStunEffect')
    elif useDefaults:
        stunParams['guaranteedStunEffect'] = stunConfig['guaranteedStunEffect']
    if section.has_key('damageEffectCoeff'):
        stunParams['damageEffectCoeff'] = _xml.readFraction(xmlCtx, section, 'damageEffectCoeff')
    elif useDefaults:
        stunParams['damageEffectCoeff'] = stunConfig['damageEffectCoeff']
    for key in stunParams:
        pass

    return stunParams
