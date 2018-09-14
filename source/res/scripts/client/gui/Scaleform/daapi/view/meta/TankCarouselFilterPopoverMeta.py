# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TankCarouselFilterPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class TankCarouselFilterPopoverMeta(SmartPopOverView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SmartPopOverView
    null
    """

    def changeFilter(self, groupId, itemId):
        """
        :param groupId:
        :param itemId:
        :return :
        """
        self._printOverrideError('changeFilter')

    def setDefaultFilter(self):
        """
        :return :
        """
        self._printOverrideError('setDefaultFilter')

    def as_setInitDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setStateS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setState(data) if self._isDAAPIInited() else None

    def as_enableDefBtnS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_enableDefBtn(value) if self._isDAAPIInited() else None
