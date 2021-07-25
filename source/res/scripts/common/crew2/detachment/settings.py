# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/detachment/settings.py
import ResMgr
from typing import Optional
from items import _xml
from crew2.detachment.images import DetachmentImages
from crew2.detachment.progression_settings import ProgressionSettings
from crew2.detachment.detachment_presets import DetachmentPresets
from crew2.settings_locator import Crew2Settings

class DetachmentSettings(object):

    def __init__(self, configsPath, settingsLocator=None):
        self._recycleBinMaxSize = None
        self._garbageThreshold = None
        self._holdInRecycleBinTerm = None
        self._specialRestoreTerm = None
        self._maxDetachments = None
        self._maxInstructors = None
        self._maxVehicleSlots = None
        self._maxInstructorSlots = None
        self._readCommonSettings('/'.join((configsPath, 'detachment.xml')))
        settingsLocator.detachmentSettings = self
        imagesPath = '/'.join((configsPath, 'crew_images.xml'))
        self._images = DetachmentImages(imagesPath)
        progressionPath = '/'.join((configsPath, 'progression.xml'))
        self._progression = ProgressionSettings(progressionPath, settingsLocator=settingsLocator)
        presetsPath = '/'.join((configsPath, 'detachment_presets.xml'))
        self._presets = DetachmentPresets(presetsPath, settingsLocator=settingsLocator)
        return

    @property
    def images(self):
        return self._images

    @property
    def progression(self):
        return self._progression

    @property
    def presets(self):
        return self._presets

    @property
    def recycleBinMaxSize(self):
        return self._recycleBinMaxSize

    @property
    def garbageThreshold(self):
        return self._garbageThreshold

    @property
    def holdInRecycleBinTerm(self):
        return self._holdInRecycleBinTerm

    @property
    def specialRestoreTerm(self):
        return self._specialRestoreTerm

    @property
    def maxDetachments(self):
        return self._maxDetachments

    @property
    def maxInstructors(self):
        return self._maxInstructors

    @property
    def maxVehicleSlots(self):
        return self._maxVehicleSlots

    @property
    def maxInstructorSlots(self):
        return self._maxInstructorSlots

    def _readCommonSettings(self, filePath):
        rootSection = ResMgr.openSection(filePath)
        xmlCtx = (None, filePath)
        dissolutionSec = _xml.getSubsection(xmlCtx, rootSection, 'dissolveSettings', throwIfMissing=True)
        self._recycleBinMaxSize = _xml.readInt(xmlCtx, dissolutionSec, 'recycleBinMaxSize', minVal=0, maxVal=999)
        self._garbageThreshold = _xml.readPositiveInt(xmlCtx, dissolutionSec, 'garbageThreshold')
        self._holdInRecycleBinTerm = _xml.readPositiveInt(xmlCtx, dissolutionSec, 'holdInRecycleBinTerm')
        self._specialRestoreTerm = _xml.readInt(xmlCtx, dissolutionSec, 'specialRestoreTerm', minVal=0, maxVal=self._holdInRecycleBinTerm)
        self._maxDetachments = _xml.readPositiveInt(xmlCtx, rootSection, 'maxDetachments')
        self._maxInstructors = _xml.readPositiveInt(xmlCtx, rootSection, 'maxInstructors')
        self._maxVehicleSlots = _xml.readPositiveInt(xmlCtx, rootSection, 'maxVehicleSlots')
        self._maxInstructorSlots = _xml.readPositiveInt(xmlCtx, rootSection, 'maxInstructorSlots')
        return
