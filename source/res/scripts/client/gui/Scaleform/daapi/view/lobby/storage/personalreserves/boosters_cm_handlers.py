# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/personalreserves/boosters_cm_handlers.py
from adisp import process
from gui import shop
from gui.Scaleform.daapi.view.lobby.shared.cm_handlers import ContextMenu, option, CMLabel
from gui.Scaleform.framework.managers.context_menu import CM_BUY_COLOR
from gui.shared import event_dispatcher as shared_events
from helpers import dependency
from ids_generators import SequenceIDGenerator
from skeletons.gui.goodies import IGoodiesCache
_SOURCE = shop.Source.EXTERNAL
_ORIGIN = shop.Origin.STORAGE

class PersonalReservesCMHandler(ContextMenu):
    __sqGen = SequenceIDGenerator()
    __goodiesCache = dependency.descriptor(IGoodiesCache)

    @option(__sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showStorageBoosterInfo(self._id)

    @option(__sqGen.next(), CMLabel.ACTIVATE)
    @process
    def activate(self):
        _ = yield shared_events.showBoosterActivateDialog(self._id)

    @option(__sqGen.next(), CMLabel.BUY_MORE)
    def buy(self):
        shop.showBuyPersonalReservesOverlay(self._id, _SOURCE, _ORIGIN)

    def _getOptionCustomData(self, label):
        optionData = super(PersonalReservesCMHandler, self)._getOptionCustomData(label)
        if label == CMLabel.ACTIVATE:
            booster = self.__goodiesCache.getBooster(self._id)
            optionData.enabled = booster is not None and booster.isReadyToActivate
        elif label == CMLabel.BUY_MORE:
            booster = self.__goodiesCache.getBooster(self._id)
            if booster is not None and not booster.isHidden:
                optionData.textColor = CM_BUY_COLOR
            else:
                optionData.enabled = False
        return optionData
