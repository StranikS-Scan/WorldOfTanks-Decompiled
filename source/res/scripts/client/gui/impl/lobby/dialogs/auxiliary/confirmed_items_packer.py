# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/auxiliary/confirmed_items_packer.py
import typing
from gui.impl.lobby.dialogs.auxiliary.confirmed_item import ConfirmedItem
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.fitting_item import FittingItem
    from typing import Iterable, Dict, Callable, Set, Tuple

class ConfirmedItemsPacker(object):

    def __init__(self, **kwargs):
        self._ctx = kwargs

    def packItemsType(self, items, typesToCombine=None):
        return set((next((typesToCombine[t] for t in typesToCombine if item.itemTypeID in t), item.itemTypeName) for item in items)) if typesToCombine is not None else set((item.itemTypeName for item in items))

    def packItems(self, items, filterFunc=None, sortFunction=None):
        if callable(sortFunction):
            return sorted([ ConfirmedItem.createFromGUIItem(i, self._ctx) for i in items if filterFunc is not None and not filterFunc(i) or filterFunc is None ], cmp=sortFunction)
        else:
            return [ ConfirmedItem.createFromGUIItem(i, self._ctx) for i in items if filterFunc is not None and not filterFunc(i) or filterFunc is None ]
