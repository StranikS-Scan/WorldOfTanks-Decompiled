# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/hubs/dev/relations_keeper.py
import logging
import typing
from gui.gift_system.hubs.base.relations_keeper import GiftEventBaseKeeper
from gui.gift_system.hubs.dev import IDevMessagesPusher
from gui.shared.formatters import text_styles
if typing.TYPE_CHECKING:
    from gui.gift_system.wrappers import GiftsWebState, IncomeSysMessage, SendGiftResponse
_logger = logging.getLogger(__name__)

class GiftEventDevKeeper(GiftEventBaseKeeper, IDevMessagesPusher):
    __slots__ = ()

    def __repr__(self):
        return 'GiftEventDevKeeper id={}'.format(self._settings.eventID)

    def processWebState(self, webState):
        _logger.info('%s received web state %s', self, webState)
        self._pushClientMessage('{}\nreceived web state'.format(self))
        super(GiftEventDevKeeper, self).processWebState(webState)

    @classmethod
    def _formatMessage(cls, message):
        return text_styles.statusAttention(message)

    def _processIncomeMessage(self, incomeData):
        if self.isMessagesSuspended(incomeData):
            _logger.info('%s skip data from income message %s', self, incomeData)
            self._pushClientMessage('{}\nskip income message'.format(self))
        super(GiftEventDevKeeper, self)._processIncomeMessage(incomeData)

    def _processOutcomeMessage(self, outcomeData):
        if self.isMessagesSuspended(outcomeData):
            _logger.info('%s skip data from outcome message %s', self, outcomeData)
            self._pushClientMessage('{}\nskip outcome message'.format(self))
        super(GiftEventDevKeeper, self)._processOutcomeMessage(outcomeData)

    def _processWebState(self, webState):
        if self.isMessagesSuspended(webState):
            _logger.info('%s skip data from web state %s', self, webState)
            self._pushClientMessage('{}\nskip web state'.format(self))
        super(GiftEventDevKeeper, self)._processWebState(webState)
