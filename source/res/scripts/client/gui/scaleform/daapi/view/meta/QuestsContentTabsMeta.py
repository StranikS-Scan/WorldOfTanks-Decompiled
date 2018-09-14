# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsContentTabsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class QuestsContentTabsMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def onSelectTab(self, id):
        """
        :param id:
        :return :
        """
        self._printOverrideError('onSelectTab')

    def as_selectTabS(self, index):
        """
        :param index:
        :return :
        """
        return self.flashObject.as_selectTab(index) if self._isDAAPIInited() else None

    def as_setTabsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setTabs(data) if self._isDAAPIInited() else None
