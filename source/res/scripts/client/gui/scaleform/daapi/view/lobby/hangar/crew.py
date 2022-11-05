# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/Crew.py
from CurrentVehicle import g_currentVehicle
from gui import SystemMessages
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import events, event_dispatcher as shared_events
from gui.shared.events import LoadViewEvent
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.gui_items.Tankman import Tankman, getCrewSkinIconSmallWithoutPath, getRoleBigIconPath
from gui.shared.gui_items.processors.tankman import TankmanUnload, TankmanEquip
from gui.shared.SoundEffectsId import SoundEffectsId
from gui.shared.utils import decorators
from gui.impl.gen import R
from gui.impl import backport
import SoundGroups
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.CrewMeta import CrewMeta
from gui.Scaleform.Waiting import Waiting
from helpers import dependency
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from items.tankmen import getSkillsConfig, compareMastery
from helpers.i18n import convert, makeString
from gui.ClientUpdateManager import g_clientUpdateManager
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext

class Crew(CrewMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.instance(ILobbyContext)

    def __init__(self):
        super(Crew, self).__init__()
        self.dogSound = None
        self._showRecruit = True
        return

    def _populate(self):
        super(Crew, self)._populate()
        g_clientUpdateManager.addCallbacks({'inventory': self.onInventoryUpdate})

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(Crew, self)._dispose()

    def onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.TANKMAN in invDiff:
            self.updateTankmen(invDiff)
        if GUI_ITEM_TYPE.CREW_SKINS in invDiff:
            self.updateTankmen(invDiff)

    def updateTankmen(self, diff=None):
        Waiting.show('updateTankmen')
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            allTankmen = self.itemsCache.items.getTankmen()
            commander_bonus = vehicle.bonuses['commander']
            roles = []
            lessMastered = 0
            tankmenDescrs = dict(vehicle.crew)
            skillsConfig = getSkillsConfig()
            for slotIdx, tman in vehicle.crew:
                if slotIdx > 0 and tman is not None and (tankmenDescrs[lessMastered] is None or compareMastery(tankmenDescrs[lessMastered].descriptor, tman.descriptor) > 0):
                    lessMastered = slotIdx
                role = vehicle.descriptor.type.crewRoles[slotIdx][0]
                roles.append({'tankmanID': tman.invID if tman is not None else None,
                 'roleType': role,
                 'role': convert(skillsConfig.getSkill(role).userString),
                 'roleIcon': getRoleBigIconPath(role),
                 'nationID': vehicle.nationID,
                 'typeID': vehicle.innationID,
                 'slot': slotIdx,
                 'vehicleType': vehicle.shortUserName,
                 'tankType': vehicle.type,
                 'vehicleElite': vehicle.isPremium or vehicle.isPremiumIGR})

            tankmenData = []
            for tankman in allTankmen.itervalues():
                if tankman.isInTank and tankman.vehicleInvID != vehicle.invID:
                    continue
                tankmanVehicle = self.itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
                bonus_role_level = commander_bonus if tankman.descriptor.role != 'commander' else 0.0
                skills_count = skillsConfig.getNumberOfActiveSkills()
                skillsList = []
                for skill in tankman.skills:
                    skillsList.append({'tankmanID': tankman.invID,
                     'id': str(tankman.skills.index(skill)),
                     'name': skill.userName,
                     'desc': skill.description,
                     'icon': skill.icon,
                     'level': skill.level,
                     'active': skill.isEnable and skill.isActive})

                newFreeSkillsCount = tankman.newFreeSkillsCount
                newSkillsCount, lastNewSkillLvl = tankman.newSkillCount
                if newSkillsCount > 0 or newFreeSkillsCount > 0:
                    skillsList.append({'buy': True,
                     'buyFreeCount': newFreeSkillsCount,
                     'buyCount': max(newSkillsCount - 1, 0),
                     'tankmanID': tankman.invID,
                     'level': lastNewSkillLvl})
                tankmanData = {'fullName': tankman.fullUserName,
                 'lastName': tankman.lastUserName or tankman.firstUserName,
                 'rank': tankman.rankUserName,
                 'specializationLevel': tankman.realRoleLevel[0],
                 'role': tankman.roleUserName,
                 'vehicleType': tankmanVehicle.shortUserName,
                 'iconFile': tankman.icon,
                 'rankIconFile': tankman.iconRank,
                 'contourIconFile': tankmanVehicle.iconContour,
                 'tankmanID': tankman.invID,
                 'nationID': tankman.nationID,
                 'typeID': tankmanVehicle.innationID,
                 'inTank': tankman.isInTank,
                 'roleType': tankman.descriptor.role,
                 'tankType': tankmanVehicle.type,
                 'efficiencyLevel': tankman.efficiencyRoleLevel,
                 'bonus': bonus_role_level,
                 'lastSkillLevel': tankman.descriptor.lastSkillLevel,
                 'isLessMastered': vehicle.crewIndices.get(tankman.invID) == lessMastered and vehicle.isXPToTman,
                 'compact': tankman.strCD,
                 'availableSkillsCount': skills_count,
                 'skills': skillsList,
                 'roles': tankman.roles(),
                 'hasCommanderFeature': tankman.role == Tankman.ROLES.COMMANDER}
                self.__updateTankmanDataByCrewSkin(tankman, tankmanData)
                tankmenData.append(tankmanData)

            self.as_tankmenResponseS({'showRecruit': self._showRecruit,
             'roles': roles,
             'tankmen': tankmenData})
            dogName = ''
            if 'dog' in self.itemsCache.items.getItemByCD(g_currentVehicle.item.intCD).tags:
                dogName = backport.text(R.strings.menu.hangar.crew.rody.dog.dyn(vehicle.nationName).name())
            self.as_dogResponseS(dogName)
            tooltipId = TOOLTIPS.HANGAR_CREW_RUDY_DOG + vehicle.nationName
            self.as_setDogTooltipS(tooltipId)
        Waiting.hide('updateTankmen')
        return

    def __updateTankmanDataByCrewSkin(self, tankman, tankmanData):
        if tankman.skinID != NO_CREW_SKIN_ID and self.lobbyContext.getServerSettings().isCrewSkinsEnabled():
            skinItem = self.itemsCache.items.getCrewSkin(tankman.skinID)
            tankmanData['iconFile'] = getCrewSkinIconSmallWithoutPath(skinItem.getIconID())
            tankmanData['fullName'] = localizedFullName(skinItem)
            tankmanData['lastName'] = makeString(skinItem.getLastName())

    def onShowRecruitWindowClick(self, rendererData, menuEnabled):
        self.fireEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.RECRUIT_WINDOW), ctx={'data': rendererData.clone(),
         'menuEnabled': menuEnabled,
         'currentVehicleId': g_currentVehicle.invID}))

    def onCrewDogMoreInfoClick(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.CREW_ABOUT_DOG_WINDOW)), EVENT_BUS_SCOPE.LOBBY)

    def onCrewDogItemClick(self):
        self.__playSound(SoundEffectsId.RUDY_DOG)

    def afterPlayingDogSound(self, *args):
        self.dogSound = None
        return

    def __playSound(self, soundID):
        SoundGroups.g_instance.playSound2D(self.app.soundManager.sounds.getEffectSound(soundID))

    @decorators.adisp_process('equipping')
    def equipTankman(self, tmanInvID, slot):
        tankman = self.itemsCache.items.getTankman(int(tmanInvID))
        result = yield TankmanEquip(tankman, g_currentVehicle.item, int(slot)).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def unloadAllTankman(self):
        self.unloadCrew()

    @staticmethod
    @decorators.adisp_process('unloading')
    def unloadCrew():
        result = yield TankmanUnload(g_currentVehicle.item).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def openPersonalCase(self, value, tabID):
        shared_events.showPersonalCase(int(value), tabID, EVENT_BUS_SCOPE.LOBBY)
