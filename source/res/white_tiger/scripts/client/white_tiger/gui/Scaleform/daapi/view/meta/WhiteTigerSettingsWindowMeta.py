# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/meta/WhiteTigerSettingsWindowMeta.py
from gui.Scaleform.daapi.view.common.settings import SettingsWindow

class WhiteTigerSettingsWindowMeta(SettingsWindow):

    def as_setIsEventS(self, isInEvent):
        return self.flashObject.as_setIsEvent(isInEvent) if self._isDAAPIInited() else None
