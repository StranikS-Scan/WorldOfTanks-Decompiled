# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FreeXPInfoWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FreeXPInfoWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def onSubmitButton(self):
        """
        :return :
        """
        self._printOverrideError('onSubmitButton')

    def onCancelButton(self):
        """
        :return :
        """
        self._printOverrideError('onCancelButton')

    def as_setSubmitLabelS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setSubmitLabel(value) if self._isDAAPIInited() else None

    def as_setTitleS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setTitle(value) if self._isDAAPIInited() else None

    def as_setTextS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setText(value) if self._isDAAPIInited() else None
