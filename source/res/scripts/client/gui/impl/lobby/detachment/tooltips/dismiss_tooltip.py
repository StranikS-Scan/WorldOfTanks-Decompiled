# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/dismiss_tooltip.py
from crew2 import settings_globals
from frameworks.wulf.view.view import ViewSettings
from gui.impl.auxiliary.detachment_helper import getDetachmentDismissState
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.dismiss_states import DismissStates
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.dismiss_tooltip_model import DismissTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers.dependency import descriptor
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.loggers import DynamicGroupTooltipLogger

class DismissTooltip(ViewImpl):
    __detachmentCache = descriptor(IDetachmentCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    uiLogger = DynamicGroupTooltipLogger()
    __slots__ = ('__detachment',)

    def __init__(self, detachmentID=None):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.DismissTooltip())
        settings.model = DismissTooltipModel()
        self.__detachment = self.__detachmentCache.getDetachment(detachmentID)
        super(DismissTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DismissTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        dismissState = getDetachmentDismissState(self.__detachment)
        with self.viewModel.transaction() as model:
            model.setState(dismissState)
            if dismissState == DismissStates.SELL_LIMIT_REACHED:
                sellLimit = self.__lobbyContext.getServerSettings().getDetachmentSellsDailyLimit()
                curSellCount = max(sellLimit - self.__itemsCache.items.stats.detachmentSellsLeft, 0)
                detLevel = self._getTrashLevel()
                model.setSellLimit(sellLimit)
                model.setCurSellCount(curSellCount)
                model.setDetLevel(detLevel)

    def _initialize(self, *args, **kwargs):
        super(DismissTooltip, self)._initialize()
        self.uiLogger.tooltipOpened()

    def _finalize(self):
        self.uiLogger.tooltipClosed(self.__class__.__name__)
        self.uiLogger.reset()
        super(DismissTooltip, self)._finalize()

    def _getTrashLevel(self):
        progression = self.__detachment.getDescriptor().progression
        return progression.getRawLevelByXP(settings_globals.g_detachmentSettings.garbageThreshold)
