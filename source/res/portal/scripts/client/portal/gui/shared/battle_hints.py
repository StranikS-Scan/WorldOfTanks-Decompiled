# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/shared/battle_hints.py
import logging
import ResMgr
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.battle_hints import BattleHintData
from gui.battle_control.controllers.battle_hints_ctrl import BattleHintsController
_logger = logging.getLogger(__name__)
_CONFIG_FILE = 'portal/gui/battle_hints.xml'
_BATTLE_HINT_DATA_MAPPING = {'waveStarted': (('currentWave', int), ('laneIndex', int)),
 'subwaveStarted': (('laneIndex', int),),
 'campBecameCapturable': (('frontier', str),),
 'campCaptured': (('frontier', str),),
 'almostBase': (('laneIndex', int),)}

def _mapBattleHintData(hintName, data):
    hintData = None
    mapping = _BATTLE_HINT_DATA_MAPPING.get(hintName)
    if mapping and data:
        hintData = {}
        for index, (k, t) in enumerate(mapping, start=1):
            value = t(data['param{}'.format(index)])
            hintData[k] = value

    elif mapping or data:
        _logger.error('Battle hint data mismatch')
    return hintData


class PortalBattleHintData(BattleHintData):

    def makeVO(self, data=None):
        hintData = _mapBattleHintData(self.name, data) or {}
        self.__processBattleHintData(hintData)
        vo = super(PortalBattleHintData, self).makeVO(hintData)
        if self.iconPath:
            vo['iconSource'] = self.__getIcon(hintData)
        return vo

    def __processBattleHintData(self, hintData):
        resource = R.strings.portal_battle.battle_hints.dyn(self.name)
        if 'laneIndex' in hintData:
            laneIndex = 'c_{}'.format(hintData['laneIndex'])
            hintData['lane'] = backport.text(resource.dyn(laneIndex)())

    def __getIcon(self, data):
        resource = R.images.portal.gui.maps.icons.battle_hints
        if 'frontier' in data:
            frontier = data['frontier'].lower()
            resource = resource.dyn(frontier)
        return backport.image(resource.dyn(self.iconPath)())


def makePortalHintsData():
    battleHintsConfig = ResMgr.openSection(_CONFIG_FILE)
    hints = []
    if battleHintsConfig:
        for hint in battleHintsConfig.values():
            hints.append(PortalBattleHintData(name=hint['name'].asString, componentAlias=hint['component'].asString, htmlTemplate=hint['htmlTemplate'].asString, iconPath=hint['iconPath'].asString if hint.has_key('iconPath') else None, duration=hint['duration'].asFloat if hint.has_key('duration') else None, maxWaitTime=hint['maxWaitTime'].asFloat if hint.has_key('maxWaitTime') else 10, priority=hint['priority'].asInt if hint.has_key('priority') else 0, soundFx=hint['soundFx'].asString if hint.has_key('soundFx') else None, soundNotification=hint['soundNotification'].asString if hint.has_key('soundNotification') else None, rawMessage=None))

    else:
        _logger.error('Failed to open: %s', _CONFIG_FILE)
    return hints


def createBattleHintsController():
    return BattleHintsController(makePortalHintsData())
