# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleCustomizationMeta.py
from gui.Scaleform.framework.entities.View import View

class VehicleCustomizationMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    null
    """

    def dropCurrentItemInSection(self, section, kind):
        """
        :param section:
        :param kind:
        :return :
        """
        self._printOverrideError('dropCurrentItemInSection')

    def applyCustomization(self, sections):
        """
        :param sections:
        :return :
        """
        self._printOverrideError('applyCustomization')

    def setNewItemId(self, section, itemId, kind, packageIdx):
        """
        :param section:
        :param itemId:
        :param kind:
        :param packageIdx:
        :return :
        """
        self._printOverrideError('setNewItemId')

    def getCurrentItem(self, section):
        """
        :param section:
        :return Object:
        """
        self._printOverrideError('getCurrentItem')

    def getItemCost(self, section, itemId, priceIndex):
        """
        :param section:
        :param itemId:
        :param priceIndex:
        :return Object:
        """
        self._printOverrideError('getItemCost')

    def closeWindow(self):
        """
        :return :
        """
        self._printOverrideError('closeWindow')

    def as_onServerResponsesReceivedS(self):
        """
        :return :
        """
        return self.flashObject.as_onServerResponsesReceived() if self._isDAAPIInited() else None

    def as_onInitS(self, sections):
        """
        :param sections:
        :return :
        """
        return self.flashObject.as_onInit(sections) if self._isDAAPIInited() else None

    def as_setActionsLockedS(self, locked):
        """
        :param locked:
        :return :
        """
        return self.flashObject.as_setActionsLocked(locked) if self._isDAAPIInited() else None

    def as_onChangeSuccessS(self):
        """
        :return :
        """
        return self.flashObject.as_onChangeSuccess() if self._isDAAPIInited() else None

    def as_onCurrentChangedS(self, section):
        """
        :param section:
        :return :
        """
        return self.flashObject.as_onCurrentChanged(section) if self._isDAAPIInited() else None

    def as_onDropSuccessS(self):
        """
        :return :
        """
        return self.flashObject.as_onDropSuccess() if self._isDAAPIInited() else None

    def as_onResetNewItemS(self):
        """
        :return :
        """
        return self.flashObject.as_onResetNewItem() if self._isDAAPIInited() else None

    def as_setCreditsS(self, credits):
        """
        :param credits:
        :return :
        """
        return self.flashObject.as_setCredits(credits) if self._isDAAPIInited() else None

    def as_setGoldS(self, gold):
        """
        :param gold:
        :return :
        """
        return self.flashObject.as_setGold(gold) if self._isDAAPIInited() else None

    def as_refreshDataS(self):
        """
        :return :
        """
        return self.flashObject.as_refreshData() if self._isDAAPIInited() else None

    def as_refreshItemsDataS(self):
        """
        :return :
        """
        return self.flashObject.as_refreshItemsData() if self._isDAAPIInited() else None
