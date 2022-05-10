# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/event_platform/gui/impl/lobby/test_view/test_view4.py
from frameworks.wulf import ViewFlags, ViewSettings
from event_platform.gui.impl.gen.view_models.views.lobby.test_view.test_view4_model import TestView4Model
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from event_platform.gui.impl.gen.view_models.views.lobby.test_view.advanced_test_item_model import AdvancedTestItemModel
from event_platform.gui.impl.gen.view_models.views.lobby.test_view.advanced_award_model import AdvancedAwardModel

class TestView4(ViewImpl):
    __slots__ = ()
    layoutID = R.views.event_platform.lobby.test_view.TestView4()

    def __init__(self, layoutID):
        super(TestView4, self).__init__(ViewSettings(layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, TestView4Model()))

    @property
    def viewModel(self):
        return super(TestView4, self).getViewModel()

    def _onLoading(self):
        self.__initModel()
        self.__startListen()

    def _finalize(self):
        self.__stopListen()

    def __startListen(self):
        self.viewModel.onFirstButtonClicked += self.__firstButtonClickHandler
        self.viewModel.onSecondButtonClicked += self.__secondButtonClickHandler

    def __stopListen(self):
        self.viewModel.onFirstButtonClicked -= self.__firstButtonClickHandler
        self.viewModel.onSecondButtonClicked -= self.__secondButtonClickHandler

    def __initModel(self):
        with self.viewModel.transaction() as vm:
            vm.setHeader('Header from python')
            vm.setDescriptor('Descriptor from python')
            advancedItems = vm.getAdvancedItems()
            for itemId in range(1, 8):
                advancedItems.addViewModel(self.__generateFakeAdvancedItem(itemId))

            award = vm.award
            award.setAwardId(9)
            award.setAwardName('Mega bonus')
            award.setAwardFlag(True)

    def __generateFakeAdvancedItem(self, itemId):
        item = AdvancedTestItemModel()
        self.__fillFakeItem(item, itemId)
        awards = item.getAwards()
        for awardId in range(1, 11):
            awards.addViewModel(self.__generateFakeAdvancedAward(awardId))

        return item

    def __fillFakeItem(self, item, itemId):
        item.setId(itemId)
        item.setName('Item {0}'.format(itemId))
        item.setFlag(itemId == 2)

    def __generateFakeAdvancedAward(self, awardId):
        award = AdvancedAwardModel()
        award.setAwardId(awardId)
        award.setAwardName('Award {0}'.format(awardId))
        award.setAwardFlag(awardId == 3)
        award.setAwardDescription('Award {0} description'.format(awardId))
        return award

    def __firstButtonClickHandler(self):
        with self.viewModel.transaction() as vm:
            vm.setHeader('Header AAA')
            vm.setDescriptor('Descriptor AAA')

    def __secondButtonClickHandler(self):
        with self.viewModel.transaction() as vm:
            vm.setHeader('Header BBB')
            vm.setDescriptor('Descriptor BBB')
