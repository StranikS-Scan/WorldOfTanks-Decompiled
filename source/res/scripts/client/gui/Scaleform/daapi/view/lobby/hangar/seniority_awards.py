# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/seniority_awards.py
import logging
from gui.impl import backport
from helpers import dependency, time_utils
from helpers.time_utils import getServerUTCTime
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getSeniorityAwardsAutoOpenDate(lobbyContext=None):
    config = lobbyContext.getServerSettings().getSeniorityAwardsConfig()
    autoOpenTime = config.autoOpenTimestamp()
    autoOpenLocalTime = time_utils.makeLocalServerTime(autoOpenTime)
    return backport.getLongDateFormat(autoOpenLocalTime)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def autoOpenTimeExpired(lobbyContext=None):
    config = lobbyContext.getServerSettings().getSeniorityAwardsConfig()
    autoOpenTime = config.autoOpenTimestamp()
    return autoOpenTime < getServerUTCTime()
