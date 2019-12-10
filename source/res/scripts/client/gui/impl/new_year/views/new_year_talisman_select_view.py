# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_talisman_select_view.py
import GUI
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_talisman_select_state_model import NewYearTalismanSelectStateModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_talisman_select_view_model import NewYearTalismanSelectViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyOverlay
from helpers import dependency
from items.components.ny_constants import ToySettings
from skeletons.new_year import ITalismanSceneController, INewYearController
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
_TALISMAN_ORDERED_SET = (ToySettings.FAIRYTALE,
 ToySettings.NEW_YEAR,
 ToySettings.CHRISTMAS,
 ToySettings.ORIENTAL)
_TALISMAN_POSITION_SET_VALUES_ = ((-372, -114, 81, 372),
 (-384, -118, 81, 388),
 (-390, -120, 86, 396),
 (-416, -128, 96, 420),
 (-436, -134, 96, 442),
 (-462, -140, 100, 462),
 (-486, -150, 110, 494),
 (-508, -154, 116, 510),
 (-516, -152, 120, 516),
 (-516, -158, 120, 526),
 (-520, -152, 120, 544),
 (-548, -160, 134, 570),
 (-580, -170, 138, 612),
 (-630, -190, 146, 630),
 (-680, -206, 150, 690),
 (-780, -240, 170, 790),
 (-1168, -360, 250, 1180),
 (-1248, -380, 270, 1268),
 (-1360, -410, 300, 1368),
 (-500, -160, 110, 512),
 (-980, -310, 220, 1000),
 (-756, -236, 150, 760),
 (-880, -270, 190, 890))
_TALISMAN_WIDTH_SET_ = (1024, 1152, 1280, 1366, 1440, 1600, 1680, 1920, 2200, 2560, 2816, 3220, 3840, 4096)
_TALISMAN_HEIGHT_SET = (768, 800, 864, 900, 960, 1024, 1050, 1080, 1137, 1200, 1440, 2337)
_TALISMAN_POSITION_SETS_TABLE_ = ((0, 1, 3, 4, 5, 6, 7, 9, 11, 12, 14, 22),
 (0, 1, 3, 4, 5, 6, 7, 9, 11, 12, 14, 22),
 (2, 2, 3, 4, 5, 6, 7, 9, 11, 12, 14, 22),
 (3, 3, 3, 3, 5, 6, 7, 9, 11, 12, 14, 22),
 (4, 4, 4, 4, 5, 6, 7, 9, 11, 12, 14, 22),
 (6, 6, 6, 6, 6, 6, 6, 10, 11, 12, 14, 22),
 (8, 8, 8, 8, 8, 8, 8, 8, 11, 12, 14, 22),
 (12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 14, 22),
 (21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 14, 22),
 (15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 22),
 (4, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22),
 (19, 19, 19, 20, 20, 20, 20, 20, 20, 20, 20, 20),
 (12, 12, 12, 12, 12, 12, 16, 16, 16, 16, 16, 16),
 (13, 13, 13, 13, 13, 13, 13, 13, 17, 17, 17, 17))

class NewYearTalismanSelectView(ViewImpl):
    __talismanController = dependency.descriptor(ITalismanSceneController)
    __newYearController = dependency.descriptor(INewYearController)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_talisman_select_view.NewYearTalismanSelectView())
        settings.model = NewYearTalismanSelectViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NewYearTalismanSelectView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NewYearTalismanSelectView, self).getViewModel()

    def _initialize(self):
        super(NewYearTalismanSelectView, self)._initialize()
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_SELECTION)
        self.viewModel.onCloseBtnClick += self.__onCloseBtnClick
        self.viewModel.onViewResized += self.__onViewResized
        width, height = GUI.screenResolution()[:2]
        self.__setTalismansPosition(width, height)
        selected = [ item.getSetting() for item in self.__newYearController.getTalismans(isInInventory=True) ]
        with self.viewModel.transaction() as tx:
            tx.setSelectedCount(len(selected))
            talismans = tx.getTalismans()
            for talismanSetting in _TALISMAN_ORDERED_SET:
                selectModel = NewYearTalismanSelectStateModel()
                selectModel.setTalismanType(talismanSetting)
                selectModel.setIsSelected(talismanSetting in selected)
                talismans.addViewModel(selectModel)

            talismans.invalidate()

    def _finalize(self):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_SELECTION_EXIT)
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        self.viewModel.onViewResized -= self.__onViewResized
        super(NewYearTalismanSelectView, self)._finalize()

    def __onCloseBtnClick(self, _=None):
        self.__talismanController.switchToHangar()
        self.destroy()

    def __onViewResized(self, args):
        self.__setTalismansPosition(args.get('width'), args.get('height'))

    def __setTalismansPosition(self, width, height):
        posWidth = 0
        posHeight = 0
        for i, wdth in enumerate(_TALISMAN_WIDTH_SET_):
            if i < len(_TALISMAN_WIDTH_SET_) - 1:
                if wdth > width:
                    posWidth = i - 1 if i > 0 else 0
                    break
            posWidth = i

        for j, hgth in enumerate(_TALISMAN_HEIGHT_SET):
            if j < len(_TALISMAN_HEIGHT_SET) - 1:
                if hgth > height:
                    posHeight = j - 1 if j > 0 else 0
                    break
            posHeight = j

        positionIndex = _TALISMAN_POSITION_SETS_TABLE_[posWidth][posHeight]
        positionSet = self.viewModel.getTalismanPositionSet()
        positionSet.clear()
        for pos in _TALISMAN_POSITION_SET_VALUES_[positionIndex]:
            positionSet.addNumber(pos)

        positionSet.invalidate()


class NewYearTalismanSelectViewWindow(LobbyOverlay):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(NewYearTalismanSelectViewWindow, self).__init__(decorator=None, content=NewYearTalismanSelectView(*args, **kwargs), parent=None)
        return
