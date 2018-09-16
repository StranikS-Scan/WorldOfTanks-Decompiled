# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NYScreenBreakMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.View import View

class NYScreenBreakMeta(View):

    def onClose(self):
        self._printOverrideError('onClose')

    def onBack(self):
        self._printOverrideError('onBack')

    def onBackClick(self):
        self._printOverrideError('onBackClick')

    def onCraftClick(self):
        self._printOverrideError('onCraftClick')

    def onBreak(self):
        self._printOverrideError('onBreak')

    def resetFilters(self):
        self._printOverrideError('resetFilters')

    def onToySelectChange(self, toyId, index, isSelected):
        self._printOverrideError('onToySelectChange')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by NYScreenBreakVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setBreakToyFragmentS(self, value):
        return self.flashObject.as_setBreakToyFragment(value) if self._isDAAPIInited() else None

    def as_setLackToyFragmentS(self, value):
        return self.flashObject.as_setLackToyFragment(value) if self._isDAAPIInited() else None

    def as_setBalanceToyFragmentS(self, value):
        return self.flashObject.as_setBalanceToyFragment(value) if self._isDAAPIInited() else None

    def as_setLackToyFragmentTypeS(self, value):
        return self.flashObject.as_setLackToyFragmentType(value) if self._isDAAPIInited() else None

    def as_setBreakButtonLabelS(self, value):
        return self.flashObject.as_setBreakButtonLabel(value) if self._isDAAPIInited() else None

    def as_setToysS(self, data):
        """
        :param data: Represented by DataProvider.<NYToyFilterItemVo> (AS)
        """
        return self.flashObject.as_setToys(data) if self._isDAAPIInited() else None

    def as_setBreakToysIndexS(self, data):
        """
        :param data: Represented by Vector.<int> (AS)
        """
        return self.flashObject.as_setBreakToysIndex(data) if self._isDAAPIInited() else None

    def as_setToysAmountStrS(self, value, isFilterActive):
        return self.flashObject.as_setToysAmountStr(value, isFilterActive) if self._isDAAPIInited() else None

    def as_onToysBreakFailedS(self):
        return self.flashObject.as_onToysBreakFailed() if self._isDAAPIInited() else None

    def as_onToyBreakStartS(self):
        return self.flashObject.as_onToyBreakStart() if self._isDAAPIInited() else None
