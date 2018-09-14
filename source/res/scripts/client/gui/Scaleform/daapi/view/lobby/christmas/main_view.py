# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/christmas/main_view.py
from collections import defaultdict
import ChristmassTreeManager as _ctm
import constants
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CHTISTMAS_VIEW_TAB
from adisp import process
from christmas_shared import TOY_TYPE_ID_TO_NAME, TOY_TYPE, TOY_TYPE_NAMES, TREE_DECORATIONS, TANK_DECORATIONS, EVENT_STATE
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.ChristmasMainViewMeta import ChristmasMainViewMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.genConsts.CHRISTMAS_ALIASES import CHRISTMAS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.CHRISTMAS import CHRISTMAS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.christmas.christmas_controller import g_christmasCtrl
from gui.christmas.christmas_items import NY_OBJECT_TYPE, NY_OBJECT_TO_TOY_TYPE
from gui.server_events.events_dispatcher import showEventsWindow
from gui.shared import events, event_dispatcher
from gui.shared.SoundEffectsId import SoundEffectsId
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from gui.shared.events import OpenLinkEvent
from gui.shared.formatters import icons
from gui.shared.formatters import text_styles
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared.utils.functions import makeTooltip
from helpers import i18n, int2roman, dependency
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
SOUNDS_IDS = {TOY_TYPE_ID_TO_NAME[TOY_TYPE.GARLAND]: SoundEffectsId.XMAS_GARLAND,
 TOY_TYPE_ID_TO_NAME[TOY_TYPE.STANDING]: SoundEffectsId.XMAS_GIFT,
 TOY_TYPE_ID_TO_NAME[TOY_TYPE.TANK_CAMOUFLAGE]: SoundEffectsId.XMAS_TANK_CAMOUFLAGE,
 TOY_TYPE_ID_TO_NAME[TOY_TYPE.TANK_FRONT]: SoundEffectsId.XMAS_TANK_FRONT,
 TOY_TYPE_ID_TO_NAME[TOY_TYPE.TANK_TURRET]: SoundEffectsId.XMAS_TANK_TURRET,
 TOY_TYPE_ID_TO_NAME[TOY_TYPE.TANK_BOARD]: SoundEffectsId.XMAS_TANK_BOARD}
TOY_RANK_LIST = (1,
 2,
 3,
 4,
 5)
TABS_DATA = ({'id': NY_OBJECT_TYPE.TREE,
  'label': CHRISTMAS.CUSTOMIZATIONTAB_TREE_LABEL,
  'tooltip': TOOLTIPS.XMAS_CUSTOMIZATION_TAB_TREE}, {'id': NY_OBJECT_TYPE.TANK,
  'label': CHRISTMAS.CUSTOMIZATIONTAB_SNOWTANK_LABEL,
  'tooltip': TOOLTIPS.XMAS_CUSTOMIZATION_TAB_TANK})
ALCHEMY_RESULT_SLOT_ID = 22
ALCHEMY_NUM_CONVERTED_ITEMS = 5
ALCHEMY_NUM_OBTAINED_ITEMS = 1
CUSTOMIZATION_SLOTS_LINKAGES = {NY_OBJECT_TYPE.TREE: CHRISTMAS_ALIASES.TREE_SLOTS_LINKAGE,
 NY_OBJECT_TYPE.TANK: CHRISTMAS_ALIASES.TANK_SLOTS_LINKAGE}
CONVERSION_DECORATIONS = TREE_DECORATIONS + TANK_DECORATIONS

def _applyFilter(filters, filterId, filtersMap):
    filterValue = filtersMap[filterId]
    if filterValue in filters:
        filters.remove(filterValue)
    else:
        filters.add(filterValue)
    return filters


def _mergeDictValues(sourceDict, typeOfValues):
    result = typeOfValues()
    for val in sourceDict.values():
        result.update(val)

    return result


class ChristmasMainView(LobbySubView, ChristmasMainViewMeta):
    __background_alpha__ = 0.0
    __SWITCH_CAMERA_DELAY_FRAMES__ = 4
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ctx=None):
        super(ChristmasMainView, self).__init__(ctx)
        self.__rankFilters = defaultdict(set)
        self.__typeFilters = defaultdict(set)
        self.__slots = g_christmasCtrl.getSlots()
        self.__tmpStorage = None
        storedObjectType = AccountSettings.getSettings(CHTISTMAS_VIEW_TAB)
        self.__objectType = ctx is not None and ctx.get('objectType') or storedObjectType
        if self.__objectType != storedObjectType:
            AccountSettings.setSettings(CHTISTMAS_VIEW_TAB, self.__objectType)
        self.__alchemySourceIds = [None] * 5
        self.__alchemyIsActive = False
        self.__alchemyRankFilters = set()
        self.__alchemyTypeFilters = set()
        self.__selected3DEntity = None
        self.__isCursorOver3dScene = False
        self.__prevRating = -1
        return

    def moveItem(self, srcSlotId, targetSlotId):
        if self.__alchemyIsActive:
            srcItemId = self.__alchemySourceIds[srcSlotId]
            targetItemId = self.__alchemySourceIds[targetSlotId]
        else:
            srcItemId = self.__tmpStorage.getToyID(srcSlotId)
            targetItemId = self.__tmpStorage.getToyID(targetSlotId)
            g_christmasCtrl.installItem(srcItemId, targetSlotId)
            g_christmasCtrl.installItem(targetItemId, srcSlotId)
        self.__moveItems(srcItemId, srcSlotId, targetSlotId)
        self.__updateSlot(srcSlotId, targetItemId)
        self.__updateSlot(targetSlotId, srcItemId)

    def installItem(self, itemId, slotId):
        if slotId == -1:
            slotId = self.__findFreeSlotId(itemId)
        if slotId >= 0 and self.__validateForAlchemy(itemId):
            self.__moveItems(itemId, targetId=slotId)
            self.__updateSlot(slotId, itemId)
            if not self.__alchemyIsActive:
                g_christmasCtrl.installItem(itemId, slotId)

    def uninstallItem(self, slotId):
        itemId = self.__alchemySourceIds[slotId] if self.__alchemyIsActive else self.__tmpStorage.getToyID(slotId)
        if itemId > 0:
            if not self.__alchemyIsActive:
                g_christmasCtrl.uninstallItem(slotId)
            else:
                self.__alchemySourceIds[slotId] = None
                if not any(self.__alchemySourceIds):
                    self.__decorationsDp.setAlchemyRank(None)
            self.__moveItems(itemId, sourceId=slotId)
            self.__updateSlot(slotId, None)
        return

    def showConversion(self):
        self.__alchemyIsActive = True
        if self.__selected3DEntity is not None:
            _ctm.highlightEntity(self.__selected3DEntity, False)
            self.__selected3DEntity = None
        self.as_showSlotsViewS(CHRISTMAS_ALIASES.CONVERSION_SLOTS_LINKAGE)
        self.__alchemyTypeFilters = _mergeDictValues(self.__typeFilters, set)
        self.__alchemyRankFilters = _mergeDictValues(self.__rankFilters, set)
        self.__setFilters()
        self.__decorationsDp.setAlchemyRank(None)
        self.__updateInventory()
        self.__updateUiFilters()
        return

    def cancelConversion(self):
        self.__alchemyIsActive = False
        self.__alchemySourceIds = [None] * 5
        self.__tmpStorage.resetAlchemy()
        self.__decorationsDp.resetAlchemy()
        self.__setFilters()
        self.as_showSlotsViewS(CUSTOMIZATION_SLOTS_LINKAGES[self.__objectType])
        self.__updateInventory()
        return

    def onConversionAnimationComplete(self):
        self.as_updateSlotS(self.__makeTreeSlotVO(ALCHEMY_RESULT_SLOT_ID, None))
        return

    @process
    def convertItems(self):
        resultID = yield g_christmasCtrl.doAlchemy(self.__alchemySourceIds, self.__tmpStorage)
        if resultID > 0:
            self.__alchemySourceIds = [None] * 5
            self.__decorationsDp.setAlchemyRank(None)
            self.__tmpStorage.resetAlchemy()
            self.__updateInventory()
            item = g_christmasCtrl.getChristmasItemByID(resultID)
            self.as_updateSlotS(self.__makeTreeSlotVO(ALCHEMY_RESULT_SLOT_ID, item, True))
            self.app.soundManager.playEffectSound(SoundEffectsId.XMAS_ALCHEMY_CONVERT)
        return

    def applyRankFilter(self, filterId):
        _applyFilter(self.__getRankFilters(), filterId, TOY_RANK_LIST)
        self.__setFilters()

    def applyTypeFilter(self, filterId):
        _applyFilter(self.__getTypeFilters(), filterId, self.__currentToyTypeList())
        self.__setFilters()

    def showRules(self):
        self.fireEvent(OpenLinkEvent(OpenLinkEvent.NY_RULES, title=i18n.makeString('#christmas:nyMarathon/promo/title')))

    def onChangeTab(self, tabId):
        self.__objectType = tabId
        AccountSettings.setSettings(CHTISTMAS_VIEW_TAB, self.__objectType)
        g_christmasCtrl.setGUIActive(self.__objectType)
        self.as_showSlotsViewS(CUSTOMIZATION_SLOTS_LINKAGES[self.__objectType])
        self.__updateInventory()
        self.__setFilters()
        self.switchCamera()

    def onEmptyListBtnClick(self):
        if self.__decorationsDp.fullLength() > 0:
            if self.__alchemyIsActive:
                self.__alchemyTypeFilters = set()
                self.__alchemyRankFilters = set()
            else:
                self.__rankFilters[self.__objectType] = set()
                self.__typeFilters[self.__objectType] = set()
            self.__setFilters()
        else:
            showEventsWindow(eventType=constants.EVENT_TYPE.BATTLE_QUEST)

    def switchOffNewItem(self, itemId):
        self.__tmpStorage.discardNew(itemId)
        self.__updateInventory()

    def closeWindow(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def switchCamera(self):
        if self.__objectType == NY_OBJECT_TYPE.TANK:
            g_christmasCtrl.switchToTank()
        else:
            g_christmasCtrl.switchToTree()

    def _populate(self):
        super(ChristmasMainView, self)._populate()
        conversion = g_christmasCtrl.getConversionInfo(1)
        conversionNumber = conversion['number']
        conversionResult = conversion['result']
        btnImproveTooltip = makeTooltip(i18n.makeString(TOOLTIPS.XMAS_BTN_CONVERSION_BTN_HEADER), i18n.makeString(TOOLTIPS.XMAS_BTN_CONVERSION_BTN_BODY, fromCnt=conversionNumber, toCnt=conversionResult['number']))
        self.as_setStaticDataS({'btnCloseLabel': CHRISTMAS.BTN_CLOSE_LABEL,
         'btnBackLabel': CHRISTMAS.BTN_BACK_LABEL,
         'btnBackDescription': CHRISTMAS.BTN_BACK_DESCRIPTION,
         'rulesLabelText': text_styles.main(i18n.makeString(CHRISTMAS.RULESLABEL_TEXT) + '  ' + icons.info()),
         'rulesLabelTooltip': TOOLTIPS_CONSTANTS.XMAS_INSTRUCTION,
         'switchCameraDelayFrames': self.__SWITCH_CAMERA_DELAY_FRAMES__,
         'tabsData': {'tabs': TABS_DATA,
                      'selectedInd': self.__getIndexOfTab(self.__objectType)},
         'slotsStaticData': _VOBuilder.getSlotsStaticData(),
         'btnConversionTooltip': btnImproveTooltip})
        self.as_showSlotsViewS(CUSTOMIZATION_SLOTS_LINKAGES[self.__objectType])
        self.__updateUiFilters()
        self.__tmpStorage = g_christmasCtrl.getTempStorage(createNew=True)
        self.__tmpStorage.init()
        self.__tmpStorage.onInventoryChanged += self.__updateInventory
        g_christmasCtrl.lockAwardsWindowsAndFightBtn(lockAwardsWindows=False)
        g_christmasCtrl.onEventStopped += self.__checkChristmasState
        g_hangarSpace.onObjectSelected += self.__on3DObjectSelected
        g_hangarSpace.onObjectUnselected += self.__on3DObjectUnSelected
        g_hangarSpace.onObjectClicked += self.__on3DObjectClicked
        self.addListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        self.__decorationsDp = _DecorationsDataProvider()
        self.__decorationsDp.setFlashObject(self.as_getDecorationsDPS())
        self.__updateInventory()
        g_christmasCtrl.setGUIActive(self.__objectType)
        self.__checkAlchemyBtnHint()

    def _dispose(self):
        g_christmasCtrl.unlockAwardsWindowsAndFightBtn()
        g_christmasCtrl.onEventStopped -= self.__checkChristmasState
        if g_christmasCtrl.getGlobalState() != EVENT_STATE.FINISHED:
            g_christmasCtrl.applyChanges(self.__tmpStorage)
        g_christmasCtrl.switchToHangar()
        g_christmasCtrl.setGUIActive(None)
        self.__tmpStorage.onInventoryChanged -= self.__updateInventory
        g_hangarSpace.onObjectSelected -= self.__on3DObjectSelected
        g_hangarSpace.onObjectUnselected -= self.__on3DObjectUnSelected
        g_hangarSpace.onObjectClicked -= self.__on3DObjectClicked
        self.removeListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        self.__tmpStorage.fini()
        self.__tmpStorage = None
        self.__currentLevel = None
        if self.__selected3DEntity is not None:
            _ctm.highlightEntity(self.__selected3DEntity, False)
        super(ChristmasMainView, self)._dispose()
        return

    def __checkChristmasState(self):
        if not g_christmasCtrl.isEventInProgress():
            self.closeWindow()

    def __setTreeSlotsData(self):
        slotsList = []
        allSlots = self.__alchemySourceIds if self.__alchemyIsActive else self.__tmpStorage.getToysOnTree()
        for slotID, itemID in enumerate(allSlots):
            item = g_christmasCtrl.getChristmasItemByID(itemID)
            if self.__alchemyIsActive:
                slotsList.append(self.__makeTreeSlotVO(slotID, item))
            slotType = self.__slots[slotID]
            if TOY_TYPE_NAMES[slotType] in self.__currentToyTypeList():
                slotsList.append(self.__makeTreeSlotVO(slotID, item))

        if self.__alchemyIsActive:
            slotsList.append(self.__makeTreeSlotVO(ALCHEMY_RESULT_SLOT_ID, None))
        slotsData = _VOBuilder.packSlots(slotsList, self.__alchemyIsActive, all(self.__alchemySourceIds))
        self.__updateConversionBtn()
        self.as_setSlotsDataS(slotsData)
        return

    def __updateConversionBtn(self):
        if not self.__alchemyIsActive:
            conversionIsPossible = False
            for rank, value in self.__tmpStorage.getRankStats().iteritems():
                conversionInfo = g_christmasCtrl.getConversionInfo(rank)
                if conversionInfo is not None and conversionInfo['number'] <= value:
                    conversionIsPossible = True
                    break

            if conversionIsPossible:
                icon = RES_ICONS.MAPS_ICONS_BUTTONS_LEVEL_UP
            else:
                icon = RES_ICONS.MAPS_ICONS_BUTTONS_LEVEL_UP_DISABLE
            self.as_updateConversionBtnS(conversionIsPossible, icon)
        return

    def __updateRatingInfo(self):
        progressInfo = self.__tmpStorage.getTreeLevelInfo()
        nextLvlRating = progressInfo['maxRating'] + 1
        progressBarValue = progressInfo['rating'] / float(nextLvlRating)
        tempLvl = progressInfo['level']
        if tempLvl > g_christmasCtrl.getRatingInfo()['level']:
            g_christmasCtrl.applyChanges(self.__tmpStorage)
        level = text_styles.bonusLocalText(int2roman(tempLvl))
        showFlash = self.__prevRating != -1 and self.__prevRating < progressInfo['rating']
        self.__prevRating = progressInfo['rating']
        self.as_setProgressS({'levelText': text_styles.highTitle(i18n.makeString(CHRISTMAS.PROGRESSBAR_LEVELTEXT_TEXT, lvl=level)),
         'progress': progressBarValue,
         'showFlash': showFlash})

    def __updateInventory(self):
        objectType = None if self.__alchemyIsActive else self.__objectType
        self.__alchemySourceIds = [ itemID or None for itemID in self.__tmpStorage.getAlchemyCache() ]
        self.__decorationsDp.buildList(self.__tmpStorage.getInventoryItems(objectType), self.__tmpStorage.getRankStats())
        self.__updateEmptyInfoText()
        self.__updateRatingInfo()
        self.__setTreeSlotsData()
        return

    def __updateUiFilters(self):
        self.as_setFiltersS(self.__getRankFiltersData(), self.__getTypeFiltersData())

    def __updateSlot(self, slotID, itemID):
        item = g_christmasCtrl.getChristmasItemByID(itemID)
        self.as_updateSlotS(self.__makeTreeSlotVO(slotID, item))

    def __findFreeSlotId(self, itemId):
        if self.__alchemyIsActive:
            if None in self.__alchemySourceIds:
                return self.__alchemySourceIds.index(None)
        else:
            item = g_christmasCtrl.getChristmasItemByID(itemId)
            treeState = self.__tmpStorage.getToysOnTree()
            for slotID, itemID in enumerate(treeState):
                itemOnTree = g_christmasCtrl.getChristmasItemByID(itemID)
                if itemOnTree is None and item.guiType == self.__slots[slotID]:
                    return slotID

        return -1

    def __updateEmptyInfoText(self):
        isVisible = False
        data = None
        if len(self.__decorationsDp.collection) <= 0:
            isVisible = True
            if self.__decorationsDp.fullLength() > 0:
                titleText = CHRISTMAS.EMPTYLIST_NOTHINGTOSHOW_TITLE
                descrText = CHRISTMAS.EMPTYLIST_NOTHINGTOSHOW_DESCRIPTION
                btnLabel = CHRISTMAS.EMPTYLIST_NOTHINGTOSHOW_BTNLABEL
            else:
                titleText = CHRISTMAS.EMPTYLIST_HASNTTOYS_TITLE
                descrText = CHRISTMAS.EMPTYLIST_HASNTTOYS_DESCRIPTION
                btnLabel = CHRISTMAS.EMPTYLIST_HASNTTOYS_BTNLABEL
            data = {'title': text_styles.middleTitle(titleText),
             'message': text_styles.main(descrText),
             'returnBtnLabel': btnLabel}
        self.as_setEmptyListDataS(isVisible, data)
        return

    def __playSlotSound(self, slotId):
        slotType = self.__slots[slotId]
        self.app.soundManager.playEffectSound(SOUNDS_IDS.get(slotType, SoundEffectsId.XMAS_TOY))

    def __moveItems(self, itemId, sourceId=None, targetId=None):
        if self.__alchemyIsActive:
            if targetId is not None:
                if sourceId is not None:
                    self.__alchemySourceIds[sourceId] = self.__alchemySourceIds[targetId]
                self.__alchemySourceIds[targetId] = itemId
                self.__decorationsDp.setAlchemyRank(g_christmasCtrl.getChristmasItemByID(itemId).rank)
                self.as_scrollToItemS(0)
            else:
                self.__alchemySourceIds[sourceId] = None
            self.__tmpStorage.moveAlchemyToy(itemId, sourceId, targetId)
        else:
            if targetId is not None:
                self.__playSlotSound(targetId)
            self.__tmpStorage.moveToy(itemId, sourceId, targetId)
        if sourceId is None or targetId is None:
            self.__updateInventory()
        return

    def __validateForAlchemy(self, newId):
        if self.__alchemyIsActive and any(self.__alchemySourceIds):
            currentId = findFirst(lambda idx: idx is not None, self.__alchemySourceIds)
            currentItem = g_christmasCtrl.getChristmasItemByID(currentId)
            newItem = g_christmasCtrl.getChristmasItemByID(newId)
            return currentItem is not None and newItem is not None and currentItem.rank == newItem.rank
        else:
            return True
            return None

    def __setFilters(self):
        self.__decorationsDp.applyRankFilters(self.__getRankFilters())
        self.__decorationsDp.applyTypeFilters(self.__getTypeFilters())
        self.__updateUiFilters()
        self.__updateEmptyInfoText()

    def __currentToyTypeList(self):
        return CONVERSION_DECORATIONS if self.__alchemyIsActive else NY_OBJECT_TO_TOY_TYPE.get(self.__objectType)

    def __getRankFilters(self):
        if self.__alchemyIsActive:
            return self.__alchemyRankFilters
        else:
            return self.__rankFilters[self.__objectType]

    def __getTypeFilters(self):
        if self.__alchemyIsActive:
            return self.__alchemyTypeFilters
        else:
            return self.__typeFilters[self.__objectType]

    def __getRankFiltersData(self):
        return {'label': text_styles.main(CHRISTMAS.FILTERS_RANK_NAME),
         'items': map(lambda rank: {'value': '../maps/icons/filters/levels/level_%s.png' % rank,
                   'selected': rank in self.__getRankFilters()}, TOY_RANK_LIST)}

    def __getTypeFiltersData(self):
        return {'label': text_styles.main(CHRISTMAS.FILTERS_TYPE_NAME),
         'items': map(lambda typeID: {'value': RES_ICONS.maps_icons_christmas_filters(TOY_TYPE_ID_TO_NAME[typeID].lower() + '.png'),
                   'selected': typeID in self.__getTypeFilters()}, self.__currentToyTypeList())}

    def __improveBtnIsActive(self):
        for rank, count in self.__tmpStorage.getRankStats().iteritems():
            if g_christmasCtrl.isEnoughForConversion(rank, count):
                return True

        return False

    def __makeTreeSlotVO(self, slotID, item, showAnimation=False):
        slotType = None if self.__alchemyIsActive else self.__slots[slotID]
        if item is not None:
            itemID = item.id
            if slotID == ALCHEMY_RESULT_SLOT_ID:
                icon = RES_ICONS.maps_icons_christmas_decorations_big_decoration(item.getIconName())
            else:
                icon = RES_ICONS.maps_icons_christmas_decorations_small_decoration(item.getIconName())
            rank = RES_ICONS.maps_icons_christmas_decorations_small_rank(item.getRankIconName())
            tooltip = TOOLTIPS_CONSTANTS.XMAS_SLOT
        else:
            itemID = -1
            rank = ''
            if not self.__alchemyIsActive:
                icon = RES_ICONS.maps_icons_christmas_slots_small('%s.png' % slotType.lower())
                tooltip = makeTooltip(i18n.makeString(TOOLTIPS.XMAS_EMPTYTOYPLACE_HEADER, toyType=i18n.makeString(CHRISTMAS.TOYTYPE_GENITIVE + '/%s' % slotType)), TOOLTIPS.XMAS_EMPTYTOYPLACE_BODY)
            else:
                icon = ''
                tooltip = ''
        return {'decorationId': itemID,
         'slotType': slotType,
         'slotId': slotID,
         'rankIcon': rank,
         'icon': icon,
         'btnRemoveVisible': item is not None and slotID != ALCHEMY_RESULT_SLOT_ID,
         'isEmpty': item is None,
         'tooltip': tooltip,
         'showAnimation': showAnimation}

    def __getIndexOfTab(self, idx):
        for index, item in enumerate(TABS_DATA):
            if item.get('id') == idx:
                return index

    def __checkAlchemyBtnHint(self):
        isHintShown = self.settingsCore.serverSettings.getOnceOnlyHintsSetting('ChristmasDecorationListHint')
        if not self.__alchemyIsActive and self.__improveBtnIsActive() and not AccountSettings.getSettings('alchemyBtnShown') and isHintShown:
            event_dispatcher.runTutorialChain('Christmas_Chain')

    def __on3DObjectSelected(self, entity):
        self.__selected3DEntity = entity
        if self.__isCursorOver3dScene and not self.__alchemyIsActive:
            _ctm.highlightEntity(entity, True)

    def __on3DObjectUnSelected(self, _):
        if self.__selected3DEntity is not None:
            _ctm.highlightEntity(self.__selected3DEntity, False)
            self.__selected3DEntity = None
        return

    def __on3DObjectClicked(self):
        if self.__isCursorOver3dScene:
            if not self.__alchemyIsActive:
                _ctm.switchCameraToEntity(self.__selected3DEntity)
                if _ctm.isTreeEntity(self.__selected3DEntity):
                    self.as_selectSlotsTabS(self.__getIndexOfTab(NY_OBJECT_TYPE.TREE))
                elif _ctm.isTankEntity(self.__selected3DEntity):
                    self.as_selectSlotsTabS(self.__getIndexOfTab(NY_OBJECT_TYPE.TANK))

    def __onNotifyCursorOver3dScene(self, event):
        self.__isCursorOver3dScene = event.ctx.get('isOver3dScene', False)
        _ctm.highlightEntity(self.__selected3DEntity, self.__isCursorOver3dScene and not self.__alchemyIsActive)


class _DecorationsDataProvider(SortableDAAPIDataProvider):

    def __init__(self):
        super(_DecorationsDataProvider, self).__init__()
        self._list = []
        self._rankFilters = []
        self._typeFilters = []
        self.__alchemyMode = False
        self.__alchemyToysRank = None
        self.__slotsStats = {}
        return

    @property
    def collection(self):
        return map(self.__makeVO, self.__filteredList())

    def setAlchemyRank(self, rank):
        self.__alchemyMode = True
        self.__alchemyToysRank = rank

    def resetAlchemy(self):
        self.__alchemyMode = False
        self.__alchemyToysRank = None
        return

    def fullLength(self):
        return len(self._list)

    def emptyItem(self):
        return None

    def clear(self):
        self._list = []

    def fini(self):
        self.clear()
        self._dispose()

    def applyRankFilters(self, filters):
        self._rankFilters = filters
        self.refresh()

    def applyTypeFilters(self, filters):
        self._typeFilters = filters
        self.refresh()

    def buildList(self, data, slotsStats):
        self.clear()
        self.__slotsStats = slotsStats
        self._list = sorted(data, cmp=self.__itemsSorter)
        self.refresh()

    def __itemsSorter(self, itemInfo1, itemInfo2):
        item1, item2 = itemInfo1.item, itemInfo2.item
        rank1, rank2 = item1.rank, item2.rank
        if rank1 == rank2:
            return cmp(item1.type, item2.type)
        else:
            return cmp(self.__isForCurrentAlchemy(item1), self.__isForCurrentAlchemy(item2)) * -1 or cmp(rank1, rank2)

    def __isForCurrentAlchemy(self, item):
        if self.__alchemyMode:
            rank = item.rank
            if self.__alchemyToysRank:
                return self.__alchemyToysRank == item.rank
            else:
                return g_christmasCtrl.isEnoughForConversion(rank, self.__slotsStats.get(rank))
        else:
            return True

    def __filteredList(self):
        filteredList = self._list
        if len(self._rankFilters):
            filteredList = filter(lambda itemInfo: itemInfo.item.rank in self._rankFilters, filteredList)
        if len(self._typeFilters):
            filteredList = filter(lambda itemInfo: itemInfo.item.type in self._typeFilters, filteredList)
        return filteredList

    def __makeVO(self, itemInfo):
        item = itemInfo.item
        slotType = item.guiType
        res = {'decorationId': item.id,
         'slotType': slotType,
         'count': text_styles.main(str(itemInfo.count)),
         'showCount': itemInfo.count > 1,
         'rankIconBig': RES_ICONS.maps_icons_christmas_decorations_big_rank(item.getRankIconName()),
         'iconBig': RES_ICONS.maps_icons_christmas_decorations_big_decoration(item.getIconName()),
         'rankIcon': RES_ICONS.maps_icons_christmas_decorations_small_rank(item.getRankIconName()),
         'icon': RES_ICONS.maps_icons_christmas_decorations_small_decoration(item.getIconName()),
         'tooltip': TOOLTIPS_CONSTANTS.XMAS_SLOT,
         'isNew': itemInfo.isNew,
         'enabled': not self.__alchemyMode or self.__isForCurrentAlchemy(item)}
        return res


class _VOBuilder(object):

    @classmethod
    def getSlotsStaticData(cls):
        return [cls.__getCustomizationStaticData(NY_OBJECT_TYPE.TREE), cls.__getCustomizationStaticData(NY_OBJECT_TYPE.TANK), cls.__getConversionStaticData()]

    @classmethod
    def packSlots(cls, slots, isAlchemy, buttonIsVisible):
        data = {'slots': slots}
        if isAlchemy:
            data['enableConvertBtn'] = buttonIsVisible
            dataClass = CHRISTMAS_ALIASES.CONVERSION_SLOTS_DATA_CLASS
        else:
            dataClass = CHRISTMAS_ALIASES.CUSTOMIZATION_SLOTS_DATA_CLASS
        return cls.__getDataClassItem(data, dataClass)

    @classmethod
    def __getCustomizationStaticData(cls, dataType):
        if dataType == NY_OBJECT_TYPE.TREE:
            icon = RES_ICONS.MAPS_ICONS_CHRISTMAS_TREE_SCHEME
        else:
            icon = RES_ICONS.MAPS_ICONS_CHRISTMAS_SNOWTANK_SCHEME
        return cls.__getSlotsViewDataItem(CUSTOMIZATION_SLOTS_LINKAGES.get(dataType), {'backIcon': icon,
         'isRulesVisible': True,
         'isTabsVisible': True,
         'isConversionBtnVisible': True,
         'isHeaderEnabled': True}, CHRISTMAS_ALIASES.CUSTOMIZATION_SLOTS_STATIC_DATA_CLASS)

    @classmethod
    def __getConversionStaticData(cls):
        return cls.__getSlotsViewDataItem(CHRISTMAS_ALIASES.CONVERSION_SLOTS_LINKAGE, {'title': text_styles.middleTitle(CHRISTMAS.CONVERSIONVIEW_TITLE),
         'description': text_styles.main(i18n.makeString(CHRISTMAS.CONVERSIONVIEW_DESCRIPTION, numConverted=text_styles.stats(ALCHEMY_NUM_CONVERTED_ITEMS), numObtained=text_styles.stats(ALCHEMY_NUM_OBTAINED_ITEMS))),
         'convertBtnLabel': CHRISTMAS.CONVERSIONVIEW_CONVERTBTN_LABEL,
         'cancelBtnLabel': CHRISTMAS.CONVERSIONVIEW_CANCELBTN_LABEL,
         'isRulesVisible': False,
         'isTabsVisible': False,
         'isConversionBtnVisible': False,
         'isHeaderEnabled': False}, CHRISTMAS_ALIASES.CONVERSION_SLOTS_STATIC_DATA_CLASS)

    @classmethod
    def __getSlotsViewDataItem(cls, linkage, data, dataClass):
        result = cls.__getDataClassItem(data, dataClass)
        result['linkageClassName'] = linkage
        return result

    @staticmethod
    def __getDataClassItem(data, dataClass):
        return {'voData': data,
         'voClassName': dataClass}
