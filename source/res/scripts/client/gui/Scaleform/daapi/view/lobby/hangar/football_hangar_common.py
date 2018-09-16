# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/football_hangar_common.py
import BigWorld
from gui.Scaleform.locale.FOOTBALL2018 import FOOTBALL2018

class OsBitness(object):
    _x86 = 1
    _x64 = 2
    _UNKNOWN = 3
    _osBit = None

    @staticmethod
    def is32Bit():
        return OsBitness.__getBitness() == OsBitness._x86

    @staticmethod
    def is64Bit():
        return OsBitness.__getBitness() == OsBitness._x64

    @staticmethod
    def __getBitness():
        if OsBitness._osBit is None:
            stats = BigWorld.wg_getClientStatistics()
            OsBitness._osBit = stats.get('osBit', OsBitness._UNKNOWN) if stats is not None else OsBitness._UNKNOWN
        return OsBitness._osBit


def getHangarBuffonTooltip(isBuffonAvaiable, isBuffonRecruited):
    if isBuffonRecruited:
        return FOOTBALL2018.HANGAR_BUFFONBTN_TOOLTIP_BUFFONRECRUITED
    return FOOTBALL2018.HANGAR_BUFFONBTN_TOOLTIP_BUFFONNOTRECRUITED if not isBuffonRecruited and isBuffonAvaiable else FOOTBALL2018.HANGAR_BUFFONBTN_TOOLTIP_BUFFONNOTAVAILABLE
