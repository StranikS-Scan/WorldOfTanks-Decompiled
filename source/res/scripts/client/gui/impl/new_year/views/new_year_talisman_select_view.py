# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_talisman_select_view.py
import GUI
import Math
from AvatarInputHandler.cameras import worldToScreenPos
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_talisman_select_state_model import NewYearTalismanSelectStateModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_talisman_select_view_model import NewYearTalismanSelectViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyOverlay
from helpers import dependency
from items.components.ny_constants import ToySettings
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.new_year import ITalismanSceneController, INewYearController
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
_TALISMANS_ORDER = (ToySettings.FAIRYTALE,
 ToySettings.NEW_YEAR,
 ToySettings.CHRISTMAS,
 ToySettings.ORIENTAL)
_DEFAULT_SCREEN_POSITION = Math.Vector2(-10000, -10000)

class NewYearTalismanSelectView(ViewImpl):
    __talismanController = dependency.descriptor(ITalismanSceneController)
    __newYearController = dependency.descriptor(INewYearController)
    __settingsCore = dependency.descriptor(ISettingsCore)
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
        self.__talismanController.addTalismanHoverObserver(self)
        self.__setTalismansPosition()
        selected = [ item.getSetting() for item in self.__newYearController.getTalismans(isInInventory=True) ]
        with self.viewModel.transaction() as tx:
            tx.setSelectedCount(len(selected))
            talismans = tx.getTalismans()
            for talismanSetting in _TALISMANS_ORDER:
                selectModel = NewYearTalismanSelectStateModel()
                selectModel.setTalismanType(talismanSetting)
                selectModel.setIsSelected(talismanSetting in selected)
                talismans.addViewModel(selectModel)

            talismans.invalidate()

    def _finalize(self):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_SELECTION_EXIT)
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        self.viewModel.onViewResized -= self.__onViewResized
        self.__talismanController.removeTalismanHoverObserver(self)
        super(NewYearTalismanSelectView, self)._finalize()

    def onTalismanMouseOver(self, talismanType):
        with self.viewModel.transaction() as tx:
            talismans = tx.getTalismans()
            for talisman in talismans:
                talisman.setIsHover(talisman.getTalismanType() == talismanType and not talisman.getIsSelected())

            talismans.invalidate()

    def onTalismanMouseOut(self, talismanType):
        with self.viewModel.transaction() as tx:
            talismans = tx.getTalismans()
            talisman = talismans[_TALISMANS_ORDER.index(talismanType)]
            talisman.setIsHover(False)
            talismans.invalidate()

    def __onCloseBtnClick(self, _=None):
        self.__talismanController.switchToHangar()
        self.destroy()

    def __onViewResized(self, *_):
        self.__setTalismansPosition()

    def __setTalismansPosition(self):
        scale = round(self.__settingsCore.interfaceScale.get(), 1)
        halfWidth = round(GUI.screenResolution()[0] / scale / 2)
        positionSet = self.viewModel.getTalismanPositionSet()
        positionSet.clear()
        for talismanName in _TALISMANS_ORDER:
            position = self.__getTalismanPreviewScreenSpacePosition(talismanName, scale) or _DEFAULT_SCREEN_POSITION
            positionSet.addNumber(position.x - halfWidth)

        positionSet.invalidate()

    def __getTalismanPreviewScreenSpacePosition(self, talismanName, scale):
        positionWS = self.__talismanController.getTalismanPosition(talismanName, preview=True)
        return worldToScreenPos(positionWS, scale=scale, clip=False) if positionWS is not None else None


class NewYearTalismanSelectViewWindow(LobbyOverlay):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(NewYearTalismanSelectViewWindow, self).__init__(content=NewYearTalismanSelectView(*args, **kwargs))
