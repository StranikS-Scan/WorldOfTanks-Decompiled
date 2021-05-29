# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/DemonstratorWindow.py
from itertools import ifilter
from operator import itemgetter
import ArenaType
from CurrentVehicle import g_currentVehicle
from account_helpers import gameplay_ctx, isDemonstratorExpert
from account_helpers.settings_core.settings_constants import GAME
from gui.Scaleform.daapi.view.meta.DemonstratorWindowMeta import DemonstratorWindowMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import ListDAAPIDataProvider
from gui.Scaleform.genConsts.BATTLE_TYPES import BATTLE_TYPES as GAMEPLAY
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency, int2roman
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.account_helpers.settings_core import ISettingsCore

class SPAWNS(object):
    ANY = 'any'
    BLUE = 'blue'
    RED = 'red'


class BATTLE_TYPES(object):
    UNKNOWN = 0
    TOP1 = 1
    TOP2 = 2
    BOT2 = 3
    TOP3 = 4
    MID3 = 5
    BOT3 = 6


BATTLE_TEMPLATES = [([-2, -1, 0], BATTLE_TYPES.TOP3),
 ([-1, 0], BATTLE_TYPES.TOP2),
 ([0], BATTLE_TYPES.TOP1),
 ([-1, 0, 1], BATTLE_TYPES.MID3),
 ([0, 1], BATTLE_TYPES.BOT2),
 ([0, 1, 2], BATTLE_TYPES.BOT3)]
BATTLE_TO_VEHICLE_LEVELS = [(1,),
 (1, 2),
 (2, 3),
 (3, 4),
 (4, 5),
 (4, 5, 6),
 (5, 6, 7),
 (6, 7, 8),
 (7, 8, 9),
 (8, 9, 10)]

class DemonstratorWindow(DemonstratorWindowMeta, IGlobalListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.instance(ISettingsCore)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__mapListDP', '__isDemonstratorExpert', '__gameplaySelected', '__mapSelected', '__spawnSelected', '__levelSelected', '__vehicleSelected', '__availableBattleTypes')

    def __init__(self, ctx=None):
        super(DemonstratorWindow, self).__init__(ctx)
        self.__mapListDP = MapListDataProvider()
        self.__isDemonstratorExpert = isDemonstratorExpert(self.__itemsCache.items.stats.attributes)
        self.__gameplaySelected = 0
        self.__mapSelected = 0
        self.__spawnSelected = 0
        self.__levelSelected = 0
        self.__vehicleSelected = None
        self.__availableGameplayTypes = []
        self.__availableBattleTypes = []
        self.__availableMapsLength = 0
        return

    def onPrbEntitySwitched(self):
        self.__setPlatoonWarning()
        self.__setMapsList()
        self.__disableBattleButton()

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        self.__setMapsList()
        self.__disableBattleButton()

    def onGameplaySelected(self, index):
        self.__gameplaySelected = index
        self.__setMapsList()
        self.__disableBattleButton()

    def onLvlSelected(self, index):
        self.__levelSelected = self.__availableBattleTypes[index]

    def onSpawnSelected(self, index):
        self.__spawnSelected = index

    def onMapSelected(self, index):
        self.__mapSelected = self.__mapListDP.collection[index]['id']
        self.__enableBattleButton()

    def onBattleStart(self):
        mmData = self.__packMMData(self.__mapSelected, self.__levelSelected, self.__spawnSelected)
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            dispatcher.doAction(PrbAction('', mmData=int(mmData)))
            self.onWindowClose()
        return

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(DemonstratorWindow, self)._populate()
        self.__vehicleSelected = g_currentVehicle.item
        if not self.__vehicleSelected:
            self.onWindowClose()
        self.__addListeners()
        self.__mapListDP.setFlashObject(self.as_getDPS())
        self.__setGameplayTabs()
        self.__setLevelsList()
        self.__setSpawnsList()
        self.__setMapsList()
        self.__setPlatoonWarning()
        self.__disableBattleButton()
        self.as_enableExtendedSettingsS(isDemonstratorExpert(self.__itemsCache.items.stats.attributes))

    def _dispose(self):
        self.__removeListeners()
        self.__mapListDP.dispose()
        self.__mapListDP = None
        super(DemonstratorWindow, self)._dispose()
        return

    def __addListeners(self):
        self.startGlobalListening()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        g_currentVehicle.onChanged += self.__onVehicleChanged

    def __removeListeners(self):
        self.stopGlobalListening()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        g_currentVehicle.onChanged -= self.__onVehicleChanged

    def __onServerSettingChanged(self, diff):
        if 'randomMapsForDemonstrator' in diff or ('randomMapsForDemonstrator', '_r') in diff:
            self.__setLevelsList()
            self.__setMapsList()
            self.__disableBattleButton()

    def __onSettingsChanged(self, diff):
        if GAME.GAMEPLAY_MASK in diff:
            self.__gameplaySelected = 0
            self.__setGameplayTabs()
            self.__setMapsList()
            self.__disableBattleButton()
        elif GAME.GAMEPLAY_ONLY_10_MODE in diff:
            self.__setLevelsList()

    def __onVehicleChanged(self):
        self.__vehicleSelected = g_currentVehicle.item
        if not self.__vehicleSelected:
            self.onWindowClose()
        else:
            self.__setLevelsList()
            self.__setMapsList()
            self.__disableBattleButton()

    def __setGameplayTabs(self):
        self.__availableGameplayTypes = [(GAMEPLAY.CTF, self.__settingsCore.getSetting(GAME.GAMEPLAY_CTF)), (GAMEPLAY.ASSAULT, self.__settingsCore.getSetting(GAME.GAMEPLAY_ASSAULT)), (GAMEPLAY.DOMINATION, self.__settingsCore.getSetting(GAME.GAMEPLAY_DOMINATION))]
        gameplayTabs = list(({'label': backport.text(R.strings.arenas.type.dyn(battleType).name()),
         'enabled': isEnabled} for battleType, isEnabled in self.__availableGameplayTypes))
        self.as_setGameplayTabsS(gameplayTabs, self.__gameplaySelected)

    def __setSpawnsList(self):
        isEnabled = self.__availableMapsLength != 0
        spawnsList = [{'label': backport.text(R.strings.menu.demonstrator.window.any()),
          'enabled': isEnabled}, {'label': backport.text(R.strings.menu.demonstrator.window.spawn.green()),
          'enabled': isEnabled}, {'label': backport.text(R.strings.menu.demonstrator.window.spawn.red()),
          'enabled': isEnabled}]
        self.as_setSpawnsS(spawnsList, 0)

    def __setMapsList(self):
        self.__mapSelected = 0
        self.__mapListDP.buildList(self.__vehicleSelected.level, self.__availableGameplayTypes[self.__gameplaySelected][0])
        self.__availableMapsLength = len(list(ifilter(itemgetter('enabled'), self.__mapListDP.collection)))
        self.__setSpawnsList()
        self.__setLevelsList()

    def __setPlatoonWarning(self):
        self.as_enablePlatoonWarningS(self.__isInUnit())

    def __enableBattleButton(self):
        isBattleButtonEnabled = True
        if self.__isInUnit() and not self.__isCommander():
            isBattleButtonEnabled = False
        self.as_enableBattleButtonS(isBattleButtonEnabled)

    def __disableBattleButton(self):
        self.as_enableBattleButtonS(False)

    def __isInUnit(self):
        dispatcher = self.prbDispatcher
        isInUnit = False
        if dispatcher is not None:
            state = dispatcher.getFunctionalState()
            isInUnit = state.isInUnit(state.entityTypeID)
        return isInUnit

    def __isCommander(self):
        entity = self.prbEntity
        isCommander = False
        if entity is not None:
            isCommander = self.prbEntity.isCommander()
        return isCommander

    def __setLevelsList(self):
        if not self.__isDemonstratorExpert:
            return
        availableLevels, availableBattleTypes = self.__getAvailableLevelsBattleTypes()
        self.__availableBattleTypes = [BATTLE_TYPES.UNKNOWN] + availableBattleTypes
        battleLevelsSelector = [{'label': backport.text(R.strings.menu.demonstrator.window.any()),
          'enabled': self.__availableMapsLength != 0}]
        for availableLevel, isEnabled in availableLevels:
            levelToRoman = [ int2roman(level) for level in availableLevel ]
            label = ', '.join(levelToRoman)
            battleLevelsSelector.append({'label': label,
             'enabled': isEnabled})

        self.as_setLevelsS(battleLevelsSelector, 0)

    def __getAvailableLevelsBattleTypes(self):
        vehicleLevel = self.__vehicleSelected.level
        minBattleLevel, maxBattleLevel = self.__getAvailableBattleLevelRange()
        clientIsOnly10ModeEnabled = self.__settingsCore.getSetting(GAME.GAMEPLAY_ONLY_10_MODE)
        serverIsOnly10ModeEnabled = dependency.instance(ILobbyContext).getServerSettings().isOnly10ModeEnabled()
        battleConfigs = BATTLE_TO_VEHICLE_LEVELS[minBattleLevel - 1:maxBattleLevel]
        battleConfigs = [ set(item) for item in battleConfigs ]
        levels = []
        battleTypes = []
        for battleTemplate, battleType in BATTLE_TEMPLATES:
            level = [ vehicleLevel + diff for diff in battleTemplate ]
            if not any((battleConfig.issuperset(level) for battleConfig in battleConfigs)):
                continue
            if not (battleType != BATTLE_TYPES.TOP1 or minBattleLevel <= vehicleLevel <= maxBattleLevel):
                continue
            isEnabled = not (serverIsOnly10ModeEnabled and clientIsOnly10ModeEnabled and vehicleLevel == 10 and battleType != BATTLE_TYPES.TOP1 or not self.__availableMapsLength)
            levels.append((level, isEnabled))
            battleTypes.append(battleType)

        return (levels, battleTypes)

    def __getAvailableBattleLevelRange(self):
        serverSettings = self.__lobbyContext.getServerSettings()
        battleLevels = serverSettings.getRandomBattleLevelsForDemonstrator()
        vehicleLevel = self.__vehicleSelected.level
        vehicleType = self.__vehicleSelected.type
        vehicleName = self.__vehicleSelected.name
        if vehicleName in battleLevels:
            vehicleBattleLevels = battleLevels[vehicleName]
        else:
            vehicleBattleLevels = battleLevels[vehicleType][vehicleLevel - 1]
        minBattleLevel, maxBattleLevel = vehicleBattleLevels
        return (minBattleLevel, maxBattleLevel)

    def __packMMData(self, arenaTypeID, levelType, team):
        return team << 28 | levelType << 24 | arenaTypeID


class ArenasCache(object):

    def __init__(self):
        self.__cache = []
        self.__playerTeam = 1
        for arenaTypeID, arenaType in ArenaType.g_cache.iteritems():
            if arenaType.explicitRequestOnly or not gameplay_ctx.isCreationEnabled(arenaType.gameplayName, False):
                continue
            self.__cache.append({'id': arenaTypeID,
             'name': arenaType.name,
             'gameplayName': arenaType.gameplayName,
             'icon': backport.image(R.images.gui.maps.icons.map.num(arenaType.geometryName)()),
             'points': self.__getPointsList(arenaType),
             'enabled': False})

        self.__cache = sorted(self.__cache, key=lambda x: (x['gameplayName'].lower(), x['name'].lower()))

    def __getPointsList(self, arenaType):
        result = []
        bottomLeft, upperRight = arenaType.boundingBox
        mapWidthScale, mapHeightScale = (upperRight - bottomLeft) / 300
        offset = (upperRight + bottomLeft) * 0.5

        def _normalizePoint(posX, posY):
            return ((posX - offset.x) / mapWidthScale, (posY - offset.y) / mapHeightScale)

        for team, teamSpawnPoints in enumerate(arenaType.teamSpawnPoints, 1):
            for spawn, spawnPoint in enumerate(teamSpawnPoints, 1):
                posX, posY = _normalizePoint(spawnPoint[0], spawnPoint[1])
                result.append({'posX': posX,
                 'posY': posY,
                 'pointType': 'spawn',
                 'color': SPAWNS.BLUE if team == self.__playerTeam else SPAWNS.RED,
                 'id': spawn + 1 if len(teamSpawnPoints) > 1 else 1})

        for team, teamBasePoints in enumerate(arenaType.teamBasePositions, 1):
            for baseNumber, basePoint in enumerate(teamBasePoints.values(), 2):
                posX, posY = _normalizePoint(basePoint[0], basePoint[1])
                result.append({'posX': posX,
                 'posY': posY,
                 'pointType': 'base',
                 'color': SPAWNS.BLUE if team == self.__playerTeam else SPAWNS.RED,
                 'id': baseNumber + 1 if len(teamBasePoints) > 1 else 1})

        if arenaType.controlPoints:
            for index, controlPoint in enumerate(arenaType.controlPoints, 2):
                posX, posY = _normalizePoint(controlPoint[0], controlPoint[1])
                result.append({'posX': posX,
                 'posY': posY,
                 'pointType': 'control',
                 'color': 'empty',
                 'id': index if len(arenaType.controlPoints) > 1 else 1})

        return result

    @property
    def cache(self):
        return self.__cache


class MapListDataProvider(ListDAAPIDataProvider):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(MapListDataProvider, self).__init__()
        self._list = []
        self._cache = ArenasCache()

    @property
    def collection(self):
        return self._list

    def emptyItem(self):
        return None

    def clear(self):
        self._list = []

    def dispose(self):
        self.clear()
        self.destroy()

    def rebuildList(self, cache):
        self.buildList(cache)
        self.refresh()

    def buildList(self, currentVehicleLevel=0, gameplayName=None):
        self.clear()
        filteredList = [ mapData for mapData in self._cache.cache if mapData['gameplayName'] == gameplayName ]
        serverSettings = self.__lobbyContext.getServerSettings()
        randomMaps = serverSettings.getRandomMapsForDemonstrator()
        for item in filteredList:
            arenaTypeID = item['id']
            geometryID = arenaTypeID & 65535
            gameplayID = arenaTypeID >> 16
            item['enabled'] = (geometryID, gameplayID) in randomMaps[currentVehicleLevel]

        self._list = filteredList
        self.refresh()
