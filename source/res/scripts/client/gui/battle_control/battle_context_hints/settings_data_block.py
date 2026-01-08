# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_context_hints/settings_data_block.py
from collections import namedtuple
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
HintData = namedtuple('HintData', 'watchingCounter watchingCounterPerBattle battlesCooldown lastBattleTriggered')

class HintDataBlock(object):

    def __init__(self, section, key):
        self.__section = section
        self.__key = key

    def section(self):
        return self.__section

    def key(self):
        return self.__key

    @dependency.replace_none_kwargs(settingsCore=ISettingsCore)
    def getValue(self, settingsCore=None):
        val = settingsCore.serverSettings.getSectionSettings(self.__section, self.__key, default=0)
        return self.unpack(val)

    @dependency.replace_none_kwargs(settingsCore=ISettingsCore)
    def setValue(self, value, settingsCore=None):
        rawValue = self.pack(value)
        settingsCore.serverSettings.setSectionSettings(self.__section, {self.__key: rawValue})

    def unpack(self, rawVal):
        raise NotImplementedError

    def pack(self, value):
        raise NotImplementedError


class HintDataCntrBlock(HintDataBlock):

    def unpack(self, rawVal):
        return HintData(rawVal, -1, 0, False)

    def pack(self, value):
        return int(value.watchingCounter)


class HintDataLongBattleCntrBlock(HintDataBlock):

    def unpack(self, rawVal):
        watchingCounter = rawVal & 15
        watchingCounterPerBattle = (rawVal & 16) >> 4
        return HintData(watchingCounter, watchingCounterPerBattle, 0, False)

    def pack(self, value):
        watchingCounter = int(value.watchingCounter)
        watchingCounter &= 15
        watchingCounterPerBattle = int(value.watchingCounterPerBattle)
        watchingCounterPerBattle &= 1
        watchingCounterPerBattle <<= 4
        rawVal = watchingCounter | watchingCounterPerBattle
        return rawVal


class HintDataShortBattleCntrBlock(HintDataBlock):

    def unpack(self, rawVal):
        watchingCounter = rawVal & 7
        watchingCounterPerBattle = (rawVal & 8) >> 3
        return HintData(watchingCounter, watchingCounterPerBattle, 0, False)

    def pack(self, value):
        watchingCounter = int(value.watchingCounter)
        watchingCounter &= 7
        watchingCounterPerBattle = int(value.watchingCounterPerBattle)
        watchingCounterPerBattle &= 1
        watchingCounterPerBattle <<= 3
        rawVal = watchingCounter | watchingCounterPerBattle
        return rawVal


class HintDataFullBlock(HintDataBlock):

    def unpack(self, rawVal):
        watchingCounter = rawVal & 7
        watchingCounterPerBattle = (rawVal & 8) >> 3
        battlesCooldown = (rawVal & 48) >> 4
        lastBattleTriggered = bool((rawVal & 64) >> 6)
        return HintData(watchingCounter, watchingCounterPerBattle, battlesCooldown, lastBattleTriggered)

    def pack(self, value):
        watchingCounter = int(value.watchingCounter)
        watchingCounter &= 7
        watchingCounterPerBattle = int(value.watchingCounterPerBattle)
        watchingCounterPerBattle &= 1
        watchingCounterPerBattle <<= 3
        battlesCooldown = int(value.battlesCooldown)
        battlesCooldown &= 3
        battlesCooldown <<= 4
        lastBattleTriggered = int(value.lastBattleTriggered)
        lastBattleTriggered &= 1
        lastBattleTriggered <<= 6
        rawVal = watchingCounter | watchingCounterPerBattle | battlesCooldown | lastBattleTriggered
        return rawVal
