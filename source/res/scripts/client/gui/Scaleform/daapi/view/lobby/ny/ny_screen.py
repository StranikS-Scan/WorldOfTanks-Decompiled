# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_screen.py
import BigWorld
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.NYScreenMeta import NYScreenMeta
from gui.Scaleform.daapi.view.lobby.ny.ny_helper_view import NYHelperView
from gui.Scaleform.genConsts.NY_CONSTANTS import NY_CONSTANTS
from gui.Scaleform.locale.NY import NY
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.new_year import INewYearController
from new_year import NewYearObjectIDs, Mappings, UiTabs
from functools import partial
from Event import Event
from new_year.camera_switcher import CameraSwitcher
from new_year.new_year_sounds import NYSoundEvents

class NYScreen(NYHelperView, NYScreenMeta):
    _newYearController = dependency.descriptor(INewYearController)
    tabSlotsMapping = {'tree': ['top',
              'hanging',
              'garland',
              'gift'],
     'snowman': ['snowman'],
     'house': ['house_decoration', 'house_lamp'],
     'light': ['street_garland']}
    __background_alpha__ = 0.0

    def __init__(self, ctx=None):
        super(NYScreen, self).__init__(ctx)
        self.__currentTabId = None
        self._initialize(ctx)
        self.__mouseEvent = Event()
        return

    def onClose(self):
        self.__switchToHangar()

    def onCraftButtonClick(self):
        NYSoundEvents.playSound(NYSoundEvents.ON_CRAFT_CLICK)
        self._switchToCraft(previewAlias=VIEW_ALIAS.LOBBY_NY_SCREEN)

    def onCollectionButtonClick(self):
        NYSoundEvents.playCloseCustomization(Mappings.ID_TO_ANCHOR[self.__currentTabId])
        self._switchToGroups(previewAlias=VIEW_ALIAS.LOBBY_NY_SCREEN, tabId=self.__currentTabId)

    def onToyFragmentButtonClick(self):
        NYSoundEvents.playSound(NYSoundEvents.ON_TOY_FRAGMENT_CLICK)
        self._switchToBreak(previewAlias=VIEW_ALIAS.LOBBY_NY_SCREEN)

    def onTabButtonClick(self, tabID):
        if tabID == self.__currentTabId:
            return
        self.__currentTabId = tabID
        self.as_enableBtnsS(False)
        NYSoundEvents.playSound(NYSoundEvents.ON_TAB_CLICK)
        if tabID in Mappings.ID_TO_ANCHOR:
            newState = Mappings.ID_TO_ANCHOR[tabID]
            if self._customizableObjMgr.state != newState:
                self._customizableObjMgr.switchTo(Mappings.ID_TO_ANCHOR[tabID], partial(self.__showViewById, tabID))
            else:
                self.__showViewById(tabID)

    def onAwardsButtonClick(self):
        NYSoundEvents.playCloseCustomization(Mappings.ID_TO_ANCHOR[self.__currentTabId])
        self._switchToRewards(previewAlias=VIEW_ALIAS.LOBBY_NY_SCREEN)

    def moveSpace(self, x, y, delta):
        self.__mouseEvent(x, y, delta)

    def _invalidate(self, ctx=None):
        super(NYScreen, self)._invalidate(ctx)
        self._initialize(ctx)

    def _initialize(self, ctx=None):
        if ctx and 'tabId' in ctx:
            self.__currentTabId = ctx['tabId']
        else:
            default = NY_CONSTANTS.SIDE_BAR_TREE_ID
            state = self._customizableObjMgr.state
            self.__currentTabId = Mappings.ANCHOR_TO_ID[state] if state in Mappings.ANCHOR_TO_ID else default

    def _populate(self):
        super(NYScreen, self)._populate()
        self._newYearController.boxStorage.onCountChanged += self.__onBoxCountChanged
        self._newYearController.onProgressChanged += self.__onProgressUpdated
        self._newYearController.onToyFragmentsChanged += self.__onToyFragmentsChanged
        self._newYearController.onInventoryUpdated += self.__onInventoryUpdated
        self._newYearController.onToysBreakStarted += self._onToysBreakStarted
        self._newYearController.onToysBreak += self._onToysBreak
        self._newYearController.onToysBreakFailed += self._onToysBreakFailed
        self.__linkCameraWithMouseEvents()
        NYSoundEvents.playOpenCustomization(self.__currentTabId)
        data, awardsCounter, progress = self.__makeVO()
        self.as_initS(data)
        self.as_updateNYAwardsCounterS(awardsCounter)
        self.__updateCounter()
        self.as_updateNYProgressS(progress)
        self.__onInventoryUpdated()

    def __onInventoryUpdated(self):
        newToys = dict.fromkeys(self.tabSlotsMapping.keys(), 0)
        for type, toys in self._newYearController.getInventory().iteritems():
            for toy in toys.values():
                for tab, slots in self.tabSlotsMapping.iteritems():
                    if type in slots:
                        newToys[tab] += toy.newCount
                        break

        for tab, newCount in newToys.iteritems():
            self.as_setTabButtonCounterS(tab, str(newCount))

    def _dispose(self):
        self._newYearController.boxStorage.onCountChanged -= self.__onBoxCountChanged
        self._newYearController.onProgressChanged -= self.__onProgressUpdated
        self._newYearController.onToyFragmentsChanged -= self.__onToyFragmentsChanged
        self._newYearController.onInventoryUpdated -= self.__onInventoryUpdated
        self._newYearController.onToysBreakStarted -= self._onToysBreakStarted
        self._newYearController.onToysBreak -= self._onToysBreak
        self._newYearController.onToysBreakFailed -= self._onToysBreakFailed
        self.__unlinkCameraFromMouseEvents()
        self.__mouseEvent.clear()
        super(NYScreen, self)._dispose()

    def __switchToHangar(self):
        self._customizableObjMgr.switchTo(None, lambda : self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY))
        return

    def _onToysBreakStarted(self):
        self.as_onBreakStartS()

    def _onToysBreak(self, toyIndexes, fromSlot):
        self.as_onBreakS()

    def _onToysBreakFailed(self):
        self.as_onBreakFailS()

    def __onProgressUpdated(self, nyProgress):
        self.as_updateNYLevelS(nyProgress.level)
        self.as_updateNYProgressS(nyProgress.progress / float(nyProgress.bound))

    def __onToyFragmentsChanged(self, fragmentsCount):
        self.as_updateNYTOYFragmentS(BigWorld.wg_getIntegralFormat(fragmentsCount))

    def __onBoxCountChanged(self, *args):
        self.__updateCounter()

    def __updateCounter(self):
        self.as_updateNYBoxCounterS(self._newYearController.boxStorage.count)

    def __makeVO(self):
        nyLevel, _, nyProgress, nyBound = self._newYearController.getProgress()
        normalizedProgress = nyProgress / float(nyBound)
        nyAwardsCounter = str(self.__getRewardsCounter())
        toyFragment = BigWorld.wg_getIntegralFormat(self._newYearController.getToyFragments())
        tabIndex = NewYearObjectIDs.ALL.index(self.__currentTabId)
        self.__currentTabId = None
        res = {'craftBtnLabel': NY.SCREEN_CRAFTBTN_LABEL,
         'sideBarData': UiTabs.ALL,
         'level': nyLevel,
         'toyFragment': toyFragment,
         'sideBarSelectedItemIndex': tabIndex}
        return (res, nyAwardsCounter, normalizedProgress)

    def __showViewById(self, tabID):
        self.as_showViewByIdS(tabID)
        self.as_enableBtnsS(True)

    def __linkCameraWithMouseEvents(self):
        cameraSwitcher = self._customizableObjMgr.getSwitchHandler(CameraSwitcher)
        if cameraSwitcher is not None:
            cameraSwitcher.subscribeToMouseEvents(self.__mouseEvent)
        return

    def __unlinkCameraFromMouseEvents(self):
        cameraSwitcher = self._customizableObjMgr.getSwitchHandler(CameraSwitcher)
        if cameraSwitcher is not None:
            cameraSwitcher.unsubscribeFromMouseEvents(self.__mouseEvent)
        return

    def __getRewardsCounter(self):
        discountSums = (sum(self._newYearController.vehDiscountsStorage.getDiscounts().values()), sum(self._newYearController.tankmanDiscountsStorage.getDiscounts().values()))
        counter = sum(discountSums)
        return counter
