# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/uilogging/loggers.py
from __future__ import absolute_import
import logging
from typing import TYPE_CHECKING
from halloween.gui.sounds.halloween_sound_controller import getEventVoiceoverLanguage
from halloween.gui.sounds.sound_constants import SoundLanguage
from halloween.uilogging.logging_constants import FEATURE, HWLogActions, HWLogKeys, MIN_VO_TIME
from uilogging.base.logger import MetricsLogger, createPartnerID
if TYPE_CHECKING:
    pass
_logger = logging.getLogger(__name__)

class HWMetricsLogger(MetricsLogger):
    __slots__ = ('_view', '_partnerID')

    def __init__(self, view, partnerID=None):
        super(HWMetricsLogger, self).__init__(FEATURE)
        self._view = view
        self._partnerID = partnerID

    def onStartView(self, action):
        self.startAction(action=action)

    def onStopView(self, action, itemState=None, info=None, timeLimit=0):
        self.stopAction(action=action, item=self._view, partnerID=self._partnerID, timeLimit=timeLimit, itemState=itemState, info=info)

    def onLog(self, action, item, itemState=None):
        self.log(action=action, item=item, parentScreen=self._view, itemState=itemState)

    def onClick(self, item, itemState=None):
        self.onLog(HWLogActions.CLICK, item, itemState)


VO_MAP = {SoundLanguage.VOICEOVER_UA: 'UA',
 SoundLanguage.VOICEOVER_EN: 'EN',
 SoundLanguage.VOICEOVER_CN: 'CN',
 SoundLanguage.VOICEOVER_RU: 'RU'}

class DecryptionMetricsLogger(HWMetricsLogger):
    __slots__ = ('_voLang',)

    def __init__(self):
        super(DecryptionMetricsLogger, self).__init__(HWLogKeys.DECRYPT_VIEW, createPartnerID())
        self._voLang = VO_MAP.get(getEventVoiceoverLanguage(), '')

    def onStartView(self, *_):
        super(DecryptionMetricsLogger, self).onStartView(HWLogActions.LIFETIME)

    def onStopView(self, itemState=None, stopVO=False, *_):
        if stopVO:
            self.stopVO(itemState)
        super(DecryptionMetricsLogger, self).onStopView(HWLogActions.LIFETIME, itemState, self._voLang)

    def startVO(self):
        self.startAction(HWLogActions.VO_LISTENED)

    def stopVO(self, itemState):
        self.stopAction(action=HWLogActions.VO_LISTENED, item=self._view, partnerID=self._partnerID, timeLimit=MIN_VO_TIME, itemState=itemState, info=self._voLang)
