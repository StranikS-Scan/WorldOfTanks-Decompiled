# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/armor_inspector_common/models.py
import typing
from dict2model import models

class ArmorInspectorConfigModel(models.Model):
    __slots__ = ('enabled', 'linkButtonURL', 'disabledVehicle')

    def __init__(self, enabled, linkButtonURL, disabledVehicle):
        super(ArmorInspectorConfigModel, self).__init__()
        self.enabled = enabled
        self.linkButtonURL = linkButtonURL
        self.disabledVehicle = disabledVehicle

    def _reprArgs(self):
        return 'enabled={} linkButtonURL={} disabledVehicle={}'.format(self.enabled, self.linkButtonURL, self.disabledVehicle)

    def isDisabledForVehicle(self, vehicleName):
        return vehicleName in self.disabledVehicle
