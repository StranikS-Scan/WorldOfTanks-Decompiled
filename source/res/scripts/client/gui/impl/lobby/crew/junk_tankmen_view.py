# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/junk_tankmen_view.py
import nations
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer, WindowFlags
from gui.impl.gen.view_models.views.lobby.crew.junk_tankmen_view_model import JunkTankmenViewModel
from gui.impl.lobby.crew.base_tankman_list_view import BaseTankmanListView
from gui.impl.lobby.crew.filter.data_providers import JunkTankmenDataProvider
from gui.impl.lobby.crew.crew_helpers.model_setters import setTankmanModel, setTmanSkillsModel
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanModel
from gui.impl.gen import R
from gui.impl.pub import WindowImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.game_control import restore_contoller

class JunkTankmenView(BaseTankmanListView):
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__dataProvider',)

    def __init__(self, layoutID=R.views.lobby.crew.JunkTankmenView(), *args, **kwargs):
        settings = ViewSettings(layoutID, flags=ViewFlags.VIEW, model=JunkTankmenViewModel(), args=args, kwargs=kwargs)
        self.__dataProvider = JunkTankmenDataProvider()
        super(JunkTankmenView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(JunkTankmenView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(JunkTankmenView, self)._onLoading(*args, **kwargs)
        self.__dataProvider.update()

    def _getEvents(self):
        return ((self.viewModel.onLoadCards, self._onLoadCards),
         (self.viewModel.onClose, self._onClose),
         (self.viewModel.onConfirm, self._onConfirm),
         (self.__dataProvider.onDataChanged, self.__fillCardList))

    @property
    def _tankmenProvider(self):
        return self.__dataProvider

    @property
    def _recruitsProvider(self):
        return None

    @property
    def _filterState(self):
        return None

    @property
    def _uiLoggingKey(self):
        return None

    def _fillTankmanCard(self, cardsList, tankman):
        tm = TankmanModel()
        setTankmanModel(tm, tankman, tmanNativeVeh=self.itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr), tmanVeh=self.itemsCache.items.getVehicle(tankman.vehicleInvID))
        setTmanSkillsModel(tm.getSkills(), tankman)
        tm.setNation(nations.NAMES[tankman.nationID])
        tm.setHasVoiceover(False)
        if tankman.isDismissed:
            _, time = restore_contoller.getTankmenRestoreInfo(tankman)
            tm.setTimeToDismiss(time)
        cardsList.addViewModel(tm)

    def _fillRecruits(self, cardsList, limit, offset):
        pass

    def _onClose(self):
        self.destroyWindow()

    def _onConfirm(self):
        self.destroyWindow()

    def _fillRecruitCard(self, cardsList, recruitInfo):
        pass

    def __fillCardList(self):
        with self.viewModel.transaction() as tx:
            tx.setItemsAmount(self.__dataProvider.itemsCount)
            tx.setItemsOffset(self._itemsOffset)
            self._fillVisibleCards(tx.getTankmanList())


class JunkTankmenWindow(WindowImpl):

    def __init__(self):
        super(JunkTankmenWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW, content=JunkTankmenView())
