# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/sorties_dps.py
import BigWorld
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import getUnitMaxLevel
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeSortieShortVO
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as I18N_FORTIFICATIONS
from gui.prb_control.items.sortie_items import getDivisionsOrderData
from gui.prb_control.prb_helpers import unitFunctionalProperty
from gui.shared.fortifications.fort_seqs import getDivisionSettings

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


class SortiesDataProvider(DAAPIDataProvider):

    def __init__(self):
        super(SortiesDataProvider, self).__init__()
        self.__list = []
        self.__mapping = {}
        self.__selectedIdx = None
        return

    @unitFunctionalProperty
    def unitFunctional(self):
        return None

    @property
    def collection(self):
        return self.__list

    def emptyItem(self):
        return None

    def clear(self):
        self.__list = []
        self.__mapping.clear()

    def fini(self):
        self.clear()
        self._dispose()

    def getSelectedIdx(self):
        return self.__selectedIdx

    def getVO(self, index):
        vo = None
        if index > -1:
            try:
                vo = self.__list[index]
            except IndexError:
                LOG_ERROR('Item not found', index)

        return vo

    def getUnitVO(self, clientIdx):
        return makeSortieShortVO(self.unitFunctional, unitIdx=clientIdx)

    def getUnitMaxLevel(self, clientIdx):
        return getUnitMaxLevel(self.unitFunctional, unitIdx=clientIdx)

    def buildList(self, cache):
        selectedID = cache.getSelectedID()
        self.__selectedIdx = -1
        self.clear()
        if not BigWorld.player().isLongDisconnectedFromCenter:
            for index, item in enumerate(cache.getIterator()):
                sortieID = item.getID()
                self.__list.append(self._makeVO(index, item))
                self.__mapping[sortieID] = index

        self.__mapping = dict(map(lambda item: (item[1]['sortieID'], item[0]), enumerate(self.__list)))
        if selectedID in self.__mapping:
            self.__selectedIdx = self.__mapping[selectedID]
        return self.__selectedIdx

    def rebuildList(self, cache):
        self.buildList(cache)
        self.refresh()
        return self.__selectedIdx

    def updateItem(self, cache, item):
        sortieID = item.getID()
        if sortieID in self.__mapping:
            index = self.__mapping[sortieID]
            try:
                self.__list[index] = self._makeVO(index, item)
            except IndexError:
                LOG_ERROR('Item is not found', sortieID, index)

            self.flashObject.update([index])
        else:
            self.rebuildList(cache)
        return self.__selectedIdx

    def removeItem(self, cache, removedID):
        if removedID in self.__mapping:
            self.rebuildList(cache)
        return self.__selectedIdx

    def _makeVO(self, index, item):
        return {'sortieID': item.getID(),
         'creatorName': item.getCommanderFullName(),
         'divisionName': I18N_FORTIFICATIONS.sortie_division_name(item.getDivisionName()),
         'playerCount': item.itemData.count,
         'commandSize': item.itemData.maxCount,
         'rallyIndex': index,
         'igrType': item.getIgrType()}
