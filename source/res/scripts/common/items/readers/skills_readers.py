# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/skills_readers.py
from collections import namedtuple
import ResMgr
from constants import IS_CLIENT, IS_WEB, TTC_TOOLTIP_SECTIONS
from items import _xml
from items.components import component_constants, skills_constants
from items.components import skills_components
from items.components.component_constants import EMPTY_STRING
from items.components.skills_constants import ParamMeasureType, ParamSignType, SkillTypeName
if IS_CLIENT or IS_WEB:
    from gui.impl import backport
    from gui.impl.gen import R
SkillUISettings = namedtuple('SkillUISettings', ('tooltipSection', 'typeName', 'kpi', 'params', 'descrArgs'))
SkillDescrsArg = namedtuple('SkillDescrsArg', ('situational', 'name', 'measureType', 'sign', 'value', 'isKpiVisible'))
TTCParamsArg = namedtuple('TTCParamsArg', ('name', 'situational', 'value'))

def _readSkillBasics(xmlCtx, section, subsectionName):
    section = _xml.getSubsection(xmlCtx, section, subsectionName)
    xmlCtx = (xmlCtx, subsectionName)
    vsePerk = _xml.readIntOrNone(xmlCtx, section, 'vsePerk')
    if IS_CLIENT or IS_WEB:
        uiSettings = _readUISettings(xmlCtx, section, 'UISettings')
        skillLocales = _readLocales(subsectionName, section)
        skill = skills_components.BasicSkill(subsectionName, i18n=skillLocales, icon=_xml.readStringWithDefaultValue(xmlCtx, section, 'icon', '{}.png'.format(subsectionName)), vsePerk=vsePerk, uiSettings=uiSettings)
    else:
        skill = skills_components.BasicSkill(subsectionName, vsePerk=vsePerk)
    return (skill, xmlCtx, section)


def _readLocales(skillName, section):

    def localeText(locRoot, dynName):
        if locRoot.isValid():
            dynStr = locRoot.dyn(dynName)
            if dynStr.isValid():
                return backport.text(dynStr())
        return EMPTY_STRING

    localeRoot = R.strings.crew_perks.dyn(skillName)
    altRoot = localeRoot.dyn('alt')
    return skills_components.SkillLocales(section.readString('userString', localeText(localeRoot, 'name')), section.readString('shortDescription', localeText(localeRoot, 'shortDescription')), section.readString('maxLvlDescription', localeText(localeRoot, 'maxLvlDescription')), section.readString('currentLvlDescription', localeText(localeRoot, 'currentLvlDescription')), section.readString('altDescription', localeText(altRoot, 'description')), section.readString('altInfo', localeText(altRoot, 'info')))


def _readUISettings(xmlCtx, section, subsectionName):
    from items.artefacts_helpers import readKpi
    section = _xml.getSubsection(xmlCtx, section, subsectionName, throwIfMissing=False)
    if not section:
        return
    kpi = []
    if IS_CLIENT and section.has_key('kpi'):
        kpi = readKpi(xmlCtx, section['kpi'])
    return SkillUISettings(tooltipSection=_xml.readStringWithDefaultValue(xmlCtx, section, 'tooltipSection', TTC_TOOLTIP_SECTIONS.SKILLS), typeName=_xml.readStringWithDefaultValue(xmlCtx, section, 'typeName', SkillTypeName.MAIN), kpi=kpi, descrArgs=_readDescrArgs(xmlCtx, section, 'descr'), params=_readTTCParams(xmlCtx, section, 'params'))


def _readDescrArgs(xmlCtx, section, subsectionName):
    section = _xml.getSubsection(xmlCtx, section, subsectionName, throwIfMissing=False)
    if not section:
        return {}
    settings = []
    for _, argSection in section.items():
        name = _xml.readNonEmptyString(xmlCtx, argSection, 'paramName')
        value = _xml.readFloat(xmlCtx, argSection, 'value')
        sign = ParamSignType.SIGN_LESS
        if value > 0:
            sign = ParamSignType.PLUS
        elif value < 0:
            sign = ParamSignType.MINUS
        settings.append((name, SkillDescrsArg(situational=_xml.readBool(xmlCtx, argSection, 'situationalParam', False), isKpiVisible=_xml.readBool(xmlCtx, argSection, 'isKpiVisible', True), name=name, measureType=_xml.readStringWithDefaultValue(xmlCtx, argSection, 'measureType', ParamMeasureType.PERCENTS), sign=_xml.readStringWithDefaultValue(xmlCtx, argSection, 'sign', sign), value=value)))

    return settings


def _readTTCParams(xmlCtx, section, subsectionName):
    section = _xml.getSubsection(xmlCtx, section, subsectionName, throwIfMissing=False)
    if not section:
        return {}
    params = {}
    for _, param in section.items():
        name = _xml.readNonEmptyString(xmlCtx, param, 'name')
        params[name] = TTCParamsArg(name=name, situational=_xml.readBool(xmlCtx, param, 'situationalParam', False), value=_xml.readFloat(xmlCtx, param, 'value'))

    return params


def _readRole(xmlCtx, section, subsectionName):
    skill, _, __ = _readSkillBasics(xmlCtx, section, subsectionName)
    return skill


def _readBrotherhoodSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.BrotherhoodSkill(skill, _xml.readFloat(xmlCtx, section, 'crewLevelIncrease', component_constants.ZERO_FLOAT))


def _readCommanderTutorSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.CommanderTutorSkill(skill, _xml.readNonNegativeFloat(xmlCtx, section, 'xpBonusFactorPerLevel'))


def _readCommanderUniversalistSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.CommanderUniversalistSkill(skill, _xml.readFraction(xmlCtx, section, 'efficiency'))


def _readCommanderSkillWithDelaySkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.CommanderSkillWithDelay(skill, _xml.readNonNegativeFloat(xmlCtx, section, 'delay'))


def _readCommonSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.CommonSkill(skill)


def _readRadiomanLastEffortSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.RadiomanLastEffortSkill(skill, _xml.readFloat(xmlCtx, section, 'durationPerLevel'))


def _readCrewMasterySkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.CrewMasterySkill(skill, _xml.readFloat(xmlCtx, section, 'crewLevelIncrease'))


def _readCommanderEnemyShotPredictorSkill(xmlCtx, section, subsectionName):
    skill, xmlCtx, section = _readSkillBasics(xmlCtx, section, subsectionName)
    return skills_components.CommanderEnemyShotPredictor(skill, _xml.readNonNegativeFloat(xmlCtx, section, 'minExplosionRadius'), _xml.readNonNegativeFloat(xmlCtx, section, 'explosionMultiplier'), _xml.readNonNegativeFloat(xmlCtx, section, 'recalculatingHeight'), _xml.readNonNegativeFloat(xmlCtx, section, 'targetRadius'))


_g_skillConfigReaders = {'repair': _readRole,
 'fireFighting': _readRole,
 'camouflage': _readRole,
 'brotherhood': _readBrotherhoodSkill,
 'commander_tutor': _readCommanderTutorSkill,
 'commander_universalist': _readCommanderUniversalistSkill,
 'commander_expert': _readCommonSkill,
 'commander_sixthSense': _readCommanderSkillWithDelaySkill,
 'commander_enemyShotPredictor': _readCommanderEnemyShotPredictorSkill,
 'commander_eagleEye': _readCommonSkill,
 'driver_tidyPerson': _readCommonSkill,
 'driver_smoothDriving': _readCommonSkill,
 'driver_virtuoso': _readCommonSkill,
 'driver_badRoadsKing': _readCommonSkill,
 'driver_rammingMaster': _readCommonSkill,
 'gunner_smoothTurret': _readCommonSkill,
 'gunner_sniper': _readCommonSkill,
 'gunner_rancorous': _readCommonSkill,
 'gunner_gunsmith': _readCommonSkill,
 'loader_pedant': _readCommonSkill,
 'loader_desperado': _readCommonSkill,
 'loader_intuition': _readCommonSkill,
 'radioman_finder': _readCommonSkill,
 'radioman_inventor': _readCommonSkill,
 'radioman_lastEffort': _readRadiomanLastEffortSkill,
 'radioman_retransmitter': _readCommonSkill}

def readSkillsConfig(xmlPath):
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
