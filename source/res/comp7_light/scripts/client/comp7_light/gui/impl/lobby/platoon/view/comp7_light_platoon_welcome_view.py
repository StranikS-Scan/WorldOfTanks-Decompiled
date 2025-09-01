# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/platoon/view/comp7_light_platoon_welcome_view.py
from comp7_light.gui.comp7_light_constants import SELECTOR_BATTLE_TYPES
from comp7_light.gui.prb_control.entities import comp7_light_prb_helpers
from constants import QUEUE_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.platoon.platoon_helpers import getPlatoonBonusState
from gui.impl.lobby.platoon.view.platoon_welcome_view import WelcomeView
from gui.impl.lobby.premacc.squad_bonus_tooltip_content import SquadBonusTooltipContent
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController, IPlatoonController

class Comp7LightWelcomeView(WelcomeView, IGlobalListener):
    _layoutID = R.views.comp7_light.lobby.PlatoonDropdown()
    __comp7LightController = dependency.descriptor(IComp7LightController)
    __platoonController = dependency.descriptor(IPlatoonController)

    def createToolTipContent(self, event, contentID):
        return SquadBonusTooltipContent(battleType=SELECTOR_BATTLE_TYPES.COMP7_LIGHT, bonusState=getPlatoonBonusState(False)) if contentID == R.views.lobby.premacc.tooltips.SquadBonusTooltip() else super(Comp7LightWelcomeView, self).createToolTipContent(event=event, contentID=contentID)

    def onPrbEntitySwitching(self):
        self.getParentWindow().destroy()

    def _initButtons(self):
        super(Comp7LightWelcomeView, self)._initButtons()
        with self.viewModel.transaction() as model:
            model.createPlatoonForTwo.setText(backport.text(R.strings.platoon.buttons.createPlatoon.comp7_light.forTwo.text()))
            model.createPlatoonForTwo.setCaption(backport.text(R.strings.platoon.buttons.createPlatoon.caption()))
            model.createPlatoonForTwo.setTooltipCaption(backport.text(R.strings.platoon.buttons.createPlatoon.comp7_light.forTwo.caption()))
            model.createPlatoonForTwo.setDescription(backport.text(R.strings.platoon.buttons.createPlatoon.comp7_light.forTwo.description()))
            model.createPlatoonForSeven.setText(backport.text(R.strings.platoon.buttons.createPlatoon.comp7_light.forSeven.text()))
            model.createPlatoonForSeven.setCaption(backport.text(R.strings.platoon.buttons.createSuperPlatoon.caption()))
            model.createPlatoonForSeven.setTooltipCaption(backport.text(R.strings.platoon.buttons.createPlatoon.comp7_light.forSeven.caption()))
            model.createPlatoonForSeven.setDescription(backport.text(R.strings.platoon.buttons.createPlatoon.comp7_light.forSeven.description()))

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
        if self.__platoonController.getQueueType() == QUEUE_TYPE.COMP7_LIGHT:
            with self.viewModel.transaction() as model:
                model.setBattleType(backport.text(R.strings.menu.headerButtons.battle.types.comp7Light()))
                model.setBackgroundImage(backport.image(R.images.gui.maps.icons.platoon.dropdown_backgrounds.comp7_light()))
        else:
            super(Comp7LightWelcomeView, self)._setBattleTypeRelatedProps()

    def __onCreateForTwo(self):
        comp7LightConfig = self.__comp7LightController.getModeSettings()
        if comp7LightConfig is None:
            return
        else:
            comp7_light_prb_helpers.createComp7LightSquad(squadSize=comp7LightConfig.squadSizes[0])
            return

    def __onCreateForSeven(self):
        comp7LightConfig = self.__comp7LightController.getModeSettings()
        if comp7LightConfig is None:
            return
        else:
            comp7_light_prb_helpers.createComp7LightSquad(squadSize=comp7LightConfig.squadSizes[1])
            return
