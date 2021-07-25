# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/convert_window_view.py
from typing import List, Tuple
from itertools import chain
import nations
from CurrentVehicle import g_currentVehicle
from async import await, async
from crew2 import settings_globals
from crew2.crew2_consts import GENDER
from frameworks.wulf import ViewSettings, Array
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.framework.entities.View import ViewKey
from gui.app_loader import sf_lobby
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import fillDetachmentShortInfoModel
from gui.impl.auxiliary.detachmnet_convert_helper import getDetachmentFromVehicle
from gui.impl.auxiliary.instructors_helper import fillInstructorConvertList, GUI_NO_INSTRUCTOR_ID
from gui.impl.dialogs.dialogs import buyDormitory
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_base_model import InstructorBaseModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_shown_page_constants import InstructorShownPageConstants
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.convert_slot_vehicle_model import ConvertSlotVehicleModel
from gui.impl.gen.view_models.views.lobby.detachment.convert_window_model import ConvertWindowModel
from gui.impl.gen.view_models.views.lobby.detachment.instructors_and_skins_model import InstructorsAndSkinsModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.convertation_vehicle_tooltip_model import ConvertationVehicleTooltipModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.points_info_tooltip_model import PointsInfoTooltipModel
from gui.impl.lobby.detachment.tooltips.colored_simple_tooltip import ColoredSimpleTooltip
from gui.impl.lobby.detachment.tooltips.commander_look_tooltip import CommanderLookTooltip
from gui.impl.lobby.detachment.tooltips.convertation_vehicle_tooltip_view import ConvertationVehicleTooltipView
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import InstructorTooltip, EmptyInstructorTooltip
from gui.impl.lobby.detachment.tooltips.level_badge_tooltip_view import LevelBadgeTooltipView
from gui.impl.lobby.detachment.tooltips.points_info_tooltip_view import PointInfoTooltipView
from gui.impl.lobby.detachment.tooltips.rank_tooltip import RankTooltip
from gui.impl.pub import ViewImpl
from gui.impl.pub.dialog_window import DialogFlags
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.event_dispatcher import showHangar, showDetachmentViewById, showConvertInfoWindow
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.Tankman import getFullUserName
from gui.shared.gui_items.Vehicle import getIconResourceName, getNationLessName
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.gui_items.detachment import Detachment
from gui.shared.gui_items.processors.common import DormitoryBuyer
from gui.shared.gui_items.processors.detachment import ConvertVehicleCrewIntoDetachment, ConvertRecruitsIntoDetachment
from gui.shared.items_cache import hasFreeDormsRooms, needDormsBlock
from gui.shared.utils import decorators
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from items.components.detachment_constants import DetachmentSlotType, NO_DETACHMENT_ID
from items.components.dormitory_constants import BuyDormitoryReason
from items.detachment import DetachmentDescr
from items.instructor import InstructorDescr
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from shared_utils import first
from sound_constants import HANGAR_OVERLAY_SOUND_SPACE
from uilogging.detachment.constants import GROUP, ACTION
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger
_DESCRIPTOR_TEMPLATE = '#detachment:{}_instructor_descr'

class ConvertWindowView(ViewImpl):
    __slots__ = ('_vehicle', '_recruits', '_instructors', '_unremovableInstructors', '_skinID', '_detDescr', '_tooltipByContentID', '_prevViewID')
    _COMMON_SOUND_SPACE = HANGAR_OVERLAY_SOUND_SPACE
    itemsCache = dependency.descriptor(IItemsCache)
    detachmentCache = dependency.descriptor(IDetachmentCache)
    itemsFactory = dependency.descriptor(IGuiItemsFactory)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __gui = dependency.descriptor(IGuiLoader)
    uiLogger = DetachmentLogger(GROUP.MOBILIZE_CREW_CONFIRMATION)

    def __init__(self, layoutID, vehicle, recruits=None, prevViewID=None):
        settings = ViewSettings(layoutID)
        settings.model = ConvertWindowModel()
        super(ConvertWindowView, self).__init__(settings, True)
        self._vehicle = vehicle
        self._recruits = recruits or vehicle.crew
        self._prevViewID = prevViewID if bool(prevViewID) else ''
        self._skinID = NO_CREW_SKIN_ID
        self._detDescr = None
        self._instructors = []
        self._unremovableInstructors = {}
        tooltips = R.views.lobby.detachment.tooltips
        self._tooltipByContentID = {tooltips.PointsInfoTooltip(): self.__getPointInfoTooltip,
         tooltips.InstructorTooltip(): self.__getInstructorOrSkinTooltip,
         tooltips.ConvertationVehicleTooltip(): self.__getConvertationVehicleTooltip,
         tooltips.ColoredSimpleTooltip(): self.__getColoredSimpleTooltip,
         tooltips.RankTooltip(): self.__getRankTooltip,
         tooltips.LevelBadgeTooltip(): self.__getLevelBadgeTooltip}
        return

    @property
    def viewModel(self):
        return super(ConvertWindowView, self).getViewModel()

    @sf_lobby
    def app(self):
        return None

    @uiLogger.dStartAction(ACTION.OPEN)
    def _initialize(self, *args, **kwargs):
        super(ConvertWindowView, self)._initialize()
        self.viewModel.onSaveChanges += self.__onPreparationSaveChanges
        self.viewModel.onCancelChanges += self.__onCancelChanges
        self.viewModel.onGoToAboutConvert += self.__goToAboutConvert
        self.viewModel.onCloseWindow += self.__onCloseWindow

    @uiLogger.dStopAction(ACTION.OPEN)
    def _finalize(self):
        self.viewModel.onSaveChanges -= self.__onPreparationSaveChanges
        self.viewModel.onCancelChanges -= self.__onCancelChanges
        self.viewModel.onGoToAboutConvert -= self.__goToAboutConvert
        self.viewModel.onCloseWindow -= self.__onCloseWindow
        self._vehicle = None
        self._recruits = None
        self._detDescr = None
        self._instructors = []
        self._unremovableInstructors = {}
        self._tooltipByContentID = {}
        self.soundManager.playInstantSound(backport.sound(R.sounds.detachment_progress_bar_stop_all()))
        super(ConvertWindowView, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        self.__createDataForDetachmentShortInfo()

    @async
    def __onPreparationSaveChanges(self):
        if not hasFreeDormsRooms(itemsCache=self.itemsCache):
            countBlocks = needDormsBlock(itemsCache=self.itemsCache, detachmentCache=self.detachmentCache)
            sdr = yield await(buyDormitory(self.getParentWindow(), countBlocks=countBlocks, reason=BuyDormitoryReason.RECRUIT_NEW_DETACHMENT))
            if sdr.result:
                self.__byDormitories(countBlocks)
        else:
            self.__onSaveChanges()

    @decorators.process('buyDormitory')
    def __byDormitories(self, countBlocks):
        result = yield DormitoryBuyer(countBlocks).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.__onSaveChanges()

    @decorators.process('updating')
    def __onSaveChanges(self):
        vehicle = self._vehicle
        skinID = self._skinID
        if skinID != NO_CREW_SKIN_ID:
            skinItem = self.itemsCache.items.getCrewSkin(skinID)
            if skinItem.getFreeCount() == 0:
                skinID = NO_CREW_SKIN_ID
        detCompDescr = self._detDescr.makeCompactDescr()
        countRecruitsBeforeConversion = self.__getCurrentCountRecruits()
        if vehicle.isCrewLocked:
            processor = ConvertVehicleCrewIntoDetachment(vehicle.invID, skinID, detCompDescr)
        else:
            processor = ConvertRecruitsIntoDetachment(self._recruits, vehicle, skinID, detCompDescr)
        result = yield processor.request()
        SystemMessages.pushMessages(result)
        if result.success and countRecruitsBeforeConversion - len(self._recruits) <= 0:
            self.__checkResetRecruitsFilter()
        self.__returnToPrevView(result.auxData.get('detachmentInvID'))

    def __checkResetRecruitsFilter(self):
        view = self.app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_HANGAR))
        if view:
            tankCarousel = view.getComponent(HANGAR_ALIASES.TANK_CAROUSEL)
            if not tankCarousel:
                return
            tankCarousel.resetFilterByKey('recruits')

    def __getCurrentCountRecruits(self):
        return len(self.itemsCache.items.getTankmen(REQ_CRITERIA.TANKMAN.REGULAR))

    def __returnToPrevView(self, detInvID=None):
        if self._vehicle.inventoryCount or not self._prevViewID:
            g_currentVehicle.selectVehicle(self._vehicle.invID)
            showHangar()
        else:
            showDetachmentViewById(NavigationViewModel.BARRACK_DETACHMENT)
        self.destroyWindow()

    def __onCancelChanges(self):
        self.destroyWindow()

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.MOBILIZE_CREW_INFO)
    def __goToAboutConvert(self):
        showConvertInfoWindow()

    def __onCloseWindow(self):
        self.destroyWindow()
        showHangar()

    def __createDataForDetachmentShortInfo(self):
        vehicle = self._vehicle
        detDescr, instDescrs, detPreset, skinID = getDetachmentFromVehicle(vehicle, self._recruits)
        detachment = self.itemsFactory.createDetachment(detDescr.makeCompactDescr())
        with self.viewModel.transaction() as vm:
            rankIcon = detachment.rankRecord.icon.split('.')[0].replace('-', '_')
            vm.setCommanderRank(R.images.gui.maps.icons.detachment.ranks.c_160x118.dyn(rankIcon)())
            vm.setLeaderName(detachment.leaderName)
            vm.setEliteTitle(detachment.eliteTitle)
            vm.setAvailablePoints(detachment.freePoints)
            self._instructors = []
            self._unremovableInstructors = {}
            self.__fillDetachment(vm.detachment, detDescr, skinID)
            self.__fillInstructorSlots(vm.getInstructorsSlots(), detDescr, instDescrs)
            self.__fillVehicleSlots(vm.getVehicleSlots(), detachment, detDescr)
            self.__fillInstructorsAndSkins(vm.getInstructors(), detPreset, vehicle, skinID)
            self.__fillVehicle(vm.vehicle, vehicle)
            vm.setPreviousViewId(self._prevViewID)
        self._detDescr = detDescr
        self._skinID = skinID

    def __fillDetachment(self, model, detDescr, skinID):
        vehicle = self._vehicle
        detachment = self.itemsFactory.createDetachment(detDescr.makeCompactDescr())
        fillDetachmentShortInfoModel(model, detachment, fillInstructors=False, vehicle=vehicle)
        if skinID != NO_CREW_SKIN_ID and self.lobbyContext.getServerSettings().isCrewSkinsEnabled():
            skinItem = self.itemsCache.items.getCrewSkin(skinID)
            if skinItem.getFreeCount():
                model.setHasCrewSkin(True)
                model.setCommanderIconName(skinItem.getIconID())
                model.setName(localizedFullName(skinItem))

    def __fillInstructorSlots(self, instructorListVM, detDescr, instrDescrs):
        self._instructors, _ = fillInstructorConvertList(instructorListVM, detDescr, instrDescrs)
        instructorListVM.invalidate()

    def __fillVehicleSlots(self, vehicleSlots, detachemnt, detDescr):
        vehicleSlots.clear()
        slotLevels = detachemnt.getVehicleSlotUnlockLevels()
        for index, slotInfo in enumerate(detDescr.getAllSlotsInfo(DetachmentSlotType.VEHICLES)):
            vehicleSlot = ConvertSlotVehicleModel()
            vehicleSlot.setId(index)
            vehicleSlot.setLevelReq(slotLevels[index])
            if slotInfo.available:
                vehicleCD = slotInfo.typeCompDescr
                if vehicleCD:
                    vehicleGuiItem = self.itemsCache.items.getItemByCD(vehicleCD)
                    vehicleSlot.setType(vehicleGuiItem.uiType)
                    vehicleSlot.setIsLocked(False)
                    vehName = getNationLessName(vehicleGuiItem.name)
                    vehicleImageR = R.images.gui.maps.shop.vehicles.c_180x135.dyn(getIconResourceName(vehName))
                    vehicleSlot.setIcon(backport.image(vehicleImageR()))
                    vehicleSlot.setNation(vehicleGuiItem.nationName)
                else:
                    vehicleSlot.setIsLocked(False)
            else:
                vehicleSlot.setIsLocked(True)
            vehicleSlots.addViewModel(vehicleSlot)

        vehicleSlots.invalidate()

    def __fillInstructorsAndSkins(self, instructorsAndSkins, detPreset, vehicle, currentSkinID):
        conversion = settings_globals.g_conversion
        instructorModels = []
        skinModels = []
        instructors = self._instructors
        instructorCache = self.detachmentCache.getInstructors()
        vehCompDescr = vehicle.descriptor.makeCompactDescr()
        processedInstrIDs = set()
        for _, recruit in self._recruits:
            if not recruit:
                continue
            instructorSettings, _ = conversion.getInstructorForTankman(recruit.descriptor)
            if instructorSettings:
                instrPreset = instructorSettings.name
                instructor = self.__searchSuitableInstructorForRecruits(instructorCache, instrPreset, recruit.nationID, processedInstrIDs)
                if instructor:
                    model = InstructorsAndSkinsModel()
                    model.setIsInstructor(True)
                    model.setId(len(instructors))
                    instructors.append(instructor)
                    processedInstrIDs.add(instructor.invID)
                    if not bool(R.images.gui.maps.icons.instructors.c_80x60.dyn(instructor.getPortraitName())):
                        if instructor.gender == GENDER.MALE:
                            model.setIcon(R.images.gui.maps.icons.instructors.c_80x60.siluet_man())
                        else:
                            model.setIcon(R.images.gui.maps.icons.instructors.c_80x60.siluet_woman())
                    else:
                        model.setIcon(R.images.gui.maps.icons.instructors.c_80x60.dyn(instructor.getPortraitName())())
                    if instructor.detInvID != NO_DETACHMENT_ID:
                        model.setStatus(InstructorsAndSkinsModel.STATUS_CHECK)
                    instructorModels.append(model)
            else:
                nativeDetPreset, fakeInstrPreset = conversion.getUnremovableInstructorForTankman(recruit.descriptor)
                if nativeDetPreset and nativeDetPreset != detPreset:
                    _, baseInstDescrs = DetachmentDescr.createByPreset(nativeDetPreset, vehCompDescr)
                    if baseInstDescrs:
                        model = InstructorsAndSkinsModel()
                        model.setIsInstructor(True)
                        model.setId(len(instructors))
                        model.setStatus(InstructorsAndSkinsModel.STATUS_WARNING)
                        _, exampleInstructor = baseInstDescrs[0]
                        instructorDescr = InstructorDescr.createByRecruit(recruit.descriptor, settingsID=exampleInstructor.settingsID)
                        instructor = self.itemsFactory.createInstructor(instructorDescr.makeCompDescr(validate=False))
                        instructor.descriptor.setIsFemale(instructorDescr.isFemale)
                        model.setIcon(R.images.gui.maps.icons.instructors.c_80x60.dyn(instructor.portrait)())
                        nativeDescriptor = _DESCRIPTOR_TEMPLATE.format(fakeInstrPreset)
                        self._unremovableInstructors[instructor] = (nativeDetPreset, nativeDescriptor)
                        instructors.append(instructor)
                        instructorModels.append(model)
            skinID = settings_globals.g_conversion.getSkinIDForTankman(recruit.descriptor) or recruit.skinID
            if skinID != NO_CREW_SKIN_ID:
                model = InstructorsAndSkinsModel()
                model.setIsInstructor(False)
                model.setId(skinID)
                skinItem = self.itemsCache.items.getCrewSkin(skinID)
                model.setIcon(R.images.gui.maps.icons.commanders.c_80x60.crewSkins.dyn(skinItem.getIconID())())
                isEquiped = skinItem.getFreeCount() == 0 or skinID == currentSkinID
                if isEquiped:
                    model.setStatus(InstructorsAndSkinsModel.STATUS_CHECK)
                skinModels.append(model)

        for model in instructorModels + skinModels:
            instructorsAndSkins.addViewModel(model)

        instructorsAndSkins.invalidate()

    def __searchSuitableInstructorForRecruits(self, instructors, presetName, nationID, processedInstrIDs):
        settingsID = settings_globals.g_instructorSettingsProvider.getIDbyName(presetName)
        instr = first(chain((instr for instr in instructors.itervalues() if instr.descriptor.settingsID == settingsID and instr.invID not in processedInstrIDs and instr.isToken()), (instr for instr in instructors.itervalues() if instr.descriptor.settingsID == settingsID and instr.invID not in processedInstrIDs and instr.detInvID == NO_DETACHMENT_ID and instr.nationID == nationID), (instr for instr in instructors.itervalues() if instr.descriptor.settingsID == settingsID and instr.invID not in processedInstrIDs and instr.detInvID != NO_DETACHMENT_ID and instr.nationID == nationID), (instr for instr in instructors.itervalues() if instr.descriptor.settingsID == settingsID and instr.invID not in processedInstrIDs and instr.detInvID == NO_DETACHMENT_ID), (instr for instr in instructors.itervalues() if instr.descriptor.settingsID == settingsID and instr.invID not in processedInstrIDs and instr.detInvID != NO_DETACHMENT_ID)))
        return instr

    def __fillVehicle(self, vehicleModel, vehicle):
        vehicleModel.setName(vehicle.shortUserName)
        vehicleIcon = getIconResourceName(vehicle.name)
        vehicleModel.setIcon(vehicleIcon)
        vehicleModel.setLevel(vehicle.level)
        vehicleModel.setType(getIconResourceName(vehicle.type))
        vehicleModel.setNation(nations.NAMES[vehicle.nationID])
        vehicleModel.setIsElite(vehicle.isElite)
        vehicleModel.setIsPremium(vehicle.isPremium)

    def createToolTipContent(self, event, contentID):
        if contentID in self._tooltipByContentID:
            tooltip = self._tooltipByContentID[contentID](event)
            if tooltip:
                return tooltip
        super(ConvertWindowView, self).createToolTipContent(event, contentID)

    def __getLevelBadgeTooltip(self, event):
        detachment = self.itemsFactory.createDetachment(self._detDescr.makeCompactDescr(), skinID=self._skinID)
        LevelBadgeTooltipView.uiLogger.setGroup(self.uiLogger.group)
        return LevelBadgeTooltipView(NO_DETACHMENT_ID, detachment)

    def __getRankTooltip(self, event):
        detachment = self.itemsFactory.createDetachment(self._detDescr.makeCompactDescr())
        RankTooltip.uiLogger.setGroup(self.uiLogger.group)
        return RankTooltip(detachment.rankRecord)

    def __getColoredSimpleTooltip(self, event):
        return ColoredSimpleTooltip(event.getArgument('header', ''), event.getArgument('body', ''))

    def __getConvertationVehicleTooltip(self, event):
        ConvertationVehicleTooltipView.uiLogger.setGroup(self.uiLogger.group)
        return ConvertationVehicleTooltipView(event.contentID, self._vehicle, state=ConvertationVehicleTooltipModel.DEFAULT)

    def __getPointInfoTooltip(self, event):
        PointInfoTooltipView.uiLogger.setGroup(self.uiLogger.group)
        return PointInfoTooltipView(event.contentID, state=PointsInfoTooltipModel.MOBILIZATION, isClickable=False, detachmentDescr=self._detDescr)

    def __getInstructorOrSkinTooltip(self, event):
        detachment = self.itemsFactory.createDetachment(self._detDescr.makeCompactDescr())
        id_ = int(event.getArgument('instructorInvID'))
        isInstructor = event.getArgument('isInstructor') if event.hasArgument('isInstructor') else True
        if isInstructor:
            if id_ == GUI_NO_INSTRUCTOR_ID:
                EmptyInstructorTooltip.uiLogger.setGroup(self.uiLogger.group)
                return EmptyInstructorTooltip(detachment, True)
            instructor = self._instructors[id_]
            nativeCrewName, nativeCommanderName, nativeDescriptor = (None, None, None)
            if instructor in self._unremovableInstructors:
                nativeDetPresetName, nativeDescriptor = self._unremovableInstructors[instructor]
                detachmentPreset = settings_globals.g_detachmentSettings.presets.getDetachmentPreset(nativeDetPresetName)
                nativeCrewName = backport.text(R.strings.detachment.presetName.dyn(detachmentPreset.name)())
                commanderPreset = detachmentPreset.commander
                nativeCommanderName = getFullUserName(detachmentPreset.nationID, commanderPreset.firstNameID, commanderPreset.secondNameID)
            InstructorTooltip.uiLogger.setGroup(self.uiLogger.group)
            return InstructorTooltip(instructor, detachment=detachment, shownPage=InstructorShownPageConstants.CONVERT, nativeCrewName=nativeCrewName, nativeCommanderName=nativeCommanderName, nativeDescriptor=nativeDescriptor)
        else:
            CommanderLookTooltip.uiLogger.setGroup(self.uiLogger.group)
            return CommanderLookTooltip(id_)
            return None


class ConvertWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, vehicle, recruits, prevViewID=None, parent=None):
        super(ConvertWindow, self).__init__(DialogFlags.TOP_FULLSCREEN_WINDOW, content=ConvertWindowView(R.views.lobby.detachment.ConvertWindow(), vehicle, recruits, prevViewID=prevViewID), parent=parent)
