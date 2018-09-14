# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleCustomizationMeta.py
from gui.Scaleform.framework.entities.View import View

class VehicleCustomizationMeta(View):

    def dropCurrentItemInSection(self, section, kind):
        self._printOverrideError('dropCurrentItemInSection')

    def applyCustomization(self, sections):
        self._printOverrideError('applyCustomization')

    def setNewItemId(self, section, itemId, kind, packageIdx):
        self._printOverrideError('setNewItemId')

    def getCurrentItem(self, section):
        self._printOverrideError('getCurrentItem')

    def getItemCost(self, section, itemId, priceIndex):
        self._printOverrideError('getItemCost')

    def closeWindow(self):
        self._printOverrideError('closeWindow')

    def as_onServerResponsesReceivedS(self):
        return self.flashObject.as_onServerResponsesReceived() if self._isDAAPIInited() else None

    def as_onInitS(self, sections):
        return self.flashObject.as_onInit(sections) if self._isDAAPIInited() else None

    def as_setActionsLockedS(self, locked):
        return self.flashObject.as_setActionsLocked(locked) if self._isDAAPIInited() else None

    def as_onChangeSuccessS(self):
        return self.flashObject.as_onChangeSuccess() if self._isDAAPIInited() else None

    def as_onCurrentChangedS(self, section):
        return self.flashObject.as_onCurrentChanged(section) if self._isDAAPIInited() else None

    def as_onDropSuccessS(self):
        return self.flashObject.as_onDropSuccess() if self._isDAAPIInited() else None

    def as_onResetNewItemS(self):
        return self.flashObject.as_onResetNewItem() if self._isDAAPIInited() else None

    def as_setCreditsS(self, credits):
        return self.flashObject.as_setCredits(credits) if self._isDAAPIInited() else None

    def as_setGoldS(self, gold):
        return self.flashObject.as_setGold(gold) if self._isDAAPIInited() else None

    def as_refreshDataS(self):
        return self.flashObject.as_refreshData() if self._isDAAPIInited() else None

    def as_refreshItemsDataS(self):
        return self.flashObject.as_refreshItemsData() if self._isDAAPIInited() else None
