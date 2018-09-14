# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SimpleDialogMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class SimpleDialogMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def onButtonClick(self, buttonId):
        """
        :param buttonId:
        :return :
        """
        self._printOverrideError('onButtonClick')

    def as_setTextS(self, text):
        """
        :param text:
        :return :
        """
        return self.flashObject.as_setText(text) if self._isDAAPIInited() else None

    def as_setTitleS(self, title):
        """
        :param title:
        :return :
        """
        return self.flashObject.as_setTitle(title) if self._isDAAPIInited() else None

    def as_setButtonsS(self, buttonNames):
        """
        :param buttonNames:
        :return :
        """
        return self.flashObject.as_setButtons(buttonNames) if self._isDAAPIInited() else None

    def as_setButtonEnablingS(self, id, isEnabled):
        """
        :param id:
        :param isEnabled:
        :return :
        """
        return self.flashObject.as_setButtonEnabling(id, isEnabled) if self._isDAAPIInited() else None

    def as_setButtonFocusS(self, id):
        """
        :param id:
        :return :
        """
        return self.flashObject.as_setButtonFocus(id) if self._isDAAPIInited() else None
