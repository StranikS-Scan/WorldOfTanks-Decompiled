# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/skills_training_confirm_dialog.py
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import ConfirmButton, CancelButton
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen.view_models.views.lobby.crew.common.skill.skill_model import SkillModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.skills_training_confirm_dialog_model import SkillsTrainingConfirmDialogModel
from gui.impl.lobby.crew.crew_helpers.skill_model_setup import skillSimpleModelSetup
from gui.shared.gui_items.Tankman import getTankmanSkill

class SkillsTrainingConfirmDialog(DialogTemplateView):
    __slots__ = ('__tankman', '__skillsList', '__availableSkillsData', '__isClosed')
    LAYOUT_ID = R.views.lobby.crew.dialogs.SkillsTrainingConfirmDialog()
    VIEW_MODEL = SkillsTrainingConfirmDialogModel

    def __init__(self, tankman, skillsList, availableSkillsData, **kwargs):
        super(SkillsTrainingConfirmDialog, self).__init__(**kwargs)
        self.__tankman = tankman
        self.__skillsList = skillsList
        self.__availableSkillsData = availableSkillsData
        self.__isClosed = False

    @property
    def viewModel(self):
        return super(SkillsTrainingConfirmDialog, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        self.setSubView(DefaultDialogPlaceHolders.TITLE, SimpleTextTitle(R.strings.dialogs.skillsTrainingConfirm.message()))
        self.addButton(ConfirmButton(R.strings.dialogs.skillsTrainingConfirm.submit()))
        self.addButton(CancelButton())
        with self.viewModel.transaction() as vm:
            skillsListVM = vm.getSkillsList()
            for idx, skillName in enumerate(self.__skillsList):
                skill = getTankmanSkill(skillName, tankman=self.__tankman)
                skillVM = SkillModel()
                level, isZero = self.__availableSkillsData[idx]
                skillSimpleModelSetup(skillVM, skill=skill, skillLevel=level, skillName=skillName)
                skillVM.setIsZero(isZero)
                skillsListVM.addViewModel(skillVM)

            skillsListVM.invalidate()
        super(SkillsTrainingConfirmDialog, self)._onLoading(*args, **kwargs)

    def _closeClickHandler(self, args=None):
        self.__isClosed = True
        super(SkillsTrainingConfirmDialog, self)._closeClickHandler(*args)

    def _getAdditionalData(self):
        return self.__isClosed
