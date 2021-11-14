# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/hubs/dev/messenger.py
import logging
import typing
from gui.gift_system.hubs.base.messenger import GiftEventBaseMessenger
from gui.gift_system.hubs.dev import IDevMessagesPusher
from gui.shared.formatters import text_styles
if typing.TYPE_CHECKING:
    from gui.gift_system.wrappers import GiftsHistoryData, IncomeSysMessage, SendGiftResponse
_logger = logging.getLogger(__name__)

class GiftEventDevMessenger(GiftEventBaseMessenger, IDevMessagesPusher):
    __slots__ = ()

    def __repr__(self):
        return 'GiftEventDevMessenger id={}'.format(self._settings.eventID)

    @classmethod
    def _formatMessage(cls, message):
        return text_styles.statInfo(message)

    def _pushHistoryMessage(self, history):
        _logger.info('%s push history message %s', self, history)
        self._pushClientMessage('{}\npush history message'.format(self))

    def _pushIncomeMessage(self, incomeData):
        _logger.info('%s push income message %s', self, incomeData)
        self._pushClientMessage('{}\npush income message'.format(self))

    def _pushOutcomeMessage(self, outcomeData):
        _logger.info('%s push outcome message %s', self, outcomeData)
        self._pushClientMessage('{}\npush outcome message'.format(self))
