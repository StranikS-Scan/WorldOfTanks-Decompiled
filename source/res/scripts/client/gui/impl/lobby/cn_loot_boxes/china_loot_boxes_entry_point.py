# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/cn_loot_boxes/china_loot_boxes_entry_point.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import LOOT_BOXES_VIEWED_COUNT
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.china_loot_boxes_entry_point_model import ChinaLootBoxesEntryPointModel
from gui.impl.lobby.cn_loot_boxes.tooltips.china_loot_boxes_entry_point_tooltip_view import ChinaLootBoxesEntryPointTooltipView
from gui.impl.lobby.cn_loot_boxes.china_loot_boxes_popover import ChinaLootBoxesPopover
from gui.impl.pub import ViewImpl
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from helpers.time_utils import ONE_DAY, getServerUTCTime
from skeletons.gui.game_control import ICNLootBoxesController

class ChinaLootBoxesEntryPointWidget(ViewImpl):
    __cnLootBoxes = dependency.descriptor(ICNLootBoxesController)

    def __init__(self):
        super(ChinaLootBoxesEntryPointWidget, self).__init__(ViewSettings(R.views.lobby.cn_loot_boxes.ChinaLootBoxEntryPointView(), ViewFlags.COMPONENT, ChinaLootBoxesEntryPointModel()))
        self.__timerNotifier = SimpleNotifier(self.__getTimeToTimerUpdate, self.__updateTime)

    @property
    def viewModel(self):
        return super(ChinaLootBoxesEntryPointWidget, self).getViewModel()

    def createPopOverContent(self, event):
        return ChinaLootBoxesPopover()

    def createToolTipContent(self, event, contentID):
        return ChinaLootBoxesEntryPointTooltipView() if contentID == R.views.lobby.cn_loot_boxes.tooltips.ChinaLootBoxesEntryPointTooltipView() else None

    def _onLoading(self, *args, **kwargs):
        super(ChinaLootBoxesEntryPointWidget, self)._onLoading(*args, **kwargs)
        self.__updateBoxesCount(self.__cnLootBoxes.getBoxesCount())
        self.__updateTime()

    def _finalize(self):
        self.__timerNotifier.stopNotification()
        super(ChinaLootBoxesEntryPointWidget, self)._finalize()

    def _getEvents(self):
        return ((self.__cnLootBoxes.onBoxesCountChange, self.__updateBoxesCount), (self.__cnLootBoxes.onStatusChange, self.__updateTime), (self.viewModel.onWidgetClick, self.__onWidgetClick))

    def __onWidgetClick(self):
        self.viewModel.setHasNew(False)
        AccountSettings.setSettings(LOOT_BOXES_VIEWED_COUNT, self.__cnLootBoxes.getBoxesCount())

    def __updateBoxesCount(self, count, *_):
        lastViewed = AccountSettings.getSettings(LOOT_BOXES_VIEWED_COUNT)
        with self.viewModel.transaction() as model:
            model.setBoxesCount(count)
            model.setHasNew(count > lastViewed)

    def __getTimeToTimerUpdate(self):
        return max(self.__getEventExpireTime() - ONE_DAY, 0)

    def __updateTime(self):
        result = self.__getEventExpireTime()
        self.viewModel.setTime(result if result < ONE_DAY else 0)
        self.__timerNotifier.startNotification()

    def __getEventExpireTime(self):
        _, finish = self.__cnLootBoxes.getEventActiveTime()
        return finish - getServerUTCTime()
