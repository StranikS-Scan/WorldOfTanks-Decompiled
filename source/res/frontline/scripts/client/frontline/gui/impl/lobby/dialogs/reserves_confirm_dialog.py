# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/dialogs/reserves_confirm_dialog.py
from gui.impl import backport
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.template_settings.default_dialog_template_settings import DisplayFlags
from frontline.gui.impl.gen.view_models.views.lobby.dialogs.reserves_confirm_dialog_model import ReservesConfirmDialogModel
from gui.impl.pub.dialog_window import DialogButtons
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from uilogging.epic_battle.constants import EpicBattleLogKeys, EpicBattleLogActions, EpicBattleLogButtons as LogButtons
from uilogging.epic_battle.loggers import EpicBattleLogger

class ReservesConfirmDialog(DialogTemplateView):
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ('__skillIds', '__vehicleType', '__applyForAllOfType', '__isBuy', '__isCloseButtonClicked', '__uiEpicBattleLogger')
    LAYOUT_ID = R.views.frontline.lobby.dialogs.ReservesConfirmDialog()
    VIEW_MODEL = ReservesConfirmDialogModel

    def __init__(self, skillIds, vehicleType='', applyForAllOfType=False, isBuy=True):
        super(ReservesConfirmDialog, self).__init__()
        self.__skillIds = skillIds
        self.__vehicleType = vehicleType
        self.__applyForAllOfType = applyForAllOfType
        self.__isBuy = isBuy
        self.__uiEpicBattleLogger = EpicBattleLogger()
        self.__isCloseButtonClicked = False

    def _onLoading(self, *args, **kwargs):
        btnLabel = R.strings.fl_dialogs.confirm.btn
        self.setDisplayFlags(DisplayFlags.RESPONSIVEHEADER.value)
        self.addButton(ConfirmButton(btnLabel.buy() if self.__isBuy else btnLabel.install()))
        self.addButton(CancelButton())
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.OPEN.value, item=EpicBattleLogKeys.ABILITIES_CONFIRM.value, parentScreen=EpicBattleLogKeys.SETUP_VIEW.value)
        self._fillViewModel()
        super(ReservesConfirmDialog, self)._onLoading(*args, **kwargs)

    def _fillViewModel(self):
        with self.viewModel.transaction() as vm:
            price = 0
            isMultipleReserves = len(self.__skillIds) > 1
            mainText = R.strings.fl_dialogs.confirm.title
            orderedSkillsData = self.__epicMetaGameCtrl.getGroupedSkills()
            icons = vm.getIcons()
            names = vm.getNames()
            icons.clear()
            names.clear()
            for _, categorySkills in orderedSkillsData:
                for skill in categorySkills:
                    if skill.skillID in self.__skillIds:
                        price = price + skill.price
                        skillInfo = skill.getSkillInfo()
                        icons.addString(skillInfo.icon)
                        names.addString(backport.text(R.strings.fl_dialogs.confirm.quotedName(), name=skillInfo.name))
                        if not isMultipleReserves:
                            vm.setSelectedSkillName(skill.getSkillInfo().name)
                        break

            if self.__isBuy:
                mainText = mainText.buy
            else:
                mainText = mainText.install
                if self.__applyForAllOfType:
                    mainText = mainText.forAllOfType
            vm.setPrice(price)
            vm.setIsBuy(self.__isBuy)
            vm.setIsMultipleReserves(isMultipleReserves)
            vm.setVehicleType(self.__vehicleType)
            vm.setBonus(self.__epicMetaGameCtrl.getRandomReservesBonusProbability())
            vm.setTitleText(backport.text(mainText.items() if isMultipleReserves else mainText.item()))

    def _getAdditionalData(self):
        return {'rollBack': not self.__isCloseButtonClicked}

    def _closeClickHandler(self, _=None):
        self.__isCloseButtonClicked = True
        super(ReservesConfirmDialog, self)._closeClickHandler(_)

    def _setResult(self, result):
        item = LogButtons.INSTALL if result == DialogButtons.SUBMIT else (LogButtons.CLOSE if self.__isCloseButtonClicked else LogButtons.NOT_INSTALL)
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK, item=item, parentScreen=EpicBattleLogKeys.ABILITIES_CONFIRM)
        super(ReservesConfirmDialog, self)._setResult(result)
