# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/squad_view.py
from adisp import process
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.prb_control import settings
from gui.prb_control.settings import CTRL_ENTITY_TYPE, REQUEST_TYPE
from gui.Scaleform.daapi.view.lobby.prb_windows.squad_action_button_state_vo import SquadActionButtonStateVO
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.meta.SquadViewMeta import SquadViewMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IBattleRoyaleController

def _unitWithPremium(unitData):
    return any((slot.player.hasPremium for slot in unitData.slotsIterator if slot.player))


class SquadView(SquadViewMeta):
    _eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def inviteFriendRequest(self):
        if self.__canSendInvite():
            self.fireEvent(events.LoadViewEvent(SFViewLoadParams(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY), ctx={'prbName': 'squad',
             'ctrlType': CTRL_ENTITY_TYPE.UNIT}), scope=EVENT_BUS_SCOPE.LOBBY)

    @process
    def toggleReadyStateRequest(self):
        changeStatePossible = True
        if not self.prbEntity.getPlayerInfo().isReady:
            changeStatePossible = yield self.__lobbyContext.isHeaderNavigationPossible()
        if changeStatePossible:
            self.prbEntity.togglePlayerReadyAction(True)

    def onUnitVehiclesChanged(self, dbID, vInfos):
        entity = self.prbEntity
        pInfo = entity.getPlayerInfo(dbID=dbID)
        needToUpdateSlots = self._eventsCache.isSquadXpFactorsEnabled()
        if pInfo.isInSlot:
            slotIdx = pInfo.slotIdx
            if vInfos and not vInfos[0].isEmpty():
                vInfo = vInfos[0]
                vehicleVO = makeVehicleVO(self.itemsCache.items.getItemByCD(vInfo.vehTypeCD), entity.getRosterSettings().getLevelsRange(), isCurrentPlayer=pInfo.isCurrentPlayer())
                slotCost = vInfo.vehLevel
            else:
                slotState = entity.getSlotState(slotIdx)
                vehicleVO = None
                if slotState.isClosed:
                    slotCost = settings.UNIT_CLOSED_SLOT_COST
                else:
                    slotCost = 0
            self.as_setMemberVehicleS(slotIdx, slotCost, vehicleVO)
            if pInfo.isCurrentPlayer():
                if len(vInfos) < slotIdx + 1:
                    needToUpdateSlots = True
            elif vehicleVO is None:
                needToUpdateSlots = True
        if self._eventsCache.isSquadXpFactorsEnabled() or self._eventsCache.isBalancedSquadEnabled():
            self.as_setActionButtonStateS(self.__getActionButtonStateVO())
        if needToUpdateSlots:
            self._updateMembersData()
        return

    def chooseVehicleRequest(self):
        pass

    def leaveSquad(self):
        self._doLeave()

    def onUnitPlayerAdded(self, pInfo):
        super(SquadView, self).onUnitPlayerAdded(pInfo)
        self._setActionButtonState()

    def onUnitPlayerRemoved(self, pInfo):
        super(SquadView, self).onUnitPlayerRemoved(pInfo)
        self._setActionButtonState()

    def onUnitPlayerStateChanged(self, pInfo):
        self._updateRallyData()
        self._setActionButtonState()

    def onUnitFlagsChanged(self, flags, timeLeft):
        super(SquadView, self).onUnitFlagsChanged(flags, timeLeft)
        self._setActionButtonState()
        if flags.isInQueue():
            self._closeSendInvitesWindow()

    def onUnitRosterChanged(self):
        super(SquadView, self).onUnitRosterChanged()
        self._setActionButtonState()
        if not self.__canSendInvite():
            self._closeSendInvitesWindow()

    def onUnitMembersListChanged(self):
        super(SquadView, self).onUnitMembersListChanged()
        self._updateRallyData()
        self._setActionButtonState()

    def getCoolDownRequests(self):
        requests = super(SquadView, self).getCoolDownRequests()
        if REQUEST_TYPE.SET_PLAYER_STATE not in requests:
            requests.append(REQUEST_TYPE.SET_PLAYER_STATE)
        return requests

    def _populate(self):
        super(SquadView, self)._populate()
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__updateHeader()

    def _dispose(self):
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        super(SquadView, self)._dispose()

    def _getHeaderPresenter(self):
        return _BonusHeaderPresenter(self.prbEntity) if self._isPremiumBonusEnabled() else _HeaderPresenter(self.prbEntity)

    def _setActionButtonState(self):
        entity = self.prbEntity
        enabled = not (entity.getFlags().isInQueue() and entity.getPlayerInfo().isReady) and self.__canSendInvite()
        if enabled:
            enabled = False
            unitMgrID = entity.getID()
            for slot in entity.getSlotsIterator(*entity.getUnit(unitMgrID=unitMgrID)):
                if not slot.player:
                    enabled = True
                    break

        self.as_updateInviteBtnStateS(enabled)
        self.as_setActionButtonStateS(self.__getActionButtonStateVO())

    def _updateMembersData(self):
        entity = self.prbEntity
        self.as_setMembersS(*vo_converters.makeSlotsVOs(entity, entity.getID(), withPrem=True))
        self._setActionButtonState()
        self.__updateHeader()

    def _updateRallyData(self):
        entity = self.prbEntity
        data = vo_converters.makeUnitVO(entity, unitMgrID=entity.getID(), withPrem=True)
        self.as_updateRallyS(data)
        self.as_updateBattleTypeS({'leaveBtnTooltip': self._getLeaveBtnTooltip()})
        self.__updateHeader()

    def _getLeaveBtnTooltip(self):
        return TOOLTIPS.SQUADWINDOW_BUTTONS_LEAVESQUAD

    def _isPremiumBonusEnabled(self):
        return self.__lobbyContext.getServerSettings().squadPremiumBonus.isEnabled

    def __updateHeader(self):
        self.as_setSimpleTeamSectionDataS(self._getHeaderPresenter().getData())

    def __getActionButtonStateVO(self):
        return SquadActionButtonStateVO(self.prbEntity)

    def __canSendInvite(self):
        return self.prbEntity.getPermissions().canSendInvite()

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE:
            self.as_setCoolDownForReadyButtonS(event.coolDown)


class EventSquadView(SquadView):

    def _getHeaderPresenter(self):
        return _EventHeaderPresenter(self.prbEntity)

    def _getLeaveBtnTooltip(self):
        return TOOLTIPS.SQUADWINDOW_BUTTONS_LEAVEEVENTSQUAD


class EpicSquadView(SquadView):

    def _getHeaderPresenter(self):
        return _BonusHeaderPresenter(self.prbEntity) if self._isPremiumBonusEnabled() else _EpicHeaderPresenter(self.prbEntity)


class BattleRoyaleSquadView(SquadView):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def _populate(self):
        super(BattleRoyaleSquadView, self)._populate()
        self.__battleRoyaleController.onUpdated += self.__battleRoyaleEnabledChanged

    def _dispose(self):
        self.__battleRoyaleController.onUpdated -= self.__battleRoyaleEnabledChanged
        super(BattleRoyaleSquadView, self)._dispose()

    def _getHeaderPresenter(self):
        return _BattleRoyaleHeaderPresenter(self.prbEntity)

    def __battleRoyaleEnabledChanged(self):
        if not self.__battleRoyaleController.isEnabled():
            self._doLeave()


class _HeaderPresenter(object):
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, prbEntity):
        self._prbEntity = prbEntity
        self._bgImage = backport.image(R.images.gui.maps.icons.squad.backgrounds.without_prem())
        self._isArtVisible = True
        self._isVisibleHeaderIcon = True

    def getData(self):
        iconSource = ''
        messageText = ''
        bonuses = self._packBonuses()
        tooltip, tooltipType = self._getInfoIconTooltipParams()
        if self._isArtVisible and not bonuses:
            iconSource, messageText = self._getMessageParams()
        return {'isVisibleInfoIcon': self._isArtVisible,
         'isVisibleHeaderIcon': self._isArtVisible and self._isVisibleHeaderIcon,
         'isVisibleHeaderMessage': self._isArtVisible,
         'bonuses': bonuses,
         'backgroundHeaderSource': self._bgImage,
         'infoIconTooltip': tooltip,
         'infoIconTooltipType': tooltipType,
         'headerIconSource': iconSource,
         'headerMessageText': messageText}

    def _packBonuses(self):
        result = []
        bonusFactor = self._eventsCache.getSquadXPFactor() * 100
        result.append(self._makeBonus(bonusFactor, 'experience'))
        if result:
            bonusFormatted = text_styles.neutral('{}{}'.format(bonusFactor, backport.text(R.strings.common.common.percent())))
            result[-1]['tooltip'] = makeTooltip(header=backport.text(R.strings.tooltips.squadBonus.complex.header()), body=backport.text(R.strings.tooltips.squadBonus.complex.body(), bonus=bonusFormatted))
            result[-1]['tooltipType'] = TOOLTIPS_CONSTANTS.COMPLEX
        return result

    @staticmethod
    def _makeBonus(value, bonusType):
        return {'icon': backport.image(R.images.gui.maps.icons.squad.bonuses.dyn(bonusType)()),
         'bonusValue': text_styles.creditsTextBig(str(int(round(value))) + backport.text(R.strings.common.common.percent())),
         'label': text_styles.playerOnline(backport.text(R.strings.messenger.dialogs.squadChannel.bonuses.dyn(bonusType)())),
         'tooltipType': None,
         'tooltip': None}

    def _getMessageParams(self):
        return (None, None)

    def _getInfoIconTooltipParams(self):
        isBalancedSquadEnabled = self._eventsCache.isBalancedSquadEnabled()
        if isBalancedSquadEnabled:
            tooltipType = TOOLTIPS_CONSTANTS.COMPLEX
            tooltip = TOOLTIPS.SQUADWINDOW_INFOICON_TECH
        else:
            tooltipType = TOOLTIPS_CONSTANTS.SPECIAL
            tooltip = TOOLTIPS_CONSTANTS.SQUAD_RESTRICTIONS_INFO
        return (tooltip, tooltipType)


class _BonusHeaderPresenter(_HeaderPresenter):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, prbEntity):
        super(_BonusHeaderPresenter, self).__init__(prbEntity)
        if _unitWithPremium(self._prbEntity.getUnitFullData()):
            self._bgImage = backport.image(R.images.gui.maps.icons.squad.backgrounds.with_prem())

    def _packBonuses(self):
        result = super(_BonusHeaderPresenter, self)._packBonuses()
        unitData = self._prbEntity.getUnitFullData()
        if _unitWithPremium(self._prbEntity.getUnitFullData()):
            creditsBonuses = self.__lobbyContext.getServerSettings().squadPremiumBonus
            bonusValue = creditsBonuses.ownCredits if unitData.playerInfo.hasPremium else creditsBonuses.mateCredits
            result.insert(0, self._makeBonus(bonusValue * 100, 'credits'))
        if result:
            result[-1]['tooltip'] = TOOLTIPS_CONSTANTS.SQUAD_BONUS
            result[-1]['tooltipType'] = TOOLTIPS_CONSTANTS.SPECIAL
        return result


class _EpicHeaderPresenter(_HeaderPresenter):

    def _getMessageParams(self):
        iconSource = backport.image(R.images.gui.maps.icons.squad.epicBattle())
        messageText = text_styles.main(backport.text(R.strings.messenger.dialogs.squadChannel.headerMsg.epicBattleFormationRestriction()))
        return (iconSource, messageText)

    def _packBonuses(self):
        return []


class _EventHeaderPresenter(_HeaderPresenter):

    def __init__(self, prbEntity):
        super(_EventHeaderPresenter, self).__init__(prbEntity)
        self._isVisibleHeaderIcon = False
        self._bgImage = backport.image(R.images.gui.maps.icons.squad.backgrounds.event())

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


class _BattleRoyaleHeaderPresenter(_HeaderPresenter):

    def __init__(self, prbEntity):
        super(_BattleRoyaleHeaderPresenter, self).__init__(prbEntity)
        self._bgImage = backport.image(R.images.gui.maps.icons.squad.backgrounds.battle_royale_bg())
        self._isVisibleHeaderIcon = False

    def _packBonuses(self):
        return []

    def _getInfoIconTooltipParams(self):
        tooltip = makeTooltip(header=backport.text(R.strings.tooltips.squadWindow.infoIcon.battleRoyale.header()), body=backport.text(R.strings.tooltips.squadWindow.infoIcon.battleRoyale.body()))
        return (tooltip, TOOLTIPS_CONSTANTS.COMPLEX)

    def _getMessageParams(self):
        headerIconSource = backport.image(R.images.gui.maps.icons.squad.event())
        headerMessageText = text_styles.main(backport.text(R.strings.messenger.dialogs.squadChannel.headerMsg.battleRoyaleHint()))
        return (headerIconSource, headerMessageText)
