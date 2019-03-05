# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/blueprints/blueprints_cm_handlers.py
from async import await, async
from gui.impl import dialogs
from gui.Scaleform.daapi.view.lobby.storage.blueprints import blueprintExitEvent
from gui.Scaleform.daapi.view.lobby.storage.cm_handlers import ContextMenu, option, CMLabel
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items.items_actions import factory
from helpers import dependency, i18n
from ids_generators import SequenceIDGenerator
from skeletons.gui.shared import IItemsCache

class BlueprintsCMHandler(ContextMenu):
    __sqGen = SequenceIDGenerator()
    __itemsCache = dependency.descriptor(IItemsCache)

    @option(__sqGen.next(), CMLabel.CONVERT_BLUEPRINT)
    @async
    def convertBlueprintFragment(self):
        isResearch = yield await(dialogs.blueprintsConversion(self._id))
        if isResearch:
            factory.doAction(factory.CONVERT_BLUEPRINT_FRAGMENT, self._id)

    @option(__sqGen.next(), CMLabel.CONVERT_BLUEPRINT_MAX)
    @async
    def convertMaxBlueprintFragments(self):
        availableCount = self.__getMaxFragmentCount()
        isResearch = yield await(dialogs.blueprintsConversion(self._id, fragmentCount=availableCount))
        if isResearch:
            factory.doAction(factory.CONVERT_BLUEPRINT_FRAGMENT, self._id, availableCount)

    @option(__sqGen.next(), CMLabel.SHOW_BLUEPRINT)
    def showBlueprintView(self):
        exitEvent = blueprintExitEvent()
        shared_events.showBlueprintView(self._id, exitEvent)

    def _makeOption(self, label, data):
        vo = super(BlueprintsCMHandler, self)._makeOption(label, data)
        if label == CMLabel.CONVERT_BLUEPRINT_MAX:
            count = data.pop('count', 0)
            if count > 0:
                vo['label'] = i18n.makeString(vo['label'], count=count)
        return vo

    def _getOptionCustomData(self, label):
        if label == CMLabel.CONVERT_BLUEPRINT_MAX:
            availableCount = self.__getMaxFragmentCount()
            if availableCount > 1:
                return {'label': 'convertBlueprintMaxCount',
                 'count': availableCount}
            return {'enabled': False}
        else:
            if label == CMLabel.CONVERT_BLUEPRINT:
                availableCount = self.__getMaxFragmentCount()
                if availableCount == 0:
                    return {'enabled': False}
            return None

    def __getMaxFragmentCount(self):
        item = self.__itemsCache.items.getItemByCD(self._id)
        return self.__itemsCache.items.blueprints.getConvertibleFragmentCount(item.intCD, item.level) if item is not None else 0
