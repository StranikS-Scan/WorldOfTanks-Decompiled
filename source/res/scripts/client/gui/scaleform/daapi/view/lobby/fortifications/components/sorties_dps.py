# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/sorties_dps.py
import random
import BigWorld
import time
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.fort_text import MAIN_TEXT, ALERT_TEXT, MIDDLE_TITLE, STANDARD_TEXT, ERROR_TEXT
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import getUnitMaxLevel, makeFortBattleShortVO
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeSortieShortVO
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider, SortableDAAPIDataProvider
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as I18N_FORTIFICATIONS, FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties, UtilsManager
from gui.prb_control.items.sortie_items import getDivisionsOrderData
from gui.prb_control.prb_helpers import unitFunctionalProperty
from gui.shared.fortifications.fort_seqs import getDivisionSettings
from helpers import i18n, time_utils

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

    def getUnitVO(self, clientIdx):
        return makeSortieShortVO(self.unitFunctional, unitIdx=clientIdx)

    def getUnitMaxLevel(self, clientIdx):
        return getUnitMaxLevel(self.unitFunctional, unitIdx=clientIdx)

    def buildList(self, cache):
        self.clear()
        if not BigWorld.player().isLongDisconnectedFromCenter:
            for index, item in enumerate(cache.getIterator()):
                self._list.append(self._makeVO(index, item))
                self._listMapping[item.getID()] = index

        self.__rebuildMapping()

    def rebuildList(self, cache):
        self.buildList(cache)
        self.refresh()

    def updateItem(self, cache, item):
        sortieID = item.getID()
        if sortieID in self.__mapping and item.filter(cache.getRosterTypeID()):
            index = self._listMapping[sortieID]
            try:
                self._list[index] = self._makeVO(index, item)
            except IndexError:
                LOG_ERROR('Item is not found', sortieID, index)

            self.flashObject.update([index])
            self.__rebuildMapping()
            return self.getSelectedIdx()
        else:
            self.rebuildList(cache)
            return None

    def removeItem(self, cache, removedID):
        if removedID in self.__mapping:
            dropSelection = removedID == self.__selectedID
            self.rebuildList(cache)
            return dropSelection
        return False

    def pyGetSelectedIdx(self):
        return self.getSelectedIdx()

    def pySortOn(self, fields, order):
        super(SortiesDataProvider, self).pySortOn(fields, order)
        self.__rebuildMapping()
        self.refresh()

    def __rebuildMapping(self):
        self.__mapping = dict(map(lambda item: (item[1]['sortieID'], item[0]), enumerate(self.sortedCollection)))

    def _makeVO(self, index, item):
        return {'sortieID': item.getID(),
         'creatorName': item.getCommanderFullName(),
         'divisionName': I18N_FORTIFICATIONS.sortie_division_name(item.getDivisionName()),
         'division': item.getDivision(),
         'playersCount': item.itemData.count,
         'commandSize': item.itemData.maxCount,
         'rallyIndex': index,
         'igrType': item.getIgrType()}


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

    def isEmpty(self):
        return len(self._list) == 0

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

    def pyGetSelectedIdx(self):
        return self.getSelectedIdx()

    def pySortOn(self, fields, order):
        super(IntelligenceDataProvider, self).pySortOn(fields, order)
        self.__rebuildMapping()
        self.refresh()

    def __rebuildMapping(self):
        self.__mapping = dict(map(lambda item: (item[1]['clanID'], item[0]), enumerate(self.sortedCollection)))

    def _makeVO(self, index, item, favorites):
        isWarDeclared = False
        day, timestamp = item.getAvailabilityFromTomorrow()
        if isWarDeclared or day > 14:
            availability = i18n.makeString(FORTIFICATIONS.FORTINTELLIGENCE_DATE_NOTAVAILABLE)
        elif day == 0:
            availability = i18n.makeString(FORTIFICATIONS.FORTINTELLIGENCE_DATE_TOMORROW)
        else:
            availability = BigWorld.wg_getShortDateFormat(timestamp)
        defenceStart, defenceFinish = item.getDefencePeriod()
        if defenceStart and defenceFinish:
            defenceTime = '%s - %s' % (BigWorld.wg_getShortTimeFormat(defenceStart), BigWorld.wg_getShortTimeFormat(defenceFinish))
        else:
            defenceTime = ''
        return {'clanID': item.getClanDBID(),
         'levelIcon': '../maps/icons/filters/levels/level_%s.png' % item.getLevel(),
         'clanTag': '[%s]' % item.getClanAbbrev(),
         'defenceTime': defenceTime,
         'defenceStartTime': defenceStart,
         'avgBuildingLvl': round(item.getAvgBuildingLevel(), 1),
         'availability': availability,
         'availabilityDays': day,
         'isFavorite': item.getClanDBID() in favorites,
         'clanLvl': item.getLevel()}


class ClanBattlesDataProvider(SortiesDataProvider):

    def getUnitVO(self, clientIdx):
        return makeFortBattleShortVO(self.unitFunctional, unitIdx=clientIdx)

    def _makeVO(self, index, item):
        if item.isDefence():
            battleType = FORTIFICATION_ALIASES.CLAN_BATTLE_DEFENCE
        else:
            battleType = FORTIFICATION_ALIASES.CLAN_BATTLE_OFFENCE
        day, timestamp = item.getAvailability()
        startTimeLeft = item.getAttackTimeLeft()
        if day > 0:
            stateOfBattle = FORTIFICATION_ALIASES.CLAN_BATTLE_BATTLE_TOMORROW
        elif startTimeLeft > time_utils.QUARTER_HOUR:
            stateOfBattle = FORTIFICATION_ALIASES.CLAN_BATTLE_BATTLE_TODAY
        elif startTimeLeft > 0:
            stateOfBattle = FORTIFICATION_ALIASES.CLAN_BATTLE_BEGINS
        else:
            stateOfBattle = FORTIFICATION_ALIASES.CLAN_BATTLE_IS_IN_BATTLE
        return {'sortieID': (item.getID(), item.getPeripheryID()),
         'battleType': battleType,
         'battleName': self.__makeBattleName(item, battleType),
         'battleDirection': self.__makeBattleDirection(item),
         'dayOfBattle': self.__makeDayOfBattle(day, timestamp),
         'beforeBegins': self.__makeTimeOfBattle(item, stateOfBattle),
         'stateOfBattle': stateOfBattle}

    def __makeBattleName(self, item, battleType):
        _, clanAbbrev, _ = item.getOpponentClanInfo()
        clanName = '[%s]' % clanAbbrev
        result = i18n.makeString(FORTIFICATIONS.fortclanbattlelist_renderbattlename(battleType), clanName=clanName)
        result = fort_text.getText(MIDDLE_TITLE, result)
        return result

    def __makeBattleDirection(self, item):
        direction = i18n.makeString('#fortifications:General/directionName%d' % item.getDirection())
        directionName = i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_RENDERDIRECTION, directionName=direction)
        return fort_text.getText(STANDARD_TEXT, directionName)

    def __makeDayOfBattle(self, day, timestamp):
        if day == 0:
            availability = i18n.makeString(FORTIFICATIONS.fortclanbattlelist_renderdayofbattle('today'))
        elif day == 1:
            availability = i18n.makeString(FORTIFICATIONS.fortclanbattlelist_renderdayofbattle('tomorrow'))
        else:
            availability = BigWorld.wg_getShortDateFormat(timestamp)
        return fort_text.getText(MAIN_TEXT, availability)

    def __makeTimeOfBattle(self, item, currentTestState):
        result = {}
        if currentTestState == FORTIFICATION_ALIASES.CLAN_BATTLE_IS_IN_BATTLE:
            icon = RES_ICONS.MAPS_ICONS_LIBRARY_BATTLERESULTICON_1
            units = UtilsManager()
            icon = units.getHtmlIconText(ImageUrlProperties(icon, 16, 16, -3, 0))
            formattedText = fort_text.getText(ERROR_TEXT, i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_RENDERCURRENTTIME_ISBATTLE))
            result['text'] = icon + ' ' + formattedText
        elif currentTestState == FORTIFICATION_ALIASES.CLAN_BATTLE_BEGINS:
            timer = {}
            htmlFormatter = fort_text.getText(ALERT_TEXT, '###')
            locale = i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_RENDERCURRENTTIME_BEFOREBATTLE)
            locale = fort_text.getText(MAIN_TEXT, locale)
            result['text'] = locale
            timer['deltaTime'] = item.getAttackTimeLeft()
            timer['htmlFormatter'] = htmlFormatter
            result['timer'] = timer
        else:
            lastBattleTimeUserString = '%s - %s' % (BigWorld.wg_getShortTimeFormat(item.getAttackTime()), BigWorld.wg_getShortTimeFormat(item.getAttackFinishTime()))
            result['text'] = fort_text.getText(MAIN_TEXT, lastBattleTimeUserString)
        i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_RENDERCURRENTTIME_BEFOREBATTLE)
        return result
