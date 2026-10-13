# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/configs/hw_upgrades_config.py
from __future__ import absolute_import
import os
import typing
import ResMgr
import section2dict
from dict2model import models, schemas, fields
from soft_exception import SoftException
_UPGRADES_CONFIG_PATH = os.path.join('halloween', 'gui/halloween_upgrades_config.xml')
_DEFAULT_VARIANT = 'DEFAULT'

class UpgradeParamModel(models.Model):
    __slots__ = ('name', 'value')

    def __init__(self, name, value=''):
        super(UpgradeParamModel, self).__init__()
        self.name = name
        self.value = value


upgradeParamSchema = schemas.Schema[UpgradeParamModel](fields={'name': fields.String(required=True),
 'value': fields.String(required=False)}, modelClass=UpgradeParamModel)

class UpgradeVariantModel(models.Model):
    __slots__ = ('param', 'vehicle')

    def __init__(self, param, vehicle=None):
        super(UpgradeVariantModel, self).__init__()
        self.param = {p.name:p.value for p in param}
        self.vehicle = vehicle or _DEFAULT_VARIANT


upgradeVariantSchema = schemas.Schema[UpgradeVariantModel](fields={'param': fields.UniCapList(fieldOrSchema=upgradeParamSchema, required=True),
 'vehicle': fields.String(required=False)}, modelClass=UpgradeVariantModel)

class UpgradeModel(models.Model):
    __slots__ = ('name', 'variant')

    def __init__(self, name, variant=None):
        super(UpgradeModel, self).__init__()
        self.name = name
        if not variant:
            variant = [UpgradeVariantModel([])]
        self.variant = {v.vehicle:v for v in variant}

    def getVehicleConfig(self, vehicleName):
        return self.variant.get(vehicleName) or self.variant[_DEFAULT_VARIANT]

    def getDefaultConfig(self):
        return self.variant[_DEFAULT_VARIANT]


upgradeSchema = schemas.Schema[UpgradeModel](fields={'name': fields.String(required=True),
 'variant': fields.UniCapList(fieldOrSchema=upgradeVariantSchema, required=False)}, modelClass=UpgradeModel)

class UpgradesConfigModel(models.Model):
    __slots__ = ('upgrade',)

    def __init__(self, upgrade):
        super(UpgradesConfigModel, self).__init__()
        self.upgrade = {k.name:k for k in upgrade}


upgradesConfigSchema = schemas.Schema[UpgradesConfigModel](fields={'upgrade': fields.UniCapList(fieldOrSchema=upgradeSchema)}, modelClass=UpgradesConfigModel)
_g_upgradesConfig = None

def initialize():
    global _g_upgradesConfig
    root = ResMgr.openSection(_UPGRADES_CONFIG_PATH)
    rawData = section2dict.parse(root)
    _g_upgradesConfig = upgradesConfigSchema.deserialize(rawData, silent=False) or UpgradesConfigModel([])


def getConfig():
    if _g_upgradesConfig is None:
        raise SoftException('Halloween upgrades config must be initialized before using it.')
    return _g_upgradesConfig
