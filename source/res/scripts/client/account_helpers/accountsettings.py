# Embedded file name: scripts/client/account_helpers/AccountSettings.py
import base64
import copy
import constants
import BigWorld
import Settings
import Event
import cPickle as pickle
from constants import FORT_BUILDING_TYPE as _FBT
from account_helpers import gameplay_ctx
from debug_utils import LOG_CURRENT_EXCEPTION
KEY_FILTERS = 'filters'
KEY_SETTINGS = 'settings'
KEY_FAVORITES = 'favorites'
CAROUSEL_FILTER = 'CAROUSEL_FILTER'
BARRACKS_FILTER = 'barracks_filter'
ORDERS_FILTER = 'ORDERS_FILTER'
VEHICLE_BUY_WINDOW_SETTINGS = 'vehicleBuyWindowSettings'
CURRENT_VEHICLE = 'current'
GUI_START_BEHAVIOR = 'GUI_START_BEHAVIOR'
EULA_VERSION = 'EULA_VERSION'
FORT_MEMBER_TUTORIAL = 'FORT_MEMBER_TUTORIAL'
IGR_PROMO = 'IGR_PROMO'
PROMO = 'PROMO'
AWARDS = 'awards'
CONTACTS = 'CONTACTS'
KNOWN_SELECTOR_BATTLES = 'knownSelectorBattles'
DEFAULT_VALUES = {KEY_FILTERS: {'shop_current': (-1, 'vehicle'),
               'shop_vehicle': (5, 'lightTank', 'mediumTank', 'heavyTank', 'at-spg', 'spg', 'locked'),
               'shop_module': (5, 'vehicleGun', 'vehicleTurret', 'vehicleEngine', 'vehicleChassis', 'vehicleRadio', 'myVehicles', 0, 'locked', 'inHangar'),
               'shop_shell': (4, 'ARMOR_PIERCING', 'ARMOR_PIERCING_CR', 'HOLLOW_CHARGE', 'HIGH_EXPLOSIVE', 'myVehicleGun', 0),
               'shop_optionalDevice': ('myVehicle', 0, 'onVehicle'),
               'shop_equipment': ('myVehicle', 0, 'onVehicle'),
               'inventory_current': (-1, 'vehicle'),
               'inventory_vehicle': (5, 'lightTank', 'mediumTank', 'heavyTank', 'at-spg', 'spg', 'brocken', 'locked'),
               'inventory_module': (5, 'vehicleGun', 'vehicleTurret', 'vehicleEngine', 'vehicleChassis', 'vehicleRadio', 'myVehicles', 0),
               'inventory_shell': (4, 'ARMOR_PIERCING', 'ARMOR_PIERCING_CR', 'HOLLOW_CHARGE', 'HIGH_EXPLOSIVE', 'myVehicleGun', 0),
               'inventory_optionalDevice': ('myVehicle', 0, 'onVehicle'),
               'inventory_equipment': ('myVehicle', 0, 'onVehicle'),
               CAROUSEL_FILTER: {'nation': -1,
                                 'tankType': -1,
                                 'ready': False},
               BARRACKS_FILTER: {'nation': -1,
                                 'role': 'None',
                                 'tankType': 'None',
                                 'location': 3,
                                 'nationID': None},
               ORDERS_FILTER: {'isSelected': False},
               GUI_START_BEHAVIOR: {'isFreeXPInfoDialogShowed': False},
               EULA_VERSION: {'version': 0},
               FORT_MEMBER_TUTORIAL: {'wasShown': False},
               IGR_PROMO: {'wasShown': False},
               CONTACTS: {'showOfflineUsers': True,
                          'showOthersCategory': True},
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
                        'battlesCountAward': -1}},
 KEY_FAVORITES: {CURRENT_VEHICLE: 0},
 KEY_SETTINGS: {'unitWindow': {'selectedIntroVehicles': [],
                               'selectedListVehicles': []},
                'fortSettings': {'clanDBID': 0,
                                 'battleConsumesIntroShown': False,
                                 'visitedBuildings': {_FBT.MILITARY_BASE,
                                                      _FBT.FINANCIAL_DEPT,
                                                      _FBT.TANKODROME,
                                                      _FBT.TRAINING_DEPT,
                                                      _FBT.MILITARY_ACADEMY,
                                                      _FBT.TRANSPORT_DEPT,
                                                      _FBT.INTENDANT_SERVICE,
                                                      _FBT.TROPHY_BRIGADE,
                                                      _FBT.OFFICE,
                                                      _FBT.MILITARY_SHOP}},
                'vehicleSellDialog': {'isOpened': False},
                KNOWN_SELECTOR_BATTLES: set(),
                'tankmanDropSkillIdx': 0,
                'cursor': False,
                'arcade': {'mixing': {'alpha': 90,
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
                VEHICLE_BUY_WINDOW_SETTINGS: True,
                'showVehicleIcon': False,
                'showVehicleLevel': False,
                'showExInf4Destroyed': False,
                'ingameHelpVersion': -1,
                'isColorBlind': False,
                'useServerAim': False,
                'showVehiclesCounter': True,
                'minimapAlpha': 0,
                'minimapSize': 0,
                'nationalVoices': False,
                'replayEnabled': 1,
                'players_panel': {'state': 'medium',
                                  'showLevels': True,
                                  'showTypes': True},
                'gameplayMask': gameplay_ctx.getDefaultMask(),
                'statsSorting': {'iconType': 'tank',
                                 'sortDirection': 'descending'},
                'statsSortingSortie': {'iconType': 'tank',
                                       'sortDirection': 'descending'},
                'backDraftInvert': False,
                'quests': {'lastVisitTime': -1,
                           'visited': [],
                           'naVisited': [],
                           'potapov': {'introShown': False,
                                       'tilesVisited': set(),
                                       'headerAlert': False}},
                'customization': {},
                'showVehModelsOnMap': 0,
                'interfaceScale': 0}}

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
    version = 12
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

            ads.writeInt('version', AccountSettings.version)

    @staticmethod
    def getFilterDefault(name):
        return DEFAULT_VALUES[KEY_FILTERS].get(name, None)

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
        if DEFAULT_VALUES[type].has_key(name) and AccountSettings.__getValue(name, type) != value:
            fds = AccountSettings.__readSection(AccountSettings.__readUserSection(), type)
            if DEFAULT_VALUES[type][name] != value:
                fds.write(name, base64.b64encode(pickle.dumps(value)))
            else:
                fds.deleteSection(name)
            AccountSettings.onSettingsChanging(name, value)
