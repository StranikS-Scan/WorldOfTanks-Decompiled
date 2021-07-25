# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/settings_globals.py
import typing
from crew2.settings_locator import Crew2Settings
from crew2.character_property_pool import CharacterPropertyPool
from crew2.commander.settings import CommanderSettings
from crew2.conversion import ConversionSettings, DEF_CONVERSION_CFG_PATH
from crew2.detachment.settings import DetachmentSettings
from crew2.instructor.instructor_settings_provider import InstructorSettingsProvider, DEF_INSTRUCTOR_SETTINGS_PATH
from crew2.perk.settings import PerkSettings, DEF_PERK_SETTINGS_PATH
from crew2.perk.builds import PerkBuildPresets
g_characterProperties = None
g_commanderSettings = None
g_detachmentSettings = None
g_perkSettings = None
g_instructorSettingsProvider = None
g_builds = None
g_conversion = None
DEFAULT_ITEMS_DEFS_PATH = '/'.join(('scripts', 'item_defs'))
DEFAULT_CREW2_PATH = '/'.join((DEFAULT_ITEMS_DEFS_PATH, 'crew2'))
DEF_CHAR_PROPS_PATH = '/'.join((DEFAULT_CREW2_PATH, 'character_properties'))
DEF_COMMANDERS_PATH = '/'.join((DEFAULT_CREW2_PATH, 'commanders'))
DEF_DETACHMENTS_PATH = '/'.join((DEFAULT_CREW2_PATH, 'detachments'))
DEF_BUILDS_PATH = DEF_PERK_SETTINGS_PATH + 'builds.xml'

def init(charPropsPath=DEF_CHAR_PROPS_PATH, commandersPath=DEF_COMMANDERS_PATH, perkSettingsPath=DEF_PERK_SETTINGS_PATH, detachmentSettingsPath=DEF_DETACHMENTS_PATH, instructorSettingsPath=DEF_INSTRUCTOR_SETTINGS_PATH, buildsPath=DEF_BUILDS_PATH, conversionPath=DEF_CONVERSION_CFG_PATH):
    global g_commanderSettings
    global g_perkSettings
    global g_builds
    global g_detachmentSettings
    global g_characterProperties
    global g_conversion
    global g_instructorSettingsProvider
    c2s = Crew2Settings()
    c2s.characterProperties = CharacterPropertyPool(charPropsPath)
    g_characterProperties = c2s.characterProperties
    c2s.commanderSettings = CommanderSettings(commandersPath)
    g_commanderSettings = c2s.commanderSettings
    c2s.perkSettings = PerkSettings(perkSettingsPath)
    g_perkSettings = c2s.perkSettings
    c2s.instructorSettingsProvider = InstructorSettingsProvider(instructorSettingsPath, settingsLocator=c2s)
    g_instructorSettingsProvider = c2s.instructorSettingsProvider
    c2s.detachmentSettings = DetachmentSettings(detachmentSettingsPath, settingsLocator=c2s)
    g_detachmentSettings = c2s.detachmentSettings
    c2s.builds = PerkBuildPresets(buildsPath, settingsLocator=c2s)
    g_builds = c2s.builds
    c2s.conversion = ConversionSettings(conversionPath, settingsLocator=c2s)
    g_conversion = c2s.conversion
