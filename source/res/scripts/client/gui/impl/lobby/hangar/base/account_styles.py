# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/base/account_styles.py
from __future__ import absolute_import
import typing
import Event
from gui.impl.lobby.hangar.base.hangar_interfaces import IAccountStyles
from gui.impl.lobby.hangar.presenters.utils import take3DStyles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
from skeletons.gui.customization import ICustomizationService
from helpers import dependency
from skeletons.gui.shared import IItemsCache
UPDATES = (CACHE_SYNC_REASON.INVENTORY_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE)

class AccountStyles(IAccountStyles):
    _customizationService = dependency.descriptor(ICustomizationService)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__styleCriteria = None
        self.onChanged = Event.Event()
        return

    @property
    def critera(self):
        return self.__styleCriteria

    def initialize(self):
        self.__updateCriteria()
        self._itemsCache.onSyncCompleted += self.__onCacheResync

    def destroy(self):
        self.onChanged.clear()
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        self.__styleCriteria = None
        return

    def recalculate(self):
        self.__updateCriteria()
        self.onChanged()

    def __updateCriteria(self):
        self.__styleCriteria = REQ_CRITERIA.VEHICLE.CAN_INSTALL_C11N(GUI_ITEM_TYPE.STYLE, REQ_CRITERIA.CUSTOMIZATION.ON_ACCOUNT, items=take3DStyles(self._customizationService))

    def __onCacheResync(self, reason, diff):
        if reason in UPDATES and GUI_ITEM_TYPE.CUSTOMIZATION in diff:
            self.recalculate()
