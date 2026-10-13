# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/meta/PostmortemPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.postmortem_panel import PostmortemPanel

class PostmortemPanelMeta(PostmortemPanel):

    def as_setHintTitleS(self, value, isShadow=True):
        return self.flashObject.as_setHintTitle(value, isShadow) if self._isDAAPIInited() else None

    def as_setHintDescrS(self, value):
        return self.flashObject.as_setHintDescr(value) if self._isDAAPIInited() else None

    def as_showRespawnIconS(self, value):
        return self.flashObject.as_showRespawnIcon(value) if self._isDAAPIInited() else None

    def as_setCanExitS(self, value):
        return self.flashObject.as_setCanExit(value) if self._isDAAPIInited() else None

    def as_showSpectatorPanelS(self, value):
        return self.flashObject.as_showSpectatorPanel(value) if self._isDAAPIInited() else None
