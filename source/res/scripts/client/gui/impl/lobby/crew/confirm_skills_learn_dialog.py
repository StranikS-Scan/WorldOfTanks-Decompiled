# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/confirm_skills_learn_dialog.py
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import ConfirmButton, CancelButton
from gui.impl.gen import R
from gui.impl.lobby.crew.confirm_skills_learn_content import ConfirmSkillsLearnContent
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from skeletons.gui.shared import IItemsCache
from helpers import dependency

class ConfirmSkillsLearnDialogData(object):
    __slots__ = ('tmanInvID', 'xpAmount', 'skill', 'level')

    def __init__(self, tmanInvID, xpAmount, skill, level):
        self.tmanInvID = tmanInvID
        self.xpAmount = xpAmount
        self.skill = skill
        self.level = level


class ConfirmSkillsLearnDialog(DialogTemplateView):
    __slots__ = ('dialogData',)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID=None, uniqueID=None, dialogData=None):
        super(ConfirmSkillsLearnDialog, self).__init__(layoutID, uniqueID)
        self.dialogData = dialogData

    def _onLoading(self, *args, **kwargs):
        content = ConfirmSkillsLearnContent(self.dialogData)
        self.setSubView(Placeholder.CONTENT, content)
        self.addButton(ConfirmButton(R.strings.crew.confirmSkills.buttonApprove()))
        self.addButton(CancelButton(R.strings.crew.confirmSkills.buttonDecline()))
        super(ConfirmSkillsLearnDialog, self)._onLoading(*args, **kwargs)
