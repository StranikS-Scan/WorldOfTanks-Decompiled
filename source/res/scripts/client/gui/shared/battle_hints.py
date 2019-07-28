# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/battle_hints.py
import logging
from functools import partial
from collections import namedtuple
import ResMgr
from helpers import i18n
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
_logger = logging.getLogger(__name__)
_CONFIG_FILE = 'gui/battle_hints.xml'
_dynamicDataHandlers = {}

def _unknownHandler(field, data):
    return 'UNKNOWN_FIELD_{}'.format(field)


class BattleHintData(namedtuple('_HintData', ('name', 'componentAlias', 'message', 'iconPath', 'duration', 'dynamicFields', 'priority', 'soundFx', 'soundNotification'))):

    def makeVO(self, data):
        data = data or {}
        for field in self.dynamicFields:
            if field not in data:
                data[field] = _dynamicDataHandlers.get(field, partial(_unknownHandler, field))(data)

        return {'message': i18n.makeString(self.message, **data),
         'iconSource': RES_ICONS.getBattleHintIcon(self.iconPath) if self.iconPath else None}


def makeHintsData():
    battleHintsConfig = ResMgr.openSection(_CONFIG_FILE)
    hints = []
    if battleHintsConfig:
        for hint in battleHintsConfig.values():
            hints.append(BattleHintData(name=hint['name'].asString, componentAlias=hint['component'].asString, message=hint['message'].asString, iconPath=hint['iconPath'].asString if hint.has_key('iconPath') else None, duration=hint['duration'].asFloat if hint.has_key('duration') else None, dynamicFields=hint['dynamicData'].asString.split() if hint.has_key('dynamicData') else [], priority=hint['priority'].asInt if hint.has_key('priority') else 0, soundFx=hint['soundFx'].asString if hint.has_key('soundFx') else None, soundNotification=hint['soundNotification'].asString if hint.has_key('soundNotification') else None))

    else:
        _logger.error('Failed to open: %s', _CONFIG_FILE)
    return hints
