# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/helpers.py
import json
import BigWorld
from gui.shared.utils import getPlayerDatabaseID
from uilogging.logging_constants import REQUESTS_LIMIT, HTTP_OK_STATUS, STATUS_REQUESTED
from uilogging import loggingSettings

class FeaturesCacheMeta(type):
    _instance = None

    def __call__(cls):
        if cls._instance is None:
            cls._instance = super(FeaturesCacheMeta, cls).__call__()
        return cls._instance


class FeaturesCache(object):
    __metaclass__ = FeaturesCacheMeta

    def __init__(self):
        self._data = {}
        self._requestsCounter = {}

    @classmethod
    def updateFeatureStatus(cls, response):
        cache = cls()
        if response.responseCode != HTTP_OK_STATUS:
            return False
        try:
            data = json.loads(response.body)
        except (TypeError, ValueError):
            return False

        isEnabled = data.get('data', {}).get('send_logs', False)
        feature = data.get('data', {}).get('feature')
        cache.setStatus(feature, isEnabled)

    def setStatus(self, feature, status):
        if feature:
            self._data[feature] = status

    def enabledForFeature(self, feature):
        if feature not in self._requestsCounter:
            self._requestsCounter[feature] = 0
        if self._requestsCounter[feature] >= REQUESTS_LIMIT:
            return False
        if feature not in self._data:
            self._requestsCounter[feature] += 1
            self._sendRequest(feature)
            return STATUS_REQUESTED
        return self._data[feature]

    def _sendRequest(self, feature):
        BigWorld.fetchURL(url=loggingSettings.apiHost, callback=FeaturesCache.updateFeatureStatus, headers=loggingSettings.headers, timeout=loggingSettings.requestTimeout, method=loggingSettings.httpMethod, postdata=json.dumps({'feature': feature,
         'spa_id': getPlayerDatabaseID()}))


featuresCache = FeaturesCache()
