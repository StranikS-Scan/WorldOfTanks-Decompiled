# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicBattlesOfflineViewMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class EpicBattlesOfflineViewMeta(WrapperViewMeta):

    def onCloseBtnClick(self):
        self._printOverrideError('onCloseBtnClick')

    def onAboutButtonClick(self):
        self._printOverrideError('onAboutButtonClick')

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
