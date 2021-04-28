# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AbilityChoicePanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class AbilityChoicePanelMeta(BaseDAAPIComponent):

    def onCardSelect(self, type):
        self._printOverrideError('onCardSelect')

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setExtendedInfoDataS(self, data):
        return self.flashObject.as_setExtendedInfoData(data) if self._isDAAPIInited() else None

    def as_showS(self, state, withAnim=True):
        return self.flashObject.as_show(state, withAnim) if self._isDAAPIInited() else None

    def as_hideS(self, withAnim=True):
        return self.flashObject.as_hide(withAnim) if self._isDAAPIInited() else None

    def as_showHighlightAnimS(self):
        return self.flashObject.as_showHighlightAnim() if self._isDAAPIInited() else None

    def as_hideHighlightAnimS(self):
        return self.flashObject.as_hideHighlightAnim() if self._isDAAPIInited() else None

    def as_showSelectedCardS(self, type):
        return self.flashObject.as_showSelectedCard(type) if self._isDAAPIInited() else None

    def as_deselectAllCardsS(self):
        return self.flashObject.as_deselectAllCards() if self._isDAAPIInited() else None
