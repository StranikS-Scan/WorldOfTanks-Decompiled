# Embedded file name: scripts/client/gui/doc_loaders/GuiSoundsLoader.py
__author__ = 'i_maliavko'
import ResMgr
from items import _xml
from gui import doc_loaders
from debug_utils import *

class GuiSoundsLoader(object):
    """
    Gui sound xml data loader.
    """
    XML_PATH = 'gui/gui_sounds.xml'
    CONTROLS = 'controls'
    CONTROLS_DEFAULT = 'default'
    CONTROLS_SCHEMAS = 'schemas'
    CONTROLS_OVERRIDES = 'overrides'
    SCHEMA_SOUNDS = 'sounds'
    SCHEMA_GROUPS = 'groups'
    EFFECTS = 'effects'

    def __init__(self):
        self.__schemas = {}
        self.__groups = {}
        self.__overrides = {}
        self.__default = {}
        self.__effects = {}

    def __readControlsSounds(self, xmlCtx):
        """
        Reading controls sounds data
        @param xmlCtx: [xml data section] xml context document
        """
        controlsSection = _xml.getSubsection(xmlCtx, xmlCtx, self.CONTROLS)
        self.__default = doc_loaders.readDict(xmlCtx, controlsSection, self.CONTROLS_DEFAULT)
        controlsOverridesSection = _xml.getSubsection(xmlCtx, controlsSection, self.CONTROLS_OVERRIDES)
        for name in controlsOverridesSection.keys():
            self.__overrides[name] = doc_loaders.readDict(xmlCtx, controlsOverridesSection, name)

        for schemaName, schemaSection in _xml.getChildren(xmlCtx, controlsSection, self.CONTROLS_SCHEMAS):
            self.__schemas[schemaName] = doc_loaders.readDict(xmlCtx, schemaSection, self.SCHEMA_SOUNDS)
            for groupName in _xml.getSubsection(xmlCtx, schemaSection, self.SCHEMA_GROUPS).asString.split():
                if groupName in self.__groups:
                    LOG_WARNING('Group has already been read. Will be overriden', groupName, schemaName)
                self.__groups[groupName] = schemaName

    def __readEffectsSounds(self, xmlCtx):
        """
        Reading effects sounds data
        @param xmlCtx: [xml data section] xml context document
        """
        self.__effects = doc_loaders.readDict(xmlCtx, xmlCtx, self.EFFECTS)

    def load(self):
        """
        Start loading xml data from file
        """
        xmlCtx = ResMgr.openSection(self.XML_PATH)
        if xmlCtx is None:
            _xml.raiseWrongXml(None, self.XML_PATH, 'can not open or read')
        self.__readControlsSounds(xmlCtx)
        self.__readEffectsSounds(xmlCtx)
        return

    def getControlSound(self, controlType, state, controlID = None):
        """
        Get sound path for given control and its state
        
        @param controlType: [str] type of control from xml document
        @param state: [str] control state
        @param controlID: [optional str] used to add some special
                                                sounds for schemas
        @return: [str] sound path
        """
        if controlID is not None and controlID in self.__overrides:
            return self.__overrides[controlID].get(state)
        elif controlType in self.__groups:
            schemaName = self.__groups[controlType]
            return self.__schemas.get(schemaName, {}).get(state)
        elif controlType in self.__schemas:
            return self.__schemas[controlType].get(state)
        else:
            return self.__default.get(state)

    def getEffectSound(self, effectName):
        """
        Returns sound path by given name from
        `effects` xml section.
        
        @param effectName: [str] effect name
        @return: [str] sound path
        """
        if effectName in self.__effects:
            return self.__effects[effectName]
        else:
            return None
