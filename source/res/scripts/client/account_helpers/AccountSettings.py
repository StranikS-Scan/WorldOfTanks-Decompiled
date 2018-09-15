# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/AccountSettings.py
import base64
import copy
import cPickle as pickle
import constants
import BigWorld
import CommandMapping
import Settings
import Event
from constants import VEHICLE_CLASSES, MAX_VEHICLE_LEVEL
from account_helpers import gameplay_ctx
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.Scaleform.genConsts.PROFILE_CONSTANTS import PROFILE_CONSTANTS
from gui.Scaleform.genConsts.MISSIONS_CONSTANTS import MISSIONS_CONSTANTS
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from copy import deepcopy
KEY_FILTERS = 'filters'
KEY_SETTINGS = 'settings'
KEY_FAVORITES = 'favorites'
KEY_COUNTERS = 'counters'
KEY_NOTIFICATIONS = 'notifications'
CAROUSEL_FILTER_1 = 'CAROUSEL_FILTER_1'
CAROUSEL_FILTER_2 = 'CAROUSEL_FILTER_2'
CAROUSEL_FILTER_CLIENT_1 = 'CAROUSEL_FILTER_CLIENT_1'
MISSION_SELECTOR_FILTER = 'MISSION_SELECTOR_FILTER'
PM_SELECTOR_FILTER = 'PM_SELECTOR_FILTER'
RANKED_CAROUSEL_FILTER_1 = 'RANKED_CAROUSEL_FILTER_1'
RANKED_CAROUSEL_FILTER_2 = 'RANKED_CAROUSEL_FILTER_2'
RANKED_CAROUSEL_FILTER_CLIENT_1 = 'RANKED_CAROUSEL_FILTER_CLIENT_1'
BARRACKS_FILTER = 'barracks_filter'
ORDERS_FILTER = 'ORDERS_FILTER'
CURRENT_VEHICLE = 'current'
GUI_START_BEHAVIOR = 'GUI_START_BEHAVIOR'
EULA_VERSION = 'EULA_VERSION'
FORT_MEMBER_TUTORIAL = 'FORT_MEMBER_TUTORIAL'
IGR_PROMO = 'IGR_PROMO'
PROMO = 'PROMO'
AWARDS = 'awards'
CONTACTS = 'CONTACTS'
BOOSTERS = 'BOOSTERS'
FALLOUT_VEHICLES = 'FALLOUT_VEHICLES'
GOLD_FISH_LAST_SHOW_TIME = 'goldFishWindowShowCooldown'
BOOSTERS_FILTER = 'boostersFilter'
LAST_PROMO_PATCH_VERSION = 'lastPromoPatchVersion'
LAST_RESTORE_NOTIFICATION = 'lastRestoreNotification'
PREVIEW_INFO_PANEL_IDX = 'previewInfoPanelIdx'
NEW_SETTINGS_COUNTER = 'newSettingsCounter'
NEW_HOF_COUNTER = 'newHofCounter'
NEW_LOBBY_TAB_COUNTER = 'newLobbyTabCounter'
PROFILE_TECHNIQUE = 'profileTechnique'
TRAJECTORY_VIEW_HINT_COUNTER = 'trajectoryViewHintCounter'
PROFILE_TECHNIQUE_MEMBER = 'profileTechniqueMember'
SHOW_CRYSTAL_HEADER_BAND = 'showCrystalHeaderBand'
ELEN_NOTIFICATIONS = 'elenNotifications'
DEFAULT_QUEUE = 'defaultQueue'
STORE_TAB = 'store_tab'
STATS_REGULAR_SORTING = 'statsSorting'
STATS_SORTIE_SORTING = 'statsSortingSortie'
MISSIONS_PAGE = 'missions_page'
DEFAULT_VEHICLE_TYPES_FILTER = [False] * len(VEHICLE_CLASSES)
DEFAULT_LEVELS_FILTERS = [False] * MAX_VEHICLE_LEVEL
SHOW_OPT_DEVICE_HINT = 'showOptDeviceHint'
KNOWN_SELECTOR_BATTLES = 'knownSelectorBattles'
DEFAULT_VALUES = {KEY_FILTERS: {STORE_TAB: 0,
               'shop_current': (-1, STORE_CONSTANTS.VEHICLE, False),
               'scroll_to_item': None,
               'shop_vehicle': {'obtainingType': STORE_CONSTANTS.VEHICLE,
                                'selectedTypes': DEFAULT_VEHICLE_TYPES_FILTER,
                                'selectedLevels': DEFAULT_LEVELS_FILTERS,
                                'extra': [STORE_CONSTANTS.LOCKED_EXTRA_NAME]},
               'shop_restoreVehicle': {'obtainingType': STORE_CONSTANTS.RESTORE_VEHICLE,
                                       'selectedTypes': DEFAULT_VEHICLE_TYPES_FILTER,
                                       'selectedLevels': DEFAULT_LEVELS_FILTERS},
               'shop_tradeInVehicle': {'obtainingType': STORE_CONSTANTS.TRADE_IN_VEHICLE,
                                       'selectedTypes': DEFAULT_VEHICLE_TYPES_FILTER,
                                       'selectedLevels': DEFAULT_LEVELS_FILTERS},
               'shop_module': {'fitsType': STORE_CONSTANTS.MY_VEHICLES_ARTEFACT_FIT,
                               'vehicleCD': -1,
                               'extra': [STORE_CONSTANTS.LOCKED_EXTRA_NAME, STORE_CONSTANTS.IN_HANGAR_EXTRA_NAME],
                               'itemTypes': [STORE_CONSTANTS.GUN_MODULE_NAME,
                                             STORE_CONSTANTS.TURRET_MODULE_NAME,
                                             STORE_CONSTANTS.ENGINE_MODULE_NAME,
                                             STORE_CONSTANTS.CHASSIS_MODULE_NAME,
                                             STORE_CONSTANTS.RADIO_MODULE_NAME]},
               'shop_shell': {'fitsType': STORE_CONSTANTS.CURRENT_VEHICLE_SHELL_FIT,
                              'vehicleCD': -1,
                              'itemTypes': [STORE_CONSTANTS.ARMOR_PIERCING_SHELL,
                                            STORE_CONSTANTS.ARMOR_PIERCING_CR_SHELL,
                                            STORE_CONSTANTS.HOLLOW_CHARGE_SHELL,
                                            STORE_CONSTANTS.HIGH_EXPLOSIVE_SHELL]},
               'shop_optionalDevice': {'fitsType': STORE_CONSTANTS.CURRENT_VEHICLE_ARTEFACT_FIT,
                                       'vehicleCD': -1,
                                       'extra': [STORE_CONSTANTS.ON_VEHICLE_EXTRA_NAME]},
               'shop_equipment': {'fitsType': STORE_CONSTANTS.CURRENT_VEHICLE_ARTEFACT_FIT,
                                  'vehicleCD': -1,
                                  'extra': [STORE_CONSTANTS.ON_VEHICLE_EXTRA_NAME]},
               'shop_battleBooster': {'targetType': STORE_CONSTANTS.ALL_KIND_FIT},
               'inventory_current': (-1, STORE_CONSTANTS.VEHICLE, False),
               'inventory_vehicle': {'selectedTypes': DEFAULT_VEHICLE_TYPES_FILTER,
                                     'selectedLevels': DEFAULT_LEVELS_FILTERS,
                                     'extra': [STORE_CONSTANTS.BROCKEN_EXTRA_NAME, STORE_CONSTANTS.LOCKED_EXTRA_NAME]},
               'inventory_module': {'fitsType': STORE_CONSTANTS.MY_VEHICLES_ARTEFACT_FIT,
                                    'vehicleCD': -1,
                                    'extra': [],
                                    'itemTypes': [STORE_CONSTANTS.GUN_MODULE_NAME,
                                                  STORE_CONSTANTS.TURRET_MODULE_NAME,
                                                  STORE_CONSTANTS.ENGINE_MODULE_NAME,
                                                  STORE_CONSTANTS.CHASSIS_MODULE_NAME,
                                                  STORE_CONSTANTS.RADIO_MODULE_NAME]},
               'inventory_shell': {'fitsType': STORE_CONSTANTS.CURRENT_VEHICLE_SHELL_FIT,
                                   'vehicleCD': -1,
                                   'itemTypes': [STORE_CONSTANTS.ARMOR_PIERCING_SHELL,
                                                 STORE_CONSTANTS.ARMOR_PIERCING_CR_SHELL,
                                                 STORE_CONSTANTS.HOLLOW_CHARGE_SHELL,
                                                 STORE_CONSTANTS.HIGH_EXPLOSIVE_SHELL]},
               'inventory_optionalDevice': {'fitsType': STORE_CONSTANTS.CURRENT_VEHICLE_ARTEFACT_FIT,
                                            'vehicleCD': -1,
                                            'extra': [STORE_CONSTANTS.ON_VEHICLE_EXTRA_NAME]},
               'inventory_equipment': {'fitsType': STORE_CONSTANTS.CURRENT_VEHICLE_ARTEFACT_FIT,
                                       'vehicleCD': -1,
                                       'extra': [STORE_CONSTANTS.ON_VEHICLE_EXTRA_NAME]},
               'inventory_battleBooster': {'targetType': STORE_CONSTANTS.ALL_KIND_FIT},
               MISSIONS_PAGE: {'hideDone': False,
                               'hideUnavailable': False},
               CAROUSEL_FILTER_1: {'ussr': False,
                                   'germany': False,
                                   'usa': False,
                                   'china': False,
                                   'france': False,
                                   'uk': False,
                                   'japan': False,
                                   'czech': False,
                                   'sweden': False,
                                   'poland': False,
                                   'lightTank': False,
                                   'mediumTank': False,
                                   'heavyTank': False,
                                   'SPG': False,
                                   'AT-SPG': False,
                                   'level_1': False,
                                   'level_2': False,
                                   'level_3': False,
                                   'level_4': False,
                                   'level_5': False,
                                   'level_6': False,
                                   'level_7': False,
                                   'level_8': False,
                                   'level_9': False,
                                   'level_10': False},
               CAROUSEL_FILTER_2: {'premium': False,
                                   'elite': False,
                                   'igr': False,
                                   'rented': True,
                                   'event': True,
                                   'favorite': False,
                                   'bonus': False},
               CAROUSEL_FILTER_CLIENT_1: {'searchNameVehicle': ''},
               RANKED_CAROUSEL_FILTER_1: {'ussr': False,
                                          'germany': False,
                                          'usa': False,
                                          'china': False,
                                          'france': False,
                                          'uk': False,
                                          'japan': False,
                                          'czech': False,
                                          'sweden': False,
                                          'poland': False,
                                          'lightTank': False,
                                          'mediumTank': False,
                                          'heavyTank': False,
                                          'SPG': False,
                                          'AT-SPG': False,
                                          'level_1': False,
                                          'level_2': False,
                                          'level_3': False,
                                          'level_4': False,
                                          'level_5': False,
                                          'level_6': False,
                                          'level_7': False,
                                          'level_8': False,
                                          'level_9': False,
                                          'level_10': True},
               RANKED_CAROUSEL_FILTER_2: {'premium': False,
                                          'elite': False,
                                          'igr': False,
                                          'rented': True,
                                          'event': True,
                                          'gameMode': False,
                                          'favorite': False,
                                          'bonus': False},
               RANKED_CAROUSEL_FILTER_CLIENT_1: {'searchNameVehicle': ''},
               MISSION_SELECTOR_FILTER: {'inventory': False},
               PM_SELECTOR_FILTER: {'inventory': False},
               BARRACKS_FILTER: {'nation': -1,
                                 'role': 'None',
                                 'tankType': 'None',
                                 'location': 3,
                                 'nationID': None},
               ORDERS_FILTER: {'isSelected': False},
               GUI_START_BEHAVIOR: {'isFreeXPInfoDialogShowed': False,
                                    'isRankedWelcomeViewShowed': False,
                                    'isRankedWelcomeViewStarted': False,
                                    'isEpicRandomCheckboxClicked': False},
               EULA_VERSION: {'version': 0},
               FORT_MEMBER_TUTORIAL: {'wasShown': False},
               IGR_PROMO: {'wasShown': False},
               BOOSTERS: {'wasShown': False},
               CONTACTS: {'showOfflineUsers': True,
                          'showOthersCategory': True},
               GOLD_FISH_LAST_SHOW_TIME: 0,
               BOOSTERS_FILTER: 0,
               'cs_intro_view_vehicle': {'nation': -1,
                                         'vehicleType': 'none',
                                         'isMain': False,
                                         'level': -1,
                                         'compatibleOnly': True},
               'cs_list_view_vehicle': {'nation': -1,
                                        'vehicleType': 'none',
                                        'isMain': False,
                                        'level': -1,
                                        'compatibleOnly': True},
               'cs_unit_view_vehicle': {'nation': -1,
                                        'vehicleType': 'none',
                                        'isMain': False,
                                        'level': -1,
                                        'compatibleOnly': True},
               'cs_unit_view_settings': {'nation': -1,
                                         'vehicleType': 'none',
                                         'isMain': False,
                                         'level': -1,
                                         'compatibleOnly': True},
               PROMO: {},
               AWARDS: {'vehicleResearchAward': -1,
                        'victoryAward': -1,
                        'battlesCountAward': -1,
                        'pveBattlesCountAward': -1},
               PROFILE_TECHNIQUE: {'selectedColumn': 4,
                                   'selectedColumnSorting': 'descending',
                                   'isInHangarSelected': False},
               PROFILE_TECHNIQUE_MEMBER: {'selectedColumn': 4,
                                          'selectedColumnSorting': 'descending'}},
 KEY_FAVORITES: {CURRENT_VEHICLE: 0,
                 FALLOUT_VEHICLES: {}},
 KEY_SETTINGS: {'unitWindow': {'selectedIntroVehicles': []},
                'vehicleSellDialog': {'isOpened': False},
                KNOWN_SELECTOR_BATTLES: set(),
                'tankmanDropSkillIdx': 0,
                'cursor': False,
                'arcade': {'mixing': {'alpha': 100,
                                      'type': 3},
                           'gunTag': {'alpha': 100,
                                      'type': 9},
                           'centralTag': {'alpha': 100,
                                          'type': 8},
                           'net': {'alpha': 100,
                                   'type': 0},
                           'reloader': {'alpha': 100,
                                        'type': 0},
                           'condition': {'alpha': 100,
                                         'type': 0},
                           'cassette': {'alpha': 100,
                                        'type': 0},
                           'reloaderTimer': {'alpha': 100,
                                             'type': 0},
                           'zoomIndicator': {'alpha': 100,
                                             'type': 0}},
                'sniper': {'mixing': {'alpha': 90,
                                      'type': 0},
                           'gunTag': {'alpha': 90,
                                      'type': 0},
                           'centralTag': {'alpha': 90,
                                          'type': 0},
                           'net': {'alpha': 90,
                                   'type': 0},
                           'reloader': {'alpha': 90,
                                        'type': 0},
                           'condition': {'alpha': 90,
                                         'type': 0},
                           'cassette': {'alpha': 90,
                                        'type': 0},
                           'reloaderTimer': {'alpha': 100,
                                             'type': 0},
                           'zoomIndicator': {'alpha': 100,
                                             'type': 0}},
                'markers': {'ally': {'markerBaseIcon': False,
                                     'markerBaseLevel': False,
                                     'markerBaseHpIndicator': False,
                                     'markerBaseDamage': True,
                                     'markerBaseHp': 0,
                                     'markerBaseVehicleName': False,
                                     'markerBasePlayerName': True,
                                     'markerAltIcon': True,
                                     'markerAltLevel': True,
                                     'markerAltHpIndicator': True,
                                     'markerAltDamage': True,
                                     'markerAltHp': 1,
                                     'markerAltVehicleName': True,
                                     'markerAltPlayerName': False},
                            'enemy': {'markerBaseIcon': False,
                                      'markerBaseLevel': False,
                                      'markerBaseHpIndicator': False,
                                      'markerBaseDamage': True,
                                      'markerBaseHp': 0,
                                      'markerBaseVehicleName': False,
                                      'markerBasePlayerName': True,
                                      'markerAltIcon': True,
                                      'markerAltLevel': True,
                                      'markerAltHpIndicator': True,
                                      'markerAltDamage': True,
                                      'markerAltHp': 1,
                                      'markerAltVehicleName': True,
                                      'markerAltPlayerName': False},
                            'dead': {'markerBaseIcon': False,
                                     'markerBaseLevel': False,
                                     'markerBaseHpIndicator': False,
                                     'markerBaseDamage': True,
                                     'markerBaseHp': 0,
                                     'markerBaseVehicleName': False,
                                     'markerBasePlayerName': True,
                                     'markerAltIcon': True,
                                     'markerAltLevel': True,
                                     'markerAltHpIndicator': True,
                                     'markerAltDamage': True,
                                     'markerAltHp': 1,
                                     'markerAltVehicleName': True,
                                     'markerAltPlayerName': False}},
                'showVehicleIcon': False,
                'showVehicleLevel': False,
                'showExInf4Destroyed': False,
                'ingameHelpVersion': -1,
                'isColorBlind': False,
                'useServerAim': False,
                'showVehiclesCounter': True,
                'minimapAlpha': 0,
                'minimapSize': 1,
                'minimapRespawnSize': 0,
                'minimapViewRange': True,
                'minimapMaxViewRange': True,
                'minimapDrawRange': True,
                'increasedZoom': True,
                'sniperModeByShift': True,
                'nationalVoices': False,
                'enableVoIP': True,
                'replayEnabled': 1,
                'players_panel': {'state': 2,
                                  'showLevels': True,
                                  'showTypes': True},
                'epic_random_players_panel': {'state': 5},
                'gameplayMask': gameplay_ctx.getDefaultMask(),
                'statsSorting': {'iconType': 'tank',
                                 'sortDirection': 'descending'},
                'statsSortingSortie': {'iconType': 'tank',
                                       'sortDirection': 'descending'},
                'backDraftInvert': False,
                'quests': {'lastVisitTime': -1,
                           'visited': [],
                           'naVisited': [],
                           'personalMissions': {'introShown': False,
                                                'operationsVisited': set(),
                                                'headerAlert': False}},
                'checkBoxConfirmator': {'questsConfirmDialogShow': True},
                'customization': {},
                'showVehModelsOnMap': 0,
                'battleLoadingInfo': 1,
                'battleLoadingRankedInfo': 1,
                'relativePower': False,
                'relativeArmor': False,
                'relativeMobility': False,
                'relativeVisibility': False,
                'relativeCamouflage': False,
                'interfaceScale': 0,
                DEFAULT_QUEUE: constants.QUEUE_TYPE.SANDBOX,
                'medKitInstalled': False,
                'repairKitInstalled': False,
                'fireExtinguisherInstalled': False,
                'PveTriggerShown': False,
                LAST_PROMO_PATCH_VERSION: '',
                LAST_RESTORE_NOTIFICATION: None,
                'dynamicRange': 0,
                'soundDevice': 0,
                'bassBoost': False,
                'lowQualitySound': False,
                'nightMode': False,
                'bulbVoices': 'lightbulb',
                PREVIEW_INFO_PANEL_IDX: 0,
                'carouselType': 0,
                'doubleCarouselType': 0,
                'vehicleCarouselStats': True,
                'siegeModeHintCounter': 10,
                NEW_SETTINGS_COUNTER: {'FeedbackSettings': {'feedbackDamageLog': {'damageLogAssistStun': True},
                                                            'feedbackBattleEvents': {'battleEventsEnemyAssistStun': True}},
                                       'GameSettings': {'gameplay_epicStandard': True,
                                                        'c11nHistoricallyAccurate': True}},
                TRAJECTORY_VIEW_HINT_COUNTER: 10,
                SHOW_OPT_DEVICE_HINT: True,
                'c11nHistoricallyAccurate': True},
 KEY_COUNTERS: {NEW_HOF_COUNTER: {PROFILE_CONSTANTS.HOF_ACHIEVEMENTS_BUTTON: True,
                                  PROFILE_CONSTANTS.HOF_VEHICLES_BUTTON: True,
                                  PROFILE_CONSTANTS.HOF_VIEW_RATING_BUTTON: True},
                NEW_LOBBY_TAB_COUNTER: {}},
 KEY_NOTIFICATIONS: {ELEN_NOTIFICATIONS: {MISSIONS_CONSTANTS.ELEN_EVENT_STARTED_NOTIFICATION: set(),
                                          MISSIONS_CONSTANTS.ELEN_EVENT_FINISHED_NOTIFICATION: set(),
                                          MISSIONS_CONSTANTS.ELEN_EVENT_TAB_VISITED: set()}}}

def _filterAccountSection(dataSec):
    for key, section in dataSec.items()[:]:
        if key == 'account':
            yield (key, section)


def _pack(value):
    return base64.b64encode(pickle.dumps(value))


def _unpack(value):
    return pickle.loads(base64.b64decode(value))


class AccountSettings(object):
    onSettingsChanging = Event.Event()
    version = 33
    __cache = {'login': None,
     'section': None}
    __isFirstRun = True

    @staticmethod
    def clearCache():
        AccountSettings.__cache['login'] = None
        AccountSettings.__cache['section'] = None
        return

    @staticmethod
    def __readSection(ds, name):
        if not ds.has_key(name):
            ds.write(name, '')
        return ds[name]

    @staticmethod
    def __readUserSection():
        if AccountSettings.__isFirstRun:
            AccountSettings.convert()
            AccountSettings.invalidateNewSettingsCounter()
            AccountSettings.__isFirstRun = False
        userLogin = getattr(BigWorld.player(), 'name', '')
        if AccountSettings.__cache['login'] != userLogin:
            ads = AccountSettings.__readSection(Settings.g_instance.userPrefs, Settings.KEY_ACCOUNT_SETTINGS)
            for key, section in ads.items():
                if key == 'account' and section.readString('login') == userLogin:
                    AccountSettings.__cache['login'] = userLogin
                    AccountSettings.__cache['section'] = section
                    break
            else:
                newSection = ads.createSection('account')
                newSection.writeString('login', userLogin)
                AccountSettings.__cache['login'] = userLogin
                AccountSettings.__cache['section'] = newSection

        return AccountSettings.__cache['section']

    @staticmethod
    def convert():
        ads = AccountSettings.__readSection(Settings.g_instance.userPrefs, Settings.KEY_ACCOUNT_SETTINGS)
        currVersion = ads.readInt('version', 0)
        if currVersion != AccountSettings.version:
            if currVersion < 1:
                for key, section in ads.items()[:]:
                    newSection = ads.createSection('account')
                    newSection.copy(section)
                    newSection.writeString('login', key)
                    ads.deleteSection(key)

            if currVersion < 2:
                MARKER_SETTINGS_MAP = {'showVehicleIcon': 'markerBaseIcon',
                 'showVehicleLevel': 'markerBaseLevel',
                 'showExInf4Destroyed': 'markerBaseDead'}
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings.__readSection(section, KEY_SETTINGS)
                        defaultMarker = DEFAULT_VALUES[KEY_SETTINGS]['markers'].copy()
                        needUpdate = False
                        for key1, section1 in accSettings.items()[:]:
                            if key1 in MARKER_SETTINGS_MAP:
                                defaultMarker[MARKER_SETTINGS_MAP[key1]] = pickle.loads(base64.b64decode(accSettings.readString(key1)))
                                accSettings.deleteSection(key1)
                                needUpdate = True

                        if needUpdate:
                            accSettings.write('markers', base64.b64encode(pickle.dumps(defaultMarker)))

            if currVersion < 3:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings.__readSection(section, KEY_SETTINGS)
                        defaultCursor = DEFAULT_VALUES[KEY_SETTINGS]['arcade'].copy()
                        cassetteDefValues = DEFAULT_VALUES[KEY_SETTINGS]['arcade'].copy()['cassette']
                        for key1, section1 in accSettings.items()[:]:
                            if key1 == 'cursors':
                                defaultCursor = pickle.loads(base64.b64decode(section1.asString))
                                defaultCursor['cassette'] = cassetteDefValues
                                accSettings.deleteSection(key1)
                                break

                        accSettings.write('cursors', base64.b64encode(pickle.dumps(defaultCursor)))

            if currVersion < 4:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings.__readSection(section, KEY_SETTINGS)
                        defaultCursor = DEFAULT_VALUES[KEY_SETTINGS]['arcade'].copy()
                        for key1, section1 in accSettings.items()[:]:
                            if key1 == 'cursors':
                                defaultCursor = pickle.loads(base64.b64decode(section1.asString))
                                accSettings.deleteSection(key1)
                                break

                        accSettings.write('arcade', base64.b64encode(pickle.dumps(defaultCursor)))

            if currVersion < 5:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings.__readSection(section, KEY_SETTINGS)
                        for key1, section1 in accSettings.items()[:]:
                            if key1 == 'markers':
                                accSettings.deleteSection(key1)

            if currVersion < 6:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings.__readSection(section, KEY_SETTINGS)
                        defaultSorting = DEFAULT_VALUES[KEY_SETTINGS]['statsSorting'].copy()
                        accSettings.write('statsSorting', base64.b64encode(pickle.dumps(defaultSorting)))

            if currVersion < 7:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings.__readSection(section, KEY_SETTINGS)
                        result = DEFAULT_VALUES[KEY_SETTINGS]['sniper'].copy()
                        for settingName, settingPickle in accSettings.items()[:]:
                            if settingName == 'sniper':
                                settingValues = pickle.loads(base64.b64decode(settingPickle.asString))
                                accSettings.deleteSection(settingName)
                                try:
                                    for k, v in settingValues.iteritems():
                                        newName = k[3].lower() + k[4:]
                                        result[newName] = v

                                except Exception:
                                    pass

                            break

                        accSettings.write('sniper', base64.b64encode(pickle.dumps(result)))

            if currVersion < 8:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accFilters = AccountSettings.__readSection(section, KEY_FILTERS)
                        for filterName, filterPickle in accFilters.items()[:]:
                            if filterName in ('cs_intro_view_vehicle', 'cs_list_view_vehicle', 'cs_unit_view_vehicle', 'cs_unit_view_settings'):
                                result = DEFAULT_VALUES[KEY_FILTERS][filterName].copy()
                                value = pickle.loads(base64.b64decode(filterPickle.asString))
                                result.update(value)
                                accFilters.write(filterName, base64.b64encode(pickle.dumps(result)))

            if currVersion < 9:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accFilters = AccountSettings.__readSection(section, KEY_FILTERS)
                        for filterName, filterPickle in accFilters.items()[:]:
                            if filterName in ('cs_intro_view_vehicle', 'cs_list_view_vehicle', 'cs_unit_view_vehicle', 'cs_unit_view_settings'):
                                defaults = DEFAULT_VALUES[KEY_FILTERS][filterName].copy()
                                userValue = pickle.loads(base64.b64decode(filterPickle.asString))
                                userValue['compatibleOnly'] = defaults['compatibleOnly']
                                accFilters.write(filterName, base64.b64encode(pickle.dumps(userValue)))

            if currVersion < 10:
                from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings.__readSection(section, KEY_SETTINGS)
                        result = set(DEFAULT_VALUES[KEY_SETTINGS][KNOWN_SELECTOR_BATTLES]).copy()
                        for key1, section1 in accSettings.items()[:]:
                            if key1 == 'unitWindow':
                                unitWindowVal = pickle.loads(base64.b64decode(section1.asString))
                                if 'isOpened' in unitWindowVal:
                                    if unitWindowVal['isOpened']:
                                        result.add(SELECTOR_BATTLE_TYPES.UNIT)
                                        accSettings.write(KNOWN_SELECTOR_BATTLES, base64.b64encode(pickle.dumps(result)))
                                    section1.deleteSection('isOpened')
                                    break

            if currVersion < 11:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings.__readSection(section, KEY_SETTINGS)
                        defaultSorting = DEFAULT_VALUES[KEY_SETTINGS]['statsSortingSortie'].copy()
                        accSettings.write('statsSortingSortie', base64.b64encode(pickle.dumps(defaultSorting)))

            if currVersion < 12:
                from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
                for key, section in _filterAccountSection(ads):
                    accSettings = AccountSettings.__readSection(section, KEY_SETTINGS)
                    if KNOWN_SELECTOR_BATTLES in accSettings.keys():
                        known = _unpack(accSettings[KNOWN_SELECTOR_BATTLES].asString)
                        if SELECTOR_BATTLE_TYPES.UNIT in known:
                            known.remove(SELECTOR_BATTLE_TYPES.UNIT)
                            accSettings.write(KNOWN_SELECTOR_BATTLES, _pack(known))
                    if 'unitWindow' in accSettings.keys():
                        accSettings.deleteSection('unitWindow')

            if currVersion < 13:
                enableVoIPVal = False
                if Settings.g_instance.userPrefs.has_key('enableVoIP'):
                    enableVoIPVal = Settings.g_instance.userPrefs.readBool('enableVoIP')
                for key, section in _filterAccountSection(ads):
                    AccountSettings.__readSection(section, KEY_SETTINGS).write('enableVoIP', _pack(enableVoIPVal))

                Settings.g_instance.userPrefs.deleteSection('enableVoIP')
            if currVersion < 17:
                for key, section in ads.items()[:]:
                    if key == 'account':
                        accSettings = AccountSettings.__readSection(section, KEY_FAVORITES)
                        for key1, section1 in accSettings.items()[:]:
                            if key1 == FALLOUT_VEHICLES:
                                accSettings.deleteSection(key1)

            if currVersion < 18:
                cmSection = AccountSettings.__readSection(Settings.g_instance.userPrefs, Settings.KEY_COMMAND_MAPPING)
                for command, section in cmSection.items()[:]:
                    newSection = None
                    satelliteKeys = ''
                    fireKey = AccountSettings.__readSection(section, 'fireKey').asString
                    if fireKey == 'KEY_SPACE':
                        if command == 'CMD_BLOCK_TRACKS':
                            pass
                        elif command == 'CMD_STOP_UNTIL_FIRE':
                            satelliteKeys = AccountSettings.__readSection(section, 'satelliteKeys').asString
                            cmSection.deleteSection('CMD_STOP_UNTIL_FIRE')
                            newSection = cmSection.createSection('CMD_STOP_UNTIL_FIRE')
                        else:
                            newSection = cmSection.createSection('CMD_BLOCK_TRACKS')
                    if newSection is not None:
                        newSection.writeString('fireKey', 'KEY_NONE')
                        newSection.writeString('satelliteKeys', satelliteKeys)

                CommandMapping.g_instance.restoreUserConfig()
            if currVersion < 19:
                pass
            if currVersion < 20:
                for key, section in _filterAccountSection(ads):
                    accSettings = AccountSettings.__readSection(section, KEY_SETTINGS)
                    accSettings.write('battleLoadingInfo', base64.b64encode(pickle.dumps(0)))
                    AccountSettings.__readSection(section, KEY_FILTERS).deleteSection('joinCommandPressed')

            if currVersion < 21:
                import SoundGroups
                SoundGroups.g_instance.setMasterVolume(1.0)
                SoundGroups.g_instance.setVolume('music', 1.0)
                SoundGroups.g_instance.setVolume('vehicles', 1.0)
                SoundGroups.g_instance.setVolume('effects', 1.0)
                SoundGroups.g_instance.setVolume('gui', 1.0)
                SoundGroups.g_instance.setVolume('ambient', 1.0)
                SoundGroups.g_instance.savePreferences()
            if currVersion < 22:
                pass
            if currVersion < 23:
                for key, section in _filterAccountSection(ads):
                    AccountSettings.__readSection(section, KEY_SETTINGS).deleteSection('FootballVehSelectedOnce')

            if currVersion < 24:
                for key, section in _filterAccountSection(ads):
                    AccountSettings.__readSection(section, KEY_SETTINGS).deleteSection('FootballCustTriggerShown')
                    AccountSettings.__readSection(section, KEY_SETTINGS).deleteSection('FootballVehSelectedOnce')

            if currVersion < 24:
                import SoundGroups
                SoundGroups.g_instance.setVolume('music_hangar', 1.0)
                SoundGroups.g_instance.setVolume('voice', 1.0)
                SoundGroups.g_instance.setVolume('ev_ambient', 0.8)
                SoundGroups.g_instance.setVolume('ev_effects', 0.8)
                SoundGroups.g_instance.setVolume('ev_gui', 0.8)
                SoundGroups.g_instance.setVolume('ev_music', 0.8)
                SoundGroups.g_instance.setVolume('ev_vehicles', 0.8)
                SoundGroups.g_instance.setVolume('ev_voice', 0.8)
                SoundGroups.g_instance.savePreferences()
            if currVersion < 25:
                for key, section in _filterAccountSection(ads):
                    accFilters = AccountSettings.__readSection(section, KEY_FILTERS)
                    for filterName, filterPickle in accFilters.items():
                        if filterName in ('shop_vehicle', 'shop_module', 'shop_shell', 'shop_optionalDevice', 'shop_equipment', 'inventory_vehicle', 'inventory_module', 'inventory_shell', 'inventory_optionalDevice', 'inventory_equipment'):
                            defaults = DEFAULT_VALUES[KEY_FILTERS][filterName].copy()
                            accFilters.write(filterName, base64.b64encode(pickle.dumps(defaults)))

            if currVersion < 26:
                for key, section in _filterAccountSection(ads):
                    AccountSettings.__readSection(section, KEY_SETTINGS).deleteSection('new_customization_items')
                    AccountSettings.__readSection(section, KEY_SETTINGS).deleteSection('statsSortingEvent')

            if currVersion < 27:
                legacyToNewMode = {'hidden': 0,
                 'short': 1,
                 'medium': 2,
                 'medium2': 3,
                 'large': 4}
                for key, section in _filterAccountSection(ads):
                    settingsSection = AccountSettings.__readSection(section, KEY_SETTINGS)
                    if 'players_panel' in settingsSection.keys():
                        panelSettings = _unpack(settingsSection['players_panel'].asString)
                        if 'state' in panelSettings:
                            presentMode = panelSettings['state']
                            if presentMode in legacyToNewMode.keys():
                                panelSettings['state'] = legacyToNewMode[presentMode]
                                settingsSection.write('players_panel', _pack(panelSettings))

            if currVersion < 28:
                for key, section in _filterAccountSection(ads):
                    filters = AccountSettings.__readSection(section, KEY_FILTERS)
                    filters.deleteSection('lastClubOpenedForApps')
                    filters.deleteSection('showInviteCommandBtnAnimation')

            if currVersion < 29:
                getSection = AccountSettings.__readSection
                cmSection = getSection(Settings.g_instance.userPrefs, Settings.KEY_COMMAND_MAPPING)
                cmdItems = cmSection.items()[:]
                if cmdItems:
                    checkUserKeyBinding = AccountSettings.__checkUserKeyBinding
                    hasKeyG, hasCmdVoice, bindedG = checkUserKeyBinding('KEY_G', 'CMD_VOICECHAT_ENABLE', cmdItems)
                    hasKeyH, hasCmdHorn, bindedH = checkUserKeyBinding('KEY_H', 'CMD_USE_HORN', cmdItems)
                    if hasCmdHorn:
                        cmSection.deleteSection('CMD_USE_HORN')
                    isKeyGDefault = not hasKeyG or bindedG
                    keyForCmdTraject = 'KEY_G' if isKeyGDefault else 'KEY_NONE'
                    getSection(cmSection, 'CMD_CM_TRAJECTORY_VIEW').writeString('fireKey', keyForCmdTraject)
                    if not hasCmdVoice or bindedG:
                        isKeyHDefault = not hasKeyH or bindedH
                        keyForCmdVoice = 'KEY_H' if isKeyHDefault else 'KEY_NONE'
                        getSection(cmSection, 'CMD_VOICECHAT_ENABLE').writeString('fireKey', keyForCmdVoice)
                    CommandMapping.g_instance.restoreUserConfig()
            if currVersion < 29:
                for key, section in _filterAccountSection(ads):
                    filtersSection = AccountSettings.__readSection(section, KEY_FILTERS)
                    if 'searchNameVehicle' in filtersSection.keys():
                        searchName = _unpack(filtersSection['searchNameVehicle'].asString)
                        filtersSection.write(CAROUSEL_FILTER_CLIENT_1, _pack({'searchNameVehicle': searchName}))
                        filtersSection.deleteSection('searchNameVehicle')

            if currVersion < 30:
                for key, section in _filterAccountSection(ads):
                    accFilters = AccountSettings.__readSection(section, KEY_FILTERS)
                    for filterName, filterPickle in accFilters.items():
                        if filterName in ('shop_vehicle', 'inventory_vehicle', 'shop_current', 'inventory_current', 'shop_tradeInVehicle', 'shop_restoreVehicle'):
                            defaults = DEFAULT_VALUES[KEY_FILTERS][filterName]
                            accFilters.write(filterName, base64.b64encode(pickle.dumps(defaults)))

            if currVersion < 32:
                for _, section in _filterAccountSection(ads):
                    accSettings = AccountSettings.__readSection(section, KEY_SETTINGS)
                    accSettings.deleteSection(NEW_SETTINGS_COUNTER)

            if currVersion < 32:
                for _, section in _filterAccountSection(ads):
                    accSettings = AccountSettings.__readSection(section, KEY_SETTINGS)
                    accSettings.deleteSection(SHOW_CRYSTAL_HEADER_BAND)

            if currVersion < 33:
                for _, section in _filterAccountSection(ads):
                    accSettings = AccountSettings.__readSection(section, KEY_SETTINGS)
                    if 'quests' in accSettings.keys():
                        quests = _unpack(accSettings['quests'].asString)
                        if 'potapov' in quests:
                            newVersion = quests.pop('potapov')
                            newVersion['operationsVisited'] = newVersion.pop('tilesVisited')
                            accSettings.write('quests', _pack(quests))

            ads.writeInt('version', AccountSettings.version)
        return

    @staticmethod
    def getFilterDefault(name):
        return DEFAULT_VALUES[KEY_FILTERS].get(name, None)

    @staticmethod
    def invalidateNewSettingsCounter():
        ads = AccountSettings.__readSection(Settings.g_instance.userPrefs, Settings.KEY_ACCOUNT_SETTINGS)
        currentDefaults = AccountSettings.getSettingsDefault(NEW_SETTINGS_COUNTER)
        filtered = _filterAccountSection(ads)
        for _, section in filtered:
            accSettings = AccountSettings.__readSection(section, KEY_SETTINGS)
            if NEW_SETTINGS_COUNTER in accSettings.keys():
                savedNewSettingsCounters = _unpack(accSettings[NEW_SETTINGS_COUNTER].asString)
                newSettingsCounters = AccountSettings.updateNewSettingsCounter(currentDefaults, savedNewSettingsCounters)
                accSettings.write(NEW_SETTINGS_COUNTER, _pack(newSettingsCounters))

    @staticmethod
    def getFilterDefaults(names):
        result = {}
        for name in names:
            result.update(AccountSettings.getFilterDefault(name))

        return result

    @staticmethod
    def getFilter(name):
        return AccountSettings.__getValue(name, KEY_FILTERS)

    @staticmethod
    def setFilter(name, value):
        AccountSettings.__setValue(name, value, KEY_FILTERS)

    @staticmethod
    def getSettingsDefault(name):
        return DEFAULT_VALUES[KEY_SETTINGS].get(name, None)

    @staticmethod
    def getSettings(name):
        return AccountSettings.__getValue(name, KEY_SETTINGS)

    @staticmethod
    def setSettings(name, value):
        AccountSettings.__setValue(name, value, KEY_SETTINGS)

    @staticmethod
    def getFavorites(name):
        return AccountSettings.__getValue(name, KEY_FAVORITES)

    @staticmethod
    def setFavorites(name, value):
        AccountSettings.__setValue(name, value, KEY_FAVORITES)

    @staticmethod
    def getCounters(name):
        return AccountSettings.__getValue(name, KEY_COUNTERS)

    @staticmethod
    def setCounters(name, value):
        AccountSettings.__setValue(name, value, KEY_COUNTERS)

    @staticmethod
    def getNotifications(name):
        return AccountSettings.__getValue(name, KEY_NOTIFICATIONS)

    @staticmethod
    def setNotifications(name, value):
        AccountSettings.__setValue(name, value, KEY_NOTIFICATIONS)

    @staticmethod
    def updateNewSettingsCounter(defaultDict, savedDict):
        finalDict = dict()

        def recursiveStep(defaultDict, savedDict, finalDict):
            for key in defaultDict:
                defaultElement = defaultDict[key]
                savedElement = savedDict.get(key, None)
                if type(defaultElement) == dict:
                    if savedElement is not None and type(savedElement) == dict:
                        finalDict[key] = dict()
                        recursiveStep(defaultElement, savedElement, finalDict[key])
                    else:
                        finalDict[key] = deepcopy(defaultElement)
                if savedElement is not None:
                    finalDict[key] = savedElement
                finalDict[key] = defaultElement

            return

        recursiveStep(defaultDict, savedDict, finalDict)
        return finalDict

    @staticmethod
    def __getValue(name, type):
        if DEFAULT_VALUES[type].has_key(name):
            fds = AccountSettings.__readSection(AccountSettings.__readUserSection(), type)
            try:
                if fds.has_key(name):
                    return pickle.loads(base64.b64decode(fds.readString(name)))
            except:
                if constants.IS_DEVELOPMENT:
                    LOG_CURRENT_EXCEPTION()

            return copy.deepcopy(DEFAULT_VALUES[type][name])
        else:
            return None

    @staticmethod
    def __setValue(name, value, type):
        assert DEFAULT_VALUES[type].has_key(name)
        if AccountSettings.__getValue(name, type) != value:
            fds = AccountSettings.__readSection(AccountSettings.__readUserSection(), type)
            if DEFAULT_VALUES[type][name] != value:
                fds.write(name, base64.b64encode(pickle.dumps(value)))
            else:
                fds.deleteSection(name)
            AccountSettings.onSettingsChanging(name, value)

    @staticmethod
    def __checkUserKeyBinding(key=None, command=None, commandSectionItems=None):
        """
        Method is used to check some user key binding
        """
        if commandSectionItems is None:
            commandSection = AccountSettings.__readSection(Settings.g_instance.userPrefs, Settings.KEY_COMMAND_MAPPING)
            commandSectionItems = commandSection.items()[:]
        hasKey, hasCommand, binded = False, False, False
        for cmd, section in commandSectionItems:
            fireKey = AccountSettings.__readSection(section, 'fireKey').asString
            if key is not None and fireKey == key:
                if cmd == command:
                    return (True, True, True)
                hasKey = True
            if command is not None and cmd == command:
                hasCommand = True

        return (hasKey, hasCommand, binded)
