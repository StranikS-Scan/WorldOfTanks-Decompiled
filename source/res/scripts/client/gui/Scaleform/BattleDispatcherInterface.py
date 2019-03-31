# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/BattleDispatcherInterface.py
# Compiled at: 2019-03-27 02:05:59
import account_helpers
import AccountCommands
import BigWorld
from account_helpers.AccountPrebattle import AccountPrebattle
from account_helpers import isDemonstrator
from adisp import process
import constants, ArenaType
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.ingame_help import IngameHelpLobbyDelegator
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.utils.requesters import StatsRequester
from gui.Scaleform.utils.functions import makeTooltip, checkAmmoLevel
from helpers import i18n
from messenger import LAZY_CHANNELS
from messenger.gui import MessengerDispatcher
from PlayerEvents import g_playerEvents
from items.tankmen import getSkillsConfig
from items.vehicles import VehicleDescr
from items import vehicles

class BattleDispatcherInterface(UIInterface):

    def __init__(self):
        self.__doTeamReady = False
        self.__totalVehicleLevels = 0
        self.__maxLightVehicleLevels = 0
        self.__maxMediumVehicleLevels = 0
        self.__maxHeavyVehicleLevels = 0
        self.__maxSPGVehicleLevels = 0
        self.__maxATSPGVehicleLevels = 0
        self.ingameHelpDelegator = IngameHelpLobbyDelegator()

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.addExternalCallbacks({'common.FightButtonClick': self.onFightButtonClick,
         'common.FightButtonSelectClick': self.onFightButtonSelectClick,
         'common.onConfirmSquadHaveNotReadyPlayers': self.onConfirmSquadHaveNotReadyPlayers,
         'common.onConfirmTeamHaveNotReadyPlayers': self.onConfirmCompanyHaveNotReadyPlayers})
        self.ingameHelpDelegator.populateUI(proxy)
        g_playerEvents.onEnqueued += self.pe_onEnqueued
        g_playerEvents.onEnqueueFailure += self.pe_onEnqueueFailure
        g_playerEvents.onKickedFromQueue += self.pe_onKickedFromQueue
        g_playerEvents.onPrebattleJoined += self.pe_onPrebattleJoined
        g_playerEvents.onPrebattleJoinFailure += self.pe_onPrebattleJoinFailure
        g_playerEvents.onPrebattleLeft += self.pe_onPrebattleLeft
        g_playerEvents.onKickedFromPrebattle += self.pe_onPrebattleLeft
        g_playerEvents.onPrebattleAutoInvitesChanged += self.updateFightButton
        self.__validateVehicleLevelLimits()

    def dispossessUI(self):
        self.uiHolder.removeExternalCallbacks('common.FightButtonClick', 'common.FightButtonSelectClick', 'common.onConfirmSquadHaveNotReadyPlayers', 'common.onConfirmTeamHaveNotReadyPlayers')
        self.ingameHelpDelegator.dispossessUI()
        g_playerEvents.onEnqueued -= self.pe_onEnqueued
        g_playerEvents.onEnqueueFailure -= self.pe_onEnqueueFailure
        g_playerEvents.onKickedFromQueue -= self.pe_onKickedFromQueue
        g_playerEvents.onPrebattleJoined -= self.pe_onPrebattleJoined
        g_playerEvents.onPrebattleJoinFailure -= self.pe_onPrebattleJoinFailure
        g_playerEvents.onPrebattleLeft -= self.pe_onPrebattleLeft
        g_playerEvents.onKickedFromPrebattle -= self.pe_onPrebattleLeft
        g_playerEvents.onPrebattleAutoInvitesChanged -= self.updateFightButton
        MessengerDispatcher.g_instance.requestCreatePrb = None
        UIInterface.dispossessUI(self)
        return

    def start(self, isInQueue=False):
        self.pe_onPrebattleJoined()
        self.prb_onPrebattleSettingsRecived()
        if isInQueue:
            self.pe_onEnqueued()
        self.updateDemonstratorButton()

    def onPageLoadInit(self, pageName):
        if pageName not in ('hangar', 'battleloading'):
            self.updateFightButton()

    def __getDisableTooltip(self):
        if not self.__isValidLightVehicleMaxLevelLimits():
            min, max = AccountPrebattle.getClassLevelLimits('lightTank')
            return makeTooltip(i18n.makeString('#tooltips:redButton/disabled/vehicleLightLevelLimits/header'), i18n.makeString('#tooltips:redButton/disabled/vehicleLightLevelLimits/body', min, max))
        elif not self.__isValidMediumVehicleMaxLevelLimits():
            min, max = AccountPrebattle.getClassLevelLimits('mediumTank')
            return makeTooltip(i18n.makeString('#tooltips:redButton/disabled/vehicleMediumLevelLimits/header'), i18n.makeString('#tooltips:redButton/disabled/vehicleMediumLevelLimits/body', min, max))
        elif not self.__isValidHeavyVehicleMaxLevelLimits():
            min, max = AccountPrebattle.getClassLevelLimits('heavyTank')
            return makeTooltip(i18n.makeString('#tooltips:redButton/disabled/vehicleHeavyLevelLimits/header'), i18n.makeString('#tooltips:redButton/disabled/vehicleHeavyLevelLimits/body', min, max))
        elif not self.__isValidSPGVehicleMaxLevelLimits():
            min, max = AccountPrebattle.getClassLevelLimits('SPG')
            return makeTooltip(i18n.makeString('#tooltips:redButton/disabled/vehicleSPGLevelLimits/header'), i18n.makeString('#tooltips:redButton/disabled/vehicleSPGLevelLimits/body', min, max))
        elif not self.__isValidATSPGVehicleMaxLevelLimits():
            min, max = AccountPrebattle.getClassLevelLimits('AT-SPG')
            return makeTooltip(i18n.makeString('#tooltips:redButton/disabled/vehicleATSPGLevelLimits/header'), i18n.makeString('#tooltips:redButton/disabled/vehicleATSPGLevelLimits/body', min, max))
        elif not self.__isValidVehicleLevelLimits():
            min, max = (1, 150)
            if AccountPrebattle.getSettings() is not None:
                min, max = AccountPrebattle.getSettings().get('limit_total_level')
            return makeTooltip(i18n.makeString('#tooltips:redButton/disabled/vehicleTotalLevelLimits/header'), i18n.makeString('#tooltips:redButton/disabled/vehicleTotalLevelLimits/body', min, max))
        elif g_currentVehicle.isReadyToFight():
            return
        elif not g_currentVehicle.isPresent():
            return '#tooltips:redButton/disabled/buyNeeded'
        elif g_currentVehicle.isInBattle():
            return '#tooltips:redButton/disabled/vehicleLocked'
        elif not g_currentVehicle.isCrewFull():
            crew_list = ''
            for index in xrange(len(g_currentVehicle.vehicle.crew)):
                if g_currentVehicle.vehicle.crew[index] is None:
                    crew_list += (', ' if len(crew_list) != 0 else '') + i18n.makeString(getSkillsConfig()[g_currentVehicle.vehicle.descriptor.type.crewRoles[index][0]]['userString']).lower()

            return makeTooltip('#tooltips:redButton/disabled/crewNotFull/header', i18n.makeString('#tooltips:redButton/disabled/crewNotFull/body') % crew_list)
        elif g_currentVehicle.isBroken():
            return '#tooltips:redButton/disabled/repairNeeded'
        else:
            return

    @process
    def updateDemonstratorButton(self):
        accountAttrs = yield StatsRequester().getAccountAttrs()
        arenaCache = ArenaType.g_cache
        maps = [isDemonstrator(accountAttrs), 'demonstration']
        for arenaTypeID, arenaTypeName in ArenaType.g_list.iteritems():
            arenaType = arenaCache.get(arenaTypeID)
            for arenaTypeID in arenaType.subtypeIDs:
                subType = arenaTypeID >> 16
                subTypeName = ArenaType._GAMEPLAY_TYPE_TO_NAME[subType]
                nameSuffix = '' if subType == constants.ARENA_GAMEPLAY_TYPE.STANDARD else ' - ' + i18n.makeString('#arenas:type/%s/name' % subTypeName)
                maps.append(arenaType.name + nameSuffix)
                maps.append(arenaTypeID)

        self.call('common.setDemonstratorButton', maps)

    def updateFightButton(self):
        isPrebattle = self.uiHolder.currentInterface == 'prebattle'
        isTraning = self.uiHolder.currentInterface == 'training'
        if not (not g_currentVehicle.isReadyToFight() and not AccountPrebattle.isMemberReady()):
            if not isPrebattle:
                if not isTraning:
                    if not not self.__isValidVehicleLevelLimits():
                        fightButtonDisabled = not self.__isValidAllLevelLimits()
                        self.call('common.disableFightButton', [fightButtonDisabled, self.__getDisableTooltip()])
                        self.call('common.disableOnlyFightButton', fightButtonDisabled or [g_currentVehicle.isVehicleTypeLocked()])
                        label = '#menu:headerButtons/battle'
                        if (AccountPrebattle.isSquad() or AccountPrebattle.isCompany() or AccountPrebattle.isBattleSession()) and not AccountPrebattle.isCreator():
                            if AccountPrebattle.isMemberReady():
                                label = '#menu:headerButtons/notReady'
                            else:
                                label = '#menu:headerButtons/ready'
                        menu = '#menu:headerButtons/battle/menu/standart'
                        menu = AccountPrebattle.isSquad() and '#menu:headerButtons/battle/menu/squad'
                    elif AccountPrebattle.isTraining():
                        menu = '#menu:headerButtons/battle/menu/training'
                    elif AccountPrebattle.isCompany():
                        menu = '#menu:headerButtons/battle/menu/team'
                    elif AccountPrebattle.isBattleSession():
                        menu = '#menu:headerButtons/battle/menu/battle_session'
                    fightTypes = [fightButtonDisabled, label, menu]
                    fightTypes.append('#menu:headerButtons/battle/types/standart')
                    fightTypes.append('standart')
                    fightTypes.append(AccountPrebattle.get() is not None)
                    fightTypes.append('#tooltips:battleTypes/standart')
                    AccountPrebattle.isSquad() or fightTypes.append('#menu:headerButtons/battle/types/squad')
                    fightTypes.append('squad')
                    fightTypes.append(AccountPrebattle.get() is not None)
                    fightTypes.append('#tooltips:battleTypes/squad')
                else:
                    fightTypes.append('#menu:headerButtons/battle/types/squadLeave%s' % ('Owner' if AccountPrebattle.isCreator() else ''))
                    fightTypes.append('prebattleLeave')
                    fightTypes.append(False)
                    fightTypes.append(None)
                fightTypes.append('#menu:headerButtons/battle/types/training')
                fightTypes.append('training')
                fightTypes.append(AccountPrebattle.get() is None or not AccountPrebattle.isTraining())
                fightTypes.append('#tooltips:battleTypes/training')
                fightTypes.append('#menu:headerButtons/battle/types/company')
                fightTypes.append('company')
                fightTypes.append(False)
                fightTypes.append('#tooltips:battleTypes/company')
                hiddenSpecPrebattles = not BigWorld.player().prebattleAutoInvites
                fightTypes.append('#menu:headerButtons/battle/types/spec')
                fightTypes.append('spec')
                fightTypes.append(hiddenSpecPrebattles)
                fightTypes.append('#tooltips:battleTypes/spec')
                messenger = MessengerDispatcher.g_instance
                cid = messenger.channels.setIsLazyChannelHidden(LAZY_CHANNELS.SPECIAL_BATTLES[0], hiddenSpecPrebattles)
                cid is not None and hiddenSpecPrebattles and messenger.currentWindow.getChannelPage(cid).close()
            messenger.currentWindow.refreshChannelList()
        self.call('common.setFightButton', fightTypes)
        self.uiHolder.updateTankParams()
        return

    @process
    def __processTraining(self):
        result = yield checkAmmoLevel()
        if result:
            self.uiHolder.movie.invoke(('loadTraining',))

    def __processSpecList(self):
        self.__openPrebattleChannelPage(LAZY_CHANNELS.SPECIAL_BATTLES)

    def __processSpec(self, confirm=False):
        if AccountPrebattle.isBattleSession():
            self.__setReadyMemberStatus(True, 'battleSession')

    def __setReadyMemberStatus(self, isReady, prbType):
        if isReady:
            if not AccountPrebattle.isMemberReady():

                @process
                def setMemberReady():
                    result = yield checkAmmoLevel()
                    if result:
                        AccountPrebattle.setMemdberReady()
                        if AccountPrebattle.isCreator():
                            self.__doTeamReady = True

                if self.uiHolder.captcha.isCaptchaRequired():
                    self.uiHolder.captcha.showCaptcha(setMemberReady)
                else:
                    setMemberReady()
            elif AccountPrebattle.isCreator():
                self.__setReadyTeam(prbType)
        elif AccountPrebattle.isMemberReady():
            BigWorld.player().prb_notReady(constants.PREBATTLE_ACCOUNT_STATE.NOT_READY, lambda code: self.onPrebattleReadyResponse(code, prbType, 'member'))

    def __setReadyTeam(self, prbType):
        if AccountPrebattle.isCreator() and AccountPrebattle.isMemberReady():

            def doTeamReady():
                BigWorld.player().prb_teamReady(AccountPrebattle.getMemberTeam(), True, lambda code: self.onPrebattleReadyResponse(code, prbType, 'team'))

            if self.uiHolder.captcha.isCaptchaRequired():
                self.uiHolder.captcha.showCaptcha(doTeamReady)
            else:
                doTeamReady()

    def __processCompanyList(self):
        self.__openPrebattleChannelPage(LAZY_CHANNELS.COMPANIES)

    def __processCompany(self, confirm=False):
        if AccountPrebattle.isCompany():
            if AccountPrebattle.isCreator():
                if AccountPrebattle.getMemberRoster() != AccountPrebattle.TEAM_ROSTERSID[0]:
                    self.call('common.showMessageDialog', ['teamDoesNotHaveCommander', False, False])
                    return
                if not self.__isValidVehicleLevelLimits():
                    settings = AccountPrebattle.getSettings()
                    minTL, maxTL = (1, 150)
                    if settings is not None:
                        minTL, maxTL = settings.get('limit_total_level', (1, 150))
                    message = i18n.makeString('#dialogs:teamLevelLimitation/messageEx', current=self.__totalVehicleLevels, min=minTL, max=maxTL)
                    self.call('common.showMessageDialog', ['teamLevelLimitation',
                     False,
                     False,
                     message])
                    return
                if not confirm:
                    notReadyCount, _, playerCount, limitMaxCount = AccountPrebattle.getPlayersReadyStat(AccountPrebattle.TEAM_ROSTERSID[0])
                    if playerCount < limitMaxCount - 1:
                        message = i18n.makeString('#dialogs:teamHaveNotReadyPlayers/messageEx', playerCount - notReadyCount)
                        self.call('common.showMessageDialog', ['teamHaveNotReadyPlayers',
                         True,
                         True,
                         message,
                         'common.onConfirmTeamHaveNotReadyPlayers'])
                        return
            self.__setReadyMemberStatus(True, 'team')
        return

    def __processSquad(self, confirm=False):
        if not AccountPrebattle.isSquad():
            if self.uiHolder.captcha.isCaptchaRequired():
                self.uiHolder.captcha.showCaptcha(self.__doCreateSquad)
            else:
                self.__doCreateSquad()
        else:
            if AccountPrebattle.isCreator() and not confirm:
                notReadyCount, haveInBattle, playerCount, _ = AccountPrebattle.getPlayersReadyStat(AccountPrebattle.SUQAD_ROSTERID)
                if haveInBattle:
                    self.call('common.showMessageDialog', ['squadHavePlayersInBattle', True, False])
                    return
                if not AccountPrebattle.isMemberReady():
                    notReadyCount -= 1
                if notReadyCount > 0:
                    message = i18n.makeString('#dialogs:squadHaveNotReadyPlayers/messageEx', notReadyCount, playerCount)
                    self.call('common.showMessageDialog', ['squadHaveNotReadyPlayers',
                     True,
                     True,
                     message,
                     'common.onConfirmSquadHaveNotReadyPlayers'])
                    return
            self.__setReadyMemberStatus(True, 'squad')

    def __doCreateSquad(self):
        MessengerDispatcher.g_instance.requestCreatePrb = constants.PREBATTLE_TYPE.SQUAD
        BigWorld.player().prb_createSquad()

    def __calculateTotalVehicleLevels(self):
        totalLevel = 0
        prebattle = AccountPrebattle.get()
        if prebattle is None:
            return
        else:
            self.__maxLightVehicleLevels = 0
            self.__maxMediumVehicleLevels = 0
            self.__maxHeavyVehicleLevels = 0
            self.__maxSPGVehicleLevels = 0
            self.__maxATSPGVehicleLevels = 0
            for player in prebattle.rosters.get(AccountPrebattle.getMemberTeam(), {}).values():
                vehCompDescr = player.get('vehCompDescr', '')
                if len(vehCompDescr) > 0:
                    vd = VehicleDescr(compactDescr=vehCompDescr)
                    level = vd.type.level
                    totalLevel += level
                    if 'lightTank' in vehicles.VEHICLE_CLASS_TAGS.intersection(vd.type.tags):
                        self.__maxLightVehicleLevels = max(self.__maxLightVehicleLevels, level)
                    elif 'mediumTank' in vehicles.VEHICLE_CLASS_TAGS.intersection(vd.type.tags):
                        self.__maxMediumVehicleLevels = max(self.__maxMediumVehicleLevels, level)
                    elif 'heavyTank' in vehicles.VEHICLE_CLASS_TAGS.intersection(vd.type.tags):
                        self.__maxHeavyVehicleLevels = max(self.__maxHeavyVehicleLevels, level)
                    elif 'SPG' in vehicles.VEHICLE_CLASS_TAGS.intersection(vd.type.tags):
                        self.__maxSPGVehicleLevels = max(self.__maxSPGVehicleLevels, level)
                    elif 'AT-SPG' in vehicles.VEHICLE_CLASS_TAGS.intersection(vd.type.tags):
                        self.__maxATSPGVehicleLevels = max(self.__maxATSPGVehicleLevels, level)

            self.__totalVehicleLevels = totalLevel
            return

    def __isValidVehicleLevelLimits(self):
        if AccountPrebattle.isCreator():
            checkLevels = AccountPrebattle.isCompany()
            settings = AccountPrebattle.getSettings()
            min, max = (1, 150)
            min, max = settings is not None and settings.get('limit_total_level', (1, 150))
        return checkLevels and (min <= self.__totalVehicleLevels <= max or not checkLevels)

    def __isValidLightVehicleMaxLevelLimits(self):
        checkLevels = AccountPrebattle.isCreator() and AccountPrebattle.isCompany()
        min, max = AccountPrebattle.getClassLevelLimits('lightTank')
        return checkLevels and (min <= self.__maxLightVehicleLevels <= max or self.__maxLightVehicleLevels == 0 or not checkLevels)

    def __isValidMediumVehicleMaxLevelLimits(self):
        checkLevels = AccountPrebattle.isCreator() and AccountPrebattle.isCompany()
        min, max = AccountPrebattle.getClassLevelLimits('mediumTank')
        return checkLevels and (min <= self.__maxMediumVehicleLevels <= max or self.__maxMediumVehicleLevels == 0 or not checkLevels)

    def __isValidHeavyVehicleMaxLevelLimits(self):
        checkLevels = AccountPrebattle.isCreator() and AccountPrebattle.isCompany()
        min, max = AccountPrebattle.getClassLevelLimits('heavyTank')
        return checkLevels and (min <= self.__maxHeavyVehicleLevels <= max or self.__maxHeavyVehicleLevels == 0 or not checkLevels)

    def __isValidSPGVehicleMaxLevelLimits(self):
        checkLevels = AccountPrebattle.isCreator() and AccountPrebattle.isCompany()
        min, max = AccountPrebattle.getClassLevelLimits('SPG')
        return checkLevels and (min <= self.__maxSPGVehicleLevels <= max or self.__maxSPGVehicleLevels == 0 or not checkLevels)

    def __isValidATSPGVehicleMaxLevelLimits(self):
        checkLevels = AccountPrebattle.isCreator() and AccountPrebattle.isCompany()
        min, max = AccountPrebattle.getClassLevelLimits('AT-SPG')
        return checkLevels and (min <= self.__maxATSPGVehicleLevels <= max or self.__maxATSPGVehicleLevels == 0 or not checkLevels)

    def __isValidAllLevelLimits(self):
        return self.__isValidLightVehicleMaxLevelLimits() and self.__isValidMediumVehicleMaxLevelLimits() and self.__isValidHeavyVehicleMaxLevelLimits() and self.__isValidSPGVehicleMaxLevelLimits() and self.__isValidATSPGVehicleMaxLevelLimits()

    def __validateVehicleLevelLimits(self):
        if not AccountPrebattle.isCompany():
            return
        prevValue = self.__totalVehicleLevels
        prevMaxLightValue = self.__maxLightVehicleLevels
        prevMaxMediumValue = self.__maxMediumVehicleLevels
        prevMaxHeavyValue = self.__maxHeavyVehicleLevels
        prevMaxSPGValue = self.__maxSPGVehicleLevels
        prevMaxATSPGValue = self.__maxATSPGVehicleLevels
        self.__calculateTotalVehicleLevels()
        if prevValue != self.__totalVehicleLevels or prevMaxLightValue != self.__maxLightVehicleLevels or prevMaxMediumValue != self.__maxMediumVehicleLevels or prevMaxHeavyValue != self.__maxHeavyVehicleLevels or prevMaxSPGValue != self.__maxSPGVehicleLevels or prevMaxATSPGValue != self.__maxATSPGVehicleLevels:
            self.updateFightButton()

    def __openPrebattleChannelPage(self, info):
        messenger = MessengerDispatcher.g_instance
        cid = messenger.channels.getLazyChannelIdByClientIdx(info[0])
        if cid is not None:
            messenger.currentWindow.getChannelPage(cid).open()
        return

    def pe_onEnqueued(self):
        self.uiHolder.movie.invoke(('loadPrebattle',))

    def pe_onEnqueueFailure(self, errorCode, errorStr):
        error = constants.JOIN_FAILURE_NAMES[errorCode]
        message = '#system_messages:arena_start_errors/join/%s' % error
        SystemMessages.pushI18nMessage(message, type=SystemMessages.SM_TYPE.Error)

    def pe_onKickedFromQueue(self):
        SystemMessages.pushI18nMessage('#system_messages:arena_start_errors/kick/timeout', type=SystemMessages.SM_TYPE.Warning)

    def pe_onPrebattleJoined(self):
        prebattle = AccountPrebattle.get()
        if prebattle is not None:
            prebattle.onSettingsReceived += self.prb_onPrebattleSettingsRecived
            prebattle.onSettingUpdated += self.prb_onPrebattleSettingsRecived
            prebattle.onRosterReceived += self.prb_onPrebattleRosterRecived
            prebattle.onTeamStatesReceived += self.prb_onTeamStateChanged
            prebattle.onPlayerStateChanged += self.prb_onPlayerStateChanged
            prebattle.onPlayerRosterChanged += self.prb_onPlayerRosterChanged
            prebattle.onPlayerAdded += self.prb_onPlayerAdded
            prebattle.onPlayerRemoved += self.prb_onPlayerRemoved
            prebattle.onKickedFromQueue += self.prb_onKickedFromQueue
        return

    def pe_onPrebattleJoinFailure(self, errorCode):
        error = constants.JOIN_FAILURE_NAMES[errorCode]
        message = '#system_messages:arena_start_errors/join/%s' % error
        SystemMessages.pushI18nMessage(message, type=SystemMessages.SM_TYPE.Error)
        self.updateFightButton()

    def pe_onPrebattleLeft(self, code=None):
        self.__totalVehicleLevels = 0
        self.__maxLightVehicleLevels = 0
        self.__maxMediumVehicleLevels = 0
        self.__maxHeavyVehicleLevels = 0
        self.__maxSPGVehicleLevels = 0
        self.__maxATSPGVehicleLevels = 0
        prebattle = AccountPrebattle.get()
        if prebattle:
            prebattle.onSettingsReceived -= self.prb_onPrebattleSettingsRecived
            prebattle.onSettingUpdated -= self.prb_onPrebattleSettingsRecived
            prebattle.onRosterReceived -= self.prb_onPrebattleRosterRecived
            prebattle.onTeamStatesReceived -= self.prb_onTeamStateChanged
            prebattle.onPlayerStateChanged -= self.prb_onPlayerStateChanged
            prebattle.onPlayerRosterChanged -= self.prb_onPlayerRosterChanged
            prebattle.onPlayerAdded -= self.prb_onPlayerAdded
            prebattle.onPlayerRemoved -= self.prb_onPlayerRemoved
            prebattle.onKickedFromQueue -= self.prb_onKickedFromQueue
        self.call('hangar.readyToFight', [g_currentVehicle.isReadyToFight(),
         g_currentVehicle.getHangarMessage() + 'Squad' if AccountPrebattle.isMemberReady() else g_currentVehicle.getHangarMessage(),
         '',
         g_currentVehicle.isPresent(),
         AccountPrebattle.isMemberReady(),
         g_currentVehicle.isCrewFull()])
        self.updateFightButton()

    def prb_onPrebattleSettingsRecived(self, name=''):
        if AccountPrebattle.isSquad() or AccountPrebattle.isCompany() or AccountPrebattle.isBattleSession():
            if AccountPrebattle.isMemberReady() and AccountPrebattle.isTeamReady():
                self.uiHolder.movie.invoke(('loadPrebattle',))
        elif AccountPrebattle.isTraining():
            if (g_currentVehicle.isReadyToFight() or AccountPrebattle.isMemberReady()) and not len(name):
                self.uiHolder.movie.invoke(('loadTraining',))
        if name in ('limit_total_level', 'limit_level', 'limit_class_level'):
            self.__calculateTotalVehicleLevels()
            self.updateFightButton()

    def prb_onPrebattleRosterRecived(self):
        self.__validateVehicleLevelLimits()
        self.updateFightButton()

    def prb_onTeamStateChanged(self):
        if AccountPrebattle.isSquad() or AccountPrebattle.isCompany() or AccountPrebattle.isBattleSession():
            if AccountPrebattle.isMemberReady() or AccountPrebattle.isCreator():
                if AccountPrebattle.isTeamReady() and AccountPrebattle.isMemberInKeyStaff():
                    self.pe_onEnqueued()
                else:
                    self.uiHolder.movie.invoke(('loadHangar',))
        self.updateFightButton()

    @process
    def prb_onPlayerStateChanged(self, id, roster):
        self.__validateVehicleLevelLimits()
        vehicleTypeLocks = yield StatsRequester().getVehicleTypeLocks()
        clanLock = vehicleTypeLocks.get(g_currentVehicle.vehicle.descriptor.type.compactDescr, {}).get(constants.WOT_CLASSIC_LOCK_MODE, None) if g_currentVehicle.isPresent() else None
        if AccountPrebattle.isSquad() or AccountPrebattle.isCompany() or AccountPrebattle.isBattleSession():
            prebattleType = 'squad' if AccountPrebattle.isSquad() else 'company'
            if BigWorld.player().id == id:
                self.updateFightButton()
                ready = AccountPrebattle.isMemberReady()
                self.call('hangar.readyToFight', [g_currentVehicle.isReadyToFight(),
                 g_currentVehicle.getHangarMessage() + (prebattleType if ready else ''),
                 '' if clanLock is None or not g_currentVehicle.isReadyToFight() else i18n.makeString('#menu:currentVehicleStatus/clanLocked') % (BigWorld.wg_getShortTimeFormat(clanLock) + ' ' + BigWorld.wg_getShortDateFormat(clanLock)),
                 g_currentVehicle.isPresent(),
                 ready,
                 g_currentVehicle.isCrewFull()])
                if AccountPrebattle.isCreator() and AccountPrebattle.isMemberReady() and self.__doTeamReady:
                    self.__doTeamReady = False
                    self.__setReadyTeam(prebattleType)
        return

    def prb_onPlayerRosterChanged(self, id, prevRoster, roster, actorID):
        self.__validateVehicleLevelLimits()

    def prb_onPlayerAdded(self, id, roster):
        self.__validateVehicleLevelLimits()

    def prb_onPlayerRemoved(self, id, roster, name):
        self.__validateVehicleLevelLimits()

    def prb_onKickedFromQueue(self, *args):
        if AccountPrebattle.isSquad() or AccountPrebattle.isCompany() or AccountPrebattle.isBattleSession():
            SystemMessages.pushI18nMessage('#system_messages:squad/kickedFromQueue', type=SystemMessages.SM_TYPE.Warning)

    def onPrebattleReadyResponse(self, code, prebattleType, playerType):
        if code == AccountCommands.RES_FAILURE and playerType == 'member':
            SystemMessages.pushI18nMessage('#system_messages:%s/notSetReadyStatus' % prebattleType, type=SystemMessages.SM_TYPE.Warning)
        elif code < 0:
            LOG_ERROR('Server return error for %s %s ready request: responseCode=%s' % (prebattleType, playerType, code))

    def onPrebattleLeaveResponse(self, code):
        if code < 0:
            LOG_ERROR('Server return error for prebattle leave request: responseCode=%s' % code)

    def onFightButtonSelectClick(self, callbackId, queueType):
        self.onFightButtonClick(callbackId, None, queueType)
        return

    def onFightButtonClick(self, callbackId, mapId=None, queueType=0, confirm=False):
        MessengerDispatcher.g_instance.requestCreatePrb = None
        if not g_currentVehicle.isPresent():
            SystemMessages.pushI18nMessage('#menu:hangar/no_current_vehicle_selected', type=SystemMessages.SM_TYPE.Error)
            return
        elif queueType == 'prebattleLeave':
            BigWorld.player().prb_leave(self.onPrebattleLeaveResponse)
            return
        elif queueType == 'company':
            self.__processCompanyList()
            return
        elif queueType == 'spec':
            self.__processSpecList()
            return
        else:
            if not g_currentVehicle.isLocked() and not g_currentVehicle.isBroken():
                if queueType == 'training' or AccountPrebattle.isTraining():
                    self.__processTraining()
                    return
                if AccountPrebattle.isCompany():
                    self.__processCompany()
                    return
                if AccountPrebattle.isBattleSession():
                    self.__processSpec()
                    return
                if queueType == 'squad' or AccountPrebattle.isSquad():
                    self.__processSquad()
                    return

                @process
                def enqueueForArena(mapId):
                    if mapId:
                        mapId = int(mapId)
                        LOG_DEBUG('Demonstrator mapID: %s' % ArenaType.g_list[mapId])
                    else:
                        mapId = -1
                    result = yield checkAmmoLevel()
                    if result:
                        BigWorld.player().enqueueForArena(g_currentVehicle.vehicle.inventoryId, mapId)

                if self.uiHolder.captcha.isCaptchaRequired():
                    self.uiHolder.captcha.showCaptcha(lambda : enqueueForArena(mapId))
                elif self.ingameHelpDelegator.isRequiredToShow():
                    self.ingameHelpDelegator.showIngameHelp(lambda : enqueueForArena(mapId))
                else:
                    enqueueForArena(mapId)
            else:
                if AccountPrebattle.get():
                    if AccountPrebattle.isCreator():
                        if AccountPrebattle.isSquad():
                            self.__processSquad()
                        if AccountPrebattle.isCompany():
                            self.__processCompany()
                        return
                    if AccountPrebattle.isMemberReady():
                        prebattleType = 'squad' if AccountPrebattle.isSquad() else 'company'
                        self.__setReadyMemberStatus(False, prebattleType)
                        return
                SystemMessages.pushI18nMessage('#menu:hangar/vehicle_locked', type=SystemMessages.SM_TYPE.Error)
            return

    def onConfirmSquadHaveNotReadyPlayers(self, callbackId):
        self.__processSquad(confirm=True)

    def onConfirmCompanyHaveNotReadyPlayers(self, callbackId):
        self.__processCompany(confirm=True)
