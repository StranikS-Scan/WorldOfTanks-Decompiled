# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StoreComponentMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StoreComponentMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def requestTableData(self, nation, type, filter):
        """
        :param nation:
        :param type:
        :param filter:
        :return :
        """
        self._printOverrideError('requestTableData')

    def requestFilterData(self, filterType):
        """
        :param filterType:
        :return :
        """
        self._printOverrideError('requestFilterData')

    def onCloseButtonClick(self):
        """
        :return :
        """
        self._printOverrideError('onCloseButtonClick')

    def onShowInfo(self, data):
        """
        :param data:
        :return :
        """
        self._printOverrideError('onShowInfo')

    def getName(self):
        """
        :return String:
        """
        self._printOverrideError('getName')

    def as_setNationsS(self, nations):
        """
        :param nations:
        :return :
        """
        return self.flashObject.as_setNations(nations) if self._isDAAPIInited() else None

    def as_completeInitS(self):
        """
        :return :
        """
        return self.flashObject.as_completeInit() if self._isDAAPIInited() else None

    def as_updateS(self):
        """
        :return :
        """
        return self.flashObject.as_update() if self._isDAAPIInited() else None

    def as_setFilterTypeS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setFilterType(data) if self._isDAAPIInited() else None

    def as_setSubFilterS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setSubFilter(data) if self._isDAAPIInited() else None

    def as_setFilterOptionsS(self, attrs):
        """
        :param attrs:
        :return :
        """
        return self.flashObject.as_setFilterOptions(attrs) if self._isDAAPIInited() else None
