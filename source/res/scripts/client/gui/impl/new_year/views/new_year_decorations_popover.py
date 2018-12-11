# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_decorations_popover.py
from frameworks.wulf.gui_constants import ViewFlags, Resource, ViewStatus
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.new_year.views.new_year_decorations_popover_model import NewYearDecorationsPopoverModel
from gui.impl.gui_decorators import trackLifeCycle
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundEvents
from gui.impl.new_year.tooltips.toy_content import ToyContent
from gui.impl.new_year.views.toy_presenter import PopoverToyPresenter
from gui.impl.pub import PopOverViewImpl
from gui.server_events import events_dispatcher as se_events
from gui.shared.utils import decorators
from helpers import dependency
from items.components.ny_constants import ToyTypes
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
_HANG_SOUNDS_MAP = {ToyTypes.TOP: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.BALL: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.GARLAND: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.FLOOR: NewYearSoundEvents.ADD_TOY_TREE_DOWN,
 ToyTypes.KITCHEN: NewYearSoundEvents.ADD_TOY_KITCHEN_BBQ,
 ToyTypes.TABLE: NewYearSoundEvents.ADD_TOY_KITCHEN_TABLE,
 ToyTypes.SCULPTURE: NewYearSoundEvents.ADD_TOY_SNOWTANK,
 ToyTypes.DECORATION: NewYearSoundEvents.ADD_TOY_SNOWTANK_LIGHT,
 ToyTypes.TREES: NewYearSoundEvents.ADD_TOY_LIGHT,
 ToyTypes.GROUND_LIGHT: NewYearSoundEvents.ADD_TOY_LIGHT_DOWN}

@trackLifeCycle('new_year.decoration_popover')
class NewYearDecorationsPopover(NewYearNavigation, PopOverViewImpl):
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _isScopeWatcher = False
    __slots__ = ('__slotID', '__decorationType', '__selectedDecoration', '__toys', '__newSeenToys')

    def __init__(self, slotID):
        super(NewYearDecorationsPopover, self).__init__(R.views.newYearDecorationsPopover, ViewFlags.VIEW, NewYearDecorationsPopoverModel)
        self.__slotID = slotID
        self.__decorationType = self.__getDecorationType()
        toyID = self.__getNewYearRequester().getSlots()[self.__slotID]
        self.__selectedDecoration = self.__getNewYearRequester().getToys().get(toyID)
        self.__toys = []

    @property
    def viewModel(self):
        return super(NewYearDecorationsPopover, self).getViewModel()

    @property
    def isCloseBtnVisible(self):
        return True

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.newYearToyTooltipContent:
            toyID = event.getArgument('toyID')
            return ToyContent(toyID)

    def _initialize(self, *args, **kwargs):
        soundConfig = {}
        super(NewYearDecorationsPopover, self)._initialize(soundConfig)
        with self.viewModel.transaction() as tx:
            self.__updateHeader(tx)
            self.__updateSlotsList()
        self.viewModel.onGetShardsBtnClick += self.__onGetShardsBtnClick
        self.viewModel.onDecorationPlusClick += self.__onDecorationPlusClick
        self.viewModel.onQuestsBtnClick += self.__onQuestsBtnClick
        self.viewModel.slotsList.onSelectionChanged += self.__onSelectionChanged
        self.viewModel.onSlotStatusIsNewChanged += self.__onSlotStatusIsNewChanged

    def _finalize(self):
        self.viewModel.onGetShardsBtnClick -= self.__onGetShardsBtnClick
        self.viewModel.slotsList.onUserSelectionChanged -= self.__onSelectionChanged
        self.viewModel.onDecorationPlusClick -= self.__onDecorationPlusClick
        self.viewModel.onQuestsBtnClick -= self.__onQuestsBtnClick
        self.viewModel.onSlotStatusIsNewChanged -= self.__onSlotStatusIsNewChanged
        self.__sendSeenToys()
        super(NewYearDecorationsPopover, self)._finalize()

    def __updateSlotsList(self):
        toys = [ toy for toy in self._nyController.getToysByType(self.__decorationType) if toy.getCount() > 0 ]
        slots = self.viewModel.slotsList
        slots.clear()
        selectedToyID = self.__selectedDecoration.getID() if self.__selectedDecoration is not None else None
        self.viewModel.setIsEmpty(not toys and not selectedToyID)
        idx = 0
        curRank = 0
        if selectedToyID:
            slots.addViewModel(PopoverToyPresenter(self.__selectedDecoration).asSlotModel(idx), isSelected=True)
            idx += 1
            curRank = self.__selectedDecoration.getRank()
        for toyDescriptor in toys:
            if toyDescriptor.getID() != selectedToyID:
                slots.addViewModel(PopoverToyPresenter(toyDescriptor).asSlotModel(idx, curRank))
                idx += 1

        return

    def __getDecorationType(self):
        return self._nyController.getSlotDescrs()[self.__slotID].type

    def __getNewYearRequester(self):
        return self._itemsCache.items.festivity

    @decorators.process('newYear/hangToyWaiting')
    def __onSelectionChanged(self, args):
        selectedItemIdx = args['selectedIndex']
        if selectedItemIdx is not None:
            selectedItem = self.viewModel.slotsList.getItem(selectedItemIdx)
        else:
            selectedItem = None
        if selectedItem:
            toyID = selectedItem.getToyID()
            toy = self.__getNewYearRequester().getToys().get(toyID)
        else:
            toyID = -1
            toy = None
        result = yield self._nyController.hangToy(toyID, self.__slotID)
        if result.success and self.viewStatus == ViewStatus.LOADED:
            self.__selectedDecoration = toy
            if selectedItem:
                self._newYearSounds.playEvent(_HANG_SOUNDS_MAP[self.__decorationType])
                self._newYearSounds.setStylesState(self.__selectedDecoration.getSetting())
                self.destroyWindow()
            else:
                with self.viewModel.transaction() as tx:
                    self.__updateHeader(tx, selectedItem)
        elif not result.success:
            self.destroyWindow()
        return

    def __updateHeader(self, tx, slotItem=None):
        if slotItem is None and self.__selectedDecoration:
            slotItem = PopoverToyPresenter(self.__selectedDecoration).asSlotModel()
        if slotItem is not None:
            title = slotItem.getTitle()
            description = R.strings.ny.settings.dyn(slotItem.getSetting())
            decorationImage = slotItem.getDecorationImage()
            rankImage = slotItem.getRankImage()
        else:
            title = R.strings.ny.decorationTypes.dyn(self.__decorationType)
            description = R.strings.ny.decorationsPopover.description
            decorationImage = R.images.gui.maps.icons.new_year.decorationTypes.blue.dyn(self.__decorationType)
            rankImage = Resource.INVALID
        tx.setTitle(title)
        tx.setDescription(description)
        tx.setDecorationImage(decorationImage)
        tx.setRankImage(rankImage)
        return

    def __onGetShardsBtnClick(self, *_):
        self._goToBreakView(toyType=self.__decorationType, blur3dScene=True)

    def __onDecorationPlusClick(self, *_):
        self._goToCraftView()

    def __onQuestsBtnClick(self, *_):
        se_events.showMissions()

    def __onSlotStatusIsNewChanged(self, args):
        slot = self.viewModel.slotsList.getItem(args.get('idx'))
        slot.setIsNew(False)

    def __sendSeenToys(self):
        serverFormatted = []
        inventoryToys = self.__getNewYearRequester().getToys()
        for toyID, toyInfo in inventoryToys.iteritems():
            if toyInfo.getToyType() == self.__decorationType and toyInfo.getCount() > 0:
                serverFormatted.append(toyID)
                serverFormatted.append(toyInfo.getUnseenCount())

        self._nyController.sendSeenToys(serverFormatted)
