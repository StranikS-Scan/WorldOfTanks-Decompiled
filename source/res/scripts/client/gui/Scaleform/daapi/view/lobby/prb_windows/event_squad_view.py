# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/event_squad_view.py
import BigWorld
from adisp import process
from UnitBase import UNIT_ROLE
from constants import REQUEST_COOLDOWN
from debug_utils import LOG_DEBUG_DEV
from gui.Scaleform.Waiting import Waiting
from gui.server_events.game_event.event_processors import ChangeSelectedDifficultyLevel
from gui.Scaleform.daapi.view.lobby.prb_windows.squad_view import _HeaderPresenter
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import getDifficultyStars
from gui.Scaleform.daapi.view.meta.EventSquadViewMeta import EventSquadViewMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.shared.utils.functions import makeTooltip, getAbsoluteUrl
from gui.shared.formatters import text_styles
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from CurrentVehicle import g_currentPreviewVehicle
from gui.impl.gen.resources import R
from helpers.CallbackDelayer import CallbackDelayer
_R_TOOLTIPS_TEXT = R.strings.tooltips.event.squad

class EventSquadView(EventSquadViewMeta):

    def _getHeaderPresenter(self):
        return _EventHeaderPresenter(self.prbEntity)

    def _populate(self):
        super(EventSquadView, self)._populate()
        self._playersWithLowerDifficultyLevel = {}
        self._squadDifficultyLevel = None
        g_currentPreviewVehicle.onChanged += self._setActionButtonState
        self._eventsCache.onSyncCompleted += self._setActionButtonState
        self.prbEntity.gameEventController.onSelectedDifficultyLevelChanged += self.__updateSelectedDifficultyLevel
        self._checkCommandersDifficultyLevel()
        self._updatePlayersWithLowerDifficultyLevel()
        self._fillDifficultyLevels()
        self._callbackDelayer = CallbackDelayer()
        self.__updateSelectedDifficultyLevel()
        return

    def _dispose(self):
        g_currentPreviewVehicle.onChanged -= self._setActionButtonState
        self._eventsCache.onSyncCompleted -= self._setActionButtonState
        self.prbEntity.gameEventController.onSelectedDifficultyLevelChanged -= self.__updateSelectedDifficultyLevel
        self._callbackDelayer.destroy()
        super(EventSquadView, self)._dispose()

    def onUnitMembersListChanged(self):
        self._fillDifficultyLevels()

    def _checkCommandersDifficultyLevel(self):
        _, unit = self.prbEntity.getUnit()
        for player in unit.getPlayers().itervalues():
            if player['role'] & UNIT_ROLE.CREATOR == UNIT_ROLE.CREATOR:
                if BigWorld.player().id == player['accountID']:
                    difficultyLevelToSet = self.prbEntity.gameEventController.getSelectedDifficultyLevel()
                else:
                    difficultyLevelToSet = player['difficultyLevel']
                self.prbEntity.gameEventController.setSquadDifficultyLevel(difficultyLevelToSet)
                self.prbEntity.canPlayerDoAction()
                self._setActionButtonState()
                return
            LOG_DEBUG_DEV('EventSquadView._setCommandersDifficultyLevel. Could not find commander.')

    def onUnitPlayerInfoChanged(self, pInfo):
        if pInfo.isCommander():
            self.prbEntity.gameEventController.setSquadDifficultyLevel(pInfo.difficultyLevel)
            if not self.isCommander():
                self.prbEntity.gameEventController.setSelectedDifficultyLevel(pInfo.difficultyLevel)
        LOG_DEBUG_DEV('EventSquadView.onUnitPlayerInfoChanged() updated with difficulty Level:', pInfo.difficultyLevel)
        self._fillDifficultyLevels()
        if self.isCommander():
            self._setActionButtonState()
        else:
            self._checkCommandersDifficultyLevel()

    def onUnitPlayerBecomeCreator(self, pInfo):
        if not pInfo.isCurrentPlayer():
            return
        currentSquadDifficultyLevel = self.prbEntity.gameEventController.getSquadDifficultyLevel()
        difficultyLevelToSet = min(pInfo.maxDifficultyLevel, currentSquadDifficultyLevel)
        self.selectDifficulty(difficultyLevelToSet, True)

    def onUnitPlayerStateChanged(self, pInfo):
        super(EventSquadView, self).onUnitPlayerStateChanged(pInfo)
        if pInfo.isCurrentPlayer() and not pInfo.isReady and not pInfo.isCommander():
            if pInfo.maxDifficultyLevel < self.prbEntity.gameEventController.getSquadDifficultyLevel():
                self.prbEntity.gameEventController.setSelectedDifficultyLevel(pInfo.maxDifficultyLevel)

    def onUnitFlagsChanged(self, flags, timeLeft):
        super(EventSquadView, self).onUnitFlagsChanged(flags, timeLeft)
        if not self.isCommander():
            return
        if flags.isInQueue():
            enable = False
        else:
            enable = True
        LOG_DEBUG_DEV('SQUAD_EVENT_VIEW.onUnitFlagsChanged: ', enable)
        self.as_enableDifficultyDropdownS(enable)

    def isCommander(self):
        return self.prbEntity.isCommander()

    @process
    def selectDifficulty(self, difficultyLevel, force=False):
        ctrl = self.prbEntity.gameEventController
        if self._eventsCache.isEventEnabled() and self.isCommander() and ctrl.hasDifficultyLevelToken(difficultyLevel):
            self._waiting(True)
            yield ChangeSelectedDifficultyLevel(difficultyLevel, force).request()
            self._waiting(False)

    def _waiting(self, waitingOn):
        if waitingOn:
            Waiting.show('sinhronize')
        else:
            self._callbackDelayer.delayCallback(REQUEST_COOLDOWN.CMD_CHANGE_SELECTED_DIFFICULTY_LEVEL, lambda : Waiting.hide('sinhronize'))

    def _showInfoWarningByLevel(self, dropDownLevel):
        for maxLevel in self._playersWithLowerDifficultyLevel.itervalues():
            if maxLevel < dropDownLevel:
                return True

        return False

    def _fillDataDict(self, level):
        self._updatePlayersWithLowerDifficultyLevel()
        locked = not self.prbEntity.gameEventController.hasDifficultyLevelToken(level)
        data = dict()
        data['label'] = backport.text(R.strings.event.event.squad_difficulty())
        data['difficultyLevel'] = level
        tooltip = ''
        if locked:
            icon = "<img src='%s' hspace='1' vspace='-2'/>" % getAbsoluteUrl(RES_ICONS.MAPS_ICONS_SQUAD_LOCKEVENTSQUAD)
            tooltip = makeTooltip(body=backport.text(_R_TOOLTIPS_TEXT.difficulty.lock(), icon=icon, level=getDifficultyStars(level - 1)))
        elif self._showInfoWarningByLevel(level):
            icon = "<img src='%s' hspace='1' vspace='-2'/>" % getAbsoluteUrl(RES_ICONS.MAPS_ICONS_SQUAD_INFOEVENTSQUAD)
            tooltip = makeTooltip(body=backport.text(_R_TOOLTIPS_TEXT.difficulty.warning(), icon=icon))
        data['tooltip'] = tooltip
        data['disabled'] = locked
        data['showInfoIcon'] = False if locked else self._showInfoWarningByLevel(level)
        data['showLockIcon'] = locked
        return data

    def _fillDifficultyLevels(self):
        entity = self.prbEntity
        levels = entity.gameEventController.getDifficultyLevels()
        data = dict()
        data['difficultiesData'] = []
        for level in levels:
            data['difficultiesData'].append(self._fillDataDict(level))

        data['isCommander'] = self.isCommander()
        squadLevel = entity.gameEventController.getSquadDifficultyLevel()
        data['difficultyLevel'] = squadLevel
        header = backport.text(_R_TOOLTIPS_TEXT.difficulty.dropdown.header(), level=getDifficultyStars(squadLevel, isGold=True))
        if self.isCommander():
            tooltip = makeTooltip(header, backport.text(_R_TOOLTIPS_TEXT.difficulty.dropdown.commander.body()))
        else:
            tooltip = makeTooltip(header, backport.text(_R_TOOLTIPS_TEXT.difficulty.dropdown.body()))
        data['tooltip'] = tooltip
        LOG_DEBUG_DEV('EventSquadView._fillDifficultyLevels.DifficultyLevelsData', data)
        self.as_updateDifficultyS(data)

    def _updatePlayersWithLowerDifficultyLevel(self):
        if not self.isCommander():
            return
        entity = self.prbEntity
        unitMgrID = entity.getID()
        playersDifficultyLevels = {}
        for slot in entity.getSlotsIterator(*entity.getUnit(unitMgrID=unitMgrID)):
            if slot.player:
                playersDifficultyLevels[slot.player.slotIdx] = slot.player.maxDifficultyLevel

        self._playersWithLowerDifficultyLevel = playersDifficultyLevels
        LOG_DEBUG_DEV('EventSquadView._updatePlayersWithLowerDifficultyLevel._playersWithLowerDifficultyLevelwas updated with players: ', playersDifficultyLevels)

    def __updateSelectedDifficultyLevel(self):
        if self.isCommander():
            difficultyLevel = self.prbEntity.gameEventController.getSelectedDifficultyLevel()
            self.prbEntity.gameEventController.setSquadDifficultyLevel(difficultyLevel)
        self._fillDifficultyLevels()


class _EventHeaderPresenter(_HeaderPresenter):

    def __init__(self, prbEntity):
        super(_EventHeaderPresenter, self).__init__(prbEntity)
        self._bgImage = backport.image(R.images.gui.maps.icons.squad.backgrounds.event_squad())
        self._isArtVisible = True
        self._isVisibleHeaderIcon = True

    def _getInfoIconTooltipParams(self):
        vehiclesNames = [ veh.userName for veh in self._eventsCache.getEventVehicles() ]
        tooltip = backport.text(R.strings.tooltips.squadWindow.eventVehicle(), tankName=', '.join(vehiclesNames))
        return (makeTooltip(body=tooltip), TOOLTIPS_CONSTANTS.COMPLEX)

    def _getMessageParams(self):
        iconSource = ''
        if self._isVisibleHeaderIcon:
            iconSource = backport.image(R.images.gui.maps.icons.squad.event())
        messageText = text_styles.main(backport.text(R.strings.messenger.dialogs.squadChannel.headerMsg.eventFormationRestriction()))
        return (iconSource, messageText)

    def _packBonuses(self):
        return []
