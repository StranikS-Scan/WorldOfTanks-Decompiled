# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_shop_rewards_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_shop_rewards_view_model import ArmoryYardShopRewardsViewModel

class ArmoryYardShopRewardsView(ViewImpl):
    __slots__ = ('__description', '__icon', '__count', '__itemType', '__closeCallback')

    def __init__(self, layoutID, description, iconPath, count, itemType='', closeCallback=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = ArmoryYardShopRewardsViewModel()
        self.__description = description
        self.__icon = iconPath
        self.__count = count
        self.__itemType = itemType
        self.__closeCallback = closeCallback
        super(ArmoryYardShopRewardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ArmoryYardShopRewardsView, self).getViewModel()

    def onClose(self):
        if self.__closeCallback is not None:
            self.__closeCallback()
        self.destroyWindow()
        return

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardShopRewardsView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            vm.setDescription(self.__description)
            vm.setIcon(self.__icon)
            vm.setCount(self.__count)
            vm.setItemType(self.__itemType)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.onClose),)

    def _finalize(self):
        super(ArmoryYardShopRewardsView, self)._finalize()
        self.__closeCallback = None
        return


class ArmoryYardShopRewardsWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, description, iconPath, count, itemType='', closeCallback=None, parent=None):
        super(ArmoryYardShopRewardsWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_SUB_VIEW, content=ArmoryYardShopRewardsView(R.views.armory_yard.lobby.feature.ArmoryYardShopRewardsView(), description=description, iconPath=iconPath, count=count, itemType=itemType, closeCallback=closeCallback), parent=parent)
