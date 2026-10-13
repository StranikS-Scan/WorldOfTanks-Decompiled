# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/hw_helpers/anomalies_helpers.py
from __future__ import absolute_import
import typing
from halloween.gui import halloween_account_settings as hw_acc_settings
from halloween.gui.halloween_account_settings import AccountSettingsKeys
from halloween.skeletons.halloween_anomalies_controller import IHalloweenAnomaliesController
from halloween_common.halloween_constants import AnomalySettings, ANOMALIES_SYSTEM_UNLOCKED, AnomalyType
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Set

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isAnomaliesSystemAvailable(itemsCache=None):
    return bool(itemsCache.items.tokens.getToken(ANOMALIES_SYSTEM_UNLOCKED))


def getShowedAnomaliesIDs():
    return set((_getAnomalyIDByToken(anomalyToken) for anomalyToken in getShowedAnomaliesTokens()))


def setAnomalyAsShowed(anomalyID):
    anomalyToken = _getAnomalyTokenByID(anomalyID)
    showedAnomaliesTokens = getShowedAnomaliesTokens()
    showedAnomaliesTokens.add(anomalyToken)
    hw_acc_settings.setSettings(AccountSettingsKeys.ANOMALIES_SHOWED, showedAnomaliesTokens)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getKnownAnomaliesIDs(itemsCache=None):
    availableAnomalyTokens = itemsCache.items.tokens.getTokensByPrefixAndPostfix(prefix=AnomalySettings.TOKEN_PREFIX)
    return set((_getAnomalyIDByToken(anomalyToken) for anomalyToken in availableAnomalyTokens))


@dependency.replace_none_kwargs(hwAnomaliesCtrl=IHalloweenAnomaliesController)
def getAnomaliesProgression(hwAnomaliesCtrl=None):
    curProgress = len(getKnownAnomaliesIDs())
    maxProgress = len([ aID for aID, aData in hwAnomaliesCtrl.anomalies.items() if aData.type != AnomalyType.SECRET ])
    return (curProgress, maxProgress)


def getNewAnomaliesIDs():
    return getKnownAnomaliesIDs() - getShowedAnomaliesIDs()


def hasNewAnomalies():
    return bool(getNewAnomaliesIDs())


def _getAnomalyIDByToken(anomalyToken):
    _, anomalyID = anomalyToken.split(':')
    return anomalyID


def _getAnomalyTokenByID(anomalyID):
    return AnomalySettings.TOKEN_PREFIX + anomalyID


def getShowedAnomaliesTokens():
    return hw_acc_settings.getSettings(AccountSettingsKeys.ANOMALIES_SHOWED)
