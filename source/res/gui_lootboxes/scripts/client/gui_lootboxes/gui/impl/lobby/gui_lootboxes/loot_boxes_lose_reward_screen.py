# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/loot_boxes_lose_reward_screen.py
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.loot_boxes_lose_reward_screen_model import LootBoxesLoseRewardScreenModel
from gui_lootboxes.gui.impl.lobby.gui_lootboxes import gui_helpers
from constants import LOOTBOX_KEY_PREFIX
from frameworks.wulf import WindowFlags, WindowLayer, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IGuiLootBoxesController

class LootBoxesLoseRewardScreen(ViewImpl):
    __slots__ = ('__rewards', '__lootbox', '__clientData', '__key')
    __GUILootboxes = dependency.descriptor(IGuiLootBoxesController)

    def __init__(self, layoutID, rewards, clientData, lootbox):
        settings = ViewSettings(layoutID)
        settings.model = LootBoxesLoseRewardScreenModel()
        self.__rewards = rewards
        self.__lootbox = lootbox
        self.__clientData = clientData or {}
        self.__key = None
        if clientData:
            self.__key = self.__GUILootboxes.getKeyByID(first(clientData.get('usedKeys', {}).keys()))
        for rewardDict in self.__rewards:
            for token, value in rewardDict.get('tokens', {}).items():
                if token.startswith(LOOTBOX_KEY_PREFIX) and value.get('count', 0) == 0:
                    rewardDict['tokens'].pop(token)

        super(LootBoxesLoseRewardScreen, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(LootBoxesLoseRewardScreen, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onRepeatOpen, self.__onRepeatOpen))

    def show(self):
        self.getWindow().show()

    def _onLoading(self, *args, **kwargs):
        super(LootBoxesLoseRewardScreen, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            self.__fillLootboxKeyModel(vm)

    def __fillLootboxKeyModel(self, vm):
        vm.setLootboxName(self.__lootbox.getUserName())
        vm.setLootboxNameKey(self.__lootbox.getUserNameKey())
        vm.setLootboxID(self.__lootbox.getID())
        if self.__key:
            gui_helpers.fillKeyModel(vm.lootboxKey, self.__key)

    def __onClose(self):
        self.destroyWindow()

    def __onRepeatOpen(self, args=None):
        gui_helpers.repeatOpen(args)
        self.destroyWindow()


class LootBoxesLoseRewardScreenWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, lootBox=None, rewards=None, clientData=None, parent=None):
        super(LootBoxesLoseRewardScreenWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=LootBoxesLoseRewardScreen(R.views.gui_lootboxes.lobby.gui_lootboxes.LootBoxesLoseRewardScreen(), rewards=rewards, lootbox=lootBox, clientData=clientData), layer=WindowLayer.OVERLAY, parent=parent)
