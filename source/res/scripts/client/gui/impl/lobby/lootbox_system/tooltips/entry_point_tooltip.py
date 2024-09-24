# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/tooltips/entry_point_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootbox_system.tooltips.entry_point_tooltip_view_model import EntryPointTooltipViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import ILootBoxSystemController

class EntryPointTooltip(ViewImpl):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.lootbox_system.tooltips.EntryPointTooltip())
        settings.model = EntryPointTooltipViewModel()
        super(EntryPointTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPointTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EntryPointTooltip, self)._onLoading(*args, **kwargs)
        self.__updateState()

    def _getEvents(self):
        return ((self.__lootBoxes.onStatusChanged, self.__onLootBoxesStatusChanged),)

    def __onLootBoxesStatusChanged(self):
        self.__updateState()

    def __updateState(self):
        with self.viewModel.transaction() as vmTx:
            vmTx.setEventName(self.__lootBoxes.eventName)
            vmTx.setIsEnabled(self.__lootBoxes.isLootBoxesAvailable)
            vmTx.setEventExpireTime(self.__getEventExpireTime())

    def __getEventExpireTime(self):
        _, finish = self.__lootBoxes.getActiveTime()
        return finish - getServerUTCTime()
