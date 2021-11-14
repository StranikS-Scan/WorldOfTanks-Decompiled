# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/tankman_tooltip_adapters.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.tooltips.contexts import NotRecruitedTankmanContext
from helpers.i18n import makeString
_IMG_PATH = R.images.gui.maps.icons

class TankmanAdapter(object):

    def getFullUserName(self):
        raise NotImplementedError

    def getLabel(self):
        raise NotImplementedError

    def getTankmanIcon(self):
        raise NotImplementedError

    def getDescription(self):
        raise NotImplementedError

    def getSkillsLabel(self):
        raise NotImplementedError

    def getSkills(self):
        raise NotImplementedError


class TokenTankmanInfoAdapter(TankmanAdapter):
    __slots__ = ('_tankmanInfo',)

    def __init__(self, recruitID):
        self._tankmanInfo = NotRecruitedTankmanContext().buildItem(recruitID)

    def getFullUserName(self):
        return self._tankmanInfo.getFullUserName()

    def getLabel(self):
        return makeString(self._tankmanInfo.getLabel())

    def getTankmanIcon(self):
        iconName = self._tankmanInfo.getSmallIcon().split('.png')[0]
        icon = _IMG_PATH.tankmen.icons.special.dyn(iconName)
        if not icon.exists():
            icon = _IMG_PATH.tankmen.icons.big.dyn(iconName)
        return backport.image(icon()) if icon.exists() else ''

    def getDescription(self):
        return makeString(self._tankmanInfo.getDescription())

    def getSkillsLabel(self):
        return backport.text(R.strings.tooltips.vehiclePreview.tankman.skillsTitle()) if self._getSkills() else ''

    def getSkills(self):
        return [ backport.image(_IMG_PATH.tankmen.skills.big.dyn(skill)()) for skill in self._getSkills() ]

    def _getSkills(self):
        return self._tankmanInfo.getLearntSkills(multiplyNew=True)


class TankmanInfoAdapter(TankmanAdapter):
    __slots__ = ('_tankmanInfo',)

    def __init__(self, tankman):
        self._tankmanInfo = tankman

    def getFullUserName(self):
        return self._tankmanInfo.fullUserName

    def getLabel(self):
        return self._tankmanInfo.roleUserName

    def getTankmanIcon(self):
        return backport.image(_IMG_PATH.tankmen.icons.big.dyn(self._tankmanInfo.extensionLessIcon)())

    def getDescription(self):
        pass

    def getSkillsLabel(self):
        return backport.text(R.strings.tooltips.vehiclePreview.tankman.skillsTitle()) if self._tankmanInfo.skills else ''

    def getSkills(self):
        return [ backport.image(_IMG_PATH.artefact.dyn(skill.name)()) for skill in self._tankmanInfo.skills ]

    def _getVehicleName(self):
        return self._tankmanInfo.vehicleDescr.getName() if self._tankmanInfo.isInTank else ''
