# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortNotCommanderFirstEnterWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortNotCommanderFirstEnterWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def as_setTitleS(self, value):
        return self.flashObject.as_setTitle(value) if self._isDAAPIInited() else None

    def as_setTextS(self, value):
        return self.flashObject.as_setText(value) if self._isDAAPIInited() else None

    def as_setWindowTitleS(self, value):
        return self.flashObject.as_setWindowTitle(value) if self._isDAAPIInited() else None

    def as_setButtonLblS(self, value):
        return self.flashObject.as_setButtonLbl(value) if self._isDAAPIInited() else None
