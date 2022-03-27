# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ui_spam/ui_spam_controller.py
from account_helpers import AccountSettings
from constants import MAX_VEHICLE_LEVEL
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.ui_spam.ui_spam_config import UISpamConfigReader
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IUISpamController

class UISpamController(IUISpamController):
    _CONFIG_PATH = 'scripts/ui_spam_conditions.xml'
    _BATTLES_COUNT = 'battlesCount'
    _HAVE_BLUEPRINTS = 'haveBluePrints'
    _HAVE_UNLOCKED_TANK_LEVEL = 'haveUnlockedTankLevel'
    _HAVE_TANK_LEVEL = 'haveTankLevel'
    _VISITED_SETTING = 'uiSpamVisited_{}'
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self._config = UISpamConfigReader.readXml(self._CONFIG_PATH)
        self._checkers = {self._BATTLES_COUNT: self._checkBattlesCount,
         self._HAVE_BLUEPRINTS: self._checkBlueprintsOrFragments,
         self._HAVE_UNLOCKED_TANK_LEVEL: self._checkUnlockedTankLevel,
         self._HAVE_TANK_LEVEL: self._checkHaveTankLevel}
        super(UISpamController, self).__init__()

    def checkRule(self, ruleId):
        rule = self._config.getRule(ruleId)
        for name, value in rule.iteritems():
            function = self._checkers.get(name)
            if function and function(value):
                return False

        return True

    def shouldBeHidden(self, aliasId):
        return not AccountSettings.getUIFlag(self._VISITED_SETTING.format(aliasId)) and not self.checkRule(self._config.getRuleIdForAlias(aliasId))

    def setVisited(self, aliasId):
        AccountSettings.setUIFlag(self._VISITED_SETTING.format(aliasId), True)

    def _checkBattlesCount(self, value):
        return self._itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount() < value

    def _checkBlueprintsOrFragments(self, _):
        return not self._itemsCache.items.blueprints.hasBlueprintsOrFragments()

    def _checkUnlockedTankLevel(self, value):
        return not self._itemsCache.items.getVehicles(REQ_CRITERIA.UNLOCKED | REQ_CRITERIA.VEHICLE.LEVELS(range(value, MAX_VEHICLE_LEVEL + 1)) | REQ_CRITERIA.CUSTOM(lambda item: not item.isPremium and not item.isSpecial and not item.isSecret))

    def _checkHaveTankLevel(self, value):
        return not self._itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(range(value, MAX_VEHICLE_LEVEL + 1)) | REQ_CRITERIA.CUSTOM(lambda item: not item.isSpecial and not item.isSecret))
