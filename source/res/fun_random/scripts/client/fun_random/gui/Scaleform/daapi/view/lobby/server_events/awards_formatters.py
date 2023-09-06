# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/server_events/awards_formatters.py
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer, formatShortData
from gui.server_events.awards_formatters import AWARDS_SIZES, AwardsPacker, getMissionsDefaultFormatterMap

class FunCurtailingAwardsComposer(CurtailingAwardsComposer):

    @classmethod
    def _getShortBonusesData(cls, preformattedBonuses, size=AWARDS_SIZES.SMALL):
        return [ formatShortData(bonus, size) for bonus in preformattedBonuses ]


def getFunFormatterMap():
    return getMissionsDefaultFormatterMap()


def getFunAwardsPacker():
    return AwardsPacker(getFunFormatterMap())
