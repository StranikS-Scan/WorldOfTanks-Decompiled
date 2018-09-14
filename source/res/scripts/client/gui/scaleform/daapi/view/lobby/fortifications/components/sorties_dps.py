# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/sorties_dps.py
import BigWorld
from UnitBase import UNIT_FLAGS
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.fort_formatters import getIconLevel
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import getUnitMaxLevel, makeFortBattleShortVO
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeSortieShortVO
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider, SortableDAAPIDataProvider
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as I18N_FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.prb_control.items.sortie_items import getDivisionsOrderData
from gui.prb_control.prb_helpers import unitFunctionalProperty
from gui.shared.formatters import icons, text_styles
from gui.shared.fortifications.fort_seqs import getDivisionSettings, BATTLE_ITEM_TYPE
from gui.shared.utils import sortByFields
from helpers import i18n, time_utils
from shared_utils import CONST_CONTAINER
from messenger import g_settings
from messenger.m_constants import USER_GUI_TYPE
from messenger.storage import storage_getter

def makeDivisionData(nameGenerator):
    result = []
    for name, level, rosterTypeID in getDivisionsOrderData():
        settings = getDivisionSettings(name)
        if settings:
            profit = settings.resourceBonus
        else:
            profit = 0
        result.append({'profit': profit,
         'level': level,
         'label': nameGenerator(name),
         'data': rosterTypeID})

    return result


class DivisionsDataProvider(DAAPIDataProvider):

    def __init__(self):
        super(DivisionsDataProvider, self).__init__()
        self.__list = []

    @property
    def collection(self):
        return self.__list

    def emptyItem(self):
        return {'label': '',
         'data': 0}

    def clear(self):
        self.__list = []

    def init(self, flashObject):
        self.buildList()
        self.setFlashObject(flashObject)

    def fini(self):
        self.clear()
        self._dispose()

    def buildList(self):
        self.__list = [{'label': I18N_FORTIFICATIONS.sortie_division_name('ALL'),
          'data': 0}]
        self.__list.extend(makeDivisionData(I18N_FORTIFICATIONS.sortie_division_name))

    def getTypeIDByIndex(self, index):
        rosterTypeID = 0
        if -1 < index < len(self.__list):
            rosterTypeID = self.__list[index]['data']
        return rosterTypeID

    def getIndexByTypeID(self, rosterTypeID):
        found = 0
        for index, item in enumerate(self.__list[1:]):
            if item['data'] == rosterTypeID:
                found = index + 1
                break

        return found


class SortiesDataProvider(SortableDAAPIDataProvider):

    def __init__(self):
        super(SortiesDataProvider, self).__init__()
        self._list = []
        self._listMapping = {}
        self._mapping = {}
        self._selectedID = None
        return

    @unitFunctionalProperty
    def unitFunctional(self):
        return None

    @property
    def collection(self):
        return self._list

    def emptyItem(self):
        return None

    def clear(self):
        self._list = []
        self._listMapping.clear()
        self._mapping.clear()
        self._selectedID = None
        return

    def fini(self):
        self.clear()
        self._dispose()

    def getSelectedIdx(self):
        if self._selectedID in self._mapping:
            return self._mapping[self._selectedID]
        return -1

    def setSelectedID(self, id):
        self._selectedID = id

    def getVO(self, index):
        vo = None
        if index > -1:
            try:
                vo = self.sortedCollection[index]
            except IndexError:
                LOG_ERROR('Item not found', index)

        return vo

    def getUnitVO(self, clientIdx):
        return makeSortieShortVO(self.unitFunctional, unitIdx=clientIdx)

    def getUnitMaxLevel(self, clientIdx):
        return getUnitMaxLevel(self.unitFunctional, unitIdx=clientIdx)

    def buildList(self, cache):
        self.clear()
        for index, item in enumerate(cache.getIterator()):
            self._list.append(self._makeVO(index, item))
            self._listMapping[item.getID()] = index

        self._rebuildMapping()

    def rebuildList(self, cache):
        self.buildList(cache)
        self.refresh()

    def updateItem(self, cache, item):
        sortieID = item.getID()
        if sortieID in self._mapping and item.filter(cache.getRosterTypeID()):
            index = self._listMapping[sortieID]
            try:
                self._list[index] = self._makeVO(index, item)
            except IndexError:
                LOG_ERROR('Item is not found', sortieID, index)

            self.flashObject.update([index])
            self._rebuildMapping()
            return self.getSelectedIdx()
        else:
            self.rebuildList(cache)
            return None

    def removeItem(self, cache, removedID):
        if removedID in self._mapping:
            dropSelection = removedID == self._selectedID
            self.rebuildList(cache)
            return dropSelection
        return False

    def pyGetSelectedIdx(self):
        return self.getSelectedIdx()

    def pySortOn(self, fields, order):
        super(SortiesDataProvider, self).pySortOn(fields, order)
        self._rebuildMapping()
        self.refresh()

    @storage_getter('users')
    def usersStorage(self):
        return None

    def _rebuildMapping(self):
        self._mapping = dict(map(lambda item: (item[1]['sortieID'], item[0]), enumerate(self.sortedCollection)))

    def _makeVO(self, index, item):
        isInBattle = item.getFlags() & UNIT_FLAGS.IN_ARENA > 0 or item.getFlags() & UNIT_FLAGS.IN_QUEUE > 0 or item.getFlags() & UNIT_FLAGS.IN_SEARCH > 0
        user = self.usersStorage.getUser(item.getCommanderDatabaseID())
        scheme = g_settings.getColorScheme('rosters')
        if user:
            colors = scheme.getColors(user.getGuiType())
            color = colors[0] if user.isOnline() else colors[1]
        else:
            colors = scheme.getColors(USER_GUI_TYPE.OTHER)
            color = colors[1]
        return {'sortieID': item.getID(),
         'creatorName': item.getCommanderFullName(),
         'divisionName': I18N_FORTIFICATIONS.sortie_division_name(item.getDivisionName()),
         'description': text_styles.standard(item.getDescription()),
         'descriptionForTT': item.getDescription(),
         'isInBattle': isInBattle,
         'division': item.getDivision(),
         'playersCount': item.itemData.count,
         'commandSize': item.itemData.maxCount,
         'rallyIndex': index,
         'igrType': item.getIgrType(),
         'color': color}


class IntelligenceDataProvider(SortableDAAPIDataProvider):

    def __init__(self):
        super(IntelligenceDataProvider, self).__init__()
        self._list = []
        self._listMapping = {}
        self.__mapping = {}
        self.__selectedID = None
        return

    @unitFunctionalProperty
    def unitFunctional(self):
        return None

    @property
    def collection(self):
        return self._list

    def emptyItem(self):
        return None

    def clear(self):
        self._list = []
        self._listMapping.clear()
        self.__mapping.clear()
        self.__selectedID = None
        return

    def fini(self):
        self.clear()
        self._dispose()

    def getSelectedIdx(self):
        if self.__selectedID in self.__mapping:
            return self.__mapping[self.__selectedID]
        return -1

    def setSelectedID(self, id):
        self.__selectedID = id

    def getVO(self, index):
        vo = None
        if index > -1:
            try:
                vo = self.sortedCollection[index]
            except IndexError:
                LOG_ERROR('Item not found', index)

        return vo

    def buildList(self, cache):
        self.clear()
        favorites = cache.getFavorites()
        for index, item in enumerate(cache.getIterator()):
            self._list.append(self._makeVO(index, item, favorites))
            self._listMapping[item.getClanDBID()] = index

        self.__rebuildMapping()

    def rebuildList(self, cache):
        self.buildList(cache)
        self.refresh()

    def refreshItem(self, cache, clanDBID):
        isSelected = self.__selectedID == clanDBID
        self.buildList(cache)
        if isSelected and clanDBID not in self.__mapping:
            return True
        return False

    def pyGetSelectedIdx(self):
        return self.getSelectedIdx()

    def pySortOn(self, fields, order):
        super(IntelligenceDataProvider, self).pySortOn(fields, order)
        self.__rebuildMapping()
        self.refresh()

    def deleteBrackets(self, element):
        element['clanTag'] = element['clanTag'][1:-1]
        return element

    def addBrackets(self, element):
        element['clanTag'] = '[%s]' % element['clanTag']
        return element

    @property
    def sortedCollection(self):
        return map(self.addBrackets, sortByFields(self._sort, map(self.deleteBrackets, self.collection)))

    def __rebuildMapping(self):
        self.__mapping = dict(map(lambda item: (item[1]['clanID'], item[0]), enumerate(self.sortedCollection)))

    def _makeVO(self, index, item, favorites):
        timestamp = item.getAvailability()
        defHour, defMin = item.getDefHourFor(timestamp)
        defenceStart = time_utils.getTimeForLocal(timestamp, defHour, defMin)
        defenceFinish = defenceStart + time_utils.ONE_HOUR
        defenceTime = '%s - %s' % (BigWorld.wg_getShortTimeFormat(defenceStart), BigWorld.wg_getShortTimeFormat(defenceFinish))
        return {'clanID': item.getClanDBID(),
         'levelIcon': getIconLevel(item.getLevel()),
         'clanTag': '[%s]' % item.getClanAbbrev(),
         'defenceTime': defenceTime,
         'defenceStartTime': int('%02d%02d' % (defHour, defMin)),
         'avgBuildingLvl': round(item.getAvgBuildingLevel(), 1),
         'isFavorite': item.getClanDBID() in favorites,
         'clanLvl': item.getLevel()}


class FortBattlesDataProvider(SortableDAAPIDataProvider):

    class DAY_OF_BATTLE(CONST_CONTAINER):
        TODAY = 0
        TOMORROW = 1
        OTHER = 2

    def __init__(self):
        super(FortBattlesDataProvider, self).__init__()
        self._list = []
        self._listMapping = {}
        self._mapping = {}
        self._selectedID = None
        return

    @unitFunctionalProperty
    def unitFunctional(self):
        return None

    @property
    def collection(self):
        return self._list

    def emptyItem(self):
        return None

    def clear(self):
        self._list = []
        self._listMapping.clear()
        self._mapping.clear()
        self._selectedID = None
        return

    def fini(self):
        self.clear()
        self._dispose()

    def getSelectedIdx(self):
        if self._selectedID in self._mapping:
            return self._mapping[self._selectedID]
        return -1

    def setSelectedID(self, id):
        self._selectedID = id

    def getVO(self, index):
        vo = None
        if index > -1:
            try:
                vo = self.sortedCollection[index]
            except IndexError:
                LOG_ERROR('Item not found', index)

        return vo

    def getUnitVO(self, clientIdx):
        return makeFortBattleShortVO(self.unitFunctional, unitIdx=clientIdx)

    def getUnitMaxLevel(self, clientIdx):
        return getUnitMaxLevel(self.unitFunctional, unitIdx=clientIdx)

    def buildList(self, cache):
        self.clear()
        if not BigWorld.player().isLongDisconnectedFromCenter:
            for index, (item, battleItem) in enumerate(cache.getIterator()):
                self._list.append(self._makeVO(index, item, battleItem))
                self._listMapping[item.getBattleID()] = index

        self._rebuildMapping()

    def rebuildList(self, cache):
        self.buildList(cache)
        self.refresh()

    def updateItem(self, cache, item, battleItem):
        fortBattleID = item.getBattleID()
        if fortBattleID in self._mapping and item.filter():
            index = self._listMapping[fortBattleID]
            try:
                self._list[index] = self._makeVO(index, item, battleItem)
            except IndexError:
                LOG_ERROR('Item is not found', fortBattleID, index)

            self.flashObject.update([index])
            self._rebuildMapping()
            return self.getSelectedIdx()
        else:
            self.rebuildList(cache)
            return None

    def removeItem(self, cache, removedID):
        if removedID in self._mapping:
            dropSelection = removedID == self._selectedID
            self.rebuildList(cache)
            return dropSelection
        return False

    def pyGetSelectedIdx(self):
        return self.getSelectedIdx()

    def pySortOn(self, fields, order):
        super(FortBattlesDataProvider, self).pySortOn(fields, order)
        self._rebuildMapping()
        self.refresh()

    def _rebuildMapping(self):
        self._mapping = dict(map(lambda item: (item[1]['sortieID'][0], item[0]), enumerate(self.sortedCollection)))

    def _makeVO(self, index, item, battleItem):
        if item.getType() == BATTLE_ITEM_TYPE.DEFENCE:
            battleType = FORTIFICATION_ALIASES.CLAN_BATTLE_DEFENCE
        else:
            battleType = FORTIFICATION_ALIASES.CLAN_BATTLE_OFFENCE
        if battleItem:
            startTime = battleItem.getRoundStartTime()
            startTimeLeft = battleItem.getRoundStartTimeLeft()
            isBattleRound = battleItem.isBattleRound()
        else:
            startTime = item.getStartTime()
            startTimeLeft = item.getStartTimeLeft()
            isBattleRound = False
        dayOfBattle = self.DAY_OF_BATTLE.TODAY
        if startTimeLeft > time_utils.QUARTER_HOUR:
            stateOfBattle = FORTIFICATION_ALIASES.CLAN_BATTLE_BATTLE_TOMORROW
            if time_utils.isTimeThisDay(startTime):
                stateOfBattle = FORTIFICATION_ALIASES.CLAN_BATTLE_BATTLE_TODAY
            elif time_utils.isTimeNextDay(startTime):
                dayOfBattle = self.DAY_OF_BATTLE.TOMORROW
            else:
                dayOfBattle = self.DAY_OF_BATTLE.OTHER
        elif startTimeLeft > 0 and not isBattleRound:
            stateOfBattle = FORTIFICATION_ALIASES.CLAN_BATTLE_BEGINS
        else:
            stateOfBattle = FORTIFICATION_ALIASES.CLAN_BATTLE_IS_IN_BATTLE
        return {'sortieID': (item.getBattleID(), item.getPeripheryID()),
         'battleType': battleType,
         'battleName': self.__makeBattleName(item, battleType),
         'battleDirection': self.__makeBattleDirection(item),
         'dayOfBattle': self.__makeDayOfBattle(dayOfBattle, startTime),
         'beforeBegins': self.__makeTimeOfBattle(item, battleItem, stateOfBattle),
         'stateOfBattle': stateOfBattle,
         'startTimeLeft': startTimeLeft,
         'direction': item.getDirection()}

    def __makeBattleName(self, item, battleType):
        _, clanAbbrev, _ = item.getOpponentClanInfo()
        clanName = '[%s]' % clanAbbrev
        result = i18n.makeString(I18N_FORTIFICATIONS.fortclanbattlelist_renderbattlename(battleType), clanName=clanName)
        result = text_styles.middleTitle(result)
        return result

    def __makeBattleDirection(self, item):
        direction = i18n.makeString('#fortifications:General/directionName%d' % item.getDirection())
        directionName = i18n.makeString(I18N_FORTIFICATIONS.FORTCLANBATTLELIST_RENDERDIRECTION, directionName=direction)
        return text_styles.standard(directionName)

    def __makeDayOfBattle(self, dayOfBattle, timestamp):
        if dayOfBattle == self.DAY_OF_BATTLE.TODAY:
            availability = i18n.makeString(I18N_FORTIFICATIONS.fortclanbattlelist_renderdayofbattle('today'))
        elif dayOfBattle == self.DAY_OF_BATTLE.TOMORROW:
            availability = i18n.makeString(I18N_FORTIFICATIONS.fortclanbattlelist_renderdayofbattle('tomorrow'))
        else:
            availability = BigWorld.wg_getShortDateFormat(timestamp)
        return text_styles.main(availability)

    def __makeTimeOfBattle(self, item, battleItem, currentState):
        result = {}
        if currentState == FORTIFICATION_ALIASES.CLAN_BATTLE_IS_IN_BATTLE:
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_BATTLERESULTICON_1, 16, 16, -3, 0)
            formattedText = text_styles.error(i18n.makeString(I18N_FORTIFICATIONS.FORTCLANBATTLELIST_RENDERCURRENTTIME_ISBATTLE))
            result['text'] = icon + ' ' + formattedText
        elif currentState == FORTIFICATION_ALIASES.CLAN_BATTLE_BEGINS:
            battleID = item.getBattleID()
            timer = {}
            htmlFormatter = text_styles.alert('###')
            locale = text_styles.main(i18n.makeString(I18N_FORTIFICATIONS.FORTCLANBATTLELIST_RENDERCURRENTTIME_BEFOREBATTLE))
            result['text'] = locale
            if battleItem:
                startTimeLeft = battleItem.getRoundStartTimeLeft()
            else:
                startTimeLeft = item.getStartTimeLeft()
            timer['useUniqueIdentifier'] = True
            timer['uniqueIdentifier'] = battleID
            timer['deltaTime'] = startTimeLeft
            timer['htmlFormatter'] = htmlFormatter
            timer['timerDefaultValue'] = '00'
            result['timer'] = timer
        else:
            lastBattleTimeUserString = '%s - %s' % (BigWorld.wg_getShortTimeFormat(item.getStartTime()), BigWorld.wg_getShortTimeFormat(item.getFinishTime()))
            result['text'] = text_styles.main(lastBattleTimeUserString)
        return result
