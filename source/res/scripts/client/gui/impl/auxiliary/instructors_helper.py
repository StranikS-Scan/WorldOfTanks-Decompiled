# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/instructors_helper.py
from collections import namedtuple
import typing
from enum import IntEnum
import nations
from crew2 import crew2_consts, settings_globals
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_base_model import InstructorBaseModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_slot_base_model import InstructorSlotBaseModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_location_constants import InstructorLocationConstants
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_state_constants import InstructorStateConstants
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_short_model import PerkShortModel
from gui.shared.gui_items.perk import PerkGUI
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import dependency
from items.components.detachment_constants import DetachmentSlotType, NO_DETACHMENT_ID, PROGRESS_MAX
from items.instructor import InstructorDescr
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    from typing import Tuple, List, Optional, Union, Type, Dict
    from gui.shared.gui_items import ItemsCollection
    from frameworks.wulf import Array
    from gui.shared.gui_items.detachment import Detachment
    from gui.shared.gui_items.instructor import Instructor
    from items.detachment import DetachmentDescr
    from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel
    from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_info_model import InstructorInfoModel
    from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_card_model import InstructorCardModel
    from gui.shared.gui_items.Vehicle import Vehicle
GUI_NO_INSTRUCTOR_ID = -1
InstructorCardData = namedtuple('InstructorCardData', ['invID', 'count', 'item'])

class InstructorLocation(IntEnum):
    DETACHMENT = 0
    BARRACKS = 1
    REMOVED = 2

    def toModelConstant(self):
        if self == InstructorLocation.DETACHMENT:
            attr = 'CREW'
        elif self == InstructorLocation.REMOVED:
            attr = InstructorLocation.BARRACKS.name
        else:
            attr = self.name
        return getattr(InstructorLocationConstants, attr, '')


class InstructorStates(IntEnum):
    NONE = 0
    TOKEN = 1
    ON_CURRENT_DET = 2
    IN_SQUAD = 3
    IN_BATTLE = 4
    REMOVED = 5
    NOT_CONVERTED = 6

    def toModelConstant(self):
        attr = self.name if self != InstructorStates.ON_CURRENT_DET else 'ASSIGNED'
        return getattr(InstructorStateConstants, attr, '')


def isInstructorsEqual(item, compareItem):
    return item.detInvID == compareItem.detInvID == NO_DETACHMENT_ID and item.nationID == compareItem.nationID and item.descriptor.settingsID == compareItem.descriptor.settingsID and item.descriptor.firstNameID == compareItem.descriptor.firstNameID and item.descriptor.secondNameID == compareItem.descriptor.secondNameID and item.descriptor.portraitID == compareItem.descriptor.portraitID and item.perksIDs == compareItem.perksIDs and item.classID == compareItem.classID and item.excludedExpData == compareItem.excludedExpData


@dependency.replace_none_kwargs(detachmentCache=IDetachmentCache)
def canInsertInstructorToSlot(detInvID, instrInvID, slotID, checkNations=True, detachmentCache=None):
    detachment = detachmentCache.getDetachment(detInvID)
    instructor = detachmentCache.getInstructor(instrInvID)
    if not detachment or not instructor:
        return False
    return False if checkNations and detachment.nationID != instructor.nationID else detachment.getDescriptor().canSetSlotValue(DetachmentSlotType.INSTRUCTORS, slotID, (instrInvID, instructor.descriptor))


def showInstructorSlotsDisabledMessage():
    SystemMessages.pushMessage(type=SystemMessages.SM_TYPE.FeatureSwitcherOff, text=backport.text(R.strings.tooltips.detachment.instructorSlots.disabled.body()), messageData={'header': backport.text(R.strings.tooltips.detachment.instructorSlots.disabled.header())})


def getInstructorCards(itemDict):
    if not itemDict:
        return []
    sortedInstructors = sorted(itemDict.itervalues(), key=lambda instructorItem: (instructorItem.nationID,
     instructorItem.descriptor.settingsID,
     instructorItem.detInvID,
     instructorItem.invID,
     instructorItem))
    cutItem = {'item': sortedInstructors.pop(0),
     'count': 1}
    countItems = [cutItem]
    for item in sortedInstructors:
        if isInstructorsEqual(cutItem['item'], item):
            cutItem['count'] += 1
        cutItem = {'item': item,
         'count': 1}
        countItems.append(cutItem)

    return [ InstructorCardData(countItem['item'].invID, countItem['count'], countItem['item']) for countItem in countItems ]


def getInstructorState(instructorItem, currentDetInvID=None):
    state = InstructorStates.NONE
    if instructorItem.isToken():
        state = InstructorStates.TOKEN
    elif instructorItem.excludedExpData:
        state = InstructorStates.REMOVED
    elif instructorItem.detInvID != NO_DETACHMENT_ID:
        if currentDetInvID is not None and instructorItem.detInvID == currentDetInvID:
            state = InstructorStates.ON_CURRENT_DET
        else:
            detachmentCache = dependency.instance(IDetachmentCache)
            detachment = detachmentCache.getDetachment(instructorItem.detInvID)
            if detachment is not None:
                itemsCache = dependency.instance(IItemsCache)
                vehicle = itemsCache.items.getVehicle(detachment.vehInvID)
                if vehicle is not None:
                    if vehicle.isInUnit:
                        state = InstructorStates.IN_SQUAD
                    elif vehicle.isInBattle or vehicle.isInPrebattle:
                        state = InstructorStates.IN_BATTLE
    return state


@dependency.replace_none_kwargs(itemsFactory=IGuiItemsFactory)
def getInstructorsByDetachmentPresetID(detachmentPresetID, itemsFactory=None):
    presets = settings_globals.g_detachmentSettings.presets
    preset = presets.getDetachmentPresetByID(detachmentPresetID)
    instructors = []
    for instSlot in preset.instructorSlots:
        instSettID = instSlot.instructorID
        if instSettID is None:
            continue
        instSettings = settings_globals.g_instructorSettingsProvider.getInstructorByID(instSettID)
        if not instSettings:
            continue
        instructorDescr = InstructorDescr.createByPreset(instSettings.name)
        instructors.append(itemsFactory.createInstructor(instructorDescr.makeCompDescr()))

    return instructors


def getInstructorLocation(instructorItem):
    if instructorItem.detInvID != NO_DETACHMENT_ID:
        location = InstructorLocation.DETACHMENT
    elif instructorItem.excludedExpData:
        location = InstructorLocation.REMOVED
    else:
        location = InstructorLocation.BARRACKS
    return location


def fillInstructorConvertList(listVM, detDescr, instrDescrList):
    itemsFactory = dependency.instance(IGuiItemsFactory)
    listVM.clear()
    instructors = []
    availableForAssign = indexSlot = fakeInstrInvID = 0
    revertInstrDescrList = instrDescrList[:]
    while indexSlot < detDescr.maxInstructorsCount:
        model = InstructorSlotBaseModel()
        instructor = None
        capacity = 1
        isSlotAvailable = detDescr.isSlotAvailable(DetachmentSlotType.INSTRUCTORS, indexSlot)
        if revertInstrDescrList:
            _, instrDescr = revertInstrDescrList.pop()
            capacity = instrDescr.getSlotsCount()
            instructor = itemsFactory.createInstructor(instrDescr.makeCompDescr(), invID=fakeInstrInvID)
            fakeInstrInvID += 1
            instructors.append(instructor)
        elif isSlotAvailable:
            availableForAssign += isSlotAvailable
        fillInstructorBaseModel(model, instructor, indexSlot, isSlotAvailable)
        indexSlot += capacity
        listVM.addViewModel(model)

    return (instructors, availableForAssign)


def fillInstructorList(instructorsLV, detachment, fillLocked=False, fillEmpty=True, customModel=None):
    instructorsLV.clear()
    instructorIDs = detachment.getInstructorsIDs()
    detachmentCache = dependency.instance(IDetachmentCache)
    modelClass = InstructorSlotBaseModel if not customModel else customModel
    fillFunction = fillInstructorSlotBaseModel if not customModel else fillInstructorBaseModel
    processedInstructors = set()
    occupiedSlotsCount = len(instructorIDs)
    for index in xrange(detachment.getMaxInstructorsCount()):
        if index < occupiedSlotsCount:
            instructorInvID = instructorIDs[index]
            instrGuiItem = detachmentCache.getInstructor(instructorInvID)
            if instrGuiItem and instructorInvID in processedInstructors:
                continue
            elif instrGuiItem:
                processedInstructors.add(instructorInvID)
            if instrGuiItem or fillEmpty:
                instructorModel = modelClass()
                fillFunction(instructorModel, instrGuiItem, index, fillPlaceholder=True)
                instructorsLV.addViewModel(instructorModel)
        if fillLocked and not detachment.getDescriptor().isSlotAvailable(DetachmentSlotType.INSTRUCTORS, index):
            instructorsLV.addViewModel(InstructorSlotBaseModel())

    instructorsLV.invalidate()


def fillInstructorsTokenList(instructorsLV, instructorsCards, instructorCardSortingCriteria, isReverse=False):
    instructorsLV.clear()
    detachmentCache = dependency.instance(IDetachmentCache)
    tokens = [ card for card in instructorsCards if card.item.isToken() ]
    tokens = sorted(tokens, key=instructorCardSortingCriteria, reverse=isReverse)[:4]
    for token in tokens:
        instructorModel = InstructorBaseModel()
        invID = token.item.invID
        instrGuiItem = detachmentCache.getInstructor(invID)
        fillInstructorBaseModel(instructorModel, instrGuiItem)
        instructorsLV.addViewModel(instructorModel)

    instructorsLV.invalidate()


def countInstructors(instructorsCards, tokens=False):
    return sum((card.count for card in instructorsCards if card.item.isToken() == tokens))


def getInstructorTokenNationInfo(instructorItem, detInvID):
    isTokenSingleNation = None
    tokenWithSuitableNation = None
    nationName = instructorItem.nationName
    if instructorItem.isToken() and instructorItem.nationID == nations.NONE_INDEX:
        availableNationIDs = instructorItem.getAvailableNationIDs()
        if len(availableNationIDs) == 1:
            nationName = nations.MAP.get(availableNationIDs[0], '')
            isTokenSingleNation = True
        else:
            isTokenSingleNation = False
            detachment = dependency.instance(IDetachmentCache).getDetachment(detInvID) if detInvID else None
            if detachment:
                tokenWithSuitableNation = detachment.nationID in availableNationIDs
    return (isTokenSingleNation, tokenWithSuitableNation, nationName)


def fillInstructorCardModel(model, card, detInvID=None):
    model.setId(card.invID)
    model.setAmount(card.count)
    instructorItem = card.item
    fillInstructorInfoModel(model, instructorItem, detInvID)
    _, isSuitableNations, nationName = getInstructorTokenNationInfo(instructorItem, detInvID)
    model.setIsTokenNationsUnsuitable(not isSuitableNations if isSuitableNations is not None else False)
    model.setNation(nationName)
    perksList = model.getPerks()
    perksList.clear()
    fillPerkShortModelArray(perksList, instructorItem)
    return


def fillInstructorCommanderModel(model, detachmentItem):
    if detachmentItem:
        model.commander.setName(detachmentItem.cmdrFullName)
        itemsCache = dependency.instance(IItemsCache)
        vehicleItem = itemsCache.items.getVehicle(detachmentItem.vehInvID)
        if vehicleItem is not None:
            fillVehicleModel(model.vehicle, vehicleItem, isShortName=True)
    return


def fillInstructorInfoModel(model, instructorItem, currentDetInvID=None, instructorState=None, isUnremovable=None):
    model.setId(instructorItem.invID)
    model.setIcon(instructorItem.getPortraitName())
    model.setBackground(instructorItem.pageBackground)
    genderTag = crew2_consts.GENDER_TO_TAG[instructorItem.gender]
    model.setGender(genderTag.lower())
    model.setName(instructorItem.getFullName())
    if not instructorItem.isToken():
        model.setTrait(instructorItem.getTrait())
    model.setGrade(instructorItem.classID)
    model.setNation(instructorItem.nationName)
    model.setBonusExperience(instructorItem.xpBonus * PROGRESS_MAX)
    model.setIsVoiced(bool(instructorItem.voiceOverID))
    model.setLocation(getInstructorLocation(instructorItem).toModelConstant())
    if isUnremovable is None:
        model.setIsUnique(instructorItem.isUnremovable)
    else:
        model.setIsUnique(isUnremovable)
    if instructorState is None:
        state = getInstructorState(instructorItem, currentDetInvID).toModelConstant()
        model.setState(state)
    else:
        model.setState(instructorState.toModelConstant())
    expDate = instructorItem.excludedExpData
    if expDate:
        model.setRemoveTime(int(expDate))
    return


def fillInstructorBaseModel(model, instrGuiItem=None, index=0, fillPlaceholder=True):
    if instrGuiItem is not None:
        model.setId(instrGuiItem.invID)
        model.setIcon(instrGuiItem.getPortraitName())
        model.setGrade(instrGuiItem.classID)
        model.setBackground(instrGuiItem.pageBackground)
    elif fillPlaceholder:
        model.setId(GUI_NO_INSTRUCTOR_ID)
        model.setIcon('c_{}'.format(index))
    return


def fillInstructorSlotBaseModel(model, instrGuiItem=None, index=0, fillPlaceholder=True):
    model.setSlotIndex(index)
    fillInstructorBaseModel(model, instrGuiItem, index, fillPlaceholder)


def fillVehicleModel(vehMdl, veh, isShortName=False):
    vehMdl.setId(veh.intCD)
    if isShortName:
        vehMdl.setName(veh.shortUserName)
    else:
        vehMdl.setName(veh.userName)
    vehMdl.setLevel(veh.level)
    vehMdl.setNation(veh.nationName)
    vehMdl.setType(replaceHyphenToUnderscore(veh.uiType))
    vehMdl.setIcon(replaceHyphenToUnderscore(veh.name.split(':')[1]))
    vehMdl.setIsElite(veh.isElite)


def fillPerkShortModelArray(perksList, instructor, bonusPerks=None):
    if instructor.isToken():
        for i, pp in enumerate(instructor.bonusClass.perkPoints):
            perkVM = PerkShortModel()
            perkVM.setId(i)
            perkVM.setPoints(pp)
            perkVM.setIcon(backport.image(R.images.gui.maps.icons.perks.normal.c_48x48.undefined_perk()))
            perksList.addViewModel(perkVM)

    else:
        for perkID, points, overcap in instructor.getPerksInfluence(bonusPerks):
            perk = PerkGUI(perkID)
            perkVM = PerkShortModel()
            perkVM.setId(perkID)
            perkVM.setPoints(points)
            perkVM.setIcon(backport.image(R.images.gui.maps.icons.perks.normal.c_48x48.dyn(perk.icon)()))
            perkVM.setName(perk.name)
            perkVM.setIsOvercapped(overcap > 0)
            perksList.addViewModel(perkVM)


def getInstructorPageBackground(backgroundName):
    backgroundRes = R.images.gui.maps.icons.instructors.backgrounds.c_1920x1080.dyn(backgroundName)
    return backgroundRes() if backgroundRes.exists() else R.images.gui.maps.icons.instructors.backgrounds.c_1920x1080.default()
