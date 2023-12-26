# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/hangar_name/hangar_name_view.py
import wg_async as future_async
import random
import BigWorld
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.hangar_name_view_model import HangarNameViewModel, TypeView
from gui.impl.lobby.new_year.dialogs.dialogs import showHangarNameChangeConfirmDialog
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.pub import ViewImpl
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.shared.utils import decorators
from helpers import dependency
from new_year.ny_helper import getNYGeneralConfig
from new_year.ny_processor import NYSetHangarNameProcessor
from ny_common.GeneralConfig import GeneralConfig
from skeletons.gui.game_control import IOverlayController
from skeletons.new_year import INewYearTutorialController, INewYearController
from uilogging.ny.loggers import NyHangarNameViewLogger

class HangarNameView(ViewImpl):
    __slots__ = ('__typeView', '__blur', '__titleId', '__descriptionId')
    __overlay = dependency.descriptor(IOverlayController)
    __nyTutorial = dependency.descriptor(INewYearTutorialController)
    __nyController = dependency.descriptor(INewYearController)
    __uiLogger = NyHangarNameViewLogger()

    def __init__(self, layoutID, layer, typeView):
        settings = ViewSettings(layoutID)
        settings.model = HangarNameViewModel()
        super(HangarNameView, self).__init__(settings)
        self.__nyTutorial.moveCameraToTop()
        self.__overlay.setOverlayState(True)
        self.__blur = CachedBlur(enabled=True, ownLayer=layer - 1)
        self.__typeView = typeView
        self.__titleId, self.__descriptionId = GeneralConfig.parseHangarNameMask(self.__nyController.getHangarNameMask())

    @property
    def viewModel(self):
        return super(HangarNameView, self).getViewModel()

    def _finalize(self):
        self.__uiLogger.stop()
        self.__overlay.setOverlayState(False)
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        super(HangarNameView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onChangeAll, self.__onChangeAll),
         (self.viewModel.onChangeTitle, self.__onChangeTitle),
         (self.viewModel.onChangeDescription, self.__onChangeDescription),
         (self.viewModel.onSubmitName, self.__onSubmitName),
         (self.viewModel.onKeepName, self.__onKeepName),
         (self.viewModel.onCloseWelcomeScreen, self.__onCloseWelcomeScreen),
         (self.viewModel.onCloseChangeNameScreen, self.__onCloseChangeNameScreen),
         (self.__nyController.onStateChanged, self.__onEventStateChanged))

    def _onLoading(self, *args, **kwargs):
        super(HangarNameView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setTypeView(self.__typeView)
            tx.hangarName.setTitle(self.__titleId)
            tx.hangarName.setDescription(self.__descriptionId)
        self.__uiLogger.start()

    def _onLoaded(self, *args, **kwargs):
        super(HangarNameView, self)._onLoaded(*args, **kwargs)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.CITY_NAME_SELECTING_ENTER)

    def __onEventStateChanged(self):
        if not self.__nyController.isEnabled():
            self.destroyWindow()

    def __checkChanges(self):
        nameID, descID = GeneralConfig.parseHangarNameMask(self.__nyController.getHangarNameMask())
        self.viewModel.setHasChanges(self.__titleId != nameID or self.__descriptionId != descID)

    def __updateTitleId(self):
        self.__titleId = random.randint(1, getNYGeneralConfig().getMaxNameTitleID())
        with self.viewModel.transaction() as tx:
            tx.hangarName.setTitle(self.__titleId)
        self.__checkChanges()

    def __updateDescriptionId(self):
        self.__descriptionId = random.randint(1, getNYGeneralConfig().getMaxNameDescriptionID())
        with self.viewModel.transaction() as tx:
            tx.hangarName.setDescription(self.__descriptionId)
        self.__checkChanges()

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

    @decorators.adisp_process('newYear/hangarNameDialog')
    def __applyName(self, nameID, descID):
        result = yield NYSetHangarNameProcessor(nameID, descID).request()
        if result.success:
            SystemMessages.pushMessage(backport.text(R.strings.ny.notification.cityNameChanged()), type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.ny.notification.cityNameChanged.header())})
        else:
            SystemMessages.pushMessage(backport.text(R.strings.ny.notification.cityNameChanged.error()), type=SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)

    @future_async.wg_async
    def __setName(self, nameID, descID):
        self.viewModel.setIsHidden(True)
        dialogResult = yield showHangarNameChangeConfirmDialog(parent=self.getParentWindow(), nameID=nameID, descID=descID)
        self.viewModel.setIsHidden(False)
        if dialogResult is not None and dialogResult.result == DialogButtons.SUBMIT:
            self.__applyName(nameID, descID)
            self.__nyTutorial.resetCameraToTank()
            self.destroyWindow()
        return

    def __onSubmitName(self):
        self.__setName(self.__titleId, self.__descriptionId)

    def __onKeepName(self):
        self.__setName(*GeneralConfig.parseHangarNameMask(self.__nyController.getHangarNameMask()))

    def __onCloseWelcomeScreen(self):
        hangarNameSetToken = getNYGeneralConfig().getHangarNameSetToken()
        BigWorld.player().requestSingleToken(hangarNameSetToken)
        self.__nyTutorial.markNameSelected()
        self.__nyTutorial.resetCameraToTank()
        self.destroyWindow()

    def __onCloseChangeNameScreen(self):
        self.__nyTutorial.resetCameraToTank()
        self.destroyWindow()


class HangarNameViewWindow(LobbyWindow):

    def __init__(self, typeView=TypeView.WELCOME):
        super(HangarNameViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=HangarNameView(R.views.lobby.new_year.HangarNameView(), WindowLayer.OVERLAY, typeView), layer=WindowLayer.OVERLAY)
