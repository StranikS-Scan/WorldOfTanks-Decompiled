# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/festival/festival_entry_point.py
import logging
from festivity.festival.hint_helper import FestivalHintHelper
from frameworks.wulf.gui_constants import ViewFlags
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.festival.festival_entry_point_model import FestivalEntryPointModel
from gui.impl.lobby.festival.festival_helper import fillFestivalPlayerCard
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showFestivalMainView
from helpers import dependency
from skeletons.festival import IFestivalController
_logger = logging.getLogger(__name__)

class FestivalEntrancePointInjectWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return FestivalEntrancePointWidget()


class FestivalEntrancePointWidget(ViewImpl):
    __festController = dependency.descriptor(IFestivalController)
    __slots__ = ()

    def __init__(self, viewKey=R.views.lobby.festival.festival_entry_point.FestivalEntrancePoint(), viewModelClazz=FestivalEntryPointModel, *args, **kwargs):
        super(FestivalEntrancePointWidget, self).__init__(viewKey, ViewFlags.VIEW, viewModelClazz, *args, **kwargs)

    def _initialize(self):
        super(FestivalEntrancePointWidget, self)._initialize()
        self.getViewModel().onWidgetClick += self.__onWidgetClick
        self.__festController.onDataUpdated += self.__onUpdate
        self.__festController.onStateChanged += self.__statusUpdate
        self.__update()
        self.__statusUpdate()

    def _finalize(self):
        self.getViewModel().onWidgetClick -= self.__onWidgetClick
        self.__festController.onDataUpdated -= self.__onUpdate
        self.__festController.onStateChanged -= self.__statusUpdate
        super(FestivalEntrancePointWidget, self)._finalize()

    @staticmethod
    def __onWidgetClick(_=None):
        showFestivalMainView()

    def __onUpdate(self, *_):
        self.__update()

    def __statusUpdate(self):
        self.getViewModel().setIsHighlight(not FestivalHintHelper.getFirstEntry())

    def __update(self):
        accountCard = self.__festController.getPlayerCard()
        fillFestivalPlayerCard(accountCard, self.getViewModel())
        unseenItems = len(self.__festController.getUnseenItems())
        self.getViewModel().Counter.setValue(unseenItems)
