# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/lootbox_entry_point_presenter.py
from __future__ import absolute_import
import logging
from account_helpers.AccountSettings import LOOT_BOXES_HAS_NEW
from constants import IS_LOOT_BOXES_ENABLED
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootbox_system.entry_point_view_model import EntryPointViewModel
from gui.impl.lobby.lootbox_system.base.tooltips.entry_point_tooltip import EntryPointTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.lootbox_system.base.common import Views, ViewID
from helpers import dependency
from helpers.server_settings import LOOTBOX_SYSTEM_CONFIG
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import ILootBoxSystemController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class LootboxEntryPointPresenter(ViewComponent[EntryPointViewModel]):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(LootboxEntryPointPresenter, self).__init__(model=EntryPointViewModel, enabled=self.__getEnabled())

    def prepare(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__lootBoxes.onBoxesAvailabilityChanged += self.__onAvailabilityChanged
        self.__lootBoxes.onStatusChanged += self.__onLootBoxesStatusChanged

    @property
    def viewModel(self):
        return super(LootboxEntryPointPresenter, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return EntryPointTooltip(self.__lootBoxes.mainEntryPoint) if contentID == R.views.mono.lootbox.tooltips.entry_point() else super(LootboxEntryPointPresenter, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(LootboxEntryPointPresenter, self)._onLoading(*args, **kwargs)
        self.__fillEventInfo()

    def _finalize(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__lootBoxes.onBoxesAvailabilityChanged -= self.__onAvailabilityChanged
        self.__lootBoxes.onStatusChanged -= self.__onLootBoxesStatusChanged
        super(LootboxEntryPointPresenter, self)._finalize()

    def _getEvents(self):
        return ((self.__lootBoxes.onBoxesCountChanged, self.__onBoxesCountChanged), (self.__lootBoxes.onBoxesInfoUpdated, self.__fillEventInfo), (self.viewModel.onEntryClick, self.__showMain))

    def __onServerSettingsChanged(self, diff):
        isEnabled = diff.get(IS_LOOT_BOXES_ENABLED, False)
        wasEnabled = self.isEnabled()
        if isEnabled != wasEnabled or any((name in diff for name in (LOOTBOX_SYSTEM_CONFIG, 'lootBoxes_config', 'lootboxes_tooltip_config'))):
            self.setEnabled(self.__getEnabled())

    def __getEnabled(self):
        lootboxesActive = self.__lootBoxes.isActive(self.__lootBoxes.mainEntryPoint)
        if lootboxesActive and not self.__lootBoxes.getActiveBoxes(self.__lootBoxes.mainEntryPoint):
            _logger.error('There is no boxes with %s type, check LootBox config.', self.__lootBoxes.mainEntryPoint)
            return False
        return lootboxesActive

    def __fillEventInfo(self):
        with self.viewModel.transaction() as model:
            model.setEventName(self.__lootBoxes.mainEntryPoint)
            model.setIsEnabled(self.__lootBoxes.isLootBoxesAvailable)
            self.__updateTime(model=model)
            self.__updateBoxesCount(model=model)

    def __onBoxesCountChanged(self):
        self.__updateBoxesCount(model=self.viewModel)

    def __onLootBoxesStatusChanged(self):
        self.setEnabled(self.__getEnabled())
        self.__fillEventInfo()

    def __onAvailabilityChanged(self):
        self.setEnabled(self.__getEnabled())
        self.viewModel.setIsEnabled(self.__lootBoxes.isLootBoxesAvailable)

    def __updateBoxesCount(self, model=None):
        model.setBoxesCount(self.__lootBoxes.getBoxesCount(self.__lootBoxes.mainEntryPoint))
        model.setHasNew(self.__lootBoxes.getSetting(self.__lootBoxes.mainEntryPoint, LOOT_BOXES_HAS_NEW))

    def __updateTime(self, model=None):
        model.setEventExpireTime(self.__getEventExpireTime())

    def __getEventExpireTime(self):
        _, finish = self.__lootBoxes.getActiveTime(self.__lootBoxes.mainEntryPoint)
        return finish - getServerUTCTime()

    def __showMain(self):
        self.__lootBoxes.setSetting(self.__lootBoxes.mainEntryPoint, LOOT_BOXES_HAS_NEW, False)
        self.viewModel.setHasNew(False)
        Views.load(ViewID.MAIN, eventName=self.__lootBoxes.mainEntryPoint)
