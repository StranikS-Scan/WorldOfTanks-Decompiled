# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/recruit_panel_base.py
import typing
from typing import TYPE_CHECKING, Any, List, Dict
import SoundGroups
from CurrentVehicle import g_currentVehicle
from crew2 import settings_globals
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform import MENU
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.CrewMeta import CrewMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import getRecruitsForMobilization
from gui.impl.auxiliary.vehicle_helper import SessionVehicleTypeFilters
from gui.impl.gen import R
from gui.shared import events
from gui.shared.SoundEffectsId import SoundEffectsId
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Tankman import getRoleBigIconPath, Tankman
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES, VEHICLE_TYPES_ORDER
from gui.shared.gui_items.crew_skin import localizedFullName, getCrewSkinIconSmall
from gui.shared.utils.functions import makeTooltip, replaceHyphenToUnderscore
from helpers import dependency
from helpers.i18n import convert, makeString
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from items.components.detachment_constants import DOG_TAG
from items.tankmen import getSkillsConfig, MAX_SKILL_LEVEL
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class RecruitPanelBase(CrewMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    detachmentCache = dependency.descriptor(IDetachmentCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, eventNameSuffix=''):
        super(RecruitPanelBase, self).__init__()
        self.__eventNameSuffix = eventNameSuffix

    @property
    def vehicleTypeFilter(self):
        return SessionVehicleTypeFilters.getVehicleTypeFilterByKey(self.__class__.__name__)

    def _populate(self):
        super(RecruitPanelBase, self)._populate()
        self._addListener(events.CrewPanelEvent.OPEN_CHANGE_ROLE, self.onOpenChangeRole)
        self._addListener(events.CrewPanelEvent.UNLOAD_RECRUITS, self.onUnloadRecruits)
        self._addListener(events.CrewPanelEvent.UNLOAD_RECRUIT, self.onUnloadRecruit)
        self._addListener(events.CrewPanelEvent.RETURN_RECRUITS, self.onReturnCrew)
        self._addListener(events.CrewPanelEvent.SET_BEST_RECRUITS, self.onSetBestCrew)
        self._addListener(events.CrewPanelEvent.RETRAIN_RECRUITS, self.onRetrainRecruits)
        self._addListener(events.CrewPanelEvent.CONVERT_RECRUITS, self.onConvertRecruits)
        g_clientUpdateManager.addCallbacks({'inventory': self.onInventoryUpdate})

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._removeListener(events.CrewPanelEvent.OPEN_CHANGE_ROLE, self.onOpenChangeRole)
        self._removeListener(events.CrewPanelEvent.UNLOAD_RECRUITS, self.onUnloadRecruits)
        self._removeListener(events.CrewPanelEvent.UNLOAD_RECRUIT, self.onUnloadRecruit)
        self._removeListener(events.CrewPanelEvent.RETURN_RECRUITS, self.onReturnCrew)
        self._removeListener(events.CrewPanelEvent.SET_BEST_RECRUITS, self.onSetBestCrew)
        self._removeListener(events.CrewPanelEvent.RETRAIN_RECRUITS, self.onRetrainRecruits)
        self._removeListener(events.CrewPanelEvent.CONVERT_RECRUITS, self.onConvertRecruits)
        super(RecruitPanelBase, self)._dispose()

    def onInventoryUpdate(self, invDiff):
        self.updateRecruitPanel()

    def openChangeRoleWindow(self, tmanInvID, requiredRole=None, vehicle=None, mobilization=False, callback=None):
        vehicle = vehicle or g_currentVehicle.item
        if not vehicle:
            return
        if not requiredRole:
            tman = self.itemsCache.items.getTankman(tmanInvID)
            if tman:
                requiredRole = tman.descriptor.role
        ctx = {'tankmanID': int(tmanInvID),
         'currentVehicleCD': vehicle.descriptor.type.compactDescr,
         'requiredRole': requiredRole,
         'callback': callback,
         'mobilization': mobilization}
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.ROLE_CHANGE), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)

    def onFilterToggle(self, index):
        vehicleType = VEHICLE_TYPES_ORDER[index]
        self.vehicleTypeFilter.toggle(vehicleType)

    def updateRecruitPanel(self):
        self._printOverrideError('onOpenChangeRole')

    def onOpenChangeRole(self, *args):
        self._printOverrideError('onOpenChangeRole')

    def onUnloadRecruits(self, *args):
        self._printOverrideError('onUnloadRecruits')

    def onUnloadRecruit(self, *args):
        self._printOverrideError('onUnloadRecruit')

    def onReturnCrew(self, *args):
        self._printOverrideError('onReturnCrew')

    def onSetBestCrew(self, *args):
        self._printOverrideError('onSetBestCrew')

    def onRetrainRecruits(self, *args):
        self._printOverrideError('onRetrainRecruits')

    def onConvertRecruits(self, *args):
        self._printOverrideError('onConvertRecruits')

    def onCrewDogMoreInfoClick(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.CREW_ABOUT_DOG_WINDOW)), EVENT_BUS_SCOPE.LOBBY)

    def onCrewDogItemClick(self):
        self._playSound(SoundEffectsId.RUDY_DOG)

    def _addListener(self, eventName, handler):
        self.addListener(eventName + self.__eventNameSuffix, handler, scope=EVENT_BUS_SCOPE.LOBBY)

    def _removeListener(self, eventName, handler):
        self.removeListener(eventName + self.__eventNameSuffix, handler, scope=EVENT_BUS_SCOPE.LOBBY)

    def _updateDogData(self, vehicle):
        dogName = ''
        if DOG_TAG in vehicle.tags:
            dogName = backport.text(R.strings.menu.hangar.crew.rody.dog.dyn(vehicle.nationName).name())
        self.as_dogResponseS(dogName)
        tooltipId = TOOLTIPS.HANGAR_CREW_RUDY_DOG + vehicle.nationName
        self.as_setDogTooltipS(tooltipId)

    def _getFilterData(self):
        return [ {'id': vehicleType,
         'value': backport.image(R.images.gui.maps.icons.filters.tanks.dyn(replaceHyphenToUnderscore(vehicleType))()),
         'tooltip': makeTooltip(MENU.getCarouselTankFilter(vehicleType), TOOLTIPS.FILTERTOGGLE_SPECIALIZATION_RECRUIT_BODY),
         'selected': self.vehicleTypeFilter.isSelected(vehicleType)} for vehicleType in VEHICLE_TYPES_ORDER ]

    def _getRoleData(self, vehicle, crew):
        roles = []
        skillsConfig = getSkillsConfig()
        for slotIdx, tman in crew:
            crewRoles = vehicle.descriptor.type.crewRoles[slotIdx]
            role = crewRoles[0]
            roles.append({'tankmanID': tman.invID if tman is not None else None,
             'roleType': role,
             'role': convert(skillsConfig.getSkill(role).userString),
             'roleIcon': getRoleBigIconPath(role),
             'nationID': vehicle.nationID,
             'typeID': vehicle.innationID,
             'slot': slotIdx,
             'vehicleType': vehicle.shortUserName,
             'tankType': vehicle.type,
             'vehicleElite': vehicle.isPremium or vehicle.isPremiumIGR,
             'roles': crewRoles})

        return roles

    def _getRecruitsData(self, vehicle, crew, showLeaderWarning, isBarracksEmpty, desiredVehicleCD=None, types=None):
        conversion = settings_globals.g_conversion
        itemsCache = self.itemsCache
        allTankmen = getRecruitsForMobilization(vehicle, types)
        commander_bonus = vehicle.bonuses['commander']
        leaderDetachmentName = self._getLeaderDetachmentName(crew) if not showLeaderWarning else None
        recruitsInTank = set([ t.invID for _, t in crew if t ])
        tankmenData = []
        allTankmen.sort(key=lambda t: (Tankman.TANKMEN_ROLES_ORDER[t.role],
         -t.descriptor.totalXP(),
         VEHICLE_TYPES_ORDER_INDICES[itemsCache.items.getItemByCD(t.vehicleNativeDescr.type.compactDescr).type],
         t.invID))
        for tankman in allTankmen:
            tankmanVehicle = itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
            isCommander = tankman.descriptor.role == Tankman.ROLES.COMMANDER
            isInSlot = tankman.invID in recruitsInTank
            bonusRoleLevel = commander_bonus if not isCommander else 0.0
            skillsConfig = getSkillsConfig()
            skills_count = skillsConfig.getNumberOfActiveSkills()
            skills = tankman.skills
            skillsList = [ {'tankmanID': tankman.invID,
             'id': str(idx),
             'name': skill.userName,
             'desc': skill.description,
             'icon': skill.icon,
             'level': skill.level,
             'active': skill.isEnable and skill.isActive} for idx, skill in enumerate(skills) ]
            newSkillsCount, lastNewSkillLvl = tankman.newSkillCount
            if newSkillsCount > 0:
                skillsList.append({'buy': True,
                 'buyCount': newSkillsCount - 1,
                 'tankmanID': tankman.invID,
                 'level': lastNewSkillLvl})
            hasSmallWarning = tankman.roleLevel < MAX_SKILL_LEVEL and not tankman.skills
            isShowUnremovableInstructor = False
            isFullSlots = len(recruitsInTank) == len(vehicle.crew)
            detachmentName = conversion.getUnremovableInstructorForTankman(tankman.descriptor)[0] if not showLeaderWarning else None
            if detachmentName and (leaderDetachmentName is None and (isBarracksEmpty or isFullSlots) or leaderDetachmentName and leaderDetachmentName != detachmentName):
                isShowUnremovableInstructor = True
            lastSkillLevel = tankman.descriptor.lastSkillLevel
            trained = tankman.vehicleNativeDescr.type.compactDescr == vehicle.intCD
            isLeader = tankman.isLeader
            tankmanData = {'fullName': tankman.fullUserName if not isLeader else text_styles.isLeader(tankman.fullUserName),
             'lastName': tankman.lastUserName or tankman.firstUserName,
             'rank': tankman.rankUserName,
             'specializationLevel': tankman.realRoleLevel[0],
             'role': tankman.roleUserName,
             'vehicleType': tankmanVehicle.shortUserName,
             'iconFile': backport.image(R.images.gui.maps.icons.tankmen.icons.small.dyn(replaceHyphenToUnderscore(tankman.extensionLessIcon))()),
             'rankIconFile': tankman.iconRank,
             'roleIconFile': getRoleBigIconPath(tankman.descriptor.role),
             'contourIconFile': tankmanVehicle.iconContour,
             'tankmanID': tankman.invID,
             'nationID': tankman.nationID,
             'typeID': tankmanVehicle.innationID,
             'inTank': tankman.isInTank,
             'inCurrentTank': isInSlot,
             'trained': trained,
             'status': tankman.getTankmanState(),
             'roleType': tankman.descriptor.role,
             'tankType': tankmanVehicle.type,
             'bonus': bonusRoleLevel,
             'lastSkillLevel': lastSkillLevel,
             'compact': tankman.strCD,
             'availableSkillsCount': skills_count,
             'skills': skillsList,
             'isLeader': isLeader,
             'hasSmallWarning': hasSmallWarning,
             'isInstructor': tankman.isInstructor,
             'unremovableInstructor': isShowUnremovableInstructor,
             'desiredTank': desiredVehicleCD}
            self._updateRecruitDataByCrewSkin(tankman, tankmanData)
            tankmenData.append(tankmanData)

        return tankmenData

    def _updateRecruitDataByCrewSkin(self, tankman, tankmanData):
        if tankman.skinID != NO_CREW_SKIN_ID and self.lobbyContext.getServerSettings().isCrewSkinsEnabled():
            skinItem = self.itemsCache.items.getCrewSkin(tankman.skinID)
            tankmanData['iconFile'] = getCrewSkinIconSmall(skinItem.getIconID())
            tankmanData['fullName'] = localizedFullName(skinItem)
            tankmanData['lastName'] = makeString(skinItem.getLastName())

    def _validateCrewConvertion(self, vehicle, crew, isBarracksNotEmpty):
        conversion = settings_globals.g_conversion
        crewDescrs = [ (tankman.descriptor if tankman else None) for _, tankman in crew ]
        validation, validationMask, _ = conversion.validateCrewToConvertIntoDetachment(crewDescrs, vehicle.compactDescr, isBarracksNotEmpty)
        return (validation, validationMask)

    def _getLeaderDetachmentName(self, crew):
        conversion = settings_globals.g_conversion
        for _, tankman in crew:
            if not tankman:
                continue
            leaderPreset = conversion.getDetachmentForTankman(tankman.descriptor)
            if leaderPreset:
                return leaderPreset.name

        return None

    def _playSound(self, soundID):
        SoundGroups.g_instance.playSound2D(self.app.soundManager.sounds.getEffectSound(soundID))
