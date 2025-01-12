# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/view/comp7_platoon_welcome_view.py
import logging
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.platoon.platoon_dropdown_model import Type
from gui.impl.lobby.platoon.platoon_helpers import getPlatoonBonusState
from gui.impl.lobby.platoon.view.platoon_welcome_view import WelcomeView
from gui.impl.lobby.premacc.squad_bonus_tooltip_content import SquadBonusTooltipContent
from gui.prb_control.entities.comp7 import comp7_prb_helpers
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
_logger = logging.getLogger(__name__)
strButtons = R.strings.platoon.buttons

class Comp7WelcomeView(WelcomeView):
    _squadType = Type.COMP7
    __comp7Controller = dependency.descriptor(IComp7Controller)

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

    def _removeListeners(self):
        with self.viewModel.transaction() as model:
            model.createPlatoonForTwo.onClick -= self.__onCreateForTwo
            model.createPlatoonForSeven.onClick -= self.__onCreateForSeven
            model.onOutsideClick -= self._onOutsideClick

    def createToolTipContent(self, event, contentID):
        return SquadBonusTooltipContent(battleType=SELECTOR_BATTLE_TYPES.COMP7, bonusState=getPlatoonBonusState(False)) if contentID == R.views.lobby.premacc.tooltips.SquadBonusTooltip() else super(Comp7WelcomeView, self).createToolTipContent(event=event, contentID=contentID)

    @staticmethod
    def __onCreateForTwo():
        comp7Config = Comp7WelcomeView.__comp7Controller.getModeSettings()
        if comp7Config is None:
            return
        else:
            comp7_prb_helpers.createComp7Squad(squadSize=comp7Config.squadSizes[0])
            return

    @staticmethod
    def __onCreateForSeven():
        comp7Config = Comp7WelcomeView.__comp7Controller.getModeSettings()
        if comp7Config is None:
            return
        else:
            comp7_prb_helpers.createComp7Squad(squadSize=comp7Config.squadSizes[1])
            return
