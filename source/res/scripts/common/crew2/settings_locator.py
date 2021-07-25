# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/settings_locator.py
import typing
if typing.TYPE_CHECKING:
    from crew2.character_property_pool import CharacterPropertyPool
    from crew2.commander.settings import CommanderSettings
    from crew2.conversion import ConversionSettings
    from crew2.detachment.settings import DetachmentSettings
    from crew2.instructor.instructor_settings_provider import InstructorSettingsProvider
    from crew2.perk.settings import PerkSettings
    from crew2.perk.builds import PerkBuildPresets

class Crew2Settings(object):

    def __init__(self):
        self.characterProperties = None
        self.commanderSettings = None
        self.perkSettings = None
        self.instructorSettingsProvider = None
        self.detachmentSettings = None
        self.builds = None
        self.conversion = None
        return
