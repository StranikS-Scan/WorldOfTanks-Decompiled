# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/dialogs/battle_abilities_confirm_dialog.py
from frameworks.wulf import ViewSettings
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.gen import R
from frontline.gui.impl.gen.view_models.views.lobby.dialogs.battle_abilities_confirm_dialog_model import BattleAbilitiesConfirmDialogModel
from gui.impl.pub.dialog_window import DialogButtons
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from PlayerEvents import g_playerEvents

class BattleAbilitiesConfirmDialog(FullScreenDialogBaseView):
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ('__skillsInteractor', '__vehicleType', '__isCloseButtonClicked')
    LAYOUT_ID = R.views.frontline.mono.lobby.dialogs.battle_abilities_confirm_dialog()

    def __init__(self, skillsInteractor, vehicleType=''):
        settings = ViewSettings(layoutID=self.LAYOUT_ID, model=BattleAbilitiesConfirmDialogModel())
        super(BattleAbilitiesConfirmDialog, self).__init__(settings)
        self.__skillsInteractor = skillsInteractor
        self.__vehicleType = vehicleType
        self.__isCloseButtonClicked = False

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattleAbilitiesConfirmDialog, self)._onLoading(*args, **kwargs)
        self._fillViewModel()

    def _getEvents(self):
        return ((self.viewModel.onCheckBoxClick, self._onCheckBoxClick),
         (self.viewModel.onSubmitClick, self._onSubmitClick),
         (self.viewModel.onCloseClick, self._onCloseClick),
         (self.viewModel.onCancelClick, self._onCancelClick),
         (g_playerEvents.onAccountBecomeNonPlayer, self.destroyWindow))

    def _fillViewModel(self):
        price = 0
        epicSkills = self.__epicMetaGameCtrl.getEpicSkills()
        skills = [ epicSkills[item.innationID] for item in self.__skillsInteractor.getChangedList() ]
        isMultipleAbilities = len(skills) > 1
        with self.viewModel.transaction() as vm:
            icons = vm.getIcons()
            names = vm.getNames()
            icons.clear()
            names.clear()
            icons.invalidate()
            names.invalidate()
            for skill in skills:
                skillInfo = skill.getSkillInfo()
                icons.addString(skillInfo.icon)
                names.addString(skillInfo.name)
                if not isMultipleAbilities:
                    vm.setSelectedSkillName(skillInfo.name)
                if not skill.isActivated:
                    price += skill.price

            vm.setIsTypeSelected(self.__skillsInteractor.getCheckboxState())
            vm.setPrice(price)
            vm.setIsBuy(price > 0)
            vm.setIsEnoughMoney(self.__epicMetaGameCtrl.getSkillPoints() >= price)
            vm.setIsMultipleAbilities(isMultipleAbilities)
            vm.setVehicleType(self.__vehicleType)
            vm.setBonus(self.__epicMetaGameCtrl.getRandomReservesBonusProbability())

    def _getAdditionalData(self):
        return {'rollBack': not self.__isCloseButtonClicked,
         'applyForAllOfType': self.__skillsInteractor.getCheckboxState()}

    def _onCheckBoxClick(self):
        state = not self.viewModel.getIsTypeSelected()
        self.__skillsInteractor.setCheckboxState(state)
        self._fillViewModel()

    def _onSubmitClick(self):
        self._setResult(DialogButtons.SUBMIT)

    def _onCancelClick(self):
        self._setResult(DialogButtons.CANCEL)

    def _onCloseClick(self):
        self.__isCloseButtonClicked = True
        self._setResult(DialogButtons.CANCEL)
