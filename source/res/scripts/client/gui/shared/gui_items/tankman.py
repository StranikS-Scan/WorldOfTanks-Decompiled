# Embedded file name: scripts/client/gui/shared/gui_items/Tankman.py
from helpers.i18n import convert
from items import tankmen, vehicles, ITEM_TYPE_NAMES
from gui import nationCompareByIndex
from gui.shared.utils.functions import getShortDescr
from gui.shared.gui_items import HasStrCD, GUIItem, ItemsCollection

class TankmenCollection(ItemsCollection):
    """
    Tankmen collection class.
    """

    def _filterItem(self, item, nation = None, role = None, isInTank = None):
        """
        Overriden method to filter collection items.
        
        @param item: item to check fo filtering
        @param nation: nation id to filter
        @param role: tankman role to filter
        @param isInTank: only tankmen in vehicles
        @return: is item match given conditions <bool>
        """
        if role is not None and item.descriptor.role != role:
            return False
        elif isInTank is not None and item.isInTank != isInTank:
            return False
        else:
            return ItemsCollection._filterItem(self, item, nation)


class TankmenComparator(object):

    def __init__(self, vehicleGetter = None):
        self._vehicleGetter = vehicleGetter

    def __call__(self, first, second):
        if first is None or second is None:
            return 1
        else:
            res = nationCompareByIndex(first.nationID, second.nationID)
            if res:
                return res
            if first.isInTank and not second.isInTank:
                return -1
            if not first.isInTank and second.isInTank:
                return 1
            if first.isInTank and second.isInTank:
                if self._vehicleGetter is not None:
                    tman1vehicle = self._vehicleGetter(first.vehicleInvID)
                    tman2vehicle = self._vehicleGetter(second.vehicleInvID)
                    if tman1vehicle is not None and tman2vehicle is not None:
                        res = tman1vehicle.__cmp__(tman2vehicle)
                        if res:
                            return res
                TANKMEN_ROLES_ORDER = Tankman.TANKMEN_ROLES_ORDER
                if TANKMEN_ROLES_ORDER[first.descriptor.role] < TANKMEN_ROLES_ORDER[second.descriptor.role]:
                    return -1
                if TANKMEN_ROLES_ORDER[first.descriptor.role] > TANKMEN_ROLES_ORDER[second.descriptor.role]:
                    return 1
            return cmp(first.lastUserName, second.lastUserName) or 1


class Tankman(GUIItem, HasStrCD):
    ROLE_ICON_PATH_BIG = '../maps/icons/tankmen/roles/big'
    ROLE_ICON_PATH_SMALL = '../maps/icons/tankmen/roles/small'
    RANK_ICON_PATH_BIG = '../maps/icons/tankmen/ranks/big'
    RANK_ICON_PATH_SMALL = '../maps/icons/tankmen/ranks/small'
    PORTRAIT_ICON_PATH_BIG = '../maps/icons/tankmen/icons/big'
    PORTRAIT_ICON_PATH_SMALL = '../maps/icons/tankmen/icons/small'
    PORTRAIT_ICON_PATH_BARRACKS = '../maps/icons/tankmen/icons/barracks'

    class ROLES:
        """ Tankmen vehicle roles constants. """
        COMMANDER = 'commander'
        RADIOMAN = 'radioman'
        DRIVER = 'driver'
        GUNNER = 'gunner'
        LOADER = 'loader'

    TANKMEN_ROLES_ORDER = {ROLES.COMMANDER: 0,
     ROLES.GUNNER: 1,
     ROLES.DRIVER: 2,
     ROLES.RADIOMAN: 3,
     ROLES.LOADER: 4}

    def __init__(self, strCompactDescr, inventoryID = -1, vehicle = None, proxy = None):
        """
        Ctor.
        
        @param strCompactDescr: string compact descriptor
        @param inventoryID: tankman's inventory id
        @param vehicle: tankman's vehicle where it has been seat
        @param proxy: instance of ItemsRequester
        """
        GUIItem.__init__(self, proxy)
        HasStrCD.__init__(self, strCompactDescr)
        self.__descriptor = None
        self.invID = inventoryID
        self.nationID = self.descriptor.nationID
        self.itemTypeID = vehicles._TANKMAN
        self.itemTypeName = ITEM_TYPE_NAMES[self.itemTypeID]
        self.combinedRoles = (self.descriptor.role,)
        self.vehicleNativeDescr = vehicles.VehicleDescr(typeID=(self.nationID, self.descriptor.vehicleTypeID))
        self.vehicleInvID = -1
        self.vehicleDescr = None
        self.vehicleBonuses = dict()
        self.vehicleSlotIdx = -1
        if vehicle is not None:
            self.vehicleInvID = vehicle.invID
            self.vehicleDescr = vehicle.descriptor
            self.vehicleBonuses = dict(vehicle.bonuses)
            self.vehicleSlotIdx = vehicle.crewIndices.get(inventoryID, -1)
            crewRoles = self.vehicleDescr.type.crewRoles
            if -1 < self.vehicleSlotIdx < len(crewRoles):
                self.combinedRoles = crewRoles[self.vehicleSlotIdx]
        self.skills = self._buildSkills(proxy)
        self.skillsMap = self._buildSkillsMap()
        if proxy is not None:
            pass
        self.__cmp__ = TankmenComparator()
        return

    def _buildSkills(self, proxy):
        """
        Returns list of `TankmanSkill` objects build
        according to the tankman's skills.
        """
        return [ TankmanSkill(skill, self, proxy) for skill in self.descriptor.skills ]

    def _buildSkillsMap(self):
        """
        Returns dict of skillName: TankmanSkill objects build
        according to the tankman's skills.
        """
        return dict([ (skill.name, skill) for skill in self.skills ])

    @property
    def realRoleLevel(self):
        """
        Returns real tankman role level calculated with
        bonuses and penalties.
        
        @return: (
                real role level,
                (
                        commander bonus,
                        brotherhood bonus,
                        equipments bonus,
                        optional devices bonus,
                        not native vehicle penalty,
                )
        )
        """
        effRoleLevel = self.efficiencyRoleLevel
        penalty = effRoleLevel - self.roleLevel
        commBonus = self.vehicleBonuses.get('commander', 0)
        if self.descriptor.role == self.ROLES.COMMANDER:
            commBonus = 0
        brothersBonus = self.vehicleBonuses.get('brotherhood', 0)
        eqsBonus = self.vehicleBonuses.get('equipment', 0)
        optDevsBonus = self.vehicleBonuses.get('optDevices', 0)
        realRoleLevel = effRoleLevel + commBonus + brothersBonus + eqsBonus + optDevsBonus
        return (realRoleLevel, (commBonus,
          brothersBonus,
          eqsBonus,
          optDevsBonus,
          penalty))

    @property
    def descriptor(self):
        if self.__descriptor is None or self.__descriptor.dossierCompactDescr != self.strCompactDescr:
            self.__descriptor = tankmen.TankmanDescr(compactDescr=self.strCompactDescr)
        return self.__descriptor

    @property
    def isInTank(self):
        """ Is tankman in vehicle. """
        return self.vehicleDescr is not None

    @property
    def roleLevel(self):
        """ Tankman's role level. """
        return self.descriptor.roleLevel

    @property
    def icon(self):
        """ Tankman's portrait icon filename. """
        return tankmen.getNationConfig(self.nationID)['icons'][self.descriptor.iconID]

    @property
    def iconRank(self):
        """ Tankman's rank icon filepath. """
        return tankmen.getNationConfig(self.nationID)['ranks'][self.descriptor.rankID]['icon']

    @property
    def iconRole(self):
        """ Tankman's role icon filename. """
        return tankmen.getSkillsConfig()[self.descriptor.role]['icon']

    @property
    def firstUserName(self):
        """ Tankman's firstname represented as user-friendly string. """
        return convert(tankmen.getNationConfig(self.nationID)['firstNames'][self.descriptor.firstNameID])

    @property
    def lastUserName(self):
        """ Tankman's lastname represented as user-friendly string. """
        return convert(tankmen.getNationConfig(self.nationID)['lastNames'][self.descriptor.lastNameID])

    @property
    def fullUserName(self):
        """ Tankman's full represented as user-friendly string. """
        return '%s %s' % (self.firstUserName, self.lastUserName)

    @property
    def rankUserName(self):
        """ Tankman's rank represented as user-friendly string. """
        return convert(tankmen.getNationConfig(self.nationID)['ranks'][self.descriptor.rankID]['userString'])

    @property
    def roleUserName(self):
        """ Tankman's role represented as user-friendly string. """
        return convert(tankmen.getSkillsConfig()[self.descriptor.role]['userString'])

    @property
    def hasNewSkill(self):
        return self.roleLevel == tankmen.MAX_SKILL_LEVEL and (self.descriptor.lastSkillLevel == tankmen.MAX_SKILL_LEVEL or not len(self.skills))

    @property
    def newSkillCount(self):
        """
        Returns number of skills to study and last new skill level.
        
        @return: ( number of new skills, last new skill level )
        """
        if self.hasNewSkill:
            tmanDescr = tankmen.TankmanDescr(self.strCD)
            i = 0
            skills_list = list(tankmen.ACTIVE_SKILLS)
            while tmanDescr.roleLevel == 100 and (tmanDescr.lastSkillLevel == 100 or len(tmanDescr.skills) == 0) and len(skills_list) > 0:
                skillname = skills_list.pop()
                if skillname not in tmanDescr.skills:
                    tmanDescr.addSkill(skillname)
                    i += 1

            return (i, tmanDescr.lastSkillLevel)
        return (0, 0)

    @property
    def efficiencyRoleLevel(self):
        """
        Returns tankman's role level on current vehicle.
        """
        factor, addition = (1, 0)
        if self.isInTank:
            factor, addition = self.descriptor.efficiencyOnVehicle(self.vehicleDescr)
        return round(self.roleLevel * factor)

    @property
    def vehicleNativeType(self):
        for tag in vehicles.VEHICLE_CLASS_TAGS.intersection(self.vehicleNativeDescr.type.tags):
            return tag

    def __cmp__(self, other):
        if other is None:
            return -1
        res = nationCompareByIndex(self.nationID, other.nationID)
        if res:
            return res
        elif self.isInTank and not other.isInTank:
            return -1
        elif not self.isInTank and other.isInTank:
            return 1
        if self.isInTank and other.isInTank:
            if self.vehicleInvID != other.vehicleInvID:
                return -1
            res = self.TANKMEN_ROLES_ORDER[self.descriptor.role] - self.TANKMEN_ROLES_ORDER[other.descriptor.role]
            if res:
                return res
        if self.lastUserName < other.lastUserName:
            return -1
        elif self.lastUserName > other.lastUserName:
            return 1
        else:
            return 0

    def __eq__(self, other):
        if other is None or not isinstance(other, Tankman):
            return False
        else:
            return self.invID == other.invID

    def __repr__(self):
        return 'Tankman<id:%d, nation:%d, vehicleID:%d>' % (self.invID, self.nationID, self.vehicleInvID)


class TankmanSkill(GUIItem):
    """
    Tankman's skill class.
    """
    ICON_PATH_BIG = '../maps/icons/tankmen/skills/big'
    ICON_PATH_SMALL = '../maps/icons/tankmen/skills/small'

    def __init__(self, skillName, tankman = None, proxy = None):
        super(TankmanSkill, self).__init__(proxy)
        self.name = skillName
        self.isPerk = self.name in tankmen.PERKS
        self.level = 0
        self.type = self.__getSkillType()
        self.roleType = None
        self.isActive = False
        self.isEnable = False
        if tankman is not None:
            tdescr = tankman.descriptor
            self.level = tdescr.lastSkillLevel if tdescr.skills.index(self.name) == len(tdescr.skills) - 1 else tankmen.MAX_SKILL_LEVEL
            self.roleType = self.__getSkillRoleType(skillName)
            self.isActive = self.__getSkillActivity(tankman)
            self.isEnable = self.__getEnabledSkill(tankman)
        return

    def __getEnabledSkill(self, tankman):
        for role in tankman.combinedRoles:
            roleSkills = tankmen.SKILLS_BY_ROLES.get(role, tuple())
            if self.name in roleSkills:
                return True

        return False

    def __getSkillRoleType(self, skillName):
        if skillName in tankmen.COMMON_SKILLS:
            return 'common'
        else:
            for role, skills in tankmen.SKILLS_BY_ROLES.iteritems():
                if skillName in skills:
                    return role

            return None

    def __getSkillActivity(self, tankman):
        """
        Returns skill activity. Skill is active in following cases:
         1. skill is not perk;
         2. skill is `brotherhood` skill and it is active on tankman's vehicle;
         3. skill is onot `brotherhood` and it is researched to max.
        """
        if tankman is None:
            return True
        else:
            isBrotherhood = tankman.vehicleBonuses.get('brotherhood', 0) > 0
            return not self.isPerk or self.name == 'brotherhood' and isBrotherhood or self.name != 'brotherhood' and self.level == tankmen.MAX_SKILL_LEVEL

    def __getSkillType(self):
        if self.isPerk:
            if self.name == 'brotherhood':
                return 'perk_common'
            else:
                return 'perk'
        return 'skill'

    @property
    def userName(self):
        """ Returns skill name represented as user-friendly string. """
        return tankmen.getSkillsConfig()[self.name]['userString']

    @property
    def description(self):
        """ Returns skill description represented as user-friendly string. """
        return convert(tankmen.getSkillsConfig()[self.name]['description'])

    @property
    def shortDescription(self):
        """ Returns skill short description represented as user-friendly string. """
        return getShortDescr(self.description)

    @property
    def icon(self):
        """ Returns skill icon filename. """
        return convert(tankmen.getSkillsConfig()[self.name]['icon'])

    def __repr__(self):
        return 'TankmanSkill<name:%s, level:%d, isActive:%s>' % (self.name, self.level, str(self.isActive))
