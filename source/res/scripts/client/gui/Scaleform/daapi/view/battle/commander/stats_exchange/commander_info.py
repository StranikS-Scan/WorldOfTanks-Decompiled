# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/stats_exchange/commander_info.py
import logging
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import broker
_logger = logging.getLogger(__name__)

class RTSCommanderInfoComposer(broker.SingleSideComposer):

    def compose(self, data):
        items = self._items
        if items:
            data[self._voField] = next(iter(items))
        return data

    def addItem(self, isEnemy, data):
        if self._items:
            _logger.warning('There is more than one commander in the %s team!', 'enemy' if isEnemy else 'ally')
        super(RTSCommanderInfoComposer, self).addItem(isEnemy, data)
