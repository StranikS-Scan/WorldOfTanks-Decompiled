# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/demobilize_detachment_dialog_view.py
from async import await, async
from crew2 import settings_globals
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import fillRoseSheetsModel, fillDetachmentBaseModel
from gui.impl.dialogs.dialogs import showReplaceDetachmentDialogView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.demobilize_detachment_dialog_view_model import DemobilizeDetachmentDialogViewModel
from gui.impl.lobby.detachment.tooltips.colored_simple_tooltip import ColoredSimpleTooltip
from gui.impl.lobby.detachment.tooltips.detachment_info_tooltip import DetachmentInfoTooltip
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import getInstructorTooltip
from gui.impl.lobby.detachment.tooltips.level_badge_tooltip_view import LevelBadgeTooltipView
from gui.impl.lobby.detachment.tooltips.skills_branch_view import SkillsBranchTooltipView
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from helpers import dependency
from items.components.detachment_constants import ExcludeInstructorOption
from skeletons.gui.detachment import IDetachmentCache, IDetachementStates
from uilogging.detachment.constants import ACTION, GROUP
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger

class DemobilizeDetachmentDialogView(FullScreenDialogView):
    _detachmentCache = dependency.descriptor(IDetachmentCache)
    _detachementStates = dependency.descriptor(IDetachementStates)
    uiLogger = DetachmentLogger(GROUP.DEMOBILIZE_DETACHMENT_DIALOG)
    __slots__ = ('__detInvID', '__detachment', '__excludeInstructors', '__reason')

    def __init__(self, ctx):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.DemobilizeDetachmentDialogView())
        settings.model = DemobilizeDetachmentDialogViewModel()
        super(DemobilizeDetachmentDialogView, self).__init__(settings)
        self.__detInvID = ctx.get('detInvID')
        self.__reason = ctx.get('reason')
        self.__detachment = self._detachmentCache.getDetachment(self.__detInvID)
        self.__excludeInstructors = ExcludeInstructorOption.FREE

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.detachment.tooltips.ColoredSimpleTooltip():
            return self.__getColoredSimpleTooltip(event)
        if event.contentID == R.views.lobby.detachment.tooltips.DetachmentInfoTooltip():
            return DetachmentInfoTooltip(detachmentInvID=self.__detInvID)
        if contentID == R.views.lobby.detachment.tooltips.SkillsBranchTooltip():
            course = event.getArgument('course')
            SkillsBranchTooltipView.uiLogger.setGroup(self.uiLogger.group)
            return SkillsBranchTooltipView(detachmentID=self.__detInvID, branchID=int(course) + 1)
        if contentID == R.views.lobby.detachment.tooltips.InstructorTooltip():
            instructorID = event.getArgument('instructorInvID')
            tooltip = getInstructorTooltip(instructorInvID=instructorID, detachment=self.__detachment)
            if hasattr(tooltip, 'uiLogger'):
                tooltip.uiLogger.setGroup(self.uiLogger.group)
            return tooltip
        return LevelBadgeTooltipView(self.__detInvID) if contentID == R.views.lobby.detachment.tooltips.LevelBadgeTooltip() else super(DemobilizeDetachmentDialogView, self).createToolTipContent(event, contentID)

    def _addListeners(self):
        super(DemobilizeDetachmentDialogView, self)._addListeners()
        model = self.viewModel
        model.onInputChange += self._onInputChange

    def _removeListeners(self):
        model = self.viewModel
        model.onInputChange -= self._onInputChange
        super(DemobilizeDetachmentDialogView, self)._removeListeners()

    def _onLoading(self, *args, **kwargs):
        super(DemobilizeDetachmentDialogView, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self):
        detachment = self.__detachment
        if not detachment:
            return
        with self.viewModel.transaction() as vm:
            fillDetachmentBaseModel(vm.detachmentLine, detachment)
            fillRoseSheetsModel(vm.detachmentLine.roseModel, detachment)
            vm.setAcceptButtonText(R.strings.dialogs.detachment.demobilize.accept.title())
            vm.setCancelButtonText(R.strings.detachment.common.cancel())
            vm.setIsInstructorsAvailable(any(detachment.getInstructorsIDs()))
            vm.setIsSkin(bool(detachment.skinID))
            vm.setRestoreDaysLimit(settings_globals.g_detachmentSettings.holdInRecycleBinTerm)
            vm.setIsFullBuffer(self._detachementStates.states.isRecycleBinFull())
            vm.setIsLowLevelDetachment(self.__isLowLevel())
            vm.setIsAcceptDisabled(True)
            vm.setCanRestore(self._isRestorable())

    def _onInputChange(self, args):
        value = args.get('value')
        checkError = args.get('checkError')
        with self.viewModel.transaction() as vm:
            isTextAvailable = bool(value)
            isCorrectInput = value.isdigit() and int(value) == self.__detachment.level
            vm.setIsAcceptDisabled(not isCorrectInput)
            if isTextAvailable:
                if checkError and not isCorrectInput:
                    vm.setInputState(DemobilizeDetachmentDialogViewModel.INPUT_STATE_INCORRECT)
                elif isCorrectInput:
                    vm.setInputState(DemobilizeDetachmentDialogViewModel.INPUT_STATE_CORRECT)
                else:
                    vm.setInputState(DemobilizeDetachmentDialogViewModel.INPUT_STATE_DEFAULT)

    def _getAdditionalData(self):
        return {'detInvID': self.__detInvID,
         'allowRemove': not self._isRestorable(),
         'freeExcludeInstructors': self.__excludeInstructors == ExcludeInstructorOption.FREE}

    def _isRestorable(self):
        return self.__detachment.isRestorable and not self._detachementStates.states.isRecycleBinFull()

    @async
    def _onAcceptClicked(self):
        isOk = True
        if self._detachementStates.states.isRecycleBinFull() and self.__detachment.isRestorable:
            g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.DELETE_DETACHMENT_DIALOG)
            isOk = yield await(showReplaceDetachmentDialogView())
        if isOk:
            self.uiLogger.log(ACTION.DIALOG_CONFIRM)
            super(DemobilizeDetachmentDialogView, self)._onAcceptClicked()

    def _onCancelClicked(self):
        self.uiLogger.log(ACTION.DIALOG_CANCEL)
        super(DemobilizeDetachmentDialogView, self)._onCancelClicked()

    def _onExitClicked(self):
        self.uiLogger.log(ACTION.DIALOG_EXIT)
        super(DemobilizeDetachmentDialogView, self)._onExitClicked()

    def __getColoredSimpleTooltip(self, event):
        body = event.getArgument('body', '')
        if body == R.strings.tooltips.detachment.demobilize.cantRestore.body():
            body = backport.text(body, number=10)
        elif body == R.strings.tooltips.detachment.demobilize.bufferIsFull.body():
            binSize = len(self._detachementStates.states.getDatachmentsRecycleBin())
            body = backport.text(body, maxCount=binSize, currCount=binSize)
        return ColoredSimpleTooltip(event.getArgument('header', ''), body)

    def __isLowLevel(self):
        return self.__detachment.level < self.__detachment.progression.firstPaidSpecializationLevel
