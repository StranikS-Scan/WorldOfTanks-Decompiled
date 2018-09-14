# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SwitchPeripheryWindowMeta.py
from gui.Scaleform.daapi.view.meta.SimpleWindowMeta import SimpleWindowMeta

class SwitchPeripheryWindowMeta(SimpleWindowMeta):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SimpleWindowMeta
    null
    """

    def requestForChange(self, id):
        """
        :param id:
        :return :
        """
        self._printOverrideError('requestForChange')

    def onDropDownOpened(self, opened):
        """
        :param opened:
        :return :
        """
        self._printOverrideError('onDropDownOpened')

    def as_setServerParamsS(self, label, showDropDown):
        """
        :param label:
        :param showDropDown:
        :return :
        """
        return self.flashObject.as_setServerParams(label, showDropDown) if self._isDAAPIInited() else None

    def as_setSelectedIndexS(self, index):
        """
        :param index:
        :return :
        """
        return self.flashObject.as_setSelectedIndex(index) if self._isDAAPIInited() else None

    def as_getServersDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getServersDP() if self._isDAAPIInited() else None
