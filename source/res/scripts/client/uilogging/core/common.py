# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/core/common.py
import logging
import typing
from gui.shared.utils import getPlayerDatabaseID
from helpers import getClientVersion
_logger = logging.getLogger(__name__)
_CLIENT_VERSION = None

def createFeatureKey(feature, group):
    return feature


def getPlayerID():
    playerID = getPlayerDatabaseID()
    if not playerID:
        _logger.warning('Player id not available or player is bot.')
        return
    return playerID


def getClientBuildVersion():
    global _CLIENT_VERSION
    if _CLIENT_VERSION is None:
        _CLIENT_VERSION = getClientVersion()
    return _CLIENT_VERSION
