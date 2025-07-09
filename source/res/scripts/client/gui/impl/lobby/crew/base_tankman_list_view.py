# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/base_tankman_list_view.py
from itertools import islice
from base_crew_view import BaseCrewSoundView
from gui.game_control import restore_contoller
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.crew.tooltips.dismissed_toggle_tooltip import DismissedToggleTooltip
from gui.impl.lobby.crew.utils import playRecruitVoiceover
from gui.server_events import recruit_helper
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.shared.gui_items.Tankman import Tankman
_START_CARDS_LIMIT = 50

class BaseTankmanListView(BaseCrewSoundView):
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, settings):
        self._itemsLimit = _START_CARDS_LIMIT
        self._itemsOffset = 0
        self.__sound = None
        super(BaseTankmanListView, self).__init__(settings)
        return

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId', None)
            if tooltipId == TooltipConstants.TANKMAN:
                toolTipMgr = self.appLoader.getApp().getToolTipMgr()
                args = (self.getParentWindow(), event.getArgument('targetId'))
                toolTipMgr.onCreateWulfTooltip(TooltipConstants.TANKMAN, args, event.mouse.positionX, event.mouse.positionY)
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

    @property
    def _viewProvider(self):
        raise NotImplementedError

    @property
    def _filterState(self):
        raise NotImplementedError

    @property
    def _uiLoggingKey(self):
        raise NotImplementedError

    def _getEvents(self):
        eventsTuple = super(BaseTankmanListView, self)._getEvents()
        return eventsTuple + ((self.restore.onTankmenBufferUpdated, self._onTankmenBufferUpdated),)

    def _finalize(self):
        if self.__sound and self.__sound.isPlaying:
            self.__sound.stop()
        self.__sound = None
        super(BaseTankmanListView, self)._finalize()
        return

    def _onTankmenBufferUpdated(self):
        for tankman in self._viewProvider.items():
            if not isinstance(tankman, Tankman):
                continue
            _, time = restore_contoller.getTankmenRestoreInfo(tankman)
            if tankman.isDismissed and time <= 0:
                self._filterState.onStateChanged()
                break

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
        sortedTman = self._getSortedTankmanList()
        totalItems = len(sortedTman)
        startIdx, endIdx = self._itemsOffset, min(self._itemsOffset + self._itemsLimit, totalItems)
        for item in islice(sortedTman, startIdx, endIdx):
            if isinstance(item, dict) and item.get('type') == 'header':
                self._fillGroupHeader(cardsList, item)
            if isinstance(item, Tankman):
                self._fillTankmanCard(cardsList, item)
            self._fillRecruitCard(cardsList, item)

        self._itemsOffset = endIdx

    def _getSortedTankmanList(self):
        raise NotImplementedError

    def _fillTankmanCard(self, cardsList, tankman):
        raise NotImplementedError

    def _fillRecruitCard(self, cardsList, recruitInfo):
        raise NotImplementedError

    def _fillGroupHeader(self, cardsList, headerInfo):
        hm = TankmanModel()
        hm.setFullUserName(headerInfo['title'])
        hm.setTankmanID(-1)
        cardsList.addViewModel(hm)

    def _onPlayVoiceover(self, recruitID):
        recruitInfo = recruit_helper.getRecruitInfo(recruitID)
        specialVoiceTag = recruitInfo.getSpecialVoiceTag()
        voiceoverParams = self.specialSounds.getVoiceoverByTankmanTag(specialVoiceTag)
        if voiceoverParams is None:
            return
        else:
            self.__sound = playRecruitVoiceover(voiceoverParams)
            return
