# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew_books/crew_books_dialog.py
import logging
from gui.ClientUpdateManager import g_clientUpdateManager
from async import async, await, AsyncEvent, AsyncReturn, AsyncScope, BrokenPromiseError
from frameworks.wulf import Window, WindowStatus, WindowSettings, ViewSettings
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from gui.impl.auxiliary.crew_books_helper import TankmanModelPresenterBase, TankmanSkillListPresenter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew_books.crew_books_dialog_content_model import CrewBooksDialogContentModel
from gui.impl.pub.dialog_window import DialogButtons, DialogLayer, DialogContent, DialogResult
from gui.impl.wrappers.background_blur import WGUIBackgroundBlurSupportImpl
from gui.impl.wrappers.user_format_string_arg_model import UserFormatStringArgModel
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory
from helpers.dependency import descriptor
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class CrewBooksDialog(Window):
    __itemsCache = descriptor(IItemsCache)
    __lobbyContext = descriptor(ILobbyContext)
    __gui = descriptor(IGuiLoader)
    __slots__ = ('__vehicle', '__selectedBook', '__tankman', '__tankmanInvID', '__blur', '__scope', '__event', '__result')

    def __init__(self, parent, crewBookCD, vehicleIntCD, tankmanInvId):
        self.__selectedBook = self.__itemsCache.items.getItemByCD(crewBookCD)
        self.__vehicle = self.__itemsCache.items.getItemByCD(vehicleIntCD)
        self.__tankman = self.__itemsCache.items.getTankman(int(tankmanInvId))
        self.__tankmanInvID = int(tankmanInvId)
        settings = WindowSettings()
        settings.flags = DialogLayer.TOP_WINDOW
        settings.content = DialogContent(ViewSettings(R.views.lobby.crew_books.crew_books_dialog_content.CrewBooksDialogContent(), model=CrewBooksDialogContentModel()))
        settings.parent = parent
        super(CrewBooksDialog, self).__init__(settings)
        self.__blur = WGUIBackgroundBlurSupportImpl()
        blurLayers = [APP_CONTAINERS_NAMES.VIEWS,
         APP_CONTAINERS_NAMES.SUBVIEW,
         APP_CONTAINERS_NAMES.BROWSER,
         APP_CONTAINERS_NAMES.WINDOWS]
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)
        self.__result = None
        self.__blur.enable(APP_CONTAINERS_NAMES.DIALOGS, blurLayers)
        return

    @property
    def contentViewModel(self):
        return self.content.getViewModel()

    @async
    def wait(self):
        try:
            yield await(self.__event.wait())
        except BrokenPromiseError:
            _logger.debug('%s has been destroyed without user decision', self)

        raise AsyncReturn(DialogResult(self.__result, None))
        return

    def _initialize(self):
        super(CrewBooksDialog, self)._initialize()
        with self.contentViewModel.transaction() as model:
            model.setTitle(R.strings.dialogs.crewBooks.confirmation.title())
            if self.__tankman is not None:
                tankmanVM = TankmanModelPresenterBase().getModel(0, self.__tankman.invID, False)
                tankmanVM.tankmanSkillList.setItems(TankmanSkillListPresenter().getList(self.__tankman.invID, False))
                tankmanList = model.crewBookTankmenList.getItems()
                tankmanList.addViewModel(tankmanVM)
                tankmanList.invalidate()
                model.setDescription(R.strings.dialogs.crewBooks.confirmation.desc.personalBook())
                descriptionFmtArgsVM = model.getDescriptionFmtArgs()
                descriptionFmtArgsVM.addViewModel(UserFormatStringArgModel(self.__tankman.fullUserName, 'name'))
                descriptionFmtArgsVM.addViewModel(UserFormatStringArgModel(self.__gui.systemLocale.getNumberFormat(self.__selectedBook.getXP()), 'exp'))
                descriptionFmtArgsVM.invalidate()
            else:
                model.setIsAllCrewIconVisible(True)
                model.setDescription(R.strings.dialogs.crewBooks.confirmation.desc.crewBook())
                descriptionFmtArgsVM = model.getDescriptionFmtArgs()
                descriptionFmtArgsVM.addViewModel(UserFormatStringArgModel(str(self.__vehicle.shortUserName), 'vehicle_name'))
                descriptionFmtArgsVM.addViewModel(UserFormatStringArgModel(self.__gui.systemLocale.getNumberFormat(self.__selectedBook.getXP()), 'exp'))
                descriptionFmtArgsVM.invalidate()
        self.__addListeners()
        return

    def __addListeners(self):
        self.contentViewModel.onUseBtnClick += self.__onUseBtnClick
        self.contentViewModel.onClosed += self.__onClosed
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryUpdate})

    def __removeListeners(self):
        self.contentViewModel.onUseBtnClick -= self.__onUseBtnClick
        self.contentViewModel.onClosed -= self.__onClosed
        g_clientUpdateManager.removeCallback('inventory', self.__onInventoryUpdate)

    def __onInventoryUpdate(self, invDiff):
        with self.contentViewModel.transaction() as model:
            if GUI_ITEM_TYPE.TANKMAN in invDiff:
                tmen = invDiff[GUI_ITEM_TYPE.TANKMAN]
                if self.__tankman is not None and self.__tankman.invID in tmen['compDescr']:
                    tankmanList = model.crewBookTankmenList.getItems()
                    tankmanVM = tankmanList.getValue(0)
                    self.__setSkillListViewModelData(tankmanVM)
                    tankmanList.invalidate()
        return

    def __setSkillListViewModelData(self, tankmanVM):
        skillListVM = tankmanVM.tankmanSkillList.getItems()
        skillListVM.clear()
        tankmanVM.tankmanSkillList.setItems(TankmanSkillListPresenter().getList(self.__tankman.invID))

    def _finalize(self):
        self.__removeListeners()
        self.__selectedBook = None
        self.__vehicle = None
        self.__tankman = None
        self.__tankmanInvID = None
        super(CrewBooksDialog, self)._finalize()
        self.__blur.disable()
        self.__scope.destroy()
        return

    def __startUseModelUpdate(self):
        with self.contentViewModel.transaction() as model:
            model.setIsUseStarted(True)
            model.setTitle(R.strings.dialogs.crewBooks.success.title())
            descriptionFmtArgsVM = model.getDescriptionFmtArgs()
            descriptionFmtArgsVM.clear()
            if self.__tankman is not None:
                model.setDescription(R.strings.dialogs.crewBooks.success.desc.personalBook())
                descriptionFmtArgsVM = model.getDescriptionFmtArgs()
                descriptionFmtArgsVM.clear()
                descriptionFmtArgsVM.addViewModel(UserFormatStringArgModel(self.__tankman.fullUserName, 'name'))
                descriptionFmtArgsVM.addViewModel(UserFormatStringArgModel(self.__gui.systemLocale.getNumberFormat(self.__selectedBook.getXP()), 'exp'))
            else:
                model.setDescription(R.strings.dialogs.crewBooks.success.desc.crewBook())
                descriptionFmtArgsVM.addViewModel(UserFormatStringArgModel(self.__gui.systemLocale.getNumberFormat(self.__selectedBook.getXP()), 'exp'))
                descriptionFmtArgsVM.addViewModel(UserFormatStringArgModel(str(self.__vehicle.shortUserName), 'vehicle_name'))
                descriptionFmtArgsVM.invalidate()
            descriptionFmtArgsVM.invalidate()
        return

    def __onUseBtnClick(self):
        if self.windowStatus == WindowStatus.LOADED:
            factory.doAction(factory.USE_CREW_BOOK, self.__selectedBook.intCD, self.__vehicle.invID, self.__tankmanInvID)
            if not self.__lobbyContext.getServerSettings().isCrewBooksEnabled():
                self.__result = DialogButtons.CANCEL
                self.__event.set()
            else:
                self.__result = DialogButtons.SUBMIT
                self.__startUseModelUpdate()

    def __onClosed(self, _=None):
        if self.__result is None:
            self.__result = DialogButtons.CANCEL
        self.__event.set()
        return
