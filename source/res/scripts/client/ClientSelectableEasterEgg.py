# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableEasterEgg.py
from ClientSelectableObject import ClientSelectableObject
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import g_eventBus, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import IBootcampController
from helpers import getClientLanguage

class ClientSelectableEasterEgg(ClientSelectableObject):
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(ClientSelectableEasterEgg, self).__init__()
        if self.bootcampController.isInBootcamp() or not GUI_SETTINGS.easterEgg.enabled:
            self.enable(False)

    def onMouseClick(self):
        super(ClientSelectableEasterEgg, self).onMouseClick()
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.IMAGE_VIEW, ctx={'img': self.__getImageName()}), EVENT_BUS_SCOPE.LOBBY)

    def __getImageName(self):
        nameParts = [self.imageName]
        if self.multiLanguageSupport:
            nameLocalizationSuffix = '_ru' if getClientLanguage() in GUI_SETTINGS.easterEgg.ruLangGroup else '_en'
            nameParts.append(nameLocalizationSuffix)
        nameParts.append('.png')
        return ''.join(nameParts)
