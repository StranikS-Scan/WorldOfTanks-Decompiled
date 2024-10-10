# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/maps_training/battle_hints_mt.py
import logging
from collections import namedtuple
from enum import Enum
import ResMgr
from gui.battle_control.controllers.battle_hints_ctrl import BattleHintsController
from gui.impl import backport
from gui.impl.gen import R
from helpers.time_utils import ONE_MINUTE
_logger = logging.getLogger(__name__)
_CONFIG_FILE = 'gui/battle_hints_maps_training.xml'

class HintType(Enum):
    HINT = 'hint'
    GOAL = 'goal'
    TIMER_GREEN = 'timerGreen'
    TIMER_RED = 'timerRed'


class BattleHintData(namedtuple('_HintData', ('name', 'componentAlias', 'duration', 'maxWaitTime', 'priority', 'hintType', 'soundFx', 'soundNotification', 'descriptionKey1', 'descriptionKey2', 'soundNotificationNewbie', 'backgroundColor'))):

    def makeVO(self, data=None):
        vo = {'hintType': self.hintType}
        if self.descriptionKey1 is not None:
            vo['description1'] = backport.text(R.strings.maps_training.hints.dyn(self.descriptionKey1)())
        if self.descriptionKey2 is not None:
            vo['description2'] = backport.text(R.strings.maps_training.hints.dyn(self.descriptionKey2)())
        if data is not None:
            self.__applyData(vo, data)
        return vo

    def __applyData(self, vo, data):
        if self.hintType is HintType.GOAL:
            vo['targetsCount'] = data['param1']
            vo['targetsTotal'] = data['param2']
        elif self.hintType in (HintType.TIMER_RED, HintType.TIMER_GREEN):
            minutes, seconds = divmod(int(data['param1']), ONE_MINUTE)
            minutesStr, secondsStr = '{}'.format(minutes), '{:02d}'.format(seconds)
            vo['description1'] = vo['description1'].format(minutes=minutesStr, seconds=secondsStr)


def makeHintsData():
    battleHintsConfig = ResMgr.openSection(_CONFIG_FILE)
    hints = []
    if battleHintsConfig:
        for hint in battleHintsConfig.values():
            hints.append(BattleHintData(name=hint['name'].asString, componentAlias=hint['component'].asString, hintType=HintType(hint['hintType'].asString), descriptionKey1=hint['descriptionKey1'].asString if hint.has_key('descriptionKey1') else None, descriptionKey2=hint['descriptionKey2'].asString if hint.has_key('descriptionKey2') else None, duration=hint['duration'].asFloat if hint.has_key('duration') else None, maxWaitTime=hint['maxWaitTime'].asFloat if hint.has_key('maxWaitTime') else 10, priority=hint['priority'].asInt if hint.has_key('priority') else 0, soundFx=hint['soundFx'].asString if hint.has_key('soundFx') else None, soundNotification=hint['soundNotification'].asString if hint.has_key('soundNotification') else None, soundNotificationNewbie=hint['soundNotificationNewbie'].asString if hint.has_key('soundNotificationNewbie') else None, backgroundColor=hint['backgroundColor'].asString if hint.has_key('backgroundColor') else None))

    else:
        _logger.error('Failed to open: %s', _CONFIG_FILE)
    return hints


def createBattleHintsController():
    return BattleHintsController(makeHintsData())
