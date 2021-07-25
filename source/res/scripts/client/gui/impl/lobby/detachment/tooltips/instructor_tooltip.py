# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/instructor_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.auxiliary.instructors_helper import GUI_NO_INSTRUCTOR_ID, fillInstructorInfoModel, getInstructorCards, fillInstructorCommanderModel, fillPerkShortModelArray, isInstructorsEqual, InstructorStates, getInstructorTokenNationInfo
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_shown_page_constants import InstructorShownPageConstants
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.empty_instructor_tooltip_model import EmptyInstructorTooltipModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.instructor_tooltip_model import InstructorTooltipModel
from gui.impl.gen_utils import INVALID_RES_ID
from gui.impl.pub import ViewImpl
from helpers.dependency import descriptor, instance
from items.components.detachment_constants import NO_INSTRUCTOR_ID
from shared_utils import first
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.loggers import DynamicGroupTooltipLogger

def getInstructorTooltip(instructorInvID=GUI_NO_INSTRUCTOR_ID, detachment=None, isLocked=True, shownPage=InstructorShownPageConstants.COMMON, bonusPerks=None):
    if instructorInvID == GUI_NO_INSTRUCTOR_ID:
        tooltip = EmptyInstructorTooltip(detachment, isLocked)
    else:
        detachmentCache = instance(IDetachmentCache)
        instructor = detachmentCache.getInstructor(instructorInvID)
        tooltip = InstructorTooltip(instructor, detachment, bonusPerks, shownPage)
    return tooltip


class InstructorTooltip(ViewImpl):
    __slots__ = ('__instructor', '__detachment', '__linkedDetachment', '__shownPage', '__nativeCrewName', '__nativeCommanderName', '__nativeDescriptor', '__bonusPerks')
    __itemsCache = descriptor(IItemsCache)
    __detachmentCache = descriptor(IDetachmentCache)
    uiLogger = DynamicGroupTooltipLogger()

    def __init__(self, instructor, detachment=None, bonusPerks=None, shownPage=InstructorShownPageConstants.COMMON, nativeCrewName=None, nativeCommanderName=None, nativeDescriptor=None):
        self.__instructor = instructor
        self.__detachment = detachment
        detInvID = self.__instructor.detInvID if self.__instructor else None
        self.__linkedDetachment = self.__detachmentCache.getDetachment(detInvID)
        self.__shownPage = shownPage
        self.__nativeCrewName = nativeCrewName
        self.__nativeCommanderName = nativeCommanderName
        self.__nativeDescriptor = nativeDescriptor
        self.__bonusPerks = bonusPerks
        settings = ViewSettings(R.views.lobby.detachment.tooltips.InstructorTooltip())
        settings.model = InstructorTooltipModel()
        super(InstructorTooltip, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(InstructorTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(InstructorTooltip, self)._onLoading()
        self.__fillModel()

    def _initialize(self, *args, **kwargs):
        super(InstructorTooltip, self)._initialize()
        self.uiLogger.tooltipOpened()

    def _finalize(self):
        self.uiLogger.tooltipClosed(self.__class__.__name__)
        self.uiLogger.reset()
        super(InstructorTooltip, self)._finalize()

    def __fillModel(self):
        detachment = self.__detachment
        with self.viewModel.transaction() as model:
            infoModel = model.information
            detachmentInvID = detachment.invID if detachment else None
            state = isUnremovable = None
            if self.__instructor.invID == NO_INSTRUCTOR_ID and not self.__nativeCrewName:
                state = InstructorStates.NOT_CONVERTED
                isUnremovable = True
            fillInstructorInfoModel(infoModel, self.__instructor, detachmentInvID, instructorState=state, isUnremovable=isUnremovable)
            _, isSuitableNation, nationName = getInstructorTokenNationInfo(self.__instructor, detachmentInvID)
            infoModel.setNation(nationName)
            model.setIsTokenNationsUnsuitable(not isSuitableNation if isSuitableNation is not None else False)
            if self.__nativeDescriptor is None:
                descUid = self.__instructor.getDescription()
            else:
                infoModel.setIcon(self.__instructor.portrait)
                descUid = backport.textRes(self.__nativeDescriptor)()
            if descUid and descUid != INVALID_RES_ID:
                infoModel.setDescription(descUid)
            requiredSlots = self.__instructor.descriptor.getSlotsCount()
            infoModel.setRequiredSlots(requiredSlots)
            items = self.__detachmentCache.getInstructors()
            amount = first((c.count for c in getInstructorCards(items) if isInstructorsEqual(c.item, self.__instructor)))
            if amount:
                infoModel.setAmount(amount)
            perksList = infoModel.getPerks()
            perksList.clear()
            fillPerkShortModelArray(perksList, self.__instructor, self.__bonusPerks)
            fillInstructorCommanderModel(model, self.__linkedDetachment)
            if detachment:
                model.setDetachmentNation(detachment.nationName)
            if self.__nativeCrewName:
                model.setIsWrongLeader(True)
                model.setLeaderName(self.__nativeCommanderName)
                model.commander.setName(self.__nativeCrewName)
        return


class EmptyInstructorTooltip(ViewImpl):
    __slots__ = ('__detachment', '__isLocked')
    uiLogger = DynamicGroupTooltipLogger()

    def __init__(self, detachment, isLocked):
        self.__detachment = detachment
        self.__isLocked = isLocked
        settings = ViewSettings(R.views.lobby.detachment.tooltips.InstructorTooltip())
        settings.model = EmptyInstructorTooltipModel()
        super(EmptyInstructorTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EmptyInstructorTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.__setDetachmentProps()

    def _initialize(self, *args, **kwargs):
        super(EmptyInstructorTooltip, self)._initialize()
        self.uiLogger.tooltipOpened()

    def _finalize(self):
        self.uiLogger.tooltipClosed(self.__class__.__name__)
        self.uiLogger.reset()
        super(EmptyInstructorTooltip, self)._finalize()

    def __setDetachmentProps(self):
        with self.viewModel.transaction() as model:
            model.setIsLocked(self.__isLocked)
            levelsList = model.getUnlockLevels()
            levelsList.clear()
            for level in self.__detachment.getInstructorUnlockLevels():
                levelsList.addNumber(level)

            levelsList.invalidate()
