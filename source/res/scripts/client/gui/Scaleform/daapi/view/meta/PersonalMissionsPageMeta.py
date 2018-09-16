# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PersonalMissionsPageMeta.py
from gui.Scaleform.framework.entities.View import View

class PersonalMissionsPageMeta(View):

    def onBarClick(self, chainID, operationIdx):
        self._printOverrideError('onBarClick')

    def onSkipTaskClick(self):
        self._printOverrideError('onSkipTaskClick')

    def onBackBtnClick(self):
        self._printOverrideError('onBackBtnClick')

    def closeView(self):
        self._printOverrideError('closeView')

    def onTutorialAcceptBtnClicked(self):
        self._printOverrideError('onTutorialAcceptBtnClicked')

    def showAwards(self):
        self._printOverrideError('showAwards')

    def as_setContentVisibleS(self, value):
        return self.flashObject.as_setContentVisible(value) if self._isDAAPIInited() else None

    def as_initViewS(self, pmType, chainsLen):
        return self.flashObject.as_initView(pmType, chainsLen) if self._isDAAPIInited() else None

    def as_reInitViewS(self, pmType, chainsLen):
        return self.flashObject.as_reInitView(pmType, chainsLen) if self._isDAAPIInited() else None

    def as_setHeaderDataS(self, data):
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None

    def as_updateSideBarDataS(self, data):
        return self.flashObject.as_updateSideBarData(data) if self._isDAAPIInited() else None

    def as_setStatusDataS(self, data):
        return self.flashObject.as_setStatusData(data) if self._isDAAPIInited() else None

    def as_setSelectedBranchIndexS(self, index):
        return self.flashObject.as_setSelectedBranchIndex(index) if self._isDAAPIInited() else None

    def as_showFirstAwardSheetObtainedPopupS(self, useAnim):
        return self.flashObject.as_showFirstAwardSheetObtainedPopup(useAnim) if self._isDAAPIInited() else None

    def as_showFourAwardSheetsObtainedPopupS(self, useAnim, data):
        return self.flashObject.as_showFourAwardSheetsObtainedPopup(useAnim, data) if self._isDAAPIInited() else None

    def as_hideAwardSheetObtainedPopupS(self):
        return self.flashObject.as_hideAwardSheetObtainedPopup() if self._isDAAPIInited() else None

    def as_showAwardsPopoverForTutorS(self):
        return self.flashObject.as_showAwardsPopoverForTutor() if self._isDAAPIInited() else None
