# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/change_commander_dialog_view.py
from async import await, async
from crew2 import settings_globals
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.dialogs.dialogs import buyDormitory
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.gf_drop_down_item import GfDropDownItem
from gui.impl.gen.view_models.ui_kit.gf_drop_down_model import GfDropDownModel
from gui.impl.gen.view_models.views.lobby.detachment.common.commander_card_constants import CommanderCardConstants
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.change_commander_dialog_view_model import ChangeCommanderDialogViewModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.new_commander_dialog_view_model import NewCommanderDialogViewModel
from gui.impl.lobby.detachment.popovers.filters.commander_filters import PortraitTypes
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.shared.items_cache import hasFreeDormsRooms, needDormsBlock
from helpers import dependency, strcmp
from helpers.i18n import makeString as _ms, encodeUtf8
from items.components.dormitory_constants import BuyDormitoryReason
from shared_utils import first
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.constants import GROUP, ACTION
from uilogging.detachment.loggers import DetachmentLogger

class ChangeCommanderDialogView(FullScreenDialogView):
    __slots__ = ('_detachment', '__gender', '__type', '__portraitType', '__portraitID', '__portraitIconName', '__selectedNameID', '__selectedSecondNameID')
    itemsCache = dependency.descriptor(IItemsCache)
    detachmentCache = dependency.descriptor(IDetachmentCache)
    uiLogger = DetachmentLogger(GROUP.CHANGE_COMMANDER_LOOK_DIALOG)

    def __init__(self, ctx, model=None):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.ChangeCommanderDialogView())
        settings.model = model or ChangeCommanderDialogViewModel()
        super(ChangeCommanderDialogView, self).__init__(settings)
        self._detachment = detachment = ctx['detachment']
        self.__gender = ctx.get('gender', detachment.cmdrGender)
        self.__portraitID = ctx['portraitID']
        self.__portraitIconName = ctx['portraitIconName']
        self.__type = ctx.get('type', CommanderCardConstants.COMMANDER_TYPE_DEFAULT)
        self.__portraitType = ctx.get('portraitType', PortraitTypes.DOCUMENT)
        self.__selectedNameID = ctx.get('firstNameID', detachment.getDescriptor().cmdrFirstNameID)
        self.__selectedSecondNameID = ctx.get('secondNameID', detachment.getDescriptor().cmdrSecondNameID)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self):
        self._fillModel()

    def _fillModel(self):
        with self.viewModel.transaction() as vm:
            vm.setType(self.__type)
            vm.setIconName(self.__portraitIconName)
            vm.setAcceptButtonText(R.strings.detachment.profile.select.accept())
            vm.setCancelButtonText(R.strings.detachment.profile.select.cancel())
            if self.__portraitType == PortraitTypes.SKIN:
                self._fillSkin(vm)
            else:
                self._fillDocument(vm)

    def _fillSkin(self, model):
        crewSkin = self.itemsCache.items.getCrewSkin(self.__portraitID)
        model.setName(localizedFullName(crewSkin))
        model.setDescription(backport.textRes(crewSkin.getDescription())())

    def _fillDocument(self, model):
        pool = settings_globals.g_characterProperties
        detachment = self._detachment
        gender = self.__gender
        commandersNames = model.names
        nameItems = commandersNames.getItems()
        firstNameIDs = pool.getCommonFirstNameIDs(detachment.nationID, gender)
        self.__fillNameModel(nameItems, firstNameIDs, pool.getFirstNameByID)
        commandersSurnames = model.surnames
        surnameItems = commandersSurnames.getItems()
        secondNameIDs = pool.getCommonSecondNameIDs(detachment.nationID, gender)
        self.__fillNameModel(surnameItems, secondNameIDs, pool.getSecondNameByID)
        if gender != detachment.cmdrGender:
            self.__selectedNameID = first(firstNameIDs)
            self.__selectedSecondNameID = first(secondNameIDs)
        self.__setSelected(model.names.getSelected(), str(self.__selectedNameID))
        self.__setSelected(model.surnames.getSelected(), str(self.__selectedSecondNameID))

    def _addListeners(self):
        super(ChangeCommanderDialogView, self)._addListeners()
        model = self.viewModel
        model.names.onChange += self.__onCommanderNameChange
        model.surnames.onChange += self.__onCommanderSurnameChange

    def _removeListeners(self):
        super(ChangeCommanderDialogView, self)._removeListeners()
        model = self.viewModel
        model.names.onChange -= self.__onCommanderNameChange
        model.surnames.onChange -= self.__onCommanderSurnameChange

    def _onAcceptClicked(self):
        self.uiLogger.log(ACTION.DIALOG_CONFIRM)
        super(ChangeCommanderDialogView, self)._onAcceptClicked()

    def _onExitClicked(self):
        self.uiLogger.log(ACTION.DIALOG_EXIT)
        super(ChangeCommanderDialogView, self)._onExitClicked()

    def _onCancelClicked(self):
        self.uiLogger.log(ACTION.DIALOG_CANCEL)
        super(ChangeCommanderDialogView, self)._onCancelClicked()

    def _getAdditionalData(self):
        return {'nameID': self.__selectedNameID,
         'secondNameID': self.__selectedSecondNameID}

    def __onCommanderNameChange(self, args=None):
        self.uiLogger.log(ACTION.COMMANDER_FIRST_NAME_CHANGED)
        with self.viewModel.transaction() as vm:
            _id = args['selectedIds']
            if _id:
                self.__setSelected(vm.names.getSelected(), _id)
                self.__selectedNameID = int(_id)

    def __onCommanderSurnameChange(self, args=None):
        self.uiLogger.log(ACTION.COMMANDER_LAST_NAME_CHANGED)
        with self.viewModel.transaction() as vm:
            _id = args['selectedIds']
            if _id:
                self.__setSelected(vm.surnames.getSelected(), _id)
                self.__selectedSecondNameID = int(_id)

    def __setSelected(self, model, value):
        model.clear()
        model.addString(value)
        model.invalidate()

    def __fillNameModel(self, modelNames, ids, nameGetter):
        detachment = self._detachment
        gender = self.__gender
        names = [ (unicode(_ms(nameGetter(detachment.nationID, _id, gender=gender))), _id) for _id in ids ]
        names.sort(cmp=lambda left, right: strcmp(left[0], right[0]))
        for name, _id in names:
            gfDropDownItemModel = GfDropDownItem()
            gfDropDownItemModel.setId(str(_id))
            gfDropDownItemModel.setLabel(encodeUtf8(name))
            modelNames.addViewModel(gfDropDownItemModel)


class NewCommanderDialogView(ChangeCommanderDialogView):
    __slots__ = ('__vehicle',)
    uiLogger = DetachmentLogger(GROUP.NEW_COMMANDER_DIALOG)

    def __init__(self, ctx):
        super(NewCommanderDialogView, self).__init__(ctx, NewCommanderDialogViewModel())
        vehInvID = ctx.get('vehInvID')
        if vehInvID is not None:
            self.__vehicle = self._itemsCache.items.getVehicle(vehInvID)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def _addListeners(self):
        super(NewCommanderDialogView, self)._addListeners()
        model = self.viewModel
        model.onBack += self.__onBack

    def _removeListeners(self):
        super(NewCommanderDialogView, self)._removeListeners()
        model = self.viewModel
        model.onBack -= self.__onBack

    def _fillModel(self):
        super(NewCommanderDialogView, self)._fillModel()
        with self.viewModel.transaction() as vm:
            vm.setAcceptButtonText(R.strings.dialogs.detachment.newCommander.submit())
            vm.setType(CommanderCardConstants.COMMANDER_TYPE_NEW)
            vm.setIsDetachmentLinked(bool(self.__vehicle.getLinkedDetachmentID()))
            if self.__vehicle:
                self.__fillVehicleModel(vm.vehicle)

    def _onAccept(self):
        if not hasFreeDormsRooms(itemsCache=self.itemsCache):
            self._buyDormitoryDialog()
        else:
            super(NewCommanderDialogView, self)._onAccept()

    @async
    def _buyDormitoryDialog(self):
        countBlocks = needDormsBlock(itemsCache=self.itemsCache, detachmentCache=self.detachmentCache)
        sdr = yield await(buyDormitory(self.getParentWindow(), countBlocks=countBlocks, reason=BuyDormitoryReason.RECRUIT_NEW_DETACHMENT))
        if sdr.result:
            ActionsFactory.doAction(ActionsFactory.BUY_DORMITORY, countBlocks)

    def __fillVehicleModel(self, model):
        vehicle = self.__vehicle
        model.setName(vehicle.shortUserName)
        model.setType(vehicle.type)
        model.setLevel(vehicle.level)
        model.setNation(vehicle.nationName)
        model.setIsElite(vehicle.isElite)

    def __onBack(self):
        self.uiLogger.log(ACTION.DIALOG_EXIT)
        self.destroyWindow()
