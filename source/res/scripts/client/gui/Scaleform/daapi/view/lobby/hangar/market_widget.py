# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/market_widget.py
from constants import LOOTBOX_TOKEN_PREFIX, Configs
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.lobby.bm2021.market_entry_point import MarketEntrancePointWidget
from gui.Scaleform.daapi.view.meta.MarketEntryPointMeta import MarketEntryPointMeta
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.shared.gui_items.loot_box import BLACK_MARKET_ITEM_TYPE
from helpers import dependency
from skeletons.gui.game_control import IEventItemsController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class MarketWidget(InjectComponentAdaptor, MarketEntryPointMeta):
    __layout = 0
    __itemsCache = dependency.descriptor(IItemsCache)
    __itemsCtrl = dependency.descriptor(IEventItemsController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def updateWidgetLayout(self, value):
        self.__layout = value
        if self._injectView is not None:
            self._injectView.setLayout(self.__layout)
        return

    def _populate(self):
        super(MarketWidget, self)._populate()
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__setVisibility()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        super(MarketWidget, self)._dispose()

    def _makeInjectView(self):
        return MarketEntrancePointWidget()

    def __onTokensUpdate(self, diff):
        for tokenID in diff:
            if tokenID.startswith(LOOTBOX_TOKEN_PREFIX):
                item = self.__itemsCache.items.tokens.getLootBoxByTokenID(tokenID)
                itemType = item.getType() if item else None
                if itemType == BLACK_MARKET_ITEM_TYPE:
                    self.__setVisibility(item)

        return

    def __setVisibility(self, item=None):
        if not item:
            item = self.__itemsCtrl.getOwnedItemsByType(BLACK_MARKET_ITEM_TYPE)
        marketItemVisible = item and item.getInventoryCount() > 0 if item else None
        if marketItemVisible:
            self.as_showWidgetS()
        else:
            self.as_hideWidgetS()
        return

    def __onServerSettingsChanged(self, diff):
        if Configs.LOOT_BOXES_CONFIG.value in diff:
            self.__setVisibility()
