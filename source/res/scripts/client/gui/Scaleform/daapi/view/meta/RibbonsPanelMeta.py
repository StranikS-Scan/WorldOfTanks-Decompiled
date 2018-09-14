# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RibbonsPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class RibbonsPanelMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def onShow(self):
        self._printOverrideError('onShow')

    def onChange(self):
        self._printOverrideError('onChange')

    def onHide(self, ribbonType):
        self._printOverrideError('onHide')

    def as_setupS(self, items, isExtendedAnim, isVisible, isWithRibbonName, isWithVehName):
        return self.flashObject.as_setup(items, isExtendedAnim, isVisible, isWithRibbonName, isWithVehName) if self._isDAAPIInited() else None

    def as_addBattleEfficiencyEventS(self, ribbonType, leftFieldStr, vehName, vehType, rightFieldStr):
        return self.flashObject.as_addBattleEfficiencyEvent(ribbonType, leftFieldStr, vehName, vehType, rightFieldStr) if self._isDAAPIInited() else None

    def as_setSettingsS(self, isVisible, isExtendedAnim, isWithRibbonName, isWithVehName):
        return self.flashObject.as_setSettings(isVisible, isExtendedAnim, isWithRibbonName, isWithVehName) if self._isDAAPIInited() else None
