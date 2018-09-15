# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/skills_readers.py
import math
import ResMgr
from constants import IS_CLIENT, IS_WEB
from items import _xml
from items.components import component_constants, skills_constants
from items.components import shared_components
from items.components import skills_components

def _readSkillBasics(xmlCtx, section, subsectionName):
    section = _xml.getSubsection(xmlCtx, section, subsectionName)
    xmlCtx = (xmlCtx, subsectionName)
    if IS_CLIENT or IS_WEB:
        skill = skills_components.BasicSkill(subsectionName, i18n=shared_components.I18nComponent(section.readString('userString'), section.readString('description')), icon=_xml.readNonEmptyString(xmlCtx, section, 'icon'))
    else:
        skill = skills_components.BasicSkill(subsectionName)
    return (skill, xmlCtx, section)


def _readRole(xmlCtx, section, subsectionName):
    skill, _, __ = _readSkillBasics(xmlCtx, section, subsectionName)
    return skill


def _readBrotherhoodSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.BrotherhoodSkill(skill, _xml.readInt(xmlCtx, section, 'crewLevelIncrease', component_constants.ZERO_INT))


def _readCommanderTutorSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.CommanderTutorSkill(skill, _xml.readNonNegativeFloat(xmlCtx, section, 'xpBonusFactorPerLevel'))


def _readCommanderUniversalistSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.CommanderUniversalistSkill(skill, _xml.readFraction(xmlCtx, section, 'efficiency'))


def _readCommanderSkillWithDelaySkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.CommanderSkillWithDelay(skill, _xml.readNonNegativeFloat(xmlCtx, section, 'delay'))


def _readCommanderEagleEye(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.CommanderEagleEyeSkill(skill, _xml.readPositiveFloat(xmlCtx, section, 'distanceFactorPerLevelWhenDeviceWorking'), _xml.readPositiveFloat(xmlCtx, section, 'distanceFactorPerLevelWhenDeviceDestroyed'))


def _readDriverTidyPersonSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.DriverTidyPersonSkill(skill, _xml.readNonNegativeFloat(xmlCtx, section, 'fireStartingChanceFactor'))


def _readDriverSmoothDrivingSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.DriverSmoothDrivingSkill(skill, _xml.readNonNegativeFloat(xmlCtx, section, 'shotDispersionFactorPerLevel'))


def _readDriverVirtuosoSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.DriverVirtuosoSkill(skill, _xml.readNonNegativeFloat(xmlCtx, section, 'rotationSpeedFactorPerLevel'))


def _readDriverRammingMasterSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.DriverRammingMasterSkill(skill, _xml.readNonNegativeFloat(xmlCtx, section, 'rammingBonusFactorPerLevel'))


def _readDriverBadRoadsKing(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.DriverBadRoadsKingSkill(skill, _xml.readPositiveFloat(xmlCtx, section, 'softGroundResistanceFactorPerLevel'), _xml.readPositiveFloat(xmlCtx, section, 'mediumGroundResistanceFactorPerLevel'))


def _readGunnerSmoothTurretSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.GunnerSmoothTurretSkill(skill, _xml.readNonNegativeFloat(xmlCtx, section, 'shotDispersionFactorPerLevel'))


def _readGunnerSniperSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.GunnerSniperSkill(skill, _xml.readFraction(xmlCtx, section, 'deviceChanceToHitBoost'))


def _readGunnerRancorousSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.GunnerRancorousSkill(skill, _xml.readPositiveFloat(xmlCtx, section, 'duration'), math.radians(_xml.readPositiveFloat(xmlCtx, section, 'sectorHalfAngle')))


def _readGunnerGunsmithSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.GunnerGunsmithSkill(skill, _xml.readPositiveFloat(xmlCtx, section, 'shotDispersionFactorPerLevel'))


def _readLoaderPedantSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.LoaderPedantSkill(skill, _xml.readNonNegativeFloat(xmlCtx, section, 'ammoBayHealthFactor'))


def _readLoaderIntuitionSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.LoaderIntuitionSkill(skill, _xml.readFraction(xmlCtx, section, 'chance'))


def _readLoaderDesperadoSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.LoaderDesperadoSkill(skill, _xml.readFraction(xmlCtx, section, 'vehicleHealthFraction'), _xml.readPositiveFloat(xmlCtx, section, 'gunReloadTimeFactor'))


def _readRadiomanFinderSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.RadiomanFinderSkill(skill, _xml.readNonNegativeFloat(xmlCtx, section, 'visionRadiusFactorPerLevel'))


def _readRadiomanInventorSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.RadiomanInventorSkill(skill, _xml.readNonNegativeFloat(xmlCtx, section, 'radioDistanceFactorPerLevel'))


def _readRadiomanLastEffortSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.RadiomanLastEffortSkill(skill, _xml.readInt(xmlCtx, section, 'duration', 1))


def _readRadiomanRetransmitterSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.RadiomanRetransmitterSkill(skill, _xml.readNonNegativeFloat(xmlCtx, section, 'distanceFactorPerLevel'))


_g_skillConfigReaders = {'repair': _readRole,
 'fireFighting': _readRole,
 'camouflage': _readRole,
 'brotherhood': _readBrotherhoodSkill,
 'commander_tutor': _readCommanderTutorSkill,
 'commander_universalist': _readCommanderUniversalistSkill,
 'commander_expert': _readCommanderSkillWithDelaySkill,
 'commander_sixthSense': _readCommanderSkillWithDelaySkill,
 'commander_eagleEye': _readCommanderEagleEye,
 'driver_tidyPerson': _readDriverTidyPersonSkill,
 'driver_smoothDriving': _readDriverSmoothDrivingSkill,
 'driver_virtuoso': _readDriverVirtuosoSkill,
 'driver_badRoadsKing': _readDriverBadRoadsKing,
 'driver_rammingMaster': _readDriverRammingMasterSkill,
 'gunner_smoothTurret': _readGunnerSmoothTurretSkill,
 'gunner_sniper': _readGunnerSniperSkill,
 'gunner_rancorous': _readGunnerRancorousSkill,
 'gunner_gunsmith': _readGunnerGunsmithSkill,
 'loader_pedant': _readLoaderPedantSkill,
 'loader_desperado': _readLoaderDesperadoSkill,
 'loader_intuition': _readLoaderIntuitionSkill,
 'radioman_finder': _readRadiomanFinderSkill,
 'radioman_inventor': _readRadiomanInventorSkill,
 'radioman_lastEffort': _readRadiomanLastEffortSkill,
 'radioman_retransmitter': _readRadiomanRetransmitterSkill}

def readSkillsConfig(xmlPath):
    """Reads shared configuration containing information about tankmen skills and roles.
    :param xmlPath: string containing relative path to xml file.
    :return: instance of SkillsConfig.
    """
    xmlCtx = (None, xmlPath)
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    config = skills_components.SkillsConfig()
    for skillName in skills_constants.ROLES:
        skillConfig = _readRole(xmlCtx, section, 'roles/' + skillName)
        config.addSkill(skillName, skillConfig)

    section = _xml.getSubsection(xmlCtx, section, 'skills')
    xmlCtx = (xmlCtx, 'skills')
    for skillName in skills_constants.ACTIVE_SKILLS:
        skillConfig = _g_skillConfigReaders[skillName](xmlCtx, section, skillName)
        config.addSkill(skillName, skillConfig)

    ResMgr.purge(xmlPath, True)
    return config
