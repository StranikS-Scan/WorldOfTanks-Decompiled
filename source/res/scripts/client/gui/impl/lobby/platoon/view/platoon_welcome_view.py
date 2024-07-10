# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/view/platoon_welcome_view.py
import logging
from gui.impl.lobby.platoon.platoon_helpers import getPlatoonBonusState, BonusState
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from skeletons.gui.game_control import IPlatoonController
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.lobby.platoon.view.platoon_search_view import SearchView
from gui.impl.gen.view_models.views.lobby.platoon.platoon_dropdown_model import PlatoonDropdownModel, Type
from gui.impl.lobby.platoon.view.subview.platoon_tiers_filter_subview import TiersFilterSubview
from gui.impl.lobby.platoon.view.subview.platoon_tiers_limit_subview import TiersLimitSubview
from gui.impl.lobby.premacc.squad_bonus_tooltip_content import SquadBonusTooltipContent
from gui.shared.events import PlatoonDropdownEvent
from constants import QUEUE_TYPE, Configs
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl.lobby.platoon.tooltip.platoon_alert_tooltip import AlertTooltip
from gui.shared import g_eventBus
from gui.prb_control.settings import REQUEST_TYPE
_logger = logging.getLogger(__name__)
strButtons = R.strings.platoon.buttons

class WelcomeView(ViewImpl):
    _squadType = Type.RANDOM
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _layoutID = R.views.lobby.platoon.PlatoonDropdown()

    def __init__(self):
        settings = ViewSettings(layoutID=self._layoutID, model=PlatoonDropdownModel())
        self.__tiersLimitSubview = TiersLimitSubview()
        self.__tiersLimitSubview.setShowCallback(self.__showSettingsCallback)
        self.__tiersFilterSubview = TiersFilterSubview()
        self.__prbEntityType = self.__platoonCtrl.getPrbEntityType()
        super(WelcomeView, self).__init__(settings)

    def getPrbEntityType(self):
        return self.__prbEntityType

    def _finalize(self):
        self.__tiersLimitSubview.setShowCallback(None)
        self._removeListeners()
        return

    def _onLoading(self, *args, **kwargs):
        self.viewModel.setType(self._squadType)
        self._addListeners()
        self.setChildView(self.__tiersLimitSubview.layoutID, self.__tiersLimitSubview)
        self.setChildView(self.__tiersFilterSubview.layoutID, self.__tiersFilterSubview)
        self._initButtons()
        self.__setBattleTypeRelatedProps()

    @property
    def viewModel(self):
        return self.getViewModel()

    def update(self, updateTiersLimitSubview=True):
        self.__updateFindButton()
        self.__setBattleTypeRelatedProps()
        if updateTiersLimitSubview:
            self.__tiersLimitSubview.update()
        self.__tiersFilterSubview.update()

    def hideSettings(self):
        self.__showSettingsCallback(False)
        self.__tiersLimitSubview.hideSettings()

    def _initButtons(self):
        with self.viewModel.transaction() as model:
            model.findPlatoon.setCaption(backport.text(strButtons.findPlayers.caption()))
            model.findPlatoon.setDescription(backport.text(strButtons.findPlayers.descriptionDropdown()))
            model.findPlatoon.setIsEnabled(self.__platoonCtrl.canStartSearch())
            model.createPlatoon.setCaption(backport.text(strButtons.createPlatoon.caption()))
            model.createPlatoon.setDescription(backport.text(strButtons.createPlatoon.description()))
            bonusState = getPlatoonBonusState(False)
            model.setHasXpBonus(BonusState.hasAnyBitSet(BonusState.XP_BONUS, bonusState))
            model.setHasCreditsBonus(BonusState.hasAnyBitSet(BonusState.SQUAD_CREDITS_BONUS | BonusState.PREM_CREDITS_BONUS, bonusState))

    def _addListeners(self):
        with self.viewModel.transaction() as model:
            model.findPlatoon.onClick += self.__onFind
            model.createPlatoon.onClick += self.__onCreate
            model.onOutsideClick += self._onOutsideClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__platoonCtrl.onAvailableTiersForSearchChanged += self.__onAvailableTiersForSearchChanged
        self.__platoonCtrl.onAutoSearchCooldownChanged += self.__updateFindButton

    def _removeListeners(self):
        with self.viewModel.transaction() as model:
            model.findPlatoon.onClick -= self.__onFind
            model.createPlatoon.onClick -= self.__onCreate
            model.onOutsideClick -= self._onOutsideClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__platoonCtrl.onAvailableTiersForSearchChanged -= self.__onAvailableTiersForSearchChanged
        self.__platoonCtrl.onAutoSearchCooldownChanged -= self.__updateFindButton

    def _onOutsideClick(self):
        if not self.getParentWindow().isHidden():
            g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': False}))
            self.hideSettings()

    def __updateFindButton(self, *args):
        with self.viewModel.transaction() as model:
            model.findPlatoon.setIsEnabled(self.__platoonCtrl.canStartSearch() and not self.__platoonCtrl.isInCoolDown(REQUEST_TYPE.AUTO_SEARCH))

    def __onServerSettingsChange(self, diff):
        if Configs.UNIT_ASSEMBLER_CONFIG.value in diff:
            self.update(updateTiersLimitSubview=False)

    def __showSettingsCallback(self, state):
        with self.viewModel.transaction() as model:
            model.setIsSettingsVisible(state)

    def __onCreate(self):
        self.__platoonCtrl.createPlatoon(startAutoSearchOnUnitJoin=False)

    def __onFind(self):
        self.__platoonCtrl.createPlatoon(startAutoSearchOnUnitJoin=True)
        SearchView.resetState()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.platoon.AlertTooltip():
            if self.__platoonCtrl.isInCoolDown(REQUEST_TYPE.AUTO_SEARCH):
                return None
            header = R.strings.platoon.buttons.findPlayers.tooltip.header()
            if not self.__platoonCtrl.isSearchingForPlayersEnabled():
                body = R.strings.platoon.buttons.findPlayers.tooltip.noAssembling.body()
            else:
                body = R.strings.platoon.buttons.findPlayers.tooltip.noSuitableTank.body()
            return AlertTooltip(header, body)
        else:
            return SquadBonusTooltipContent(bonusState=getPlatoonBonusState(False)) if contentID == R.views.lobby.premacc.tooltips.SquadBonusTooltip() else super(WelcomeView, self).createToolTipContent(event=event, contentID=contentID)

    def __setBattleTypeRelatedProps(self):
        queueType = self.__platoonCtrl.getQueueType()
        backgrounds = R.images.gui.maps.icons.platoon.dropdown_backgrounds
        battleType = R.strings.menu.headerButtons.battle.types
        battleTypeStr = battleType.standart()
        bgImage = backgrounds.squad()
        with self.viewModel.transaction() as model:
            if queueType == QUEUE_TYPE.EVENT_BATTLES:
                battleTypeStr = battleType.eventSquad()
                bgImage = backgrounds.event()
            elif queueType == QUEUE_TYPE.EPIC:
                battleTypeStr = battleType.epic()
                bgImage = backgrounds.epic()
            elif queueType == QUEUE_TYPE.BATTLE_ROYALE:
                battleTypeStr = battleType.battleRoyale()
                bgImage = backgrounds.battle_royale()
            elif queueType == QUEUE_TYPE.COMP7:
                battleTypeStr = battleType.comp7()
                bgImage = backgrounds.comp7()
        model.setBattleType(backport.text(battleTypeStr))
        model.setBackgroundImage(backport.image(bgImage))

    def __onAvailableTiersForSearchChanged(self):
        self.update(updateTiersLimitSubview=True)
