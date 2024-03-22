# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/base_tankman_list_view.py
from base_crew_view import BaseCrewSoundView
from gui.game_control import restore_contoller
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.crew.tooltips.dismissed_toggle_tooltip import DismissedToggleTooltip
from gui.impl.lobby.crew.utils import playRecruitVoiceover
from gui.server_events import recruit_helper
from gui.shared.gui_items.Vehicle import NO_VEHICLE_ID
from gui.shared.gui_items.Tankman import NO_SLOT
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
_START_CARDS_LIMIT = 50

class BaseTankmanListView(BaseCrewSoundView):
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, settings):
        self._itemsLimit = _START_CARDS_LIMIT
        self._itemsOffset = 0
        self.__sound = None
        super(BaseTankmanListView, self).__init__(settings)
        return

    def _getEvents(self):
        eventsTuple = super(BaseTankmanListView, self)._getEvents()
        return eventsTuple + ((self.restore.onTankmenBufferUpdated, self._onTankmenBufferUpdated),)

    def _finalize(self):
        if self.__sound and self.__sound.isPlaying:
            self.__sound.stop()
        self.__sound = None
        super(BaseTankmanListView, self)._finalize()
        return

    @property
    def _tankmenProvider(self):
        raise NotImplementedError

    @property
    def _recruitsProvider(self):
        raise NotImplementedError

    @property
    def _filterState(self):
        raise NotImplementedError

    @property
    def _uiLoggingKey(self):
        raise NotImplementedError

    def _onTankmenBufferUpdated(self):
        for tankman in self._tankmenProvider.items():
            _, time = restore_contoller.getTankmenRestoreInfo(tankman)
            if tankman.isDismissed and time <= 0:
                self._filterState.onStateChanged()
                break

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId', None)
            if tooltipId == TooltipConstants.TANKMAN:
                toolTipMgr = self.appLoader.getApp().getToolTipMgr()
                args = (event.getArgument('targetId'),)
                toolTipMgr.onCreateWulfTooltip(TooltipConstants.TANKMAN, args, event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                return TooltipConstants.TANKMAN
        return super(BaseTankmanListView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId', None)
            if tooltipId == TooltipConstants.TANKMAN_NOT_RECRUITED:
                return createBackportTooltipContent(specialAlias=TooltipConstants.TANKMAN_NOT_RECRUITED, specialArgs=(event.getArgument('targetId'),))
        elif contentID == R.views.lobby.crew.tooltips.DismissedToggleTooltip():
            return DismissedToggleTooltip()
        return super(BaseTankmanListView, self).createToolTipContent(event, contentID)

    @args2params(int)
    def _onTankmanRestore(self, tankmanID):
        dialogs.showRestoreTankmanDialog(tankmanID, NO_VEHICLE_ID, NO_SLOT, parentViewKey=self._uiLoggingKey)

    @args2params(int, int)
    def _onLoadCards(self, limit, offset):
        viewModel = self.getViewModel()
        self._itemsLimit = limit
        with viewModel.transaction() as tx:
            self._itemsOffset = max(min(offset, tx.getItemsAmount() - 1), 0)
            tx.setItemsOffset(self._itemsOffset)
            self._fillVisibleCards(tx.getTankmanList())

    def _fillVisibleCards(self, cardsList):
        cardsList.clear()
        cardsList.invalidate()
        recruitsAmount, visibleAmount = self._fillRecruits(cardsList, self._itemsLimit, self._itemsOffset)
        tankmanOffset = max(self._itemsOffset - recruitsAmount, 0)
        self._fillTankmen(cardsList, self._itemsLimit - visibleAmount, tankmanOffset)

    def _fillTankmen(self, cardsList, limit, offset):
        items = self._tankmenProvider.items()
        visibleItems = items[offset:limit + offset]
        for tankmen in visibleItems:
            self._fillTankmanCard(cardsList, tankmen)

        return (len(items), len(visibleItems))

    def _fillRecruits(self, cardsList, limit, offset):
        recruits = self._recruitsProvider.items()
        visibleRecruits = recruits[offset:limit + offset]
        for recruitInfo in visibleRecruits:
            self._fillRecruitCard(cardsList, recruitInfo)

        return (len(recruits), len(visibleRecruits))

    def _fillTankmanCard(self, cardsList, tankman):
        raise NotImplementedError

    def _fillRecruitCard(self, cardsList, recruitInfo):
        raise NotImplementedError

    def _onPlayVoiceover(self, recruitID):
        recruitInfo = recruit_helper.getRecruitInfo(recruitID)
        specialVoiceTag = recruitInfo.getSpecialVoiceTag(self.specialSounds)
        voiceoverParams = self.specialSounds.getVoiceoverByTankmanTagOrVehicle(specialVoiceTag)
        if voiceoverParams is None:
            return
        else:
            self.__sound = playRecruitVoiceover(voiceoverParams)
            return
