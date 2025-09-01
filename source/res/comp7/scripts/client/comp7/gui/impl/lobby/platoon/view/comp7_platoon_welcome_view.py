# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/platoon/view/comp7_platoon_welcome_view.py
import logging
from comp7.gui.comp7_constants import SELECTOR_BATTLE_TYPES
from comp7.gui.prb_control.entities import comp7_prb_helpers
from constants import QUEUE_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.platoon.platoon_helpers import getPlatoonBonusState
from gui.impl.lobby.platoon.view.platoon_welcome_view import WelcomeView
from gui.impl.lobby.premacc.squad_bonus_tooltip_content import SquadBonusTooltipContent
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller, IPlatoonController
_logger = logging.getLogger(__name__)
strButtons = R.strings.platoon.buttons

class Comp7WelcomeView(WelcomeView, IGlobalListener):
    __comp7Ctrl = dependency.descriptor(IComp7Controller)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self):
        super(Comp7WelcomeView, self).__init__(layoutID=R.views.comp7.lobby.PlatoonDropdown())

    def createToolTipContent(self, event, contentID):
        return SquadBonusTooltipContent(battleType=SELECTOR_BATTLE_TYPES.COMP7, bonusState=getPlatoonBonusState(False)) if contentID == R.views.lobby.premacc.tooltips.SquadBonusTooltip() else super(Comp7WelcomeView, self).createToolTipContent(event=event, contentID=contentID)

    def onPrbEntitySwitching(self):
        self.getParentWindow().destroy()

    def _initButtons(self):
        super(Comp7WelcomeView, self)._initButtons()
        with self.viewModel.transaction() as model:
            model.createPlatoonForTwo.setText(backport.text(strButtons.createPlatoon.comp7.forTwo.text()))
            model.createPlatoonForTwo.setCaption(backport.text(strButtons.createPlatoon.caption()))
            model.createPlatoonForTwo.setTooltipCaption(backport.text(strButtons.createPlatoon.comp7.forTwo.caption()))
            model.createPlatoonForTwo.setDescription(backport.text(strButtons.createPlatoon.comp7.forTwo.description()))
            model.createPlatoonForSeven.setText(backport.text(strButtons.createPlatoon.comp7.forSeven.text()))
            model.createPlatoonForSeven.setCaption(backport.text(strButtons.createSuperPlatoon.caption()))
            model.createPlatoonForSeven.setTooltipCaption(backport.text(strButtons.createPlatoon.comp7.forSeven.caption()))
            model.createPlatoonForSeven.setDescription(backport.text(strButtons.createPlatoon.comp7.forSeven.description()))

    def _addListeners(self):
        with self.viewModel.transaction() as model:
            model.createPlatoonForTwo.onClick += self.__onCreateForTwo
            model.createPlatoonForSeven.onClick += self.__onCreateForSeven
            model.onOutsideClick += self._onOutsideClick
        self.startGlobalListening()

    def _removeListeners(self):
        with self.viewModel.transaction() as model:
            model.createPlatoonForTwo.onClick -= self.__onCreateForTwo
            model.createPlatoonForSeven.onClick -= self.__onCreateForSeven
            model.onOutsideClick -= self._onOutsideClick
        self.stopGlobalListening()

    def _setBattleTypeRelatedProps(self):
        queueType = self.__platoonCtrl.getQueueType()
        if queueType == QUEUE_TYPE.COMP7:
            with self.viewModel.transaction() as model:
                model.setBattleType(backport.text(R.strings.menu.headerButtons.battle.types.comp7()))
                model.setBackgroundImage(backport.image(R.images.gui.maps.icons.platoon.dropdown_backgrounds.comp7()))
        else:
            super(Comp7WelcomeView, self)._setBattleTypeRelatedProps()

    @staticmethod
    def __onCreateForTwo():
        comp7Config = Comp7WelcomeView.__comp7Ctrl.getModeSettings()
        if comp7Config is None:
            return
        else:
            comp7_prb_helpers.createComp7Squad(squadSize=comp7Config.squadSizes[0])
            return

    @staticmethod
    def __onCreateForSeven():
        comp7Config = Comp7WelcomeView.__comp7Ctrl.getModeSettings()
        if comp7Config is None:
            return
        else:
            comp7_prb_helpers.createComp7Squad(squadSize=comp7Config.squadSizes[1])
            return
