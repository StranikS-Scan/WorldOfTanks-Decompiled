# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/quick_training/components/books_list_component.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.quick_training.books_list_component_model import TrainingBookModel
from gui.impl.lobby.container_views.base.components import ComponentBase
from gui.impl.lobby.crew.tooltips.crew_book_mouse_tooltip import CrewBookMouseTooltip
from gui.impl.lobby.crew.tooltips.quick_training_lostxp_tooltip import QuickTrainingLostXpTooltip
from gui.impl.lobby.crew.utils import jsonArgsConverter
if typing.TYPE_CHECKING:
    from typing import List
    from gui.impl.gen.view_models.views.lobby.crew.quick_training.quick_training_view_model import QuickTrainingViewModel
    from gui.impl.gen.view_models.views.lobby.crew.quick_training.books_list_component_model import BooksListComponentModel
    from gui.shared.gui_items.crew_book import CrewBook

class BooksListComponent(ComponentBase):

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.crew.tooltips.QuickTrainingLostXpTooltip():
            return QuickTrainingLostXpTooltip()
        return CrewBookMouseTooltip() if contentID == R.views.lobby.crew.tooltips.CrewBookMouseTooltip() else None

    def _getViewModel(self, vm):
        return vm.books

    def _getEvents(self):
        return super(BooksListComponent, self)._getEvents() + ((self.viewModel.mouseEnter, self._onBookMouseEnter),
         (self.viewModel.select, self._onBookSelected),
         (self.viewModel.buy, self._onBuyBook),
         (self.viewModel.openPostProgression, self.events.onPostProgressionOpen))

    @jsonArgsConverter(('bookId',))
    def _onBuyBook(self, bookId):
        self.events.onBuyBook(bookId)

    @jsonArgsConverter(('intCD',))
    def _onBookMouseEnter(self, intCD):
        self.events.onBookMouseEnter(intCD)

    @jsonArgsConverter(('intCD', 'count'))
    def _onBookSelected(self, intCD, count):
        self.events.onBookSelected(intCD, count)

    def _fillViewModel(self, vm):
        ctx = self.context
        rewardBook = ctx.rewardBook
        hiddenItems = ctx.hiddenShopItems
        hasMaxedTankmen = ctx.accountMaxedTankmenCount > 0
        cauUsePersonalBook = ctx.canCurrentTankmanUsePersonalBook and ctx.canCurrentTankmanUseMorePersonalBook
        isPersonalBookDisabled = not ctx.canCrewSelectPersonalBook
        cauUseCommonBook = ctx.canCrewSelectBook
        isCommonBookDisabled = ctx.isSingleTankman
        hasCommonBookError = ctx.hasCrewMaxedTman
        bookList = vm.getItems()
        bookList.clear()
        for book in ctx.crewBooks:
            if book.isPersonal():
                stateFlags = (cauUsePersonalBook,
                 isPersonalBookDisabled,
                 isPersonalBookDisabled,
                 hasMaxedTankmen)
            else:
                stateFlags = (cauUseCommonBook,
                 isCommonBookDisabled,
                 hasCommonBookError,
                 hasMaxedTankmen)
            bookList.addViewModel(self.__fillBookItemModel(book, rewardBook, hiddenItems, *stateFlags))

        bookList.invalidate()

    def __fillBookItemModel(self, book, rewardBook, hiddenItems, canUseBook, isDisabled, hasError, hasMaxedTankmen):
        selectedCount = self.context.selection.getBookCountById(book.intCD)
        bookLocaleRoot = R.strings.crew_books.card.dyn(book.getBookSpread()) if book.hasNoNation() else R.strings.crew_books.card.nationBook
        isDisabled = isDisabled or not canUseBook and selectedCount == 0 and not self.context.selection.isBookPreSelecteed(book.intCD)
        availableCount = book.getFreeCount()
        bookItem = TrainingBookModel()
        bookItem.setIntCD(book.intCD)
        bookItem.setType(book.getBookType())
        bookItem.setIcon(book.icon)
        if bookLocaleRoot.isValid:
            bookTitle = bookLocaleRoot.title
            if bookTitle.isValid:
                bookItem.setTitle(backport.text(bookTitle()) if book.isPersonal() else backport.text(bookTitle.dyn(book.getBookType())()))
            bookItem.setMainText(backport.text(bookLocaleRoot.mainText()))
            bookItem.setAdditionalText(backport.text(bookLocaleRoot.additionalText()))
        bookItem.setBookAddedXp(book.getXP())
        bookItem.setAvailableCount(availableCount)
        bookItem.setSelectedCount(selectedCount)
        bookItem.setCanBuyBook(book.isForPurchase and book.intCD not in hiddenItems)
        bookItem.setCanAddMoreBooks(canUseBook)
        bookItem.setIsDisabled(isDisabled)
        bookItem.setHasError((hasError or isDisabled) and availableCount > 0)
        bookItem.setIsPersonal(book.isPersonal())
        bookItem.setHasPotentialLoss(not book.isPersonal() and self.context.hasCrewMaxedTman)
        if hasMaxedTankmen and book.getBookType() == rewardBook.getBookType():
            bookItem.setIsPostProgressionShown(True)
            bookItem.setPostProgressionClaimCount(self.context.postProgressionXp / rewardBook.getXP())
        return bookItem
