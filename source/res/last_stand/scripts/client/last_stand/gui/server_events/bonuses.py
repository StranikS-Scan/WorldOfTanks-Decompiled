# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/server_events/bonuses.py
from __future__ import absolute_import
from gui.server_events.bonuses import TokensBonus
from last_stand_common.last_stand_constants import BoostersSettings, ProgressPointsSettings

def boosterTokenChecker(tokenID):
    return tokenID.startswith(BoostersSettings.TOKEN_PREFIX)


class BoosterTokenBonus(TokensBonus):

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(TokensBonus, self).__init__(BoostersSettings.BONUS_NAME, value, isCompensation, ctx)

    def isShowInGUI(self):
        return True


def progressPointTokenChecker(tokenID):
    return tokenID == ProgressPointsSettings.TOKEN


class ProgressPointTokenBonus(TokensBonus):

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(TokensBonus, self).__init__(ProgressPointsSettings.BONUS_NAME, value.get(ProgressPointsSettings.TOKEN, {}), isCompensation, ctx)

    def isShowInGUI(self):
        return True
