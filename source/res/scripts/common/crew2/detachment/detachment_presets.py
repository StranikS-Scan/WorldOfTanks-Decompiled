# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/detachment/detachment_presets.py
import typing
import ResMgr
from crew2.detachment.detachment_preset import DetachmentPreset
from crew2.settings_locator import Crew2Settings
from items import _xml

class DetachmentPresets(object):

    def __init__(self, path, settingsLocator=None):
        self._detachmentPresetsByID = {}
        self._detachmentPresets = {}
        self.__load(path, settingsLocator)

    def getDetachmentPresetByID(self, presetID):
        return self._detachmentPresetsByID.get(presetID)

    def getDetachmentPreset(self, name):
        return self._detachmentPresets.get(name)

    def __load(self, path, settingsLocator):
        rootSection = ResMgr.openSection(path)
        xmlCtx = (None, path)
        for _, subsection in _xml.getChildren(xmlCtx, rootSection, 'detachmentPresets'):
            preset = DetachmentPreset(xmlCtx, subsection, settingsLocator)
            if preset.id in self._detachmentPresetsByID:
                _xml.raiseWrongXml(xmlCtx, '', 'Duplicated preset id {}'.format(preset.id))
            self._detachmentPresetsByID[preset.id] = preset
            if preset.name in self._detachmentPresets:
                _xml.raiseWrongXml(xmlCtx, '', "Duplicated preset name '{}'".format(preset.name))
            self._detachmentPresets[preset.name] = preset

        ResMgr.purge(path)
        return
