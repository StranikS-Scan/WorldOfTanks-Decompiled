# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ClanInvitesViewWithTableMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ClanInvitesViewWithTableMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def showMore(self):
        """
        :return :
        """
        self._printOverrideError('showMore')

    def refreshTable(self):
        """
        :return :
        """
        self._printOverrideError('refreshTable')

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_getTableDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getTableDP() if self._isDAAPIInited() else None

    def as_updateDefaultSortFieldS(self, defaultSortField, defaultSortDirection):
        """
        :param defaultSortField:
        :param defaultSortDirection:
        :return :
        """
        return self.flashObject.as_updateDefaultSortField(defaultSortField, defaultSortDirection) if self._isDAAPIInited() else None

    def as_showDummyS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_showDummy(data) if self._isDAAPIInited() else None

    def as_hideDummyS(self):
        """
        :return :
        """
        return self.flashObject.as_hideDummy() if self._isDAAPIInited() else None

    def as_updateButtonRefreshStateS(self, enabled, tooltip):
        """
        :param enabled:
        :param tooltip:
        :return :
        """
        return self.flashObject.as_updateButtonRefreshState(enabled, tooltip) if self._isDAAPIInited() else None
