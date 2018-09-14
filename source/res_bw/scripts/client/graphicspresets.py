# Embedded file name: scripts/client/GraphicsPresets.py
import BigWorld
import ResMgr
graphicsPresetsResource = 'system/data/graphics_settings_presets.xml'

class GraphicsPresets:
    """
    This class implements the GraphicsPresets functionality.
    
    The graphics presets store a number of graphics settings in a dictionary
    and lets you apply them all at once.
    
    The graphics presets are stored in an xml file.
    
    When initialised, the graphics presets will check against the currently set
    graphics options to see if any of its options are selected.
    
    The graphics presets have the following members:
    
    GraphicsPresets.entries - a dictionary of dictionaries that store the values
    for each preset graphics setting
    
    GraphicsPresets.entryNames - a list of the names of the presets in the order
    they appear in the .xml file. These names are the same as the keys for the 
    GraphicsSettings.entries dictionary
    
    GraphicsPresets.selectedOption - this is an index into the GraphicsPresets.entryNames
    member or -1 if a preset has not been set
    """

    def __init__(self):
        sect = ResMgr.openSection(graphicsPresetsResource)
        self.entries = {}
        self.entryNames = []
        self.selectedOption = -1
        for group in sect.values():
            if group.asString != '':
                entry = {}
                for setting in group.values():
                    if setting.name == 'entry':
                        entry[setting.readString('label')] = setting.readInt('activeOption')

                self.entries[group.asString] = entry
                self.entryNames.append(group.asString)

        self.setSelectedOption()

    def setSelectedOption(self):
        self.selectedOption = -1
        currentOptionMap = {}
        for currentOption in BigWorld.graphicsSettings():
            currentOptionMap[currentOption[0]] = currentOption[1]

        for i in range(0, len(self.entryNames)):
            foundOption = True
            for setting in self.entries[self.entryNames[i]].items():
                if currentOptionMap.get(setting[0]) != setting[1]:
                    foundOption = False
                    break

            if foundOption == True:
                self.selectedOption = i
                break

    def selectGraphicsOptions(self, option):
        currentOption = self.entries[self.entryNames[option]]
        for setting in currentOption.items():
            try:
                BigWorld.setGraphicsSetting(setting[0], setting[1])
            except:
                print 'selectGraphicsOptions: unable to set option ', setting[0]

        self.selectedOption = option
