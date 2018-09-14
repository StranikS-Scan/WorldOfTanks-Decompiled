# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SimpleDialogMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class SimpleDialogMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def onButtonClick(self, buttonId):
        self._printOverrideError('onButtonClick')

    def as_setTextS(self, text):
        return self.flashObject.as_setText(text) if self._isDAAPIInited() else None

    def as_setTitleS(self, title):
        return self.flashObject.as_setTitle(title) if self._isDAAPIInited() else None

    def as_setButtonsS(self, buttonNames):
        return self.flashObject.as_setButtons(buttonNames) if self._isDAAPIInited() else None

    def as_setButtonEnablingS(self, id, isEnabled):
        return self.flashObject.as_setButtonEnabling(id, isEnabled) if self._isDAAPIInited() else None

    def as_setButtonFocusS(self, id):
        return self.flashObject.as_setButtonFocus(id) if self._isDAAPIInited() else None
