# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WaitingViewMeta.py
from gui.Scaleform.framework.entities.View import View

class WaitingViewMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    null
    """

    def showS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.show(data) if self._isDAAPIInited() else None

    def hideS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.hide(data) if self._isDAAPIInited() else None
