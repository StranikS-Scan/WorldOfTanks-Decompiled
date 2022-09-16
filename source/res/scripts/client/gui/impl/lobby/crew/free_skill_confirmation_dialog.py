# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/free_skill_confirmation_dialog.py
from gui.impl import backport
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.common.simple_text import ImageSubstitution
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache

class FreeSkillConfirmationDialog(DialogTemplateView):
    __appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ('__skillName', '__isAlreadyEarned')
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, skillName, isAlreadyEarned=False, layoutID=None, uniqueID=None):
        super(FreeSkillConfirmationDialog, self).__init__(layoutID, uniqueID)
        self.__skillName = skillName
        self.__isAlreadyEarned = isAlreadyEarned

    def _onLoading(self, *args, **kwargs):
        if self.__isAlreadyEarned:
            titleRes = R.strings.dialogs.freeSkillsLearning.title.relearning
        else:
            titleRes = R.strings.dialogs.freeSkillsLearning.title.learning
        skillNameText = backport.text(R.strings.item_types.tankman.skills.dyn(self.__skillName)())
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(backport.text(titleRes(), skillName=skillNameText)))
        self.setSubView(Placeholder.CONTENT, SimpleTextContent(R.strings.dialogs.freeSkillsLearning.message(), [ImageSubstitution(R.images.gui.maps.icons.library.alertIcon1(), 'iconWarning', 0, -2, 6, 0)]))
        self.setSubView(Placeholder.ICON, IconSet(R.images.gui.maps.icons.tankmen.skills.dialogs.dyn(self.__skillName)()))
        self.addButton(ConfirmButton())
        self.addButton(CancelButton())
        super(FreeSkillConfirmationDialog, self)._onLoading(*args, **kwargs)
