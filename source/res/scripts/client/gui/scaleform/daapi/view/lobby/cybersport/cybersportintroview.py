# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/CyberSportIntroView.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers.i18n import makeString as _ms
from adisp import process
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.prb_helpers import unitFunctionalProperty
from gui.shared import events
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME as _VCN
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.events import CSVehicleSelectEvent
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, icons
from gui.clubs import formatters as club_fmts, events_dispatcher as club_events, contexts as club_ctx
from gui.clubs.club_helpers import MyClubListener, tryToConnectClubBattle
from gui.clubs.settings import CLIENT_CLUB_STATE, getLadderChevron256x256, LADDER_CHEVRON_ICON_PATH, CLIENT_CLUB_RESTRICTIONS
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.meta.CyberSportIntroMeta import CyberSportIntroMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.game_control.battle_availability import isHourInForbiddenList
_ACCEPTED_VEH_TYPES = (_VCN.LIGHT_TANK, _VCN.MEDIUM_TANK, _VCN.HEAVY_TANK)

class _IntroViewVO(object):

    def __init__(self):
        self.__data = {'clubId': 0,
         'ladderIconSource': '',
         'isLadderBtnEnabled': True,
         'isClockIconVisible': False,
         'clockIconSource': '',
         'isRequestWaitingTextVisible': False,
         'requestWaitingText': '',
         'teamHeaderText': '',
         'teamDescriptionText': '',
         'isTeamDescriptionBackVisible': False,
         'isTeamDescriptionTooltip': False,
         'teamDescriptionTooltip': '',
         'createBtnLabel': '',
         'createBtnTooltip': '',
         'isCreateBtnEnabled': False,
         'isCreateBtnVisible': False,
         'isTeamAdditionalBtnVisible': False,
         'teamAdditionalBtnLabel': '',
         'teamAdditionalBtnTooltip': '',
         'isCancelBtnVisible': False,
         'cancelBtnLabel': '',
         'cancelBtnTooltip': '',
         'isCanCreateBattle': False,
         'isCanJoinBattle': False,
         'isNeedAddPlayers': False,
         'isHaveTeamToShow': False}

    def getData(self):
        return self.__data

    def acceptNavigationByChevron(self, isAccepted):
        self.__data['isLadderBtnEnabled'] = isAccepted

    def setClubLadderChevron(self, club):
        ladderInfo = club.getLadderInfo()
        if ladderInfo.isInLadder():
            chevron = getLadderChevron256x256(ladderInfo.getDivision())
        else:
            chevron = getLadderChevron256x256()
        self.__data['ladderIconSource'] = chevron

    def setNoClubChevron(self, isApplicationSent):
        if isApplicationSent:
            self.__data['isClockIconVisible'] = True
            self.__data['clockIconSource'] = RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_CLOCKICON
            self.__data['isRequestWaitingTextVisible'] = True
            self.__data['requestWaitingText'] = text_styles.alert(CYBERSPORT.WINDOW_INTRO_REQUESTWAITING)
        else:
            self.__data['ladderIconSource'] = '%s/256/empty.png' % LADDER_CHEVRON_ICON_PATH

    def setClubLabel(self, label):
        self.__data['teamHeaderText'] = text_styles.promoSubTitle(label)

    def setClubDBbID(self, ClubDBbID):
        self.__data['clubId'] = ClubDBbID

    def setClubDescription(self, description, isBackVisible = False):
        self.__data['teamDescriptionText'] = description
        self.__data['isTeamDescriptionBackVisible'] = isBackVisible

    def setClubDescriptionTooltip(self, tooltip):
        self.__data['isTeamDescriptionTooltip'] = True
        self.__data['teamDescriptionTooltip'] = tooltip

    def showCreateButton(self, label, tooltip, enabled = True):
        self.__data['isCreateBtnVisible'] = True
        self.__data['isCreateBtnEnabled'] = enabled
        self.__data['createBtnLabel'] = label
        self.__data['createBtnTooltip'] = tooltip

    def showAdditionalButton(self, label, tooltip):
        self.__data['isTeamAdditionalBtnVisible'] = True
        self.__data['teamAdditionalBtnLabel'] = label
        self.__data['teamAdditionalBtnTooltip'] = tooltip

    def showCancelButton(self, label, tooltip):
        self.__data['isCancelBtnVisible'] = True
        self.__data['cancelBtnLabel'] = label
        self.__data['cancelBtnTooltip'] = tooltip

    def moveToTheUnitByCreateButton(self):
        self.__data['isCanCreateBattle'] = self.__data['isCanJoinBattle'] = True

    def needAddPlayers(self):
        self.__data['isNeedAddPlayers'] = True

    def openClubProfileByChevronClick(self):
        self.__data['isHaveTeamToShow'] = True

    def fillDefault(self):
        self.__data['ladderIconSource'] = getLadderChevron256x256()
        self.__data['isRequestWaitingTextVisible'] = True
        self.__data['requestWaitingText'] = text_styles.alert('#cybersport:window/intro/unavailableWaiting')
        self.setClubLabel(_ms(CYBERSPORT.WINDOW_INTRO_TEAM_HEADER_STATICTEAMS))
        self.setClubDescription(text_styles.error('#cybersport:window/intro/team/description/unavailable'), isBackVisible=True)
        self.showCreateButton(_ms(CYBERSPORT.WINDOW_INTRO_CREATE_BTN_ASSEMBLETEAM), TOOLTIPS.CYBERSPORT_INTRO_CREATEBTN_ASSEMBLETEAM, enabled=False)


class CyberSportIntroView(CyberSportIntroMeta, MyClubListener):

    def __init__(self):
        super(CyberSportIntroView, self).__init__()
        self._section = 'selectedIntroVehicles'

    def showSelectorPopup(self):
        rosterSettings = self.unitFunctional.getRosterSettings()
        self.fireEvent(events.LoadViewEvent(CYBER_SPORT_ALIASES.VEHICLE_SELECTOR_POPUP_PY, ctx={'isMultiSelect': False,
         'infoText': CYBERSPORT.WINDOW_VEHICLESELECTOR_INFO_INTRO,
         'componentsOffset': 45,
         'selectedVehicles': self.__getSelectedVehicles(),
         'section': 'cs_intro_view_vehicle',
         'levelsRange': rosterSettings.getLevelsRange(),
         'vehicleTypes': _ACCEPTED_VEH_TYPES}), scope=EVENT_BUS_SCOPE.LOBBY)

    def showStaticTeamProfile(self):
        club = self.getClub()
        if club is not None:
            club_events.showClubProfile(club.getClubDbID())
        return

    def showStaticTeamStaff(self):
        club = self.getClub()
        if club is not None:
            club_events.showClubProfile(club.getClubDbID(), viewIdx=1)
        return

    def joinClubUnit(self):
        tryToConnectClubBattle(self.getClub(), self.clubsState.getJoiningTime())

    @process
    def cancelWaitingTeamRequest(self):
        state = self.clubsState
        if self.clubsState.getStateID() == CLIENT_CLUB_STATE.SENT_APP:
            result = yield self.clubsCtrl.sendRequest(club_ctx.RevokeApplicationCtx(state.getClubDbID(), 'clubs/app/revoke'))
            if result.isSuccess():
                SystemMessages.pushMessage(club_fmts.getAppRevokeSysMsg(self.getClub()))

    @unitFunctionalProperty
    def unitFunctional(self):
        return None

    def setData(self, initialData):
        pass

    def onClubUpdated(self, club):
        self.__updateClubData()

    def onClubsSeasonStateChanged(self, seasonState):
        self.__updateClubData()

    def onClubUnitInfoChanged(self, unitInfo):
        self.__updateClubData()

    def onAccountClubStateChanged(self, state):
        self.__updateClubData()

    def onAccountClubRestrictionsChanged(self):
        self.__updateClubData()

    def onClubNameChanged(self, name):
        self.__updateClubData()

    def onClubLadderInfoChanged(self, ladderInfo):
        self.__updateClubData()

    def onClubMembersChanged(self, members):
        self.__updateClubData()

    def onStatusChanged(self):
        self.__updateClubData()

    def _populate(self):
        super(CyberSportIntroView, self)._populate()
        self.addListener(CSVehicleSelectEvent.VEHICLE_SELECTED, self.__updateSelectedVehicles)
        self.as_setTextsS({'titleLblText': text_styles.promoTitle(CYBERSPORT.WINDOW_INTRO_TITLE),
         'descrLblText': text_styles.main(CYBERSPORT.WINDOW_INTRO_DESCRIPTION),
         'listRoomTitleLblText': text_styles.promoSubTitle(CYBERSPORT.WINDOW_INTRO_SEARCH_TITLE),
         'listRoomDescrLblText': text_styles.main(CYBERSPORT.WINDOW_INTRO_SEARCH_DESCRIPTION),
         'listRoomBtnLabel': _ms(CYBERSPORT.WINDOW_INTRO_SEARCH_BTN),
         'autoTitleLblText': text_styles.middleTitle(CYBERSPORT.WINDOW_INTRO_AUTO_TITLE),
         'autoDescrLblText': text_styles.main(CYBERSPORT.WINDOW_INTRO_AUTO_DESCRIPTION),
         'vehicleBtnTitleTfText': text_styles.standard(CYBERSPORT.BUTTON_CHOOSEVEHICLES_SELECTED),
         'regulationsInfoText': '{0}{1}'.format(icons.info(), text_styles.main(CYBERSPORT.LADDERREGULATIONS_INFO)),
         'regulationsInfoTooltip': TOOLTIPS_CONSTANTS.LADDER_REGULATIONS})
        self.__updateClubData()
        self.__updateAutoSearchVehicle(self.__getSelectedVehicles())
        self.startMyClubListening()
        self.clubsCtrl.getAvailabilityCtrl().onStatusChanged += self.onStatusChanged

    def _dispose(self):
        self.stopMyClubListening()
        self.removeListener(CSVehicleSelectEvent.VEHICLE_SELECTED, self.__updateSelectedVehicles)
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.clubsCtrl.getAvailabilityCtrl().onStatusChanged -= self.onStatusChanged
        super(CyberSportIntroView, self)._dispose()

    def __updateClubData(self):
        resultVO = _IntroViewVO()
        club = self.getClub()
        if self.clubsState.getStateID() == CLIENT_CLUB_STATE.HAS_CLUB and club:
            profile = self.clubsCtrl.getProfile()
            limits = self.clubsCtrl.getLimits()
            resultVO.setClubLabel(club.getUserName())
            resultVO.setClubDBbID(club.getClubDbID())
            resultVO.setClubLadderChevron(club)
            resultVO.showAdditionalButton(_ms(CYBERSPORT.WINDOW_INTRO_ADDITIONALBTN_LIST), TOOLTIPS.CYBERSPORT_INTRO_ADDITIONALBTN)
            resultVO.moveToTheUnitByCreateButton()
            resultVO.openClubProfileByChevronClick()
            if club.hasActiveUnit():
                unitInfo = club.getUnitInfo()
                resultVO.showCreateButton(_ms(CYBERSPORT.WINDOW_INTRO_CREATE_BTN_JOINTEAM), TOOLTIPS.CYBERSPORT_INTRO_CREATEBTN_JOINTEAM)
                if unitInfo.isInBattle():
                    isInBattleIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_SWORDSICON, 16, 16, -3, 0)
                    resultVO.setClubDescription(text_styles.neutral('%s %s' % (isInBattleIcon, _ms(CYBERSPORT.WINDOW_INTRO_TEAM_DESCRIPTION_TEAMINBATTLE))))
                else:
                    resultVO.setClubDescription(text_styles.neutral(CYBERSPORT.STATICFORMATIONPROFILEWINDOW_STATUSLBL_CLUBISCALLED))
            else:
                canCreateUnit = limits.canCreateUnit(profile, club)
                if canCreateUnit.success:
                    resultVO.setClubDescription(text_styles.neutral(CYBERSPORT.WINDOW_INTRO_TEAM_DESCRIPTION_ASSEMBLINGTEAM))
                    resultVO.showCreateButton(_ms(CYBERSPORT.WINDOW_INTRO_CREATE_BTN_ASSEMBLETEAM), TOOLTIPS.CYBERSPORT_INTRO_CREATEBTN_ASSEMBLETEAM)
                elif canCreateUnit.reason == CLIENT_CLUB_RESTRICTIONS.NOT_ENOUGH_MEMBERS:
                    if club.getPermissions().isOwner():
                        resultVO.setClubDescription(text_styles.main(CYBERSPORT.WINDOW_INTRO_TEAM_DESCRIPTION_NOTENOUGHPLAYERS))
                        resultVO.showCreateButton(_ms(CYBERSPORT.WINDOW_INTRO_CREATE_BTN_ADDPLAYERS), TOOLTIPS.CYBERSPORT_INTRO_CREATEBTN_ADDPLAYERS)
                    else:
                        resultVO.setClubDescription(text_styles.error(CYBERSPORT.WINDOW_INTRO_TEAM_DESCRIPTION_OWNERASSEMBLINGTEAM), isBackVisible=True)
                        resultVO.showCreateButton(_ms('#cybersport:window/intro/create/btn/private/seeStaff'), '#tooltips:cyberSport/intro/createBtn/addPlayers/private')
                    resultVO.needAddPlayers()
                else:
                    resultVO.setClubDescription(text_styles.error(CYBERSPORT.WINDOW_INTRO_TEAM_DESCRIPTION_NOTENOUGHPERMISSIONS_ASSEMBLINGTEAM), isBackVisible=True)
                    resultVO.showCreateButton(_ms(CYBERSPORT.WINDOW_INTRO_CREATE_BTN_ASSEMBLETEAM), '#tooltips:StaticFormationProfileWindow/actionBtn/notEnoughPermissions', enabled=False)
        elif self.clubsState.getStateID() == CLIENT_CLUB_STATE.NO_CLUB:
            resultVO.setNoClubChevron(isApplicationSent=False)
            resultVO.setClubLabel(_ms(CYBERSPORT.WINDOW_INTRO_TEAM_HEADER_STATICTEAMS))
            resultVO.setClubDescription(text_styles.main(CYBERSPORT.WINDOW_INTRO_TEAM_DESCRIPTION_CREATEORFIND))
            resultVO.showCreateButton(_ms(CYBERSPORT.WINDOW_INTRO_CREATE_BTN_LOOK), TOOLTIPS.CYBERSPORT_INTRO_CREATEBTN_LOOK)
        elif self.clubsState.getStateID() == CLIENT_CLUB_STATE.SENT_APP:
            resultVO.setNoClubChevron(isApplicationSent=True)
            resultVO.openClubProfileByChevronClick()
            if club is not None:
                resultVO.setClubLabel(club.getUserName())
                resultVO.setClubLadderChevron(club)
            resultVO.setClubDescription(text_styles.neutral(CYBERSPORT.WINDOW_INTRO_TEAM_DESCRIPTION_WAITINGFORREQUEST))
            resultVO.showCancelButton(_ms(CYBERSPORT.WINDOW_INTRO_CANCEL_BTN_LABEL), TOOLTIPS.CYBERSPORT_INTRO_CANCELBTN)
            resultVO.showAdditionalButton(_ms(CYBERSPORT.WINDOW_INTRO_ADDITIONALBTN_LIST), TOOLTIPS.CYBERSPORT_INTRO_ADDITIONALBTN)
        else:
            resultVO.fillDefault()
            resultVO.acceptNavigationByChevron(False)
        if isHourInForbiddenList(self.clubsCtrl.getAvailabilityCtrl().getForbiddenHours()):
            resultVO.setClubDescriptionTooltip(TOOLTIPS_CONSTANTS.LADDER_REGULATIONS)
            resultVO.setClubDescription('{0}{1}'.format(icons.alert(), text_styles.main(CYBERSPORT.LADDERREGULATIONS_WARNING)), True)
        self.as_setStaticTeamDataS(resultVO.getData())
        return

    def __updateSelectedVehicles(self, event):
        if event.ctx is not None and len(event.ctx) > 0:
            vehIntCD = int(event.ctx[0])
            self.unitFunctional.setSelectedVehicles(self._section, [vehIntCD])
            self.__updateAutoSearchVehicle([vehIntCD])
        return

    def __updateAutoSearchVehicle(self, vehsIntCD):
        if len(vehsIntCD):
            vehIntCD = vehsIntCD[0]
            vehicle = g_itemsCache.items.getItemByCD(vehIntCD)
            levelsRange = self.unitFunctional.getRosterSettings().getLevelsRange()
            if vehicle.level not in levelsRange:
                isReadyVehicle = False
                warnTooltip = TOOLTIPS.CYBERSPORT_INTRO_SELECTEDVEHICLEWARN_INCOMPATIBLELEVEL
            elif vehicle.type not in _ACCEPTED_VEH_TYPES:
                isReadyVehicle = False
                warnTooltip = TOOLTIPS.CYBERSPORT_INTRO_SELECTEDVEHICLEWARN_INCOMPATIBLETYPE
            else:
                warnTooltip, isReadyVehicle = '', vehicle.isReadyToPrebattle()
            self.as_setSelectedVehicleS(makeVehicleVO(vehicle), isReadyVehicle, warnTooltip)
        else:
            self.as_setNoVehiclesS(TOOLTIPS.CYBERSPORT_NOVEHICLESINHANGAR)

    def __getSelectedVehicles(self):
        return self.unitFunctional.getSelectedVehicles(self._section)
