# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_collection_view.py
from frameworks.wulf import ViewFlags, WindowFlags, Window
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.views.new_year_collection_view_model import NewYearCollectionViewModel
from gui.impl.pub import ViewImpl
from gui.shared import event_dispatcher

class NewYearCollectionView(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(NewYearCollectionView, self).__init__(R.views.newYearCollectionView, ViewFlags.LOBBY_SUB_VIEW, NewYearCollectionViewModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(NewYearCollectionView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(NewYearCollectionView, self)._initialize()
        self.viewModel.onCloseBtnClick += self.__onCloseBtnClick

    def _finalize(self):
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        super(NewYearCollectionView, self)._finalize()

    def __onCloseBtnClick(self):
        window = self.getParentWindow()
        if window is not None:
            window.destroy()
        else:
            self.destroy()
        event_dispatcher.showNewYearMainView()
        return


class NewYearCollectionViewWindow(Window):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(NewYearCollectionViewWindow, self).__init__(content=NewYearCollectionView(*args, **kwargs), wndFlags=WindowFlags.WINDOW, decorator=None)
        return
