# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/perk_learn_confirmation_dialog.py
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui.impl import backport
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.shared.gui_items.Tankman import TankmanSkill

class PerkLearnConfirmationDialog(BaseCrewDialogTemplateView):
    __slots__ = ('__skill', '__level')

    def __init__(self, skill, level):
        super(PerkLearnConfirmationDialog, self).__init__()
        self.__skill = skill
        self.__level = level

    def _onLoading(self, *args, **kwargs):
        titleRes = R.strings.dialogs.perkLearnConfirm.title
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(str(backport.text(titleRes(), skillName=self.__skill.userName))))
        self.setSubView(Placeholder.ICON, IconSet(R.images.gui.maps.icons.tankmen.skills.dialogs.dyn(self.__skill.extensionLessIconName)(), [R.images.gui.maps.icons.tankmen.skills.dialogs.bgGlow()]))
        descRes = R.strings.dialogs.perkLearnConfirm.desc
        self.setSubView(Placeholder.CONTENT, SimpleTextContent(str(backport.text(descRes(), level=self.__level))))
        self.addButton(ConfirmButton(R.strings.dialogs.perkLearnConfirm.learn()))
        self.addButton(CancelButton())
        super(PerkLearnConfirmationDialog, self)._onLoading(*args, **kwargs)
