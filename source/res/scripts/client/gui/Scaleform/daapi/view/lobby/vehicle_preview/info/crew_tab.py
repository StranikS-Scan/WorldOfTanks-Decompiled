# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/crew_tab.py
from collections import namedtuple
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.view.lobby.vehicle_preview.items_kit_helper import OFFER_CHANGED_EVENT
from gui.Scaleform.daapi.view.meta.VehiclePreviewCrewTabMeta import VehiclePreviewCrewTabMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.RES_COMMON import RES_COMMON
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.MENU import MENU
from gui.shared import g_eventBus
from gui.impl.gen import R
from gui.impl import backport
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Tankman import SabatonTankmanSkill, OffspringTankmanSkill, YhaTankmanSkill, BROTHERHOOD_SKILL_NAME, NO_TANKMAN, WitchesTankmanSkill, getTankmanSkill
from gui.shared.gui_items.Tankman import getFullUserName, getSmallIconPath, getBigIconPath
from gui.shared.gui_items.Vehicle import sortCrew
from helpers.i18n import makeString as _ms
from items import tankmen, vehicles
from shared_utils import first
from soft_exception import SoftException
from web.web_client_api.common import ItemPackType, ItemPackTypeGroup
NEW_SKILL_ICON = '../maps/icons/tankmen/skills/big/preview_new_skill.png'
_SimpleSkill = namedtuple('_SimpleSkill', ('name', 'customName', 'userName', 'bigIconPath', 'isPerk'))
_SimpleSkill.__new__.__defaults__ = ('new',
 '',
 'new',
 NEW_SKILL_ICON,
 False)

def _createPreviewTankman(slotIdx, tmanData=None):
    return PreviewTankman(slotIdx, tmanData) if tmanData else None


class PreviewTankman(object):
    _TANKWOMAN_ICON_FORMAT_STRING = '../maps/icons/tankmen/icons/{}/girl-empty.png'

    def __init__(self, slotIdx, tmanData):
        self.slotIdx = slotIdx
        self.firstNameID = tmanData.get('firstNameID', None)
        self.lastNameID = tmanData.get('lastNameID', None)
        self.iconID = tmanData.get('iconID', None)
        self.isPremium = tmanData.get('isPremium', False)
        self.role = tmanData.get('role', '')
        self.nationID = tmanData.get('nationID', None)
        self.roleLevel = tmanData.get('roleLevel', 100)
        self.freeXP = tmanData.get('freeXP', None)
        self.isFemale = tmanData.get('isFemale', False)
        self.vehicleTypeID = tmanData.get('vehicleTypeID', None)
        self.gid = tmanData.get('gId', -1)
        if 'fnGroupID' not in tmanData:
            tmanData['fnGroupID'] = self.gid
        if 'lnGroupID' not in tmanData:
            tmanData['lnGroupID'] = self.gid
        if 'iGroupID' not in tmanData:
            tmanData['iGroupID'] = self.gid
        self.descriptor = tankmen.TankmanDescr(compactDescr=tankmen.makeTmanDescrByTmanData(tmanData))
        skills = tmanData.get('skills', []) + tmanData.get('freeSkills', [])
        self.skills = self._buildSkills(skills)
        return

    @property
    def fullUserName(self):
        if self.firstNameID and self.lastNameID:
            return getFullUserName(self.nationID, self.firstNameID, self.lastNameID)
        return TOOLTIPS.AWARDITEM_TANKWOMEN_HEADER if self.isFemale else ITEM_TYPES.tankman_roles(self.role)

    @property
    def vehicleName(self):
        return vehicles.g_cache.vehicle(self.nationID, self.vehicleTypeID).userString if self.vehicleTypeID else ''

    @property
    def icon(self):
        if self.iconID:
            return getSmallIconPath(self.nationID, self.iconID)
        return self._TANKWOMAN_ICON_FORMAT_STRING.format('small') if self.isFemale else RES_ICONS.getItemBonus42x42(self.role)

    @property
    def bigIcon(self):
        if self.iconID:
            return getBigIconPath(self.nationID, self.iconID)
        return self._TANKWOMAN_ICON_FORMAT_STRING.format('big') if self.isFemale else ''

    @property
    def tooltip(self):
        return TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_CREW_MEMBER

    @property
    def hasNewSkill(self):
        return self.freeXP > 0

    def getVO(self, showTankmanSkills=True):
        skillsList = []
        for idx, skill in enumerate(self.skills):
            skillsList.append({'tankmanID': 1,
             'id': str(idx),
             'name': skill.userName,
             'desc': skill.description,
             'icon': skill.icon,
             'level': tankmen.MAX_SKILL_LEVEL,
             'active': True})

        if self.hasNewSkill:
            skillsList.append({'buy': True,
             'buyCount': 0,
             'tankmanID': 1,
             'level': tankmen.MAX_SKILL_LEVEL})
        tankmanVO = {'icon': self.icon,
         'name': self.fullUserName,
         'tooltip': self.tooltip,
         'role': self.role}
        if showTankmanSkills and skillsList:
            tankmanVO.update({'tankman': {'skills': skillsList,
                         'lastSkillLevel': tankmen.MAX_SKILL_LEVEL}})
        return tankmanVO

    def getTooltipVO(self):
        skillsItems = [ (skill.bigIconPath, skill.userName, False) for skill in self.skills ]
        if self.hasNewSkill:
            skillsItems.append((NEW_SKILL_ICON, TOOLTIPS.VEHICLEPREVIEW_TANKMAN_NEWPERK_HEADER, True))
        return (self.role,
         NO_TANKMAN,
         self.slotIdx,
         self.fullUserName,
         self.vehicleName,
         self.bigIcon,
         '',
         skillsItems)

    def roles(self):
        return (self.role,)

    def _buildSkills(self, skills):
        return [ getTankmanSkill(skill, self, proxy=(0,)) for skill in skills ]


class VehiclePreviewCrewTab(VehiclePreviewCrewTabMeta):

    def __init__(self):
        super(VehiclePreviewCrewTab, self).__init__()
        self.__crewItems = ()
        self.__vehicleItems = ()
        self.__customCrew = None
        self.__crewStr = None
        return

    def setActiveState(self, isActive):
        pass

    def setVehicleCrews(self, vehicleItems, crewItems):
        self.__vehicleItems = vehicleItems
        self.__crewItems = crewItems
        self._update()

    def setCrewText(self, crewStr):
        self.__crewStr = crewStr
        self._update()

    def getTooltipData(self, crewId, slotIdx):
        if self.__customCrew:
            for idx, tman in self.__customCrew:
                if idx == crewId:
                    return tman.getTooltipVO()

        return [tankmen.SKILL_NAMES[crewId],
         NO_TANKMAN,
         slotIdx,
         None,
         None,
         None,
         None,
         None]

    def update(self, *args):
        if g_currentPreviewVehicle.isPresent():
            self._update()

    def _populate(self):
        super(VehiclePreviewCrewTab, self)._populate()
        g_currentPreviewVehicle.onComponentInstalled += self.update
        g_currentPreviewVehicle.onChanged += self.update
        g_eventBus.addListener(OFFER_CHANGED_EVENT, self.__onOfferChanged)
        self.update()

    def _dispose(self):
        g_eventBus.removeListener(OFFER_CHANGED_EVENT, self.__onOfferChanged)
        g_currentPreviewVehicle.onChanged -= self.update
        g_currentPreviewVehicle.onComponentInstalled -= self.update
        super(VehiclePreviewCrewTab, self)._dispose()

    def _update(self):
        currentVehicle = g_currentPreviewVehicle.item
        if self.__crewStr is not None:
            vehicleCrewComment = self.__crewStr
        else:
            vehicleCrewComment = backport.text(R.strings.tooltips.vehiclePreview.vehiclePanel.info.header.noCrew())
        skillIcon = ''
        skillName = ''
        customName = ''
        gID = None
        regularCrewList = []
        uniqueCrewList = []
        isLockedCrew = False
        if self.__vehicleItems is not None and self.__crewItems is not None:
            for item in self.__vehicleItems:
                if item.id == currentVehicle.intCD:
                    gID = item.groupID
                    break

            if gID is not None:
                crewItems = sorted([ item for item in self.__crewItems if item.groupID == gID ], key=lambda i: ItemPackTypeGroup.CREW.index(i.type), reverse=True)
                topCrewItem = crewItems[0] if crewItems else None
                if topCrewItem and topCrewItem.type == ItemPackType.CREW_CUSTOM:
                    isLockedCrew = (topCrewItem.extra or False) and topCrewItem.extra.get('isLockedCrew', False)
                self.__setCustomCrew(topCrewItem, currentVehicle)
                vehicleCrewComment, skillIcon, skillName, customName = self.__getCrewCommentAndIcon(topCrewItem)
                regularCrewList, uniqueCrewList = self.__getCrewData(currentVehicle, not bool(skillIcon))
        self.as_setDataS({'vehicleCrewComment': text_styles.middleTitle(vehicleCrewComment) if vehicleCrewComment else '',
         'regularCrewList': regularCrewList,
         'uniqueCrewList': uniqueCrewList,
         'skillIcon': skillIcon,
         'skillName': skillName,
         'skillCustomisation': customName,
         'lockedCrew': isLockedCrew})
        return

    def _getCustomCrewComment(self):
        crew = [ tMan for _, tMan in sorted(self.__customCrew) ]
        skills = [ (tMan.skills[:] + [_SimpleSkill()] if tMan.hasNewSkill else tMan.skills[:]) for tMan in crew ]
        notEmptySkills = [ s for s in skills if s ]
        if not notEmptySkills:
            return (_ms(TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_WITHCREW),
             '',
             '',
             '')
        if all((len(s) <= 1 for s in skills)):
            firstSkill = first(notEmptySkills)[0]
            icon = firstSkill.bigIconPath
            skillName = firstSkill.name if not firstSkill.name == 'new' else ''
            customName = firstSkill.customName
            notEmptySkillsLen = len(notEmptySkills)
            if notEmptySkillsLen == 1:
                role = first((tMan.role for tMan in crew if tMan.hasNewSkill)) if firstSkill.name == 'new' else first((tMan.role for tMan in crew if tMan.skills))
                return (getCrewComment(firstSkill, role, True),
                 icon,
                 skillName,
                 customName)
            if notEmptySkillsLen == len(skills) and all((firstSkill.name == s[0].name for s in notEmptySkills)):
                return (getCrewComment(firstSkill, '', False),
                 icon,
                 skillName,
                 customName)
        return (_ms(TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_CREW_ANYSKILLS),
         '',
         '',
         '')

    def __onOfferChanged(self, event):
        ctx = event.ctx
        self.setVehicleCrews(ctx.get('vehicleItems'), ctx.get('crewItems'))

    def __setCustomCrew(self, topCrewItem, vehicle):
        if topCrewItem and topCrewItem.extra and topCrewItem.type == ItemPackType.CREW_CUSTOM:
            roles = vehicle.descriptor.type.crewRoles
            tmenItems = topCrewItem.extra.get('tankmen', [])
            if not isValidCrewForVehicle(tmenItems, roles):
                raise SoftException('Invalid crew preset for this vehicle')
            crew = [ (idx, _createPreviewTankman(idx, tmanData)) for idx, tmanData in enumerate(tmenItems) ]
            self.__customCrew = sortCrew(crew, roles)
        else:
            self.__customCrew = None
        return

    def __getCrewData(self, currentVehicle, showTankmanSkills):
        regularCrewList, uniqueCrewList = [], []
        if currentVehicle:
            uniqueCrewList.extend(getUniqueMembers(currentVehicle))
        if self.__customCrew:
            for idx, tankman in self.__customCrew:
                tankmanData = tankman.getVO(showTankmanSkills)
                tankmanData.update({'crewId': idx})
                if tankman.iconID or tankman.isFemale:
                    uniqueCrewList.append(tankmanData)
                regularCrewList.append(tankmanData)

        else:
            for idx, tankman in currentVehicle.crew:
                role = tankman.descriptor.role
                roleIdx = tankmen.SKILL_INDICES[role]
                regularCrewList.append({'slotIdx': idx,
                 'crewId': roleIdx,
                 'icon': RES_ICONS.getItemBonus42x42(role),
                 'name': ITEM_TYPES.tankman_roles(role),
                 'tooltip': TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_CREW_MEMBER,
                 'role': role})

        return (regularCrewList, uniqueCrewList)

    def __getCrewCommentAndIcon(self, itemCrew):
        if self.__customCrew:
            return self._getCustomCrewComment()
        elif itemCrew and itemCrew.type in (ItemPackType.CREW_50,
         ItemPackType.CREW_75,
         ItemPackType.CREW_100,
         ItemPackType.CUSTOM_CREW_100):
            return (_ms(TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_WITHCREW),
             '',
             '',
             '')
        else:
            return (self.__crewStr,
             '',
             '',
             '') if self.__crewStr is not None else (_ms(TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_NOCREW),
             '',
             '',
             '')


def getCrewComment(skill, role, forOne):
    if skill.name == 'new':
        if forOne:
            tKey = TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_CREW_NEWSKILL_FORONE
        else:
            tKey = TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_CREW_NEWSKILL_FORALL
    elif forOne:
        tKey = TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_CREW_ONESKILL_FORONE
    else:
        tKey = TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_CREW_ONESKILL_FORALL
    return _ms(key=tKey, role=_ms(TOOLTIPS.crewRole(role)) if role != '' else None, skillType=_ms(TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_CREW_ISABILLITY), skillName=text_styles.statusAttention(_ms(MENU.QUOTE, string=skill.userName)))


def _isSabatonBrotherhood(skill):
    return isinstance(skill, SabatonTankmanSkill) and skill.name == BROTHERHOOD_SKILL_NAME


def _isOffspringBrotherhood(skill):
    return isinstance(skill, OffspringTankmanSkill) and skill.name == BROTHERHOOD_SKILL_NAME


def _isYhaBrotherhood(skill):
    return isinstance(skill, YhaTankmanSkill) and skill.name == BROTHERHOOD_SKILL_NAME


def _isWitchesBrotherhood(skill):
    return isinstance(skill, WitchesTankmanSkill) and skill.name == BROTHERHOOD_SKILL_NAME


def getUniqueMembers(vehicle):
    uniqueMembers = []
    if 'dog' in vehicle.tags:
        uniqueMembers.append({'crewId': -1,
         'icon': RES_COMMON.MAPS_ICONS_TANKMEN_ICONS_SMALL_USSR_DOG_1,
         'name': backport.text(R.strings.menu.hangar.crew.rody.dog.dyn(vehicle.nationName).name()),
         'tooltip': TOOLTIPS.HANGAR_CREW_RUDY_DOG + vehicle.nationName,
         'role': ''})
    return uniqueMembers


def isValidCrewForVehicle(tmenItems, roles):
    tmenItemsLen = len(tmenItems)
    if tmenItemsLen <= 0 and tmenItemsLen != len(roles):
        return False
    cleanRoles = [ first(role) for role in roles ]
    for tItem in tmenItems:
        if tItem['role'] not in cleanRoles:
            return False

    tmenItems.sort(key=lambda i: cleanRoles.index(i['role']))
    firstRoleLvl = first(tmenItems).get('roleLevel', [])
    for slot, tmanData in enumerate(tmenItems):
        if cleanRoles[slot] != tmanData['role'] or firstRoleLvl != tmanData.get('roleLevel', []):
            return False

    return True
