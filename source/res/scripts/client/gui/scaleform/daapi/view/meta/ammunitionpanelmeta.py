# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AmmunitionPanelMeta.py
from gui.Scaleform.daapi.view.meta.ModulesPanelMeta import ModulesPanelMeta

class AmmunitionPanelMeta(ModulesPanelMeta):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends ModulesPanelMeta
    """

    def showTechnicalMaintenance(self):
        self._printOverrideError('showTechnicalMaintenance')

    def showCustomization(self):
        self._printOverrideError('showCustomization')

    def toRentContinue(self):
        self._printOverrideError('toRentContinue')

    def as_setAmmoS(self, shells, stateWarning):
        """
        :param shells: Represented by Vector.<ShellButtonVO> (AS)
        """
        return self.flashObject.as_setAmmo(shells, stateWarning) if self._isDAAPIInited() else None

    def as_updateVehicleStatusS(self, data):
        """
        :param data: Represented by VehicleMessageVO (AS)
        """
        return self.flashObject.as_updateVehicleStatus(data) if self._isDAAPIInited() else None
