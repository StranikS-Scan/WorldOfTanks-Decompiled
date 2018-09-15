# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_decorations_popover.py
from itertools import chain
from account_helpers.AccountSettings import AccountSettings, NY_DECORATIONS_POPOVER_FILTER_1
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.lobby.ny.ny_common import getFilterRadioButtons, SORTED_NATIONS_SETTINGS
from gui.Scaleform.daapi.view.meta.NYDecorationsPopoverMeta import NYDecorationsPopoverMeta
from gui.Scaleform.locale.NY import NY
from gui.Scaleform.genConsts.NY_CONSTANTS import NY_CONSTANTS
from gui.server_events.events_dispatcher import showMissions
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.new_year import INewYearController, ICustomizableObjectsManager
from items.new_year_types import g_cache
from new_year.new_year_sounds import NYSoundEvents
from items.new_year_types import INVALID_TOY_ID
from new_year.mappings import AnchorNames
_POPOVER_TITLES = (NY.POPOVER_DECORATIONS_HEADER_TOP,
 NY.POPOVER_DECORATIONS_HEADER_TREE_HANDING,
 NY.POPOVER_DECORATIONS_HEADER_TREE_HANDING,
 NY.POPOVER_DECORATIONS_HEADER_TREE_HANDING,
 NY.POPOVER_DECORATIONS_HEADER_TREE_HANDING,
 NY.POPOVER_DECORATIONS_HEADER_TREE_GARLAND,
 NY.POPOVER_DECORATIONS_HEADER_TREE_GARLAND,
 NY.POPOVER_DECORATIONS_HEADER_UNDER_TREE,
 NY.POPOVER_DECORATIONS_HEADER_UNDER_TREE,
 NY.POPOVER_DECORATIONS_HEADER_SNOWMAN,
 NY.POPOVER_DECORATIONS_HEADER_HOUSE,
 NY.POPOVER_DECORATIONS_HEADER_HOUSE_LIGHT,
 NY.POPOVER_DECORATIONS_HEADER_LAMPPOSTS)
_PLACED_TOY_INDEX = 0
_FILTER_SETTINGS_NAMES_TO_ID = {name:idx for idx, name in enumerate(SORTED_NATIONS_SETTINGS, 1)}

class NYDecorationsPopover(NYDecorationsPopoverMeta):
    newYearController = dependency.descriptor(INewYearController)
    _customizableObjMgr = dependency.descriptor(ICustomizableObjectsManager)

    def __init__(self, ctx):
        super(NYDecorationsPopover, self).__init__()
        self.__slotID = -1
        self.__arrowDirection = -1
        if 'data' in ctx:
            self.__slotID = ctx['data'].slotId
            self.__arrowDirection = ctx['data'].arrowDirection
        self.__defaultLevel, self.__defaultNation = AccountSettings.getFilterDefault(NY_DECORATIONS_POPOVER_FILTER_1)
        self.__filterLevel, self.__filterNation = AccountSettings.getFilter(NY_DECORATIONS_POPOVER_FILTER_1)
        self.__toysCount = 0
        self.__seenToys = {}

    def onSlotClick(self, toyID, toyIndex):
        LOG_DEBUG('toyIndex: ' + str(toyIndex))
        toyID = int(toyID)
        placedToy = self.newYearController.getPlacedToy(self.__slotID)
        if placedToy.id == toyID and toyIndex == _PLACED_TOY_INDEX:
            toyID = INVALID_TOY_ID
        else:
            objectName = g_cache.slots[self.__slotID].object
            toyDescr = g_cache.toys.get(toyID, None)
            if toyDescr is not None and toyDescr.type == NY_CONSTANTS.SLOT_TYPE_LAMP and objectName == AnchorNames.HOUSE:
                NYSoundEvents.playSound(NYSoundEvents.ON_HOUSE_LAMP_SET)
            else:
                NYSoundEvents.playSound(NYSoundEvents.ON_TOY_HANG.get(objectName, None))
        if self.newYearController.placeToy(toyID, self.__slotID):
            self._updateToysData()
        self.destroy()
        return

    def goToTasks(self):
        self._customizableObjMgr.switchTo(None, showMissions)
        self.destroy()
        return

    def onResetFilterClick(self):
        self.onFilterChange(self.__defaultLevel, self.__defaultNation)

    def onFilterChange(self, level, nation):
        self.__filterLevel = int(level)
        self.__filterNation = int(nation)
        AccountSettings.setFilter(NY_DECORATIONS_POPOVER_FILTER_1, (self.__filterLevel, self.__filterNation))
        self._updateToysData()

    def onHideNew(self, toyId, index):
        if toyId in self.__seenToys:
            self.__seenToys[toyId] += 1
        else:
            self.__seenToys[toyId] = 1

    def _updateToysData(self):
        reinit = self.__toysCount == 0
        self.as_setDataS(self.__makeVO(), reinit)

    def _onToysBreak(self, toyIndexes, fromSlot):
        if toyIndexes and not fromSlot:
            self.as_breakToyS(toyIndexes[0])

    def _onToysBreakFailed(self):
        self.as_breakToyFailS()

    def _onToysBreakStarted(self):
        self.as_breakToyStartS()

    def _populate(self):
        super(NYDecorationsPopover, self)._populate()
        self.newYearController.onInventoryUpdated += self._updateToysData
        self.newYearController.onToysBreak += self._onToysBreak
        self.newYearController.onToysBreakFailed += self._onToysBreakFailed
        self.newYearController.onToysBreakStarted += self._onToysBreakStarted
        self.as_setupS(self.__arrowDirection)
        self.as_initFilterS(getFilterRadioButtons())
        self._updateToysData()
        self.__seenToys = {}

    def _dispose(self):
        super(NYDecorationsPopover, self)._dispose()
        self.newYearController.onInventoryUpdated -= self._updateToysData
        self.newYearController.onToysBreak -= self._onToysBreak
        self.newYearController.onToysBreakFailed -= self._onToysBreakFailed
        self.newYearController.onToysBreakStarted -= self._onToysBreakStarted
        if self.__seenToys:
            self.newYearController.markToysAsSeen(self.__seenToys.items())
            self.__seenToys = {}

    def __filterToysList(self, toys):
        if self.__filterLevel != self.__defaultLevel:
            toys = filter(lambda item: 2 ** (item.rank - 1) & self.__filterLevel, toys)
        if self.__filterNation != self.__defaultNation:
            toys = filter(lambda item: _FILTER_SETTINGS_NAMES_TO_ID[item.setting] == self.__filterNation, toys)
        toys.sort(key=lambda t: [-t.item.rank, self.newYearController.getSettingIndexInNationsOrder(t.item.setting)])
        return toys

    def __makeVO(self):
        toys = self.newYearController.getToysForSlot(self.__slotID)
        self.__toysCount = toysTotal = sum((toy.count for toy in toys))
        toys = self.__filterToysList(toys)
        placedToy = self.newYearController.getPlacedToy(self.__slotID)
        toysFiltered = sum((toy.count for toy in toys))
        toysFilteredStr = text_styles.error('0') if toysFiltered == 0 else text_styles.stats(str(toysFiltered))
        toysAmountStr = text_styles.main('{} {} / {}'.format(_ms(NY.POPOVER_DECORATIONS_FILTER_LABEL), toysFilteredStr, toysTotal))
        toysVO = []
        if placedToy.id != INVALID_TOY_ID:
            toysTotal += 1
            toysVO = self.__makeItemVO(placedToy, self.__slotID, True)
        toysVO.extend(list(chain.from_iterable((self.__makeItemVO(item, self.__slotID, False, item.count) for item in toys))))
        data = {'title': _POPOVER_TITLES[self.__slotID],
         'decorationsAmountText': toysAmountStr,
         'isFilterActive': self.__filterLevel != self.__defaultLevel or self.__filterNation != self.__defaultNation,
         'nation': self.__filterNation,
         'level': self.__filterLevel,
         'toys': toysVO,
         'allToys': toysTotal}
        return data

    def __makeItemVO(self, item, slotID, isCurrent=False, count=1):
        res = []
        for i in range(count):
            res.append({'id': item.id,
             'slotID': slotID,
             'icon': item.icon,
             'level': item.rank,
             'isNew': item.newCount > i,
             'isCanUpdateNew': True,
             'canShowContextMenu': True,
             'settings': item.setting,
             'isCurrent': isCurrent})

        return res
