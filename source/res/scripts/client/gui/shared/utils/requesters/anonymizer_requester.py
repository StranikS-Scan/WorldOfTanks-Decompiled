# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/anonymizer_requester.py
from __future__ import absolute_import
import typing
import BigWorld
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IAnonymizerRequester

class AnonymizerRequester(AbstractSyncDataRequester, IAnonymizerRequester):

    @property
    def isPlayerAnonymized(self):
        return bool(self.getCacheValue('enabled', 0))

    @property
    def contactsFeedback(self):
        return self.getCacheValue('contactsFeedback', [])

    def _requestCache(self, callback=None):
        BigWorld.player().anonymizer.getCache(lambda resID, value: self._response(resID, value, callback))
