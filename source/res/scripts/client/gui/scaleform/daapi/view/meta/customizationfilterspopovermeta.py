# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationFiltersPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class CustomizationFiltersPopoverMeta(SmartPopOverView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SmartPopOverView
    """

    def changeFilter(self, groupId, itemId):
        self._printOverrideError('changeFilter')

    def setDefaultFilter(self):
        self._printOverrideError('setDefaultFilter')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by FiltersPopoverVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setStateS(self, data):
        """
        :param data: Represented by FiltersStateVO (AS)
        """
        return self.flashObject.as_setState(data) if self._isDAAPIInited() else None

    def as_enableDefBtnS(self, value):
        return self.flashObject.as_enableDefBtn(value) if self._isDAAPIInited() else None
