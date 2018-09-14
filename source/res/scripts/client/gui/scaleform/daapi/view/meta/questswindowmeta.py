# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class QuestsWindowMeta(AbstractWindowView):

    def onTabSelected(self, tabID):
        self._printOverrideError('onTabSelected')

    def as_loadViewS(self, flashAlias, pyAlias):
        if self._isDAAPIInited():
            return self.flashObject.as_loadView(flashAlias, pyAlias)

    def as_selectTabS(self, tabID):
        if self._isDAAPIInited():
            return self.flashObject.as_selectTab(tabID)

    def as_initS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_init(data)
