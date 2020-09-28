# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/minimap.py
import itertools
import math_utils
from constants import WtTeams
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.Scaleform.daapi.view.battle.shared.minimap.common import EntriesPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import ArenaVehiclesPlugin
from gui.battle_control.avatar_getter import getArena
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import WtGameEvent
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME

class EventMinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(EventMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['waves'] = WavesPositionsPlugin
        setup['groupdrops'] = GroupdropsPositionsPlugin
        setup['vehicles'] = WtArenaVehiclesPlugin
        setup['attention'] = WaveAttentionPlugin
        return setup


class BasePositionsPlugin(EntriesPlugin):
    __slots__ = ('__event',)

    def __init__(self, parent, event):
        super(BasePositionsPlugin, self).__init__(parent)
        self.__event = event

    def initControlMode(self, mode, available):
        super(BasePositionsPlugin, self).initControlMode(mode, available)
        self.__addMarkers()
        g_eventBus.addListener(self.__event, self.__onUpdatePositions, scope=EVENT_BUS_SCOPE.BATTLE)

    def fini(self):
        super(BasePositionsPlugin, self).fini()
        g_eventBus.removeListener(self.__event, self.__onUpdatePositions, scope=EVENT_BUS_SCOPE.BATTLE)

    def _showMarker(self, item):
        pass

    def __onUpdatePositions(self, event):
        delIDs = {item.id for item in event.ctx['delPositions']}
        addIDs = {item.id for item in event.ctx['addPositions']}
        self.__delMarkers(delIDs)
        self.__addMarkers(addIDs)

    def __addMarkers(self, ids=None):
        arenaInfo = getArena().arenaInfo
        for item in getattr(arenaInfo, self.__event):
            if ids is None or item.id in ids:
                self._showMarker(item)

        return

    def __delMarkers(self, ids=None):
        ids = ids if ids is not None else self._entries.keys()
        for removedID in ids:
            self._delEntryEx(removedID)

        return


class WavesPositionsPlugin(BasePositionsPlugin):

    def __init__(self, parent):
        super(WavesPositionsPlugin, self).__init__(parent, WtGameEvent.WAVES_POSITIONS)

    def _showMarker(self, item):
        waveID = item.id
        isUpcoming = item.isUpcoming
        position = item.position
        iconNumber = waveID
        isGrayscale = isUpcoming and waveID > 1
        if self._arenaDP.getNumberOfTeam() == WtTeams.BOSS:
            symbol = _S_NAME.WT_ALLY_WAVE_SPAWN
        else:
            symbol = _S_NAME.WT_ENEMY_WAVE_SPAWN
        self._addEntryEx(waveID, symbol, _C_NAME.TEAM_POINTS, active=True, matrix=math_utils.createTranslationMatrix(position))
        entryId = self._entries[waveID].getID()
        self._invoke(entryId, 'setPointNumber', iconNumber)
        self._invoke(entryId, 'setGrayscale', isGrayscale)


class GroupdropsPositionsPlugin(BasePositionsPlugin):

    def __init__(self, parent):
        super(GroupdropsPositionsPlugin, self).__init__(parent, WtGameEvent.GROUPDRPOP_POSITIONS)

    def _showMarker(self, item):
        position = item.position
        self._addEntryEx(item.id, _S_NAME.WT_ENERGY_ENTRY, _C_NAME.TEAM_POINTS, active=True, matrix=math_utils.createTranslationMatrix(position))


class WaveAttentionPlugin(BasePositionsPlugin):
    __slots__ = ('__animationIDs', '__pastWaves')

    def __init__(self, parent):
        super(WaveAttentionPlugin, self).__init__(parent, WtGameEvent.GROUPDRPOP_POSITIONS)
        self.__animationIDs = itertools.cycle(('spawnAnim_0', 'spawnAnim_1', 'spawnAnim_2'))
        self.__pastWaves = set()

    def _showMarker(self, item):
        arenaInfo = getArena().arenaInfo
        for wave in arenaInfo.wavesPositions:
            if wave.isUpcoming and wave.id not in self.__pastWaves:
                self.__pastWaves.add(wave.id)
                if self._arenaDP.getNumberOfTeam() == WtTeams.BOSS:
                    symbol = _S_NAME.WT_ALLY_BOT_NEXT_SPAWN_ENTRY
                else:
                    symbol = _S_NAME.WT_BOT_NEXT_SPAWN_ENTRY
                self.__playSpawnAnimation(symbol, wave.position)

    def __playSpawnAnimation(self, entryName, position):
        matrix = math_utils.createTranslationMatrix(position)
        animationID = self.__animationIDs.next()
        if animationID in self._entries:
            entryID = self._entries[animationID].getID()
            self._setMatrix(entryID, matrix)
            self._invoke(entryID, 'playAnimation')
        else:
            self._addEntryEx(animationID, entryName, _C_NAME.TEAM_POINTS, active=True, matrix=matrix)


class WtArenaVehiclesPlugin(ArenaVehiclesPlugin):

    def _setVehicleInfo(self, vehicleID, entry, vInfo, guiProps, isSpotted=False):
        vehicleType = vInfo.vehicleType
        classTag = vehicleType.classTag
        name = vehicleType.shortNameWithPrefix
        isTiger = 'event_boss' in vehicleType.tags
        isEnemy = not guiProps.isFriend
        if isTiger:
            classTag = 'WT'
        if classTag is not None:
            entry.setVehicleInfo(isEnemy, guiProps.name(), classTag, vInfo.isAlive())
            animation = self._getSpottedAnimation(entry, isSpotted)
            if animation:
                self._playSpottedSound(entry)
            self._invoke(entry.getID(), 'setVehicleInfo', vehicleID, classTag, name, guiProps.name(), animation)
        return
