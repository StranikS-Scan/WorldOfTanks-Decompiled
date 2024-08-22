# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/recruit_window/confirm_irrelevant_perk_reset_dialog.py
from gui.impl.auxiliary.tankman_operations import packMajorSkills
from gui.impl.dialogs.dialog_template_button import ConfirmButton, CancelButton
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.crew.crew_constants import CrewConstants
from gui.impl.gen.view_models.views.lobby.crew.dialogs.recruit_window.confirm_irrelevant_dialog_model import ConfirmIrrelevantDialogModel
from gui.impl.lobby.crew.dialogs.base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui.impl.lobby.crew.dialogs.recruit_window.recruit_dialog_utils import getIcon, getIconBackground, getIconName, getTitleFromTokenData

class ConfirmIrrelevantPerkResetDialog(BaseCrewDialogTemplateView):
    __slots__ = ('__tokenData', '__selectedRole', '__tankman', '__tankmanAfter', '__vehicle')
    LAYOUT_ID = R.views.lobby.crew.dialogs.RecruitConfirmIrrelevantDialog()
    VIEW_MODEL = ConfirmIrrelevantDialogModel

    def __init__(self, ctx, **kwargs):
        super(ConfirmIrrelevantPerkResetDialog, self).__init__(**kwargs)
        self.__tokenData = ctx.get('tokenData')
        self.__selectedRole = ctx.get('selectedRole')
        self.__vehicle = ctx.get('selectedVehicle')
        self.__tankman = self.__tokenData.getFakeTankmanInVehicle(self.__vehicle, self.__selectedRole)
        self.__tankmanAfter = self.__tokenData.getFakeTankmanInVehicle(self.__vehicle, self.__selectedRole, True)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ConfirmIrrelevantPerkResetDialog, self)._onLoading(*args, **kwargs)
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        self.viewModel.setName(getTitleFromTokenData(self.__tokenData))
        iconID, hasBackground = getIcon(getIconName(self.__tokenData.getSmallIcon()), self.__tokenData.isFemale())
        self.viewModel.iconModel.icon.setPath(iconID)
        if not hasBackground:
            self.viewModel.iconModel.bgIcon.setPath(getIconBackground(self.__tokenData.getSourceID(), self.__tokenData.getSmallIcon()))
        self.viewModel.tankmanBefore.skillList.setSkillsEfficiency(CrewConstants.SKILL_EFFICIENCY_MAX_LEVEL)
        self.viewModel.tankmanAfter.skillList.setSkillsEfficiency(CrewConstants.SKILL_EFFICIENCY_MAX_LEVEL)
        packMajorSkills(self.viewModel.tankmanBefore.skillList, self.__tankman, skipIrrelevantCheck=True)
        packMajorSkills(self.viewModel.tankmanAfter.skillList, self.__tankmanAfter)
        self.addButton(ConfirmButton(R.strings.dialogs.recruitWindow.submit()))
        self.addButton(CancelButton(R.strings.dialogs.recruitWindow.cancel()))
