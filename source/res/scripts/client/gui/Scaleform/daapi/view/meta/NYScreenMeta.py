# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NYScreenMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.View import View

class NYScreenMeta(View):

    def onClose(self):
        self._printOverrideError('onClose')

    def onTabButtonClick(self, tabID):
        self._printOverrideError('onTabButtonClick')

    def onAwardsButtonClick(self):
        self._printOverrideError('onAwardsButtonClick')

    def onCraftButtonClick(self):
        self._printOverrideError('onCraftButtonClick')

    def onCollectionButtonClick(self):
        self._printOverrideError('onCollectionButtonClick')

    def onToyFragmentButtonClick(self):
        self._printOverrideError('onToyFragmentButtonClick')

    def moveSpace(self, x, y, delta):
        self._printOverrideError('moveSpace')

    def as_initS(self, nyData):
        """
        :param nyData: Represented by NYScreenDataVO (AS)
        """
        return self.flashObject.as_init(nyData) if self._isDAAPIInited() else None

    def as_enableBtnsS(self, isEnable):
        return self.flashObject.as_enableBtns(isEnable) if self._isDAAPIInited() else None

    def as_showViewByIdS(self, tabID):
        return self.flashObject.as_showViewById(tabID) if self._isDAAPIInited() else None

    def as_updateNYAwardsCounterS(self, counter):
        return self.flashObject.as_updateNYAwardsCounter(counter) if self._isDAAPIInited() else None

    def as_updateNYBoxCounterS(self, counter):
        return self.flashObject.as_updateNYBoxCounter(counter) if self._isDAAPIInited() else None

    def as_updateNYLevelS(self, level):
        return self.flashObject.as_updateNYLevel(level) if self._isDAAPIInited() else None

    def as_updateNYProgressS(self, value):
        return self.flashObject.as_updateNYProgress(value) if self._isDAAPIInited() else None

    def as_updateNYTOYFragmentS(self, value):
        return self.flashObject.as_updateNYTOYFragment(value) if self._isDAAPIInited() else None

    def as_setTabButtonCounterS(self, id, counter):
        return self.flashObject.as_setTabButtonCounter(id, counter) if self._isDAAPIInited() else None

    def as_onBreakStartS(self):
        return self.flashObject.as_onBreakStart() if self._isDAAPIInited() else None

    def as_onBreakS(self):
        return self.flashObject.as_onBreak() if self._isDAAPIInited() else None

    def as_onBreakFailS(self):
        return self.flashObject.as_onBreakFail() if self._isDAAPIInited() else None
