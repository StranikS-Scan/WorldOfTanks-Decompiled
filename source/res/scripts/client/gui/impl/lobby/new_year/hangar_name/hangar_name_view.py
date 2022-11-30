# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/hangar_name/hangar_name_view.py
import random
from enum import Enum
from adisp import adisp_process
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.hangar_name_view_model import HangarNameViewModel, Action
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.view_helpers.blur_manager import CachedBlur
from new_year.ny_processor import NYSetHangarNameProcessor
from skeletons.gui.game_control import IOverlayController
from skeletons.new_year import INewYearTutorialController, INewYearController
from uilogging.ny.loggers import NyHangarNameViewLogger
from visual_script_client.arena_blocks import dependency
_MAX_TITLE_ID = 40
_MAX_DESCRIPTION_ID = 40

class ScreenAction(Enum):
    SELECT = Action.SELECT
    CHANGE = Action.CHANGE


class HangarNameView(ViewImpl):
    __slots__ = ('__action', '__blur', '__titleId', '__descriptionId')
    __maxTitleId = 10
    __maxDescriptionId = 9
    __overlay = dependency.descriptor(IOverlayController)
    __nyTutorial = dependency.descriptor(INewYearTutorialController)
    __nyController = dependency.descriptor(INewYearController)
    __uiLogger = NyHangarNameViewLogger()

    def __init__(self, layoutID, layer, action):
        settings = ViewSettings(layoutID)
        settings.model = HangarNameViewModel()
        super(HangarNameView, self).__init__(settings)
        self.__blur = CachedBlur(enabled=False, ownLayer=layer - 1, blurRadius=0.1)
        self.__action = action.value
        self.__titleId = random.randint(1, _MAX_TITLE_ID)
        self.__descriptionId = random.randint(1, _MAX_DESCRIPTION_ID)

    @property
    def viewModel(self):
        return super(HangarNameView, self).getViewModel()

    def _finalize(self):
        self.__uiLogger.stop()
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        self.__overlay.setOverlayState(False)
        super(HangarNameView, self)._finalize()
        return

    def _getEvents(self):
        events = super(HangarNameView, self)._getEvents()
        return events + ((self.viewModel.onChangeAll, self.__onChangeAll),
         (self.viewModel.onChangeTitle, self.__onChangeTitle),
         (self.viewModel.onChangeDescription, self.__onChangeDescription),
         (self.viewModel.onSubmitName, self.__onSubmitName),
         (self.viewModel.enableBlur, self.__enableBlur),
         (self.viewModel.onAnimationRelease, self.__onAnimationRelease),
         (self.__nyController.onStateChanged, self.__onEventStateChanged))

    def _onLoading(self, *args, **kwargs):
        super(HangarNameView, self)._onLoading(*args, **kwargs)
        self.__overlay.setOverlayState(True)
        with self.viewModel.transaction() as tx:
            tx.setShowError(False)
            tx.setAction(self.__action)
            tx.hangarName.setTitle(self.__titleId)
            tx.hangarName.setDescription(self.__descriptionId)
        self.__uiLogger.start()

    def __onEventStateChanged(self):
        if not self.__nyController.isEnabled():
            self.destroyWindow()

    def __updateTitleId(self):
        self.__titleId = random.randint(1, _MAX_TITLE_ID)
        with self.viewModel.transaction() as tx:
            tx.hangarName.setTitle(self.__titleId)

    def __updateDescriptionId(self):
        self.__descriptionId = random.randint(1, _MAX_DESCRIPTION_ID)
        with self.viewModel.transaction() as tx:
            tx.hangarName.setDescription(self.__descriptionId)

    def __enableBlur(self):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.CITY_NAME_SELECTING_ENTER)
        self.__blur.enable()

    def __onAnimationRelease(self):
        pass

    def __onChangeAll(self):
        self.__uiLogger.logClick('all')
        NewYearSoundsManager.playEvent(NewYearSoundEvents.CHANGE_CITY_NAME)
        self.__updateTitleId()
        self.__updateDescriptionId()

    def __onChangeTitle(self):
        self.__uiLogger.logClick('title')
        NewYearSoundsManager.playEvent(NewYearSoundEvents.CHANGE_CITY_NAME)
        self.__updateTitleId()

    def __onChangeDescription(self):
        self.__uiLogger.logClick('description')
        NewYearSoundsManager.playEvent(NewYearSoundEvents.CHANGE_CITY_NAME)
        self.__updateDescriptionId()

    def __getHangarFullName(self):
        name = backport.text(R.strings.ny_hangar_name.title.num(self.__titleId)())
        description = backport.text(R.strings.ny_hangar_name.description.num(self.__descriptionId)())
        return backport.text(R.strings.ny.notification.fullCityName(), description=description, name=name)

    @adisp_process
    def __onSubmitName(self):
        result = yield NYSetHangarNameProcessor(self.__titleId, self.__descriptionId).request()
        if result.success:
            self.__nyTutorial.markNameSelected()
            SystemMessages.pushMessage(backport.text(R.strings.ny.notification.cityNameChanged(), name=self.__getHangarFullName()), type=SM_TYPE.Information, priority=NotificationPriorityLevel.LOW)
            self.destroyWindow()
        else:
            self.viewModel.setShowError(True)
            SystemMessages.pushMessage(backport.text(R.strings.ny.notification.cityNameChanged.error()), type=SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)


class HangarNameViewWindow(LobbyWindow):

    def __init__(self, action=ScreenAction.SELECT):
        super(HangarNameViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=HangarNameView(R.views.lobby.new_year.HangarNameView(), WindowLayer.OVERLAY, action), layer=WindowLayer.OVERLAY)
