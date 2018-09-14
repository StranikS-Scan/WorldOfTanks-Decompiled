# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ClanProfileTableStatisticsViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ClanProfileTableStatisticsViewMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setAdditionalTextS(self, visible, text):
        """
        :param visible:
        :param text:
        :return :
        """
        return self.flashObject.as_setAdditionalText(visible, text) if self._isDAAPIInited() else None

    def as_getDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getDP() if self._isDAAPIInited() else None
