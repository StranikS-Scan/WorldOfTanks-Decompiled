# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/entry_point.py
import logging
from account_helpers.AccountSettings import LOOT_BOXES_HAS_NEW
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootbox_system.entry_point_view_model import EntryPointViewModel
from gui.impl.lobby.lootbox_system.tooltips.entry_point_tooltip import EntryPointTooltip
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.lootbox_system.common import ViewID, Views
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import ILootBoxSystemController
from skeletons.gui.hangar import ICarouselEventEntry
_logger = logging.getLogger(__name__)
_ENABLED_PRE_QUEUES = (QUEUE_TYPE.RANDOMS, QUEUE_TYPE.WINBACK)

class LootBoxSystemEntryPoint(ViewImpl, ICarouselEventEntry):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self):
        super(LootBoxSystemEntryPoint, self).__init__(ViewSettings(R.views.lobby.lootbox_system.EntryPointView(), ViewFlags.VIEW, EntryPointViewModel()))

    @property
    def viewModel(self):
        return super(LootBoxSystemEntryPoint, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return EntryPointTooltip() if contentID == R.views.lobby.lootbox_system.tooltips.EntryPointTooltip() else super(LootBoxSystemEntryPoint, self).createToolTipContent(event, contentID)

    @staticmethod
    def getIsActive(state):
        lootBoxSystem = LootBoxSystemEntryPoint.__lootBoxes
        if lootBoxSystem.isActive and not lootBoxSystem.getBoxesIDs(lootBoxSystem.eventName):
            _logger.error('There is no boxes with %s type, check LootBox config.', lootBoxSystem.eventName)
            return False
        return lootBoxSystem.isActive and (any((state.isInPreQueue(preQueue) for preQueue in _ENABLED_PRE_QUEUES)) or state.isInUnit(PREBATTLE_TYPE.SQUAD))

    def _onLoading(self, *args, **kwargs):
        super(LootBoxSystemEntryPoint, self)._onLoading(*args, **kwargs)
        self.__fillEventInfo()

    def _getEvents(self):
        return ((self.__lootBoxes.onBoxesCountChanged, self.__updateBoxesCount),
         (self.__lootBoxes.onStatusChanged, self.__onLootBoxesStatusChanged),
         (self.__lootBoxes.onBoxesAvailabilityChanged, self.__onAvailabilityChanged),
         (self.viewModel.onEntryClick, self.__showMain))

    def __fillEventInfo(self):
        with self.viewModel.transaction() as vmTx:
            vmTx.setEventName(self.__lootBoxes.eventName)
            vmTx.setIsEnabled(self.__lootBoxes.isLootBoxesAvailable)
            self.__updateTime(model=vmTx)
            self.__updateBoxesCount(model=vmTx)

    def __onLootBoxesStatusChanged(self):
        self.__fillEventInfo()

    def __onAvailabilityChanged(self):
        self.viewModel.setIsEnabled(self.__lootBoxes.isLootBoxesAvailable)

    @replaceNoneKwargsModel
    def __updateBoxesCount(self, model=None):
        model.setBoxesCount(self.__lootBoxes.getBoxesCount())
        model.setHasNew(self.__lootBoxes.getSetting(LOOT_BOXES_HAS_NEW))

    @replaceNoneKwargsModel
    def __updateTime(self, model=None):
        model.setEventExpireTime(self.__getEventExpireTime())

    def __getEventExpireTime(self):
        _, finish = self.__lootBoxes.getActiveTime()
        return finish - getServerUTCTime()

    def __showMain(self):
        self.__lootBoxes.setSetting(LOOT_BOXES_HAS_NEW, False)
        self.viewModel.setHasNew(False)
        Views.load(ViewID.MAIN)
