# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class QuestsWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def onTabSelected(self, tabID):
        """
        :param tabID:
        :return :
        """
        self._printOverrideError('onTabSelected')

    def as_loadViewS(self, flashAlias, pyAlias):
        """
        :param flashAlias:
        :param pyAlias:
        :return :
        """
        return self.flashObject.as_loadView(flashAlias, pyAlias) if self._isDAAPIInited() else None

    def as_selectTabS(self, tabID):
        """
        :param tabID:
        :return :
        """
        return self.flashObject.as_selectTab(tabID) if self._isDAAPIInited() else None

    def as_initS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_init(data) if self._isDAAPIInited() else None
