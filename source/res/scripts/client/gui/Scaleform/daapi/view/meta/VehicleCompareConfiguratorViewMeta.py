# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleCompareConfiguratorViewMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_base import VehicleCompareConfiguratorBaseView

class VehicleCompareConfiguratorViewMeta(VehicleCompareConfiguratorBaseView):

    def removeDevice(self, slotType, slotIndex):
        self._printOverrideError('removeDevice')

    def selectShell(self, shellId, slotIndex):
        self._printOverrideError('selectShell')

    def camoSelected(self, selected):
        self._printOverrideError('camoSelected')

    def showModules(self):
        self._printOverrideError('showModules')

    def toggleTopModules(self, value):
        self._printOverrideError('toggleTopModules')

    def skillSelect(self, skillType, slotIndex, selected):
        self._printOverrideError('skillSelect')

    def changeCrewLevel(self, crewLevelId):
        self._printOverrideError('changeCrewLevel')

    def as_setDevicesDataS(self, data):
        """
        :param data: Represented by Vector.<DeviceSlotVO> (AS)
        """
        return self.flashObject.as_setDevicesData(data) if self._isDAAPIInited() else None

    def as_setAmmoS(self, shells):
        """
        :param shells: Represented by Vector.<ShellButtonVO> (AS)
        """
        return self.flashObject.as_setAmmo(shells) if self._isDAAPIInited() else None

    def as_setSelectedAmmoIndexS(self, index):
        return self.flashObject.as_setSelectedAmmoIndex(index) if self._isDAAPIInited() else None

    def as_setCamoS(self, selected):
        return self.flashObject.as_setCamo(selected) if self._isDAAPIInited() else None

    def as_setSkillsBlockedS(self, value):
        return self.flashObject.as_setSkillsBlocked(value) if self._isDAAPIInited() else None

    def as_setCrewAttentionIconVisibleS(self, value):
        return self.flashObject.as_setCrewAttentionIconVisible(value) if self._isDAAPIInited() else None

    def as_setSkillsS(self, skills):
        """
        :param skills: Represented by Vector.<VehConfSkillVO> (AS)
        """
        return self.flashObject.as_setSkills(skills) if self._isDAAPIInited() else None

    def as_setTopModulesSelectedS(self, value):
        return self.flashObject.as_setTopModulesSelected(value) if self._isDAAPIInited() else None

    def as_setCrewLevelIndexS(self, value):
        return self.flashObject.as_setCrewLevelIndex(value) if self._isDAAPIInited() else None
