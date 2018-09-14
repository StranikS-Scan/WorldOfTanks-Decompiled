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
        if self._isDAAPIInited():
            return self.flashObject.as_onServerResponsesReceived()

    def as_onInitS(self, sections):
        if self._isDAAPIInited():
            return self.flashObject.as_onInit(sections)

    def as_setActionsLockedS(self, locked):
        if self._isDAAPIInited():
            return self.flashObject.as_setActionsLocked(locked)

    def as_onChangeSuccessS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_onChangeSuccess()

    def as_onCurrentChangedS(self, section):
        if self._isDAAPIInited():
            return self.flashObject.as_onCurrentChanged(section)

    def as_onDropSuccessS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_onDropSuccess()

    def as_onResetNewItemS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_onResetNewItem()

    def as_setCreditsS(self, credits):
        if self._isDAAPIInited():
            return self.flashObject.as_setCredits(credits)

    def as_setGoldS(self, gold):
        if self._isDAAPIInited():
            return self.flashObject.as_setGold(gold)

    def as_refreshDataS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_refreshData()

    def as_refreshItemsDataS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_refreshItemsData()
