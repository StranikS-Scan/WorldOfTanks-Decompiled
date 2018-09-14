# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AwardWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class AwardWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def onOKClick(self):
        self._printOverrideError('onOKClick')

    def onTakeNextClick(self):
        self._printOverrideError('onTakeNextClick')

    def onCloseClick(self):
        self._printOverrideError('onCloseClick')

    def as_setDataS(self, data):
        """
        :param data: Represented by AwardWindowVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
