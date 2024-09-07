# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/crew_tab_helper.py
from collections import namedtuple
import typing
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.crew_constants import CrewConstants
from gui.shared.gui_items.Tankman import Tankman, getBigIconPath, NO_TANKMAN
from helpers.i18n import makeString
from items.tankmen import TankmanDescr, makeTmanDescrByTmanData
from shared_utils import first
from web.web_client_api.common import ItemPackType
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
GIRL_EMPTY = 'girl-empty'

class PreviewTankman(Tankman):
    __slots__ = ('_previewData',)

    def __init__(self, slotIdx, tmanData=None, tankman=None, vehicle=None):
        if tankman is not None:
            strCD = tankman.descriptor.makeCompactDescr()
            self._previewData = {}
        else:
            gid = tmanData.get('gId', -1)
            if 'fnGroupID' not in tmanData:
                tmanData['fnGroupID'] = gid
            if 'lnGroupID' not in tmanData:
                tmanData['lnGroupID'] = gid
            if 'iGroupID' not in tmanData:
                tmanData['iGroupID'] = gid
            self._previewData = tmanData
            strCD = TankmanDescr(compactDescr=makeTmanDescrByTmanData(tmanData)).makeCompactDescr()
        super(PreviewTankman, self).__init__(strCD, vehicleSlotIdx=slotIdx, vehicle=vehicle)
        return

    @property
    def fullUserName(self):
        if self._previewData.get('firstNameID', None) and self._previewData.get('lastNameID', None):
            return super(PreviewTankman, self).fullUserName
        else:
            return backport.text(R.strings.tooltips.awardItem.tankwomen.header()) if self.isFemale else ''

    @property
    def extensionLessIcon(self):
        if self._previewData.get('iconID', None):
            return super(PreviewTankman, self).extensionLessIcon
        else:
            return GIRL_EMPTY if self.isFemale else ''

    @property
    def bigIconPath(self):
        iconID = self._previewData.get('iconID', None)
        if self._previewData.get('iconID', None):
            return getBigIconPath(self.nationID, iconID)
        else:
            return backport.image(R.images.gui.maps.icons.tankmen.icons.big.girl_empty()) if self.isFemale else backport.image(R.images.gui.maps.icons.tankmen.icons.big.empty())

    @property
    def backportSkillList(self):
        result = [ (skill.bigIconPath, skill.userName) for skill in self.skills ]
        if self.descriptor.freeXP > 0:
            newSkills, _ = self.newSkillsCount
            if newSkills:
                img = backport.image(R.images.gui.maps.icons.tankmen.skills.big.preview_new_skill_trained())
                result.extend([(img, TOOLTIPS.VEHICLEPREVIEW_TANKMAN_NEWPERK_HEADER)] * newSkills)
        return result

    @property
    def previewVehicleName(self):
        return self.vehicleNativeDescr.type.userString


def isValidCrewForVehicle(tankmenItems, roles):
    tmenItemsLen = len(tankmenItems)
    if tmenItemsLen == 0 and tmenItemsLen != len(roles):
        return False
    cleanRoles = [ first(role) for role in roles ]
    for tItem in tankmenItems:
        if tItem['role'] not in cleanRoles:
            return False

    tankmenItems.sort(key=lambda i: cleanRoles.index(i['role']))
    for slot, tmanData in enumerate(tankmenItems):
        if cleanRoles[slot] != tmanData['role']:
            return False

    return True


def getCrewPreviewTitle(title, itemCrew):
    if itemCrew and itemCrew.type in (ItemPackType.CREW_50,
     ItemPackType.CREW_75,
     ItemPackType.CREW_100,
     ItemPackType.CUSTOM_CREW_100):
        return makeString(TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_WITHCREW)
    else:
        return title if title is not None else makeString(TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_NOCREW)


def getCustomTitle(skill, role, forOne):
    if skill.name == CrewConstants.NEW_SKILL:
        if forOne:
            tKey = TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_CREW_NEWSKILL_FORONE
        else:
            tKey = TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_CREW_NEWSKILL_FORALL
    elif forOne:
        tKey = TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_CREW_ONESKILL_FORONE
    else:
        tKey = TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_CREW_ONESKILL_FORALL
    return makeString(key=tKey, role=makeString(TOOLTIPS.crewRole(role)) if role != '' else None, skillName=skill.userName)


NEW_SKILL_ICON = 'preview_new_skill_trained'
_SimpleSkill = namedtuple('_SimpleSkill', ('name', 'customName', 'userName', 'extensionLessIconName'))
_SIMPLE_SKILL = _SimpleSkill(CrewConstants.NEW_SKILL, '', CrewConstants.NEW_SKILL, NEW_SKILL_ICON)

def getCustomHeader(customCrew):
    crew = [ tMan for _, tMan in sorted(customCrew) ]
    skills = [ (tMan.skills[:] + [_SIMPLE_SKILL] if tMan.descriptor.freeXP > 0 else tMan.skills[:]) for tMan in crew ]
    notEmptySkills = [ s for s in skills if s ]
    if not notEmptySkills:
        return (makeString(TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_WITHCREW),
         '',
         '',
         '')
    if all((len(s) <= 1 for s in skills)):
        firstSkill = first(notEmptySkills)[0]
        icon = firstSkill.extensionLessIconName
        skillName = firstSkill.name
        customName = firstSkill.customName
        notEmptySkillsLen = len(notEmptySkills)
        if notEmptySkillsLen == 1:
            role = first((tMan.role for tMan in crew if tMan.hasNewSkill)) if firstSkill.name == CrewConstants.NEW_SKILL else first((tMan.role for tMan in crew if tMan.skills))
            return (getCustomTitle(firstSkill, role, True),
             icon,
             skillName,
             customName)
        if notEmptySkillsLen == len(skills) and all((firstSkill.name == s[0].name for s in notEmptySkills)):
            return (getCustomTitle(firstSkill, '', False),
             icon,
             skillName,
             customName)
    return (makeString(TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_CREW_ANYSKILLS),
     '',
     '',
     '')


def getPreviewCrewMemberArgs(isCustom, slotIdx, tankman):
    args = [tankman.role, NO_TANKMAN, slotIdx]
    if isCustom:
        args.extend([tankman.fullUserName,
         tankman.previewVehicleName,
         tankman.bigIconPath,
         '',
         tankman.backportSkillList])
    else:
        args.extend([None,
         None,
         None,
         None,
         None])
    return args
