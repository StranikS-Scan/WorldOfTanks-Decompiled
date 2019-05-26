# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/filters/filter_by_nation.py
import nations
from gui import GUI_NATIONS
from gui.Scaleform.daapi.view.meta.ItemsWithTypeAndNationFilterTabViewMeta import ItemsWithTypeAndNationFilterTabViewMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA

class FiltrableInventoryCategoryByNationTabView(ItemsWithTypeAndNationFilterTabViewMeta):

    def __init__(self):
        super(FiltrableInventoryCategoryByNationTabView, self).__init__()
        self.__selectedNationID = nations.NONE_INDEX

    def selectNation(self, id):
        self.__selectedNationID = id
        self._buildItems()

    def resetFilter(self):
        self.__selectedNationID = nations.NONE_INDEX
        super(FiltrableInventoryCategoryByNationTabView, self).resetFilter()

    def _parseLoadedFilters(self, filterDict):
        self.__selectedNationID = filterDict['nationID']
        super(FiltrableInventoryCategoryByNationTabView, self)._parseLoadedFilters(filterDict)

    def _prepareDataForFilterSaving(self):
        data = super(FiltrableInventoryCategoryByNationTabView, self)._prepareDataForFilterSaving()
        data['nationID'] = self.__selectedNationID
        return data

    def _initFilter(self):
        super(FiltrableInventoryCategoryByNationTabView, self)._initFilter()
        nationsIds = [{'id': nations.NONE_INDEX,
          'label': backport.text(R.strings.storage.crewBooks.filters.nation.all())}]
        for name in GUI_NATIONS:
            if name in nations.AVAILABLE_NAMES:
                nationsIds.append({'id': nations.INDICES[name],
                 'label': backport.text(R.strings.menu.nations.dyn(name)())})

        self.as_initNationFilterS({'enabled': True,
         'selectedIndex': 0,
         'data': nationsIds})

    def _shouldShowCounter(self):
        return super(FiltrableInventoryCategoryByNationTabView, self)._shouldShowCounter() or self.__selectedNationID != nations.NONE_INDEX

    def _getFilteredCriteria(self):
        criteria = super(FiltrableInventoryCategoryByNationTabView, self)._getFilteredCriteria()
        if self.__selectedNationID != nations.NONE_INDEX:
            criteria |= REQ_CRITERIA.CREW_ITEM.NATIONS([self.__selectedNationID])
        return criteria
