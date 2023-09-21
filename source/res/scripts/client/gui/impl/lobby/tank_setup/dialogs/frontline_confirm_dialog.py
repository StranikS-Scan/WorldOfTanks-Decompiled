# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/frontline_confirm_dialog.py
from helpers import dependency
from gui.impl import backport
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.lobby.tank_setup.dialogs.sub_views.frontline_confirm_icons import FrontlineConfirmIcons
from gui.impl.lobby.tank_setup.dialogs.sub_views.frontline_confirm_title import FrontlineConfirmTitle
from gui.impl.lobby.tank_setup.dialogs.sub_views.frontline_confirm_info import FrontlineConfirmInfo
from gui.impl.lobby.tank_setup.dialogs.sub_views.frontline_confirm_footer_money import FrontlineConfirmFooterMoney
from gui.impl.lobby.tank_setup.dialogs.sub_views.frontline_confirm_multiple_names import FrontlineConfirmMultipleNames
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.template_settings.default_dialog_template_settings import DisplayFlags
from skeletons.gui.game_control import IEpicBattleMetaGameController

class FrontlineReserveConfirmDialog(DialogTemplateView):
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ('__skillIds', '__vehicleType', '__applyForAllOfType', '__isBuy', '__isRandomReservesEnabled')

    def __init__(self, skillIds, vehicleType='', applyForAllOfType=False, isBuy=True):
        self.__skillIds = skillIds
        self.__vehicleType = vehicleType
        self.__applyForAllOfType = applyForAllOfType
        self.__isBuy = isBuy
        self.__isRandomReservesEnabled = self.__epicMetaGameCtrl.isRandomReservesModeEnabled()
        super(FrontlineReserveConfirmDialog, self).__init__()

    def _onLoading(self, *args, **kwargs):
        price = 0
        isMultipleItems = len(self.__skillIds) > 1
        info = FrontlineConfirmInfo(self.__epicMetaGameCtrl.getRandomReservesBonusProbability())
        names = FrontlineConfirmMultipleNames()
        icons = FrontlineConfirmIcons(isMultipleItems)
        mainText = R.strings.fl_dialogs.confirm.title
        skillsData = self.__epicMetaGameCtrl.getAllSkillsInformation().values()
        for skill in skillsData:
            if skill.skillID in self.__skillIds:
                price = price + skill.price
                skillInfo = skill.getSkillInfo()
                icons.addIcon(skillInfo.icon)
                names.addName(backport.text(R.strings.fl_dialogs.confirm.quotedName(), name=skillInfo.name))

        if self.__isBuy:
            mainText = mainText.buy
            btnLabel = R.strings.dialogs.buyInstallConfirmation.submit()
        else:
            mainText = mainText.install
            btnLabel = R.strings.tank_setup.dialogs.confirm.confirm.setup()
            if self.__applyForAllOfType:
                mainText = mainText.forAllOfType
        if isMultipleItems:
            title = FrontlineConfirmTitle(backport.text(mainText.items()), self.__vehicleType, isMultipleItems)
        else:
            selectedSkill = next((skill for skill in skillsData if skill.skillID in self.__skillIds))
            title = FrontlineConfirmTitle(backport.text(mainText.item()), self.__vehicleType, isMultipleItems, selectedSkill.getSkillInfo().name)
        self.setDisplayFlags(DisplayFlags.RESPONSIVEHEADER.value)
        self.setSubView(Placeholder.ICON, icons)
        self.setSubView(Placeholder.TITLE, title)
        if isMultipleItems:
            self.setSubView(Placeholder.CONTENT, names)
        if self.__isBuy:
            self.setSubView(Placeholder.FOOTER, FrontlineConfirmFooterMoney(price, isMultipleItems))
        elif self.__isRandomReservesEnabled:
            self.setSubView(Placeholder.FOOTER, info)
        self.addButton(ConfirmButton(btnLabel))
        self.addButton(CancelButton())
        super(FrontlineReserveConfirmDialog, self)._onLoading(*args, **kwargs)

    @staticmethod
    def _getAdditionalData():
        return {'rollBack': True}
