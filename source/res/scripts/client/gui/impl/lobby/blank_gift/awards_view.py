# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/blank_gift/awards_view.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.common.awards_view_model import AwardsViewModel
from gui.impl.gen.view_models.views.lobby.common.reward_item_model import RewardItemModel

class BlankGiftView(ViewImpl):
    __ICON = 'blanks'

    def __init__(self, itemCD, count):
        settings = ViewSettings(R.views.lobby.common.AwardsView())
        settings.model = AwardsViewModel()
        self.__count = count
        self.__itemCD = itemCD
        super(BlankGiftView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BlankGiftView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BlankGiftView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setBackground(R.images.gui.maps.icons.windows.crewWelcomeScreens.bg.crew22Welcome())
            tx.setTitle(R.strings.awards.multipleAwards.status.gift())
            tx.setButtonTitle(R.strings.lootboxes.specialReward.continueBtn())
            mainRewards = tx.mainRewards
            reward = RewardItemModel()
            itemName = R.strings.recertification_form.userName() if self.__count < 2 else R.strings.recertification_form.multipleUserName()
            reward.setName(backport.text(itemName))
            reward.setIcon(self.__ICON)
            reward.setValue(self.__count)
            reward.setOverlayType('')
            reward.setTooltipContentId(R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent())
            reward.setTooltipId(TOOLTIPS_CONSTANTS.EPIC_BATTLE_RECERTIFICATION_FORM_TOOLTIP)
            mainRewards.addViewModel(reward)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EPIC_BATTLE_RECERTIFICATION_FORM_TOOLTIP, specialArgs=[self.__itemCD]), self.getParentWindow())
            window.load()
            return window


class BlankGiftWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, itemCD, count):
        super(BlankGiftWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BlankGiftView(itemCD, count))
