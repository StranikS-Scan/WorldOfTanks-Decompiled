# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/conversion_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.conversion_tooltip_book_model import ConversionTooltipBookModel
from gui.impl.gen.view_models.views.lobby.crew.tooltips.conversion_tooltip_model import ConversionTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class ConversionTooltip(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__books', '__title', '__description')

    def __init__(self, books, **kwargs):
        settings = ViewSettings(R.views.lobby.crew.tooltips.ConversionTooltip())
        settings.model = ConversionTooltipModel()
        self.__books = books
        self.__title = kwargs.get('title')
        self.__description = kwargs.get('description')
        super(ConversionTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ConversionTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ConversionTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setTitle(self.__title)
            vm.setDescription(self.__description)
            booksList = vm.getBooksList()
            booksList.clear()
            for book, value in self.__books:
                tbm = ConversionTooltipBookModel()
                tbm.setIcon(book.getBonusIconName())
                tbm.setTitle(backport.text(R.strings.crew_books.items.dyn(book.getBookType()).noNationName()))
                tbm.setNation(backport.text(R.strings.nations.dyn(book.getNation())()))
                tbm.setValue(value)
                booksList.addViewModel(tbm)
