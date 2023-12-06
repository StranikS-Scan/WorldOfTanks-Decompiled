# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/development/__init__.py
from account_helpers.AccountSettings import LOOT_BOXES_INTRO_SHOWN
from gui.impl.gen import R
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui_lootboxes.gui.shared.event_dispatcher import showRewardScreenWindow
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IGuiLootBoxesController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache

def _getLootBoxBonusesExample():
    return {'blueprints': {65523: 10},
     'freeXP': 100000,
     'crewSkins': [{'count': 1,
                    'id': 2}],
     'gold': 100000,
     'crystal': 100000,
     'dossier': {1: {('playerBadges', 105): {'unique': False,
                                             'type': 'append',
                                             'value': 1}}},
     'items': {27643: 1,
               38905: 1,
               2590: 1,
               14073: 1,
               16633: 1,
               11769: 1,
               507: 10,
               15390: 1},
     'vehicles': {59985: {'noCrew': True,
                          'customCompensation': (0, 9000),
                          'compensatedNumber': 1},
                  60209: {'noCrew': True,
                          'rent': {'battles': 10}},
                  32001: {'noCrew': True}},
     'customizations': [{'custType': 'camouflage',
                         'id': 15400,
                         'value': 1},
                        {'custType': 'decal',
                         'id': 15574,
                         'value': 1},
                        {'custType': 'paint',
                         'id': 128,
                         'value': 1},
                        {'custType': 'projection_decal',
                         'id': 564,
                         'value': 1},
                        {'custType': 'style',
                         'id': 62,
                         'value': 1},
                        {'custType': 'style',
                         'id': 434,
                         'value': 1},
                        {'custType': 'decal',
                         'id': 14580,
                         'value': 1}],
     'dogTagComponents': [{'unlock': True,
                           'id': 600,
                           'value': 0.0}],
     'premium_plus': 1,
     'tokens': {'tman_template:::men1::::brotherhood::base:': {'count': 1,
                                                               'expires': {'at': 4104777660L}},
                'battle_bonus_x5': {'count': 1,
                                    'expires': {'at': 2524608000L}}},
     'credits': 100000,
     'slots': 5,
     'goodies': {121001: {'count': 3},
                 12852: {'count': 5},
                 13461: {'count': 1}}}


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def printAllLootBoxes(itemsCache=None):
    import pprint
    pprint.pprint(sorted(itemsCache.items.tokens.getLootBoxes().values()))


@dependency.replace_none_kwargs(guiLoader=IGuiLoader)
def getStorageViewInstance(guiLoader=None):
    return first(guiLoader.windowsManager.findViews(lambda v: v.layoutID == R.views.gui_lootboxes.lobby.gui_lootboxes.StorageView()))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def devShowRewardScreenWindow(bonuses=None, itemsCache=None, mainReward='vehicle'):
    if bonuses == 'example':
        bonuses = _getLootBoxBonusesExample()
    elif bonuses == 'example2':
        bonuses = {'tokens': {'lb_comp:credits:1000:cllc:31001': {'count': 1,
                                                        'expires': {'at': 0},
                                                        'limit': 0}},
         'vehicles': [{itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, 0, 144).intCD: {'customCompensation': (0, 10550),
                                                                                       'compensatedNumber': 1}}]}
    elif bonuses is None:
        bonuses = {'premium_plus': 2,
         'gold': 750,
         'credits': 100000,
         'crystal': 500,
         'freeXP': 5000,
         'items': {27131: 20,
                   12025: 1,
                   27643: 10,
                   22009: 1,
                   27387: 10},
         'dossier': {1: {('singleAchievements', 'hw2019Medal'): {'value': 1,
                                                                 'unique': True,
                                                                 'type': 'set'}}},
         'tokens': {'lb_comp:credits:1000:cllc:31001': {'count': 1,
                                                        'expires': {'at': 0},
                                                        'limit': 0}},
         'entitlements': {'cllc_item_31001_1': {'count': 1,
                                                'expires': 0}},
         'vehicles': [{itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, 0, 144).intCD: {'customCompensation': (0, 10550),
                                                                                       'compensatedNumber': 1}}]}
        if mainReward == 'vehicle':
            bonuses['vehicles'] = [{itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, 0, 144).intCD: {}}]
        elif mainReward == 'customization':
            bonuses['customizations'] = [{'custType': 'style',
              'id': 31013,
              'value': 1}]
        elif mainReward == 'cllc':
            bonuses['entitlements'] = {'cllc_item_31001_1': {'count': 1,
                                   'expires': 0}}
        elif mainReward == 'tankmen':
            bonuses['tokens'] = {'tman_template:::tankmen_bp10_3:210060:::brotherhood!commander_sixthSense::tankmen_bp10_3:commander': {'count': 1,
                                                                                                                    'expires': {'at': 0},
                                                                                                                    'limit': 0}}
        elif mainReward == 'vehicleCompensation':
            bonuses['vehicles'] = [{itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, 0, 144).intCD: {'customCompensation': (0, 10550),
                                                                              'compensatedNumber': 1}}]
            bonuses['gold'] += 10550
        elif mainReward == 'customizationCompensation':
            bonuses['customizations'] = [{'custType': 'style',
              'id': 31013,
              'value': 1,
              'customCompensation': (0, 10550)}]
            bonuses['gold'] += 10550
    lootbox = first(itemsCache.items.tokens.getLootBoxes().values())
    showRewardScreenWindow([bonuses], lootbox)
    return


@dependency.replace_none_kwargs(guiLootBoxesCtrl=IGuiLootBoxesController)
def getGuiLootBoxesCtr(guiLootBoxesCtrl=None):
    return guiLootBoxesCtrl


@dependency.replace_none_kwargs(guiLootBoxesCtrl=IGuiLootBoxesController)
def devResetLootBoxesIntro(guiLootBoxesCtrl=None):
    guiLootBoxesCtrl.setSetting(LOOT_BOXES_INTRO_SHOWN, False)
