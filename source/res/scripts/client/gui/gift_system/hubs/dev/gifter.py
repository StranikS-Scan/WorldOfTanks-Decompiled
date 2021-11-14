# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/hubs/dev/gifter.py
import logging
from adisp import process
from gui.gift_system.constants import GifterResponseState
from gui.gift_system.hubs.base.gifter import GiftEventBaseGifter
from gui.gift_system.hubs.dev import IDevMessagesPusher
from gui.shared.formatters import text_styles
_logger = logging.getLogger(__name__)

class GiftEventDevGifter(GiftEventBaseGifter, IDevMessagesPusher):
    __slots__ = ()

    def __repr__(self):
        return 'GiftEventDevGifter id={}'.format(self._settings.eventID)

    @process
    def sendGift(self, entitlementCode, receiverID, metaInfo, callback=None):
        result = yield super(GiftEventDevGifter, self).sendGift(entitlementCode, receiverID, metaInfo)
        if result.state not in (GifterResponseState.WEB_SUCCESS, GifterResponseState.WEB_FAILURE):
            _logger.info('%s send gift rejected by reason=%s', self, result.state.value)
            self._pushClientMessage('{}\nsend gift rejected'.format(self))

    @classmethod
    def _formatMessage(cls, message):
        return text_styles.statusAlert(message)
