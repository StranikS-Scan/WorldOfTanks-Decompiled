# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/postmortem_panel.py
import logging
import WWISE
import BattleReplay
from gui.Scaleform.daapi.view.battle.shared.formatters import normalizeHealthPercent
from gui.Scaleform.settings import ICONS_SIZES
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.doc_loaders import messages_panel_reader
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl.gen import R
from gui.impl import backport
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.PostmortemPanelMeta import PostmortemPanelMeta
from gui.shared.badges import buildBadge
from gui.shared.gui_items import Vehicle
from constants import ATTACK_REASON_INDICES, ATTACK_REASON
from account_helpers.settings_core.settings_constants import GRAPHICS
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.shared.view_helpers import UsersInfoHelper
from helpers import dependency
from helpers import int2roman
from items import vehicles
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.dog_tag_composer import layoutComposer
from dog_tags_common.player_dog_tag import PlayerDogTag, DisplayableDogTag
_logger = logging.getLogger(__name__)
_POSTMORTEM_PANEL_SETTINGS_PATH = 'gui/postmortem_panel.xml'
_VEHICLE_SMALL_ICON_RES_PATH = '../maps/icons/vehicle/small/{0}.png'
_ATTACK_REASON_CODE_TO_MSG = {ATTACK_REASON_INDICES['shot']: 'DEATH_FROM_SHOT',
 ATTACK_REASON_INDICES['fire']: 'DEATH_FROM_FIRE',
 ATTACK_REASON_INDICES['ramming']: 'DEATH_FROM_RAMMING',
 ATTACK_REASON_INDICES['world_collision']: 'DEATH_FROM_WORLD_COLLISION',
 ATTACK_REASON_INDICES['death_zone']: 'DEATH_FROM_DEATH_ZONE',
 ATTACK_REASON_INDICES['drowning']: 'DEATH_FROM_DROWNING',
 ATTACK_REASON_INDICES['overturn']: 'DEATH_FROM_WORLD_COLLISION',
 ATTACK_REASON_INDICES['artillery_protection']: 'DEATH_FROM_ARTILLERY_PROTECTION',
 ATTACK_REASON_INDICES['artillery_sector']: 'DEATH_FROM_SECTOR_PROTECTION',
 ATTACK_REASON_INDICES['bombers']: 'DEATH_FROM_SECTOR_BOMBERS',
 ATTACK_REASON_INDICES['recovery']: 'DEATH_FROM_RECOVERY',
 ATTACK_REASON_INDICES['artillery_eq']: 'DEATH_FROM_SHOT',
 ATTACK_REASON_INDICES['bomber_eq']: 'DEATH_FROM_SHOT',
 ATTACK_REASON_INDICES[ATTACK_REASON.MINEFIELD_EQ]: 'DEATH_FROM_MINE_EXPLOSION'}
_ALLOWED_EQUIPMENT_DEATH_CODES = ['DEATH_FROM_MINE_EXPLOSION']

class _ENTITIES_POSTFIX(object):
    UNKNOWN = '_UNKNOWN'
    SELF_SUICIDE = '_SELF_SUICIDE'
    ALLY_SELF = '_ALLY_SELF'
    ENEMY_SELF = '_ENEMY_SELF'


class _BasePostmortemPanel(PostmortemPanelMeta):
    __slots__ = ('__messages', '__deathInfo')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(_BasePostmortemPanel, self).__init__()
        self.__messages = {}
        self.__deathInfo = None
        return

    def getDeathInfo(self):
        return self.__deathInfo

    def resetDeathInfo(self):
        self.__deathInfo = None
        return

    def _populate(self):
        super(_BasePostmortemPanel, self)._populate()
        _, _, self.__messages = messages_panel_reader.readXML(_POSTMORTEM_PANEL_SETTINGS_PATH)
        self._addGameListeners()

    def _dispose(self):
        self._removeGameListeners()
        super(_BasePostmortemPanel, self)._dispose()

    def _addGameListeners(self):
        ctrl = self.sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowVehicleMessageByCode += self.__onShowVehicleMessageByCode
        return

    def _removeGameListeners(self):
        ctrl = self.sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowVehicleMessageByCode -= self.__onShowVehicleMessageByCode
        return

    def _deathInfoReceived(self):
        pass

    def _prepareMessage(self, code, killerVehID, device=None):
        msgText, colors = self.__messages[code]
        context = self.sessionProvider.getCtx()
        if context.isTeamKiller(killerVehID):
            _, colors = self.__messages['DEATH_FROM_TEAM_KILLER']
        self.__deathInfo = {'text': msgText,
         'colors': colors,
         'killerVehicle': killerVehID,
         'device': device}
        self._deathInfoReceived()

    def __onShowVehicleMessageByCode(self, code, postfix, entityID, extra, equipmentID):
        if extra is not None:
            device = extra.deviceUserString
        else:
            device = None
        if equipmentID:
            equipment = vehicles.g_cache.equipments().get(equipmentID)
            if code in _ALLOWED_EQUIPMENT_DEATH_CODES:
                pass
            elif equipment is not None:
                code = '_'.join((code, equipment.name.split('_')[0].upper()))
                entityID = 0
        elif postfix:
            extCode = '{0}_{1}'.format(code, postfix)
            if extCode in self.__messages:
                self._prepareMessage(extCode, entityID, device)
                return
        if code in self.__messages:
            self._prepareMessage(code, entityID, device)
        return


class _SummaryPostmortemPanel(_BasePostmortemPanel):

    def _addGameListeners(self):
        super(_SummaryPostmortemPanel, self)._addGameListeners()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onPostmortemSummaryReceived += self.__onPostmortemSummaryReceived
            missedEvent = ctrl.getCachedEvent(FEEDBACK_EVENT_ID.POSTMORTEM_SUMMARY)
            if missedEvent:
                self.__onPostmortemSummaryReceived(missedEvent)
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            deathInfo = ctrl.getStateValue(VEHICLE_VIEW_STATE.DEATH_INFO)
            if deathInfo:
                self.__prepareMessageFromSummary(deathInfo['killerID'], deathInfo['reason'])
        return

    def _removeGameListeners(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onPostmortemSummaryReceived -= self.__onPostmortemSummaryReceived
        super(_SummaryPostmortemPanel, self)._removeGameListeners()
        return

    def __onPostmortemSummaryReceived(self, postmortemSummaryEvent):
        vehID = postmortemSummaryEvent.getKillerID()
        deathReasonID = postmortemSummaryEvent.getDeathReasonID()
        self.__prepareMessageFromSummary(vehID, deathReasonID)

    def __prepareMessageFromSummary(self, vehID, deathReasonCode):
        if deathReasonCode == ATTACK_REASON_INDICES['shot']:
            if vehID != 0:
                self._prepareMessage(_ATTACK_REASON_CODE_TO_MSG[deathReasonCode], killerVehID=vehID)
        elif deathReasonCode == ATTACK_REASON_INDICES['fire']:
            self._prepareMessage(_ATTACK_REASON_CODE_TO_MSG[deathReasonCode], killerVehID=None)
        else:
            msgCode = _ATTACK_REASON_CODE_TO_MSG[deathReasonCode]
            msgCode += self.__getPostfixByKiller(vehID)
            self._prepareMessage(msgCode, killerVehID=vehID)
        return

    def __getPostfixByKiller(self, killerVehID):
        battleCtx = self.sessionProvider.getCtx()
        if battleCtx.isCurrentPlayer(killerVehID):
            return _ENTITIES_POSTFIX.SELF_SUICIDE
        if battleCtx.isAlly(killerVehID):
            return _ENTITIES_POSTFIX.ALLY_SELF
        return _ENTITIES_POSTFIX.ENEMY_SELF if battleCtx.isEnemy(killerVehID) else _ENTITIES_POSTFIX.UNKNOWN


class PostmortemPanel(_SummaryPostmortemPanel):
    __slots__ = ('__playerInfo', '_isPlayerVehicle', '__maxHealth', '__healthPercent', '__isInPostmortem', '_deathAlreadySet', '__isColorBlind')

    def __init__(self):
        super(PostmortemPanel, self).__init__()
        self.__playerInfo = None
        self._isPlayerVehicle = False
        self.__maxHealth = 0
        self.__healthPercent = 0
        self.__isInPostmortem = False
        self._deathAlreadySet = False
        self.__isColorBlind = self.settingsCore.getSetting('isColorBlind')
        self.__userInfoHelper = UsersInfoHelper()
        return

    def _addGameListeners(self):
        super(PostmortemPanel, self)._addGameListeners()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            ctrl.onVehicleControlling += self.__onVehicleControlling
            ctrl.onPostMortemSwitched += self.__onPostMortemSwitched
            ctrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
            self.__isInPostmortem = ctrl.isInPostmortem
            vehicle = ctrl.getControllingVehicle()
            if vehicle is not None:
                self.__setPlayerInfo(vehicle.id)
                self.__onVehicleControlling(vehicle)
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        dogTagsCtrl = self.sessionProvider.dynamic.dogTags
        if dogTagsCtrl is not None:
            dogTagsCtrl.onKillerDogTagSet += self.__onKillerDogTagSet
            dogTagsCtrl.onVictimDogTagSet += self.__onVictimDogTagSet
        return

    def _removeGameListeners(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            ctrl.onVehicleControlling -= self.__onVehicleControlling
            ctrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            ctrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(PostmortemPanel, self)._removeGameListeners()
        dogTagsCtrl = self.sessionProvider.dynamic.dogTags
        if dogTagsCtrl is not None:
            dogTagsCtrl.onKillerDogTagSet -= self.__onKillerDogTagSet
            dogTagsCtrl.onVictimDogTagSet -= self.__onVictimDogTagSet
        return

    def _deathInfoReceived(self):
        self._updateVehicleInfo()

    def __setHealthPercent(self, health):
        self.__healthPercent = normalizeHealthPercent(health, self.__maxHealth)

    def __setPlayerInfo(self, vehicleID):
        self.__playerInfo = self.sessionProvider.getCtx().getPlayerFullNameParts(vID=vehicleID, showVehShortName=True)

    def __onVehicleControlling(self, vehicle):
        self.__maxHealth = vehicle.maxHealth
        self._isPlayerVehicle = vehicle.isPlayerVehicle
        self.__setHealthPercent(vehicle.health)
        self._updateVehicleInfo()

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.HEALTH:
            if self.__maxHealth != 0 and self.__maxHealth > value:
                self.__setHealthPercent(value)
                self._updateVehicleInfo()
        elif state == VEHICLE_VIEW_STATE.PLAYER_INFO:
            self.__setPlayerInfo(value)
        elif state == VEHICLE_VIEW_STATE.SWITCHING:
            self.__maxHealth = 0
            self.__healthPercent = 0

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.__isInPostmortem = True
        self._updateVehicleInfo()

    def __onRespawnBaseMoving(self):
        self.__isInPostmortem = False
        self.__deathAlreadySet = False
        self.resetDeathInfo()

    def _updateVehicleInfo(self):
        if not self.__isInPostmortem:
            return
        if self._isPlayerVehicle:
            self._showOwnDeathInfo()
        else:
            self._showPlayerInfo()

    def _showOwnDeathInfo(self):
        if self._deathAlreadySet:
            self.as_showDeadReasonS()
        else:
            deathInfo = self.getDeathInfo()
            if deathInfo:
                killerVehID = deathInfo['killerVehicle']
                battleCtx = self.sessionProvider.getCtx()
                if killerVehID and not battleCtx.isCurrentPlayer(killerVehID) and battleCtx.getArenaDP().getVehicleInfo(killerVehID).vehicleType.compactDescr:
                    showVehicle = True
                    vInfoVO = battleCtx.getArenaDP().getVehicleInfo(killerVehID)
                    vTypeInfoVO = vInfoVO.vehicleType
                    vehImg = _VEHICLE_SMALL_ICON_RES_PATH.format(vTypeInfoVO.iconName)
                    if not vTypeInfoVO.isOnlyForBattleRoyaleBattles:
                        vehLvl = int2roman(vTypeInfoVO.level)
                        vehClass = Vehicle.getTypeVPanelIconPath(vTypeInfoVO.classTag)
                    else:
                        vehLvl = None
                        vehClass = None
                    vehName = vTypeInfoVO.shortNameWithPrefix
                    killerUserVO = self.__makeKillerVO(vInfoVO)
                else:
                    showVehicle = False
                    vehLvl = vehImg = vehClass = vehName = None
                    killerUserVO = {}
                reason = self.__makeReasonInfo(deathInfo)
                self.as_setDeadReasonInfoS(reason, showVehicle, vehLvl, vehImg, vehClass, vehName, killerUserVO)
                self._deathAlreadySet = True
            else:
                self.as_setDeadReasonInfoS('', False, None, None, None, None, None)
        return

    def __makeKillerVO(self, vInfoVO):
        fullName = self.sessionProvider.getCtx().getPlayerFullNameParts(vInfoVO.vehicleID, showVehShortName=False)
        playerVO = vInfoVO.player
        userVO = {'userName': fullName.playerName,
         'fakeName': fullName.playerFakeName,
         'clanAbbrev': playerVO.clanAbbrev,
         'region': fullName.regionCode,
         'igrType': playerVO.igrType,
         'tags': self.__userInfoHelper.getUserTags(playerVO.avatarSessionID, playerVO.igrType)}
        badgeID = vInfoVO.selectedBadge
        badge = buildBadge(badgeID, vInfoVO.getBadgeExtraInfo())
        if badge is not None:
            userVO['badgeVisualVO'] = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': True}, shortIconName=True)
        return userVO

    def __makeReasonInfo(self, deathInfo):
        colors = deathInfo['colors']
        if self.__isColorBlind:
            color = colors[1]
        else:
            color = colors[0]
        names = {'device': '',
         'entity': '',
         'killer': '',
         'color': color}
        device = deathInfo['device']
        if device:
            names['device'] = device
        reason = ''
        try:
            reason = deathInfo['text'] % names
        except TypeError:
            LOG_CURRENT_EXCEPTION()

        return reason

    def _showPlayerInfo(self):
        ctx = {'name': self.__playerInfo.playerFullName,
         'health': self.__healthPercent}
        template = 'other'
        msg = makeHtmlString('html_templates:battle/postmortemMessages', template, ctx=ctx)
        self.as_setPlayerInfoS(msg)

    def __onSettingsChanged(self, diff):
        if GRAPHICS.COLOR_BLIND in diff:
            self.__isColorBlind = diff[GRAPHICS.COLOR_BLIND]
            self._deathAlreadySet = False
            self._updateVehicleInfo()

    def onDogTagKillerInPlaySound(self):
        if not BattleReplay.isPlaying():
            WWISE.WW_eventGlobal(backport.sound(R.sounds.dt_pc_destroyed()))

    def onVictimDogTagInPlaySound(self):
        WWISE.WW_eventGlobal(backport.sound(R.sounds.dt_enemy()))

    @staticmethod
    def _buildDogTag(dogTag):
        return DisplayableDogTag(PlayerDogTag.fromDict(dogTag), dogTag['playerName'], dogTag['clanTag'])

    def __onKillerDogTagSet(self, dogTagInfo):
        dogTagModel = layoutComposer.getModel(self._buildDogTag(dogTagInfo['dogTag']))
        _logger.info('PostmortemPanel.__onKillerDogTagSet: dogTagInfo %s, dogTagModel %s', str(dogTagInfo), str(dogTagModel))
        self.as_showKillerDogTagS(dogTagModel)

    def __onVictimDogTagSet(self, dogTagInfo):
        dogTagModel = layoutComposer.getModel(self._buildDogTag(dogTagInfo['dogTag']))
        _logger.info('PostmortemPanel.__onVictimDogTagSet: dogTagInfo %s, dogTagModel %s', str(dogTagInfo), str(dogTagModel))
        self.as_showVictimDogTagS(dogTagModel)
