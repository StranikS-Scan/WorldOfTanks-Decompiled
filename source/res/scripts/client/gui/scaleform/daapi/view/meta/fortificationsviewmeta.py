# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortificationsViewMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortificationsViewMeta(DAAPIModule):

    def onFortCreateClick(self):
        self._printOverrideError('onFortCreateClick')

    def onDirectionCreateClick(self):
        self._printOverrideError('onDirectionCreateClick')

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def as_loadViewS(self, flashAlias, pyAlias):
        if self._isDAAPIInited():
            return self.flashObject.as_loadView(flashAlias, pyAlias)

    def as_setCommonDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setCommonData(data)
