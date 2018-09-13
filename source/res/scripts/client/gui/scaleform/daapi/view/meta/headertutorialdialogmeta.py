# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HeaderTutorialDialogMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class HeaderTutorialDialogMeta(DAAPIModule):

    def onButtonClick(self, buttonID, isCbSelected):
        self._printOverrideError('onButtonClick')

    def as_setSettingsS(self, settings):
        if self._isDAAPIInited():
            return self.flashObject.as_setSettings(settings)
