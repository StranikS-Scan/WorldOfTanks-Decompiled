# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/battle_hints_event.py
import logging
from collections import namedtuple
import ResMgr
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from items import _xml
from white_tiger.gui.battle_control.controllers.battle_hints_ctrl import WTBattleHintsController
_logger = logging.getLogger(__name__)
_CONFIG_FILE = 'gui/battle_hints_event.xml'
_XML_CTX = (None, _CONFIG_FILE)

class BattleHintData(namedtuple('_HintData', ('name', 'componentAlias', 'iconPath', 'duration', 'maxWaitTime', 'priority', 'soundFx', 'soundNotification', 'htmlTemplate', 'rawMessage', 'backgroundColor', 'useCountdownTimer'))):

    def makeVO(self, data=None):
        if data is None:
            data = {}
        message = self.rawMessage or makeHtmlString('html_templates:battleHints', self.htmlTemplate)
        message = self._applyDataParams(message, data)
        hasIcon = self.iconPath and self.iconPath in R.images.gui.maps.icons.battleHints.event.keys()
        timer = self.duration
        if 'elapsed' in data:
            timer -= data['elapsed']
        return {'message': message,
         'iconSource': backport.image(R.images.gui.maps.icons.battleHints.event.dyn(self.iconPath)()) if hasIcon else None,
         'timer': timer * 1000,
         'useCountdownTimer': self.useCountdownTimer,
         'backgroundColor': self.backgroundColor}

    def _applyDataParams(self, message, data):
        try:
            return message.format(**data)
        except KeyError:
            _logger.error('BattleHintData::_applyDataParams: Incorrect format for: %s', str(data))
            return message


def makeHintsData():
    battleHintsConfig = ResMgr.openSection(_CONFIG_FILE)
    hints = []
    if battleHintsConfig:
        for hint in battleHintsConfig.values():
            hints.append(BattleHintData(name=hint['name'].asString, componentAlias=_xml.readTupleOfStrings(_XML_CTX, hint, 'component'), htmlTemplate=hint['htmlTemplate'].asString, iconPath=hint['iconPath'].asString if hint.has_key('iconPath') else None, duration=hint['duration'].asFloat if hint.has_key('duration') else None, maxWaitTime=hint['maxWaitTime'].asFloat if hint.has_key('maxWaitTime') else 10, priority=hint['priority'].asInt if hint.has_key('priority') else 0, soundFx=hint['soundFx'].asString if hint.has_key('soundFx') else None, useCountdownTimer=hint['useCountdownTimer'].asBool if hint.has_key('useCountdownTimer') else False, backgroundColor=hint['backgroundColor'].asString if hint.has_key('backgroundColor') else None, soundNotification=hint['soundNotification'].asString if hint.has_key('soundNotification') else None, rawMessage=None))

    else:
        _logger.error('Failed to open: %s', _CONFIG_FILE)
    return hints


def createWTBattleHintsController():
    return WTBattleHintsController(makeHintsData())
