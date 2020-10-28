# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/battle_hints.py
import json
import logging
from collections import namedtuple
import ResMgr
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from debug_utils import LOG_ERROR
_logger = logging.getLogger(__name__)
_CONFIG_FILE = 'gui/battle_hints.xml'

class BattleHintData(namedtuple('_HintData', ('name', 'componentAlias', 'iconPath', 'duration', 'dynamicFields', 'priority', 'soundFx', 'soundNotification', 'htmlTemplate'))):

    def makeVO(self, data=''):
        message = makeHtmlString('html_templates:battleHints', self.htmlTemplate)
        message = self._applyDataParams(message, data)
        return {'message': message,
         'iconSource': backport.image(R.images.gui.maps.icons.battleHints.event.dyn(self.iconPath)()) if self.iconPath else None}

    def _applyDataParams(self, message, paramsStr):
        if not paramsStr:
            return message
        try:
            data = json.loads(paramsStr)
            return message.format(**data)
        except ValueError:
            LOG_ERROR('BattleHintData::_applyDataParams: Incorrect json format for: {}'.format(paramsStr))
            return message


def makeHintsData():
    battleHintsConfig = ResMgr.openSection(_CONFIG_FILE)
    hints = []
    if battleHintsConfig:
        for hint in battleHintsConfig.values():
            hints.append(BattleHintData(name=hint['name'].asString, componentAlias=hint['component'].asString, htmlTemplate=hint['htmlTemplate'].asString, iconPath=hint['iconPath'].asString if hint.has_key('iconPath') else None, duration=hint['duration'].asFloat if hint.has_key('duration') else None, dynamicFields=hint['dynamicData'].asString.split() if hint.has_key('dynamicData') else [], priority=hint['priority'].asInt if hint.has_key('priority') else 0, soundFx=hint['soundFx'].asString if hint.has_key('soundFx') else None, soundNotification=hint['soundNotification'].asString if hint.has_key('soundNotification') else None))

    else:
        _logger.error('Failed to open: %s', _CONFIG_FILE)
    return hints
