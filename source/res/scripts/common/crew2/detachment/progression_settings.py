# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/detachment/progression_settings.py
import typing
import ResMgr
from crew2.detachment.progression_record import ProgressionRecord
from items import _xml
if typing.TYPE_CHECKING:
    from crew2.settings_locator import Crew2Settings

class ProgressionSettings(object):

    def __init__(self, xmlPath, settingsLocator=None):
        self._settingsLocator = settingsLocator
        self._progressions = {}
        self._load(xmlPath)

    def getProgressionByID(self, progressionID):
        return self._progressions.get(progressionID)

    def _load(self, xmlPath):
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        xmlCtx = (None, xmlPath)
        self._progressions = self._loadProgressions(xmlCtx, section, 'progression')
        ResMgr.purge(xmlPath, True)
        return

    def _loadProgressions(self, xmlCtx, section, subsectionName):
        progressionsSection = _xml.getSubsection(xmlCtx, section, subsectionName)
        progressions = {}
        for layoutSection in progressionsSection.values():
            progression = ProgressionRecord(xmlCtx, layoutSection, self._settingsLocator)
            progressions[progression.ID] = progression

        return progressions
