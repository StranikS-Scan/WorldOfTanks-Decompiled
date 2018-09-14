# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CursorMeta.py
from gui.Scaleform.framework.entities.View import View

class CursorMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    null
    """

    def as_setCursorS(self, cursor):
        """
        :param cursor:
        :return :
        """
        return self.flashObject.as_setCursor(cursor) if self._isDAAPIInited() else None

    def as_showCursorS(self):
        """
        :return :
        """
        return self.flashObject.as_showCursor() if self._isDAAPIInited() else None

    def as_hideCursorS(self):
        """
        :return :
        """
        return self.flashObject.as_hideCursor() if self._isDAAPIInited() else None
