# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/personalreserves/boosters_cm_handlers.py
from gui import ingame_shop as shop
from gui.Scaleform.daapi.view.lobby.storage.cm_handlers import ContextMenu, option, CMLabel, CM_BUY_COLOR
from gui.shared import event_dispatcher as shared_events
from helpers import dependency
from ids_generators import SequenceIDGenerator
from skeletons.gui.goodies import IGoodiesCache
_SOURCE = shop.Source.EXTERNAL
_ORIGIN = shop.Origin.STORAGE

class PersonalReservesCMHandler(ContextMenu):
    _sqGen = SequenceIDGenerator()
    _goodiesCache = dependency.descriptor(IGoodiesCache)

    @option(_sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showStorageBoosterInfo(self._id)

    @option(_sqGen.next(), CMLabel.ACTIVATE)
    def activate(self):
        shared_events.showBoosterActivateDialog(self._id)

    @option(_sqGen.next(), CMLabel.BUY_MORE)
    def buy(self):
        shop.showBuyBoosterOverlay(self._id, _SOURCE, _ORIGIN)

    def _getOptionCustomData(self, label):
        if label == CMLabel.ACTIVATE:
            booster = self._goodiesCache.getBooster(self._id)
            return {'enabled': booster.isReadyToActivate}
        elif label == CMLabel.BUY_MORE:
            booster = self._goodiesCache.getBooster(self._id)
            if not booster.isHidden:
                return {'textColor': CM_BUY_COLOR}
            return {'enabled': False}
        else:
            return None
