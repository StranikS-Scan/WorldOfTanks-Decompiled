# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/ny_anchor_view.py
from frameworks.wulf import ViewFlags, ViewStatus
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.views.ny_anchor_view_model import NyAnchorViewModel
from gui.impl.new_year.views.new_year_decorations_popover import NewYearDecorationsPopover
from gui.impl.pub import ViewImpl
from gui.impl.new_year.components.new_year_pop_over_window import NewYearPopOverWindow
from soft_exception import SoftException

class NyAnchorView(ViewImpl):
    __slots__ = ('__decorationsPopover', '__slotID')

    def __init__(self, *args, **kwargs):
        super(NyAnchorView, self).__init__(R.views.nyAnchorView, ViewFlags.COMPONENT, NyAnchorViewModel, *args, **kwargs)
        self.__decorationsPopover = None
        self.__slotID = None
        return

    @property
    def viewModel(self):
        return super(NyAnchorView, self).getViewModel()

    def createPopOverContent(self, event):
        self.__tryClearDecorationsPopover()
        self.__decorationsPopover = NewYearDecorationsPopover(self.__slotID)
        self.__decorationsPopover.onStatusChanged += self.__popoverOnStatusChanged
        self.viewModel.setIsSelected(True)
        return self.__decorationsPopover

    def createPopOver(self, event):
        content = self.createPopOverContent(event)
        window = None
        if content is not None:
            if not isinstance(content, NewYearDecorationsPopover):
                raise SoftException('NewYearDecorationsPopover content should be derived from NewYearPopOverWindow.')
            window = NewYearPopOverWindow(event, content, self.getParentWindow())
            window.load()
        return window

    def setSlotID(self, slotID):
        self.__slotID = slotID

    def _finalize(self):
        self.__tryClearDecorationsPopover()
        super(NyAnchorView, self)._finalize()

    def __tryClearDecorationsPopover(self):
        if self.__decorationsPopover is not None:
            self.__decorationsPopover.onStatusChanged -= self.__popoverOnStatusChanged
            self.__decorationsPopover = None
        return

    def __popoverOnStatusChanged(self, status):
        if status in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
            self.viewModel.setIsSelected(False)
            self.__tryClearDecorationsPopover()
