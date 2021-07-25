# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/instructor.py
import typing
from itertools import izip
from crew2.instructor.professions import InstructorProfessions
from debug_utils import LOG_WARNING
from helpers import dependency
from frameworks import wulf
from gui.shared.gui_items.gui_item import GUIItem, HasStrCD
from crew2 import settings_globals
from crew2.crew2_consts import BOOL_TO_GENDER, GENDER
from gui.impl import backport
from gui.impl.gen import R
from items import ITEM_TYPE_NAMES
from items.components.detachment_constants import DetachmentSlotType, NO_DETACHMENT_ID, NO_INSTRUCTOR_ID
from items.instructor import InstructorDescr
from skeletons.gui.lobby_context import ILobbyContext
import nations
from gui.shared.gui_items import GUI_ITEM_TYPE
from skeletons.gui.detachment import IDetachementStates, IDetachmentCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.impl.gen_utils import DynAccessor
_GENDER_TO_PORTRAIT_MAP = {GENDER.MALE: 'siluet_man',
 GENDER.FEMALE: 'siluet_woman'}

class Instructor(GUIItem):
    __slots__ = ('__descriptor', '_detInvID', '_invID', '_excludedExpData', '_itemTypeID', '_itemTypeName')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __detachmentsStates = dependency.descriptor(IDetachementStates)
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, strCompactDescr, proxy=None, invID=NO_INSTRUCTOR_ID, detInvID=NO_DETACHMENT_ID):
        super(Instructor, self).__init__(strCD=HasStrCD(strCompactDescr))
        self.__descriptor = None
        self._detInvID = detInvID
        self._invID = invID
        self._itemTypeID = GUI_ITEM_TYPE.INSTRUCTOR
        self._itemTypeName = ITEM_TYPE_NAMES[self.itemTypeID]
        self._excludedExpData = self.__detachmentsStates.states.getExcludedInstructorExpDate(invID)
        return

    def __cmp__(self, other):
        return cmp(self.invID, other.invID)

    def __repr__(self):
        return '{}(invID={}, detInvID={})'.format(self.__class__.__name__, self.invID, self.detInvID)

    @property
    def descriptor(self):
        if self.__descriptor is None:
            self.__descriptor = InstructorDescr.createByCompDescr(self.strCD)
        return self.__descriptor

    @property
    def detInvID(self):
        return self._detInvID

    @property
    def invID(self):
        return self._invID

    @property
    def excludedExpData(self):
        return self._excludedExpData

    @property
    def isExcluded(self):
        expDate = self._excludedExpData
        return expDate is not None

    @property
    def nationID(self):
        return self.descriptor.nationID

    @property
    def itemTypeID(self):
        return self._itemTypeID

    @property
    def itemTypeName(self):
        return self._itemTypeName

    @property
    def nationName(self):
        return nations.MAP.get(self.descriptor.nationID, '')

    def getAvailableNationIDs(self):
        iSettings = settings_globals.g_instructorSettingsProvider.getInstructorByID(self.descriptor.settingsID)
        return iSettings.getAvailableNations()

    @property
    def gender(self):
        return BOOL_TO_GENDER[self.descriptor.isFemale]

    @property
    def voiceOverID(self):
        return self.descriptor.voiceOverID

    @property
    def pageBackground(self):
        return self.descriptor.pageBackground

    def getPortraitName(self):
        if self.isToken():
            iSettingsID = self.descriptor.settingsID
            iSettings = settings_globals.g_instructorSettingsProvider.getInstructorByID(iSettingsID)
            portrait = iSettings.token.portrait if iSettings.token is not None else None
        else:
            portrait = settings_globals.g_characterProperties.getPortraitByID(self.nationID, self.descriptor.portraitID, gender=self.gender)
        if portrait is None:
            portrait = _GENDER_TO_PORTRAIT_MAP[self.gender]
        return portrait

    @property
    def portrait(self):
        return settings_globals.g_characterProperties.getPortraitByID(self.nationID, self.descriptor.portraitID, self.gender)

    def getPortraitDynAccessor(self, dynAccessor=None):
        pName = self.getPortraitName()
        if dynAccessor is not None:
            pAccessor = dynAccessor.dyn(pName)
            if pAccessor.isValid():
                return pAccessor
            portrait = _GENDER_TO_PORTRAIT_MAP[self.gender]
            pAccessor = dynAccessor.dyn(portrait)
            if pAccessor.isValid():
                LOG_WARNING('Instructor icon "{}" not found'.format(pName))
                return pAccessor
        LOG_WARNING('Instructor icon "{}" not found'.format(pName))
        return R.images.gui.maps.icons.instructors.c_290x300.siluet_man if self.gender == GENDER.MALE else R.images.gui.maps.icons.instructors.c_290x300.siluet_woman

    def getPortraitResID(self, dynAccessor=None):
        pAccessor = self.getPortraitDynAccessor(dynAccessor=dynAccessor)
        return pAccessor()

    def getFirstName(self, nationID=None, firstNameID=None):
        if nationID is None:
            nationID = self.nationID
        if firstNameID is None:
            firstNameID = self.descriptor.firstNameID
        gender = self.gender
        firstNameKey = settings_globals.g_characterProperties.getFirstNameByID(nationID, firstNameID, gender)
        return backport.textRes(firstNameKey)()

    @property
    def firstName(self):
        return self.getFirstName()

    def getSecondName(self, nationID=None, secondNameID=None):
        if nationID is None:
            nationID = self.nationID
        if secondNameID is None:
            secondNameID = self.descriptor.secondNameID
        gender = self.gender
        fullSecondName = settings_globals.g_characterProperties.getSecondNameByID(nationID, secondNameID, gender)
        return None if not wulf.getTranslatedText(fullSecondName) else backport.textRes(fullSecondName)()

    @property
    def secondName(self):
        return self.getSecondName()

    def getFullName(self):
        if self.descriptor.firstNameID > 0 and self.descriptor.secondNameID > 0:
            return ' '.join((name for name in map(backport.text, (self.getFirstName(), self.getSecondName())) if name))
        celebrityTokenName = self.getCelebrityTokenName()
        return celebrityTokenName if celebrityTokenName else ''

    @property
    def fullName(self):
        return self.getFullName()

    @property
    def classID(self):
        return self.descriptor.classID

    @property
    def bonusClass(self):
        bonusClass = settings_globals.g_instructorSettingsProvider.classes.getClassByID(self.classID)
        return bonusClass

    @property
    def xpBonus(self):
        return self.bonusClass.xpBonus

    def isToken(self):
        return self.descriptor.isToken()

    @property
    def perksIDs(self):
        return self.descriptor.perksIDs

    @property
    def bonusPerks(self):
        return dict(izip(self.perksIDs, self.bonusClass.perkPoints)) if self.perksIDs is not None else {}

    @property
    def bonusPerksList(self):
        return zip(self.perksIDs, self.bonusClass.perkPoints, (0,) * len(self.perksIDs)) if self.perksIDs is not None else []

    @property
    def bonusPerksOvercap(self):
        return dict(izip(self.perksIDs, self.bonusClass.overcapPoints)) if self.perksIDs is not None else {}

    def getInstructorSettings(self):
        return self.descriptor.getInstructorSettings()

    def getCelebrityTokenName(self):
        isp = settings_globals.g_instructorSettingsProvider
        iSettings = isp.getInstructorByID(self.descriptor.settingsID)
        if iSettings.token is None or iSettings.token.nameFromNationID is None:
            return
        else:
            nameFromNationID = iSettings.token.nameFromNationID
            fID, sID, _pID = iSettings.getCharacterProperties(nameFromNationID)
            firstName = self.getFirstName(nationID=nameFromNationID, firstNameID=fID)
            secondName = self.getSecondName(nationID=nameFromNationID, secondNameID=sID)
            return ' '.join((name for name in map(backport.text, (firstName, secondName)) if name))

    def getTokenName(self):
        isp = settings_globals.g_instructorSettingsProvider
        iSettings = isp.getInstructorByID(self.descriptor.settingsID)
        if iSettings.token is None:
            return ''
        else:
            key = iSettings.token.name
            return backport.textRes(key)()

    def getTokenPortrait(self):
        return self.getInstructorSettings().token.portrait

    def getDescription(self):
        descrKey = self.getInstructorSettings().description
        return None if descrKey is None else backport.textRes(descrKey)()

    @property
    def isUnremovable(self):
        detachment = self.__detachmentCache.getDetachment(self.detInvID)
        return detachment.getDescriptor().isValueInSlotsLocked(DetachmentSlotType.INSTRUCTORS, self.invID) if detachment is not None else False

    def getTrait(self):
        res = R.strings.detachment.instructorCard.professions
        return res.dyn(InstructorProfessions.getProfessionNameByID(self.descriptor.professionID))()

    def getPerksInfluence(self, bonusPerks=None):
        detachment = self.__detachmentCache.getDetachment(self.detInvID)
        return detachment.getPerksInstructorByIDInfluence(self.invID, bonusPerks) if detachment else self.bonusPerksList
