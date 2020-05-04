# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MissionDetailsContainerViewMeta.py
from gui.Scaleform.daapi.view.meta.BaseMissionDetailsContainerViewMeta import BaseMissionDetailsContainerViewMeta

class MissionDetailsContainerViewMeta(BaseMissionDetailsContainerViewMeta):

    def onTokenBuyClick(self, tokenId, questId):
        self._printOverrideError('onTokenBuyClick')

    def onToEventClick(self):
        self._printOverrideError('onToEventClick')

    def as_showBackButtonS(self, label, description):
        return self.flashObject.as_showBackButton(label, description) if self._isDAAPIInited() else None

    def as_hideBackButtonS(self):
        return self.flashObject.as_hideBackButton() if self._isDAAPIInited() else None
