# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_craft_popover.py
from gui.Scaleform.daapi.view.lobby.ny.ny_common import getFilterRadioButtons, SORTED_NATIONS_SETTINGS
from gui.Scaleform.daapi.view.meta.NYCraftPopoverMeta import NYCraftPopoverMeta
from gui.Scaleform.genConsts.NY_CONSTANTS import NY_CONSTANTS
from items.new_year_types import MAX_TOY_RANK, TOY_TYPES, NATIONAL_SETTINGS
from helpers import dependency
from skeletons.new_year import INewYearUIManager
from debug_utils import LOG_DEBUG
TYPEDATA_TO_TYPE = {0: 'top',
 1: 'hanging',
 3: 'garland',
 2: 'gift',
 4: 'snowman',
 5: 'house_decoration',
 6: 'house_lamp',
 7: 'street_garland'}
NATION_DATA_TO_NATION = {0: NATIONAL_SETTINGS}
for idx, name in enumerate(SORTED_NATIONS_SETTINGS, 1):
    NATION_DATA_TO_NATION[idx] = (name,)

def typeDataToType(typeData):
    return TYPEDATA_TO_TYPE.get(typeData, None)


def levelDataToLevel(levelData):
    return levelData + 1


def nationDataToNation(nationData):
    return NATION_DATA_TO_NATION.get(nationData, None)


def typeToTypeData(typeInfo):
    for key, value in TYPEDATA_TO_TYPE.items():
        if value == typeInfo:
            return key

    return None


def levelToLevelData(levelInfo):
    return levelInfo - 1


def nationToNationData(nationInfo):
    for key, value in NATION_DATA_TO_NATION.items():
        if value == nationInfo:
            return key

    return None


class NYCraftPopover(NYCraftPopoverMeta):
    newYearUIManager = dependency.descriptor(INewYearUIManager)

    def __init__(self, _):
        self.__selectedLevelsData = [ 0 for _ in range(MAX_TOY_RANK) ]
        self.__selectedTypesData = [ 0 for _ in range(len(TOY_TYPES)) ]
        self.__selectedNationData = 0
        super(NYCraftPopover, self).__init__()

    def _populate(self):
        super(NYCraftPopover, self)._populate()
        self.__updateSelectionData()
        self.as_setDataS({'levels': self.__selectedLevelsData,
         'types': self.__selectedTypesData,
         'nationSelected': self.__selectedNationData,
         'settingsData': getFilterRadioButtons()})

    def filterChange(self, index, type):
        LOG_DEBUG('DAAPI filterChange', 'Index:', '{}'.format(index), ' Type:', type)
        if type == NY_CONSTANTS.TYPES_SECTION:
            self.__selectedTypesData[index] = int(not self.__selectedTypesData[index])
        elif type == NY_CONSTANTS.LEVELS_SECTION:
            self.__selectedLevelsData[index] = int(not self.__selectedLevelsData[index])
        elif type == NY_CONSTANTS.NATIONS_SECTION:
            self.__selectedNationData = index
        self.__updateToyFilter()

    def __updateToyFilter(self):
        filterData = dict()
        levels = list()
        for i in range(len(self.__selectedLevelsData)):
            if self.__selectedLevelsData[i]:
                levels.append(levelDataToLevel(i))

        filterData['levels'] = levels
        types = list()
        for i in range(len(self.__selectedTypesData)):
            if self.__selectedTypesData[i]:
                types.append(typeDataToType(i))

        filterData['types'] = types
        filterData['nations'] = nationDataToNation(self.__selectedNationData)
        self.newYearUIManager.setCraftPopoverFilter(filterData)

    def __updateSelectionData(self):
        filterData = self.newYearUIManager.getCraftPopoverFilter()
        if filterData is None:
            return
        else:
            self.__selectedLevelsData = [ 0 for _ in range(MAX_TOY_RANK) ]
            levelSettings = filterData.get('levels', None)
            if levelSettings is not None:
                for levelSetting in levelSettings:
                    self.__selectedLevelsData[levelToLevelData(levelSetting)] = 1

            self.__selectedTypesData = [ 0 for _ in range(len(TOY_TYPES)) ]
            typeSettings = filterData.get('types', None)
            if typeSettings is not None:
                for typeSetting in typeSettings:
                    self.__selectedTypesData[typeToTypeData(typeSetting)] = 1

            nationSetting = filterData.get('nations', None)
            if nationSetting is not None:
                self.__selectedNationData = nationToNationData(nationSetting)
            return
