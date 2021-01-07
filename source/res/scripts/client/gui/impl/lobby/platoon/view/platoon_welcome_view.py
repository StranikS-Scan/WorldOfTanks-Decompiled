# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/view/platoon_welcome_view.py
import logging
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from skeletons.gui.game_control import IPlatoonController
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.pub import ViewImpl
from gui.impl.lobby.platoon.view.platoon_search_view import SearchView
from gui.impl.gen.view_models.views.lobby.platoon.platoon_dropdown_model import PlatoonDropdownModel
from gui.impl.lobby.platoon.view.subview.platoon_tiers_filter_subview import TiersFilterSubview
from gui.impl.lobby.platoon.view.subview.platoon_tiers_limit_subview import TiersLimitSubview
from gui.impl.lobby.premacc.squad_bonus_tooltip_content import SquadBonusTooltipContent
from gui.shared.events import PlatoonDropdownEvent
from constants import QUEUE_TYPE
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.platoon.tooltip.platoon_alert_tooltip import AlertTooltip
from gui.shared import g_eventBus
from gui.impl.lobby.platoon.platoon_helpers import PreloadableWindow
_logger = logging.getLogger(__name__)
strButtons = R.strings.platoon.buttons

class WelcomeView(ViewImpl):
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.platoon.PlatoonDropdown(), model=PlatoonDropdownModel())
        self.__tiersLimitSubview = TiersLimitSubview()
        self.__tiersLimitSubview.setShowCallback(self.__showSettingsCallback)
        self.__tiersFilterSubview = TiersFilterSubview()
        super(WelcomeView, self).__init__(settings)

    def _finalize(self):
        self.__tiersLimitSubview.setShowCallback(None)
        self.__removeListeners()
        return

    def _onLoading(self, *args, **kwargs):
        self.__addListerens()
        TiersLimitSubview.resetState()
        self.setChildView(self.__tiersLimitSubview.layoutID, self.__tiersLimitSubview)
        self.setChildView(self.__tiersFilterSubview.layoutID, self.__tiersFilterSubview)
        self.__showSettingsCallback(False)
        self.__initButtons()
        self.__setBattleTypeRelatedProps()

    @property
    def viewModel(self):
        return self.getViewModel()

    def update(self, updateTiersLimitSubview=True):
        with self.viewModel.transaction() as model:
            model.btnFind.setIsEnabled(self.__platoonCtrl.canStartSearch())
        self.__setBattleTypeRelatedProps()
        if updateTiersLimitSubview:
            self.__tiersLimitSubview.update()
        self.__tiersFilterSubview.update()

    def hideSettings(self):
        self.__showSettingsCallback(False)
        self.__tiersLimitSubview.hideSettings()

    def __addListerens(self):
        with self.viewModel.transaction() as model:
            model.btnFind.onClick += self.__onFind
            model.btnCreate.onClick += self.__onCreate
            model.onOutsideClick += self.__onOutsideClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__itemsCache.onSyncCompleted += self.__onVehicleStateChanged

    def __removeListeners(self):
        with self.viewModel.transaction() as model:
            model.btnFind.onClick -= self.__onFind
            model.btnCreate.onClick -= self.__onCreate
            model.onOutsideClick -= self.__onOutsideClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__itemsCache.onSyncCompleted -= self.__onVehicleStateChanged

    def __onServerSettingsChange(self, diff):
        if 'unit_assembler_config' in diff:
            self.update(updateTiersLimitSubview=False)

    def __onOutsideClick(self):
        if not self.getParentWindow().isHidden():
            g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': False}))
            self.hideSettings()

    def __showSettingsCallback(self, state):
        with self.viewModel.transaction() as model:
            model.setIsSettingsVisible(state)

    def __onCreate(self):
        self.__platoonCtrl.createPlatoon(startAutoSearchOnUnitJoin=False)

    def __onFind(self):
        self.__platoonCtrl.createPlatoon(startAutoSearchOnUnitJoin=True)
        SearchView.resetState()
        TiersLimitSubview.resetState()

    def __initButtons(self):
        with self.viewModel.transaction() as model:
            model.btnFind.setCaption(backport.text(strButtons.findPlayers.caption()))
            model.btnFind.setDescription(backport.text(strButtons.findPlayers.descriptionDropdown()))
            model.btnFind.setIsEnabled(self.__platoonCtrl.canStartSearch())
            model.btnCreate.setCaption(backport.text(strButtons.createPlatoon.caption()))
            model.btnCreate.setDescription(backport.text(strButtons.createPlatoon.description()))

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.platoon.AlertTooltip():
            header = R.strings.platoon.buttons.findPlayers.tooltip.header()
            if not self.__platoonCtrl.isSearchingForPlayersEnabled():
                body = R.strings.platoon.buttons.findPlayers.tooltip.noAssembling.body()
            else:
                body = R.strings.platoon.buttons.findPlayers.tooltip.noSuitableTank.body()
            return AlertTooltip(header, body)
        return SquadBonusTooltipContent() if contentID == R.views.lobby.premacc.squad_bonus_tooltip_content.SquadBonusTooltipContent() else super(WelcomeView, self).createToolTipContent(event=event, contentID=contentID)

    def __setBattleTypeRelatedProps(self):
        queueType = self.__platoonCtrl.getQueueType()
        backgrounds = R.images.gui.maps.icons.platoon.dropdown_backgrounds
        battleType = R.strings.menu.headerButtons.battle.types
        with self.viewModel.transaction() as model:
            if queueType == QUEUE_TYPE.EVENT_BATTLES:
                model.setBattleType(backport.text(battleType.eventSquad()))
                model.setBackgroundImage(backport.image(backgrounds.event()))
            elif queueType == QUEUE_TYPE.EPIC:
                model.setBattleType(backport.text(battleType.epic()))
                model.setBackgroundImage(backport.image(backgrounds.epic()))
            elif queueType == QUEUE_TYPE.BATTLE_ROYALE:
                model.setBattleType(backport.text(battleType.battleRoyale()))
                model.setBackgroundImage(backport.image(backgrounds.battle_royale()))
            else:
                model.setBattleType(backport.text(battleType.standart()))
                model.setBackgroundImage(backport.image(backgrounds.standard()))

    def __onVehicleStateChanged(self, *args, **kwargs):
        self.update(updateTiersLimitSubview=True)


class SelectionWindow(PreloadableWindow):
    previousPosition = None

    def __init__(self, initialPosition=None):
        super(SelectionWindow, self).__init__(wndFlags=WindowFlags.POP_OVER, content=WelcomeView())
        if initialPosition:
            SelectionWindow.previousPosition = initialPosition
        if SelectionWindow.previousPosition:
            self.move(SelectionWindow.previousPosition.x, SelectionWindow.previousPosition.y)

    def show(self):
        g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': True}))
        if self.content:
            self.content.update(updateTiersLimitSubview=True)
        super(SelectionWindow, self).show()

    def hide(self):
        g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': False}))
        super(SelectionWindow, self).hide()

    def _onContentReady(self):
        if not self._isPreloading():
            g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': True}))
        super(SelectionWindow, self)._onContentReady()

    def _finalize(self):
        g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': False}))
