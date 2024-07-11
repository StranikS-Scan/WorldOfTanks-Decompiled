# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/tooltips/lootbox_key_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.lootbox_key_tooltip_model import LootboxKeyTooltipModel
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class LootboxKeyTooltip(ViewImpl):
    __slots__ = ('__key', '__isActionTooltip', '__isShowCount')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, key, isActionTooltip=False, isShowCount=True):
        settings = ViewSettings(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxKeyTooltip())
        settings.model = LootboxKeyTooltipModel()
        super(LootboxKeyTooltip, self).__init__(settings)
        self.__key = key
        self.__isActionTooltip = isActionTooltip
        self.__isShowCount = isShowCount

    @property
    def viewModel(self):
        return super(LootboxKeyTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(LootboxKeyTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            self.__fillmodel(vm)

    def __fillmodel(self, vm):
        boxes = self.__itemsCache.items.tokens.getLootBoxes().itervalues()
        lootboxNames = self.viewModel.getLootboxNames()
        for box in boxes:
            if self.__key.keyID in box.getUnlockKeyIDs():
                lootboxNames.addString(box.getUserNameKey())

        lootboxNames.invalidate()
        vm.setIsActionTooltip(self.__isActionTooltip)
        vm.setIsShowCount(self.__isShowCount)
        vm.lootboxKey.setKeyID(self.__key.keyID)
        vm.lootboxKey.setCount(self.__key.count)
        vm.lootboxKey.keyType.setValue(self.__key.keyType)
        vm.lootboxKey.setIconName(self.__key.iconName)
        vm.lootboxKey.setUserName(self.__key.userName)
        vm.lootboxKey.setOpenProbability(self.__key.openProbability)
