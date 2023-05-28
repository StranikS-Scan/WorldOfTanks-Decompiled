# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/frontline_confirm_dialog.py
from enum import Enum
from helpers import dependency
from gui.impl import backport
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.lobby.tank_setup.dialogs.sub_views.frontline_confirm_icons import FrontlineConfirmIcons
from gui.impl.lobby.tank_setup.dialogs.sub_views.frontline_confirm_title import FrontlineConfirmTitle
from gui.impl.lobby.tank_setup.dialogs.sub_views.frontline_confirm_footer_money import FrontlineConfirmFooterMoney
from gui.impl.lobby.tank_setup.dialogs.sub_views.frontline_confirm_multiple_names import FrontlineConfirmMultipleNames
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.template_settings.default_dialog_template_settings import DisplayFlags
from skeletons.gui.game_control import IEpicBattleMetaGameController

class ConfirmType(Enum):
    Buy = 'buy'
    Install = 'install'


class FrontlineReserveConfirmDialog(DialogTemplateView):
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ('__skillIds', '__confirmType')

    def __init__(self, skillIds, confirmType=ConfirmType.Buy):
        self.__skillIds = skillIds
        self.__confirmType = confirmType
        super(FrontlineReserveConfirmDialog, self).__init__()

    def _onLoading(self, *args, **kwargs):
        price = 0
        isMultipleItems = len(self.__skillIds) > 1
        names = FrontlineConfirmMultipleNames()
        icons = FrontlineConfirmIcons(isMultipleItems)
        mainText = R.strings.epic_battle.dialogs.title
        skillsData = self.__epicMetaGameCtrl.getAllSkillsInformation().values()
        for skill in skillsData:
            if skill.skillID in self.__skillIds:
                price = price + skill.price
                skillInfo = skill.getSkillInfo()
                icons.addIcon(skillInfo.icon)
                names.addName(backport.text(R.strings.epic_battle.dialogs.quotedName(), name=skillInfo.name))

        if self.__confirmType == ConfirmType.Buy:
            mainText = mainText.buy
            btnLabel = R.strings.dialogs.buyInstallConfirmation.submit()
        else:
            mainText = mainText.install
            btnLabel = R.strings.tank_setup.dialogs.confirm.confirm.setup()
        if isMultipleItems:
            title = backport.text(mainText.items(), type=backport.text(R.strings.tank_setup.dialogs.confirm.items.battleAbility()))
        else:
            selectedSkill = next((skill for skill in skillsData if skill.skillID in self.__skillIds))
            title = backport.text(mainText.item(), type=backport.text(R.strings.tank_setup.dialogs.confirm.item.battleAbility()), name=selectedSkill.getSkillInfo().name)
        self.setDisplayFlags(DisplayFlags.RESPONSIVEHEADER.value)
        self.setSubView(Placeholder.ICON, icons)
        self.setSubView(Placeholder.TITLE, FrontlineConfirmTitle(title))
        if isMultipleItems:
            self.setSubView(Placeholder.CONTENT, names)
        if self.__confirmType == ConfirmType.Buy:
            self.setSubView(Placeholder.FOOTER, FrontlineConfirmFooterMoney(price, isMultipleItems))
        self.addButton(ConfirmButton(btnLabel))
        self.addButton(CancelButton())
        super(FrontlineReserveConfirmDialog, self)._onLoading(*args, **kwargs)
