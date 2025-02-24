# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/mentor_assignment_dialog.py
import typing
import SoundGroups
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.auxiliary.tankman_operations import packBaseTankman
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.template_settings.default_dialog_template_settings import DisplayFlags
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.crew.dialogs.mentor_assignment_dialog_model import MentorAssignmentDialogModel
from gui.impl.lobby.crew.crew_helpers.model_setters import setTmanMajorSkillsModel
from gui.impl.lobby.crew.crew_sounds import SOUNDS
from gui.impl.lobby.crew.dialogs.base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui.impl.lobby.crew.tooltips.empty_skill_tooltip import EmptySkillTooltip
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.gui_items.Tankman import crewMemberRealSkillLevel
from gui.shared.gui_items.Vehicle import getTankmanIndex
from helpers import dependency
from nations import NAMES
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from frameworks.wulf import ViewEvent
    from typing import Any
    from gui.shared.gui_items.Tankman import Tankman
    from gui.impl.gen.view_models.views.lobby.crew.dialogs.mentor_assignment_tankman_model import MentorAssignmentTankmanModel

def _packTankman(vmTankman, guiTankman):
    packBaseTankman(vmTankman, guiTankman)
    vmTankman.setUserName(guiTankman.getFullUserNameWithSkin())
    setTmanMajorSkillsModel(vmTankman.getMajorSkills(), guiTankman)


class MentorAssignmentDialog(BaseCrewDialogTemplateView):
    __slots__ = ('__sourceTankman', '__targetTankman', '__targetVehicle', '__totalXp', '__loseXp', '_toolTipMgr')
    LAYOUT_ID = R.views.lobby.crew.dialogs.MentorAssignmentDialog()
    VIEW_MODEL = MentorAssignmentDialogModel
    _itemsCache = dependency.descriptor(IItemsCache)
    _itemsFactory = dependency.descriptor(IGuiItemsFactory)
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, sourceTmanId, targetTmanId):
        super(MentorAssignmentDialog, self).__init__()
        self._toolTipMgr = self._appLoader.getApp().getToolTipMgr()
        self.__sourceTankman = self._itemsCache.items.getTankman(sourceTmanId)
        targetTankman = self._itemsCache.items.getTankman(targetTmanId)
        targetVehicle = targetTankman.getVehicle()
        self.__targetVehicle = self._itemsCache.items.getVehicleCopy(targetVehicle) if targetVehicle else None
        self.__targetTankman = self._itemsFactory.createTankman(targetTankman.strCD, targetTankman.invID, self.__targetVehicle, proxy=self._itemsCache.items, vehicleSlotIdx=targetTankman.vehicleSlotIdx)
        self.__totalXp = self.__sourceTankman.descriptor.totalXP()
        self.__loseXp = max(self.__totalXp - self.__targetTankman.descriptor.needXpForMaxSkills, 0)
        self.__targetTankman.descriptor.addXP(self.__totalXp, isCheckForEfficiency=False)
        self._updateData()
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TooltipConstants.SKILL:
                isDonor = event.getArgument('isDonor')
                skillName = event.getArgument('skillName')
                roleName = event.getArgument('roleName')
                tankman = self.__sourceTankman if isDonor else self.__targetTankman
                vehicle = self.__sourceTankman.getVehicle() if isDonor else self.__targetVehicle
                args = [skillName,
                 roleName,
                 None,
                 None,
                 True,
                 '',
                 None,
                 -1,
                 tankman,
                 vehicle]
                self._toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_PERK_GF, args, event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                return TOOLTIPS_CONSTANTS.CREW_PERK_GF
        super(MentorAssignmentDialog, self).createToolTip(event)
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.crew.tooltips.EmptySkillTooltip():
            isDonor = event.getArgument('isDonor')
            tankman = self.__sourceTankman if isDonor else self.__targetTankman
            return EmptySkillTooltip(tankman, int(event.getArgument('skillIndex')))
        return super(MentorAssignmentDialog, self).createToolTipContent(event, contentID)

    def _updateData(self):
        if not self.__targetVehicle:
            return
        else:
            targetTmanIndex = getTankmanIndex(self.__targetVehicle, self.__targetTankman.vehicleSlotIdx)
            self.__targetVehicle.crew[targetTmanIndex] = (self.__targetTankman.vehicleSlotIdx, self.__targetTankman)
            inVehicleTankmanId = self.__targetVehicle.getTankmanIDBySlotIdx(self.__sourceTankman.vehicleSlotIdx)
            if inVehicleTankmanId == self.__sourceTankman.invID:
                sourceTmanIndex = getTankmanIndex(self.__targetVehicle, self.__sourceTankman.vehicleSlotIdx)
                self.__targetVehicle.crew[sourceTmanIndex] = (self.__sourceTankman.vehicleSlotIdx, None)
            crewDescr = [ (tman.descriptor.makeCompactDescr() if tman else None) for _, tman in self.__targetVehicle.crew ]
            self.__targetVehicle.calcCrewBonuses(crewDescr, None, fromBattle=True)
            for _, tman in self.__targetVehicle.crew:
                if tman:
                    tman.updateBonusesFromVehicle(self.__targetVehicle)

            self.__targetTankman.rebuildSkills()
            return

    def _getEvents(self):
        return ((self.viewModel.onInputChange, self.__onInputChange),)

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        self.addButton(ConfirmButton(isDisabled=True))
        self.addButton(CancelButton())
        self.setDisplayFlags(DisplayFlags.DISABLERESPONSIVECONTENTPOSITION.value)
        with self.viewModel.transaction() as vm:
            _packTankman(vm.sourceTankman, self.__sourceTankman)
            _packTankman(vm.targetTankman, self.__targetTankman)
            vm.setXpTransfer(self.__totalXp)
            vm.setXpLose(self.__loseXp)
            vm.setNation(NAMES[self.__sourceTankman.nationID])
            vm.setIsConfirmRequire(True)
            vm.setIsSourceMaxXp(self.__sourceTankman.descriptor.isMaxSkillXp())
            vm.setIsTargetMaxXp(self.__targetTankman.descriptor.isMaxSkillXp())
        super(MentorAssignmentDialog, self)._onLoading(*args, **kwargs)

    def _onLoaded(self, *args, **kwargs):
        super(MentorAssignmentDialog, self)._onLoaded(*args, **kwargs)
        SoundGroups.g_instance.playSound2D(SOUNDS.CREW_RESET_PERK_SELECTION)

    def _finalize(self):
        self._toolTipMgr = None
        self.__sourceTankman = None
        self.__targetTankman = None
        self.__targetVehicle = None
        super(MentorAssignmentDialog, self)._finalize()
        return

    def __onInputChange(self, event):
        isDisabled = str(event.get('input')) != str(self.__totalXp)
        self.__updateSubmitButton(isDisabled)

    def __updateSubmitButton(self, isDisabled=True):
        submitBtn = self.getButton(DialogButtons.SUBMIT)
        submitBtn.isDisabled = isDisabled

    def __getSkillLevel(self, isDonor, skillName, event):
        if isDonor:
            return None
        else:
            return crewMemberRealSkillLevel(self.__targetVehicle, skillName) if self.__targetVehicle else event.getArgument('level')
