# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/new_commander_window_view.py
from collections import namedtuple
from async import await, async
from crew2 import settings_globals
from crew2.crew2_consts import TAG_TO_GENDER
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui import SystemMessages
from gui.shared.event_dispatcher import showHangar
from gui.impl.lobby.detachment.tooltips.colored_simple_tooltip import ColoredSimpleTooltip
from gui.shared.gui_items.processors.detachment import DetachmentCreate
from gui.shared.utils import decorators
from gui.impl.dialogs.dialogs import showDetachmentNewCommanderDialogView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.commander_card_constants import CommanderCardConstants
from gui.impl.gen.view_models.views.lobby.detachment.common.commander_card_model import CommanderCardModel
from gui.impl.gen.view_models.views.lobby.detachment.new_commander_window_model import NewCommanderWindowModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from items.components.detachment_constants import DetachmentAttrs, DETACHMENT_DEFAULT_PRESET
from items.detachment import DetachmentDescr
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger
from uilogging.detachment.constants import GROUP, ACTION
_CardInfo = namedtuple('_CardInfo', 'id iconName isFemale')

class NewCommanderWindowView(ViewImpl):
    __slots__ = ('_vehInvID', '_cards', '_vehicle', '_selectedCardID')
    detachmentCache = dependency.descriptor(IDetachmentCache)
    _itemsCache = dependency.descriptor(IItemsCache)
    _itemsFactory = dependency.descriptor(IGuiItemsFactory)
    uiLogger = DetachmentLogger(GROUP.NEW_COMMANDER_LIST)

    def __init__(self, layoutID, vehInvID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = NewCommanderWindowModel()
        super(NewCommanderWindowView, self).__init__(settings, True)
        self._vehInvID = vehInvID
        self._vehicle = self._itemsCache.items.getVehicle(self._vehInvID)
        self._cards = self.__getCards()
        self._selectedCardID = None
        return

    @property
    def viewModel(self):
        return super(NewCommanderWindowView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.__fillModel()

    def _initialize(self):
        super(NewCommanderWindowView, self)._finalize()
        self._addListeners()
        self.uiLogger.startAction(ACTION.OPEN)

    def _finalize(self):
        self.uiLogger.stopAction(ACTION.OPEN)
        super(NewCommanderWindowView, self)._finalize()
        self._removeListeners()

    def _addListeners(self):
        model = self.viewModel
        model.onClose += self.__onClose
        model.onCancel += self.__onCancel
        model.onContinue += self.__onContinue
        model.onCommanderClick += self.__onCommanderClick

    def _removeListeners(self):
        model = self.viewModel
        model.onClose -= self.__onClose
        model.onCancel -= self.__onCancel
        model.onContinue -= self.__onContinue
        model.onCommanderClick -= self.__onCommanderClick

    def createToolTipContent(self, event, contentID):
        return ColoredSimpleTooltip(event.getArgument('header', ''), event.getArgument('body', '')) if contentID == R.views.lobby.detachment.tooltips.ColoredSimpleTooltip() else super(NewCommanderWindowView, self).createToolTipContent(event, contentID)

    def __onClose(self):
        self.uiLogger.log(ACTION.DIALOG_EXIT)
        self.destroyWindow()

    def __getDetachmentFromVehicle(self, isFemale, iconID):
        overrideCtx = {DetachmentAttrs.IS_FEMALE: isFemale,
         DetachmentAttrs.CMDR_PORTRAIT_ID: iconID}
        detDescr, _ = DetachmentDescr.createByPreset(DETACHMENT_DEFAULT_PRESET, self._vehicle.strCD, overrideDetachmentCtx=overrideCtx)
        return detDescr

    @async
    def __onContinue(self):
        cardItem = self._cards[self._selectedCardID]
        detDescr = self.__getDetachmentFromVehicle(cardItem.isFemale, cardItem.id)
        detachment = self._itemsFactory.createDetachment(detDescr.makeCompactDescr())
        ctx = {'detachment': detachment,
         'portraitID': cardItem.id,
         'portraitIconName': cardItem.iconName,
         'vehInvID': self._vehInvID}
        g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.NEW_COMMANDER_DIALOG)
        sdr = yield await(showDetachmentNewCommanderDialogView(self.getParentWindow(), ctx))
        if sdr.result is None:
            return
        else:
            result, data = sdr.result
            if result is DialogButtons.SUBMIT:
                nameID = data['nameID'] or detachment.getDescriptor().cmdrFirstNameID
                secondNameID = data['secondNameID'] or detachment.getDescriptor().cmdrSecondNameID
                detDescr.changeFirstName(nameID)
                detDescr.changeSecondName(secondNameID)
                self.__createDetachment(detDescr)
            if result in (DialogButtons.EXIT, DialogButtons.SUBMIT):
                self.destroyWindow()
                showHangar()
            return

    @decorators.process('updating')
    def __createDetachment(self, detDescr):
        processor = DetachmentCreate(self._vehInvID, detDescr.makeCompactDescr())
        result = yield processor.request()
        SystemMessages.pushMessages(result)

    def __onCancel(self):
        self.uiLogger.log(ACTION.DIALOG_CANCEL)
        self.destroyWindow()

    def __onCommanderClick(self, args):
        cardID = args['id']
        with self.viewModel.transaction() as model:
            commandersList = model.getCommandersList()
            if self._selectedCardID is not None:
                commandersList[self._selectedCardID].setState(CommanderCardConstants.STATE_AVAILABLE)
            commandersList[cardID].setState(CommanderCardConstants.STATE_SELECTED)
            model.setIsNextButtonDisabled(False)
            commandersList.invalidate()
        self._selectedCardID = cardID
        return

    def __fillModel(self):
        with self.viewModel.transaction() as model:
            self.__fillList(model)
            self.__fillVehicleModel(model.vehicle)

    def __fillList(self, model):
        commandersList = model.getCommandersList()
        commandersList.clear()
        for uid, card in self._cards.iteritems():
            commanderCardModel = CommanderCardModel()
            commanderCardModel.setId(uid)
            commanderCardModel.setIconName(card.iconName)
            commanderCardModel.setState(CommanderCardConstants.STATE_AVAILABLE)
            commanderCardModel.setAmount(0)
            commanderCardModel.setType(CommanderCardConstants.COMMANDER_TYPE_NEW)
            commandersList.addViewModel(commanderCardModel)

        commandersList.invalidate()

    def __fillVehicleModel(self, model):
        vehicle = self._vehicle
        model.setName(vehicle.userName)
        model.setType(vehicle.type)
        model.setLevel(vehicle.level)
        model.setNation(vehicle.nationName)
        model.setIsElite(vehicle.isElite)

    def __getCards(self):
        cardList = []
        nationID = self._vehicle.nationID
        for gender in TAG_TO_GENDER.itervalues():
            portraitIDs = settings_globals.g_characterProperties.getCommonPortraitIDs(nationID, gender)
            for portraitID in portraitIDs:
                iconName = settings_globals.g_characterProperties.getPortraitByID(nationID, portraitID, gender)
                cardList.append(_CardInfo(portraitID, iconName, bool(gender.value)))

        return dict(enumerate(cardList))


class NewCommanderWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, vehInvID=None, parent=None, *args, **kwargs):
        super(NewCommanderWindow, self).__init__(WindowFlags.WINDOW_FULLSCREEN, content=NewCommanderWindowView(R.views.lobby.detachment.NewCommanderWindow(), vehInvID, *args, **kwargs), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)
