# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NYScreenCraftMeta.py
from gui.Scaleform.framework.entities.View import View

class NYScreenCraftMeta(View):

    def onClose(self):
        self._printOverrideError('onClose')

    def onCraft(self):
        self._printOverrideError('onCraft')

    def onGetShards(self):
        self._printOverrideError('onGetShards')

    def onFilterChange(self, type, index):
        self._printOverrideError('onFilterChange')

    def onToyCreatePlaySound(self, level):
        self._printOverrideError('onToyCreatePlaySound')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by NYCraftInitVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setCraftButtonEnableS(self, value):
        return self.flashObject.as_setCraftButtonEnable(value) if self._isDAAPIInited() else None

    def as_setShardsButtonShineS(self, value):
        return self.flashObject.as_setShardsButtonShine(value) if self._isDAAPIInited() else None

    def as_updateShardsS(self, value):
        return self.flashObject.as_updateShards(value) if self._isDAAPIInited() else None

    def as_setPriceS(self, value, enoughMoney):
        return self.flashObject.as_setPrice(value, enoughMoney) if self._isDAAPIInited() else None

    def as_setCraftS(self, data):
        """
        :param data: Represented by NYToyFilterItemVo (AS)
        """
        return self.flashObject.as_setCraft(data) if self._isDAAPIInited() else None
