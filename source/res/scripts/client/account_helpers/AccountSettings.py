# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/AccountSettings.py
# Compiled at: 2019-01-28 18:54:24
import BigWorld, Settings, Event, pickle, base64
KEY_FILTERS = 'filters'
KEY_SETTINGS = 'settings'
KEY_FAVORITES = 'favorites'
CAROUSEL_FILTER = 'carousel_filter'
BARRACKS_FILTER = 'barracks_filter'
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
                                 'role': -1,
                                 'tankType': -1,
                                 'location': 3,
                                 'nationID': None}},
 KEY_FAVORITES: {'vehicles': [],
                 'current': 0},
 KEY_SETTINGS: {'cursor': False,
                'cursors': {'mixing': {'alpha': 90,
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
                                          'type': 0}},
                'markers': {'markerBaseHp': 1,
                            'markerBaseName': 0,
                            'markerBaseIcon': False,
                            'markerBaseLevel': False,
                            'markerBaseHpIndicator': True,
                            'markerBaseDead': False,
                            'markerAltHp': 0,
                            'markerAltName': 1,
                            'markerAltIcon': True,
                            'markerAltLevel': True,
                            'markerAltHpIndicator': True,
                            'markerAltDead': True},
                'shopBuyWindow': True,
                'ingameHelpVersion': -1,
                'isColorBlind': False,
                'minimapAlpha': 0,
                'minimapSize': 0,
                'nationalVoices': False,
                'players_panel': {'state': 'medium',
                                  'showLevels': True,
                                  'showTypes': True}}}

class AccountSettings(object):
    onSettingsChanging = Event.Event()

    @staticmethod
    def __readSection(ds, name):
        if not ds.has_key(name):
            ds.write(name, '')
        return ds[name]

    @staticmethod
    def __readUserSection():
        ads = AccountSettings.__readSection(Settings.g_instance.userPrefs, Settings.KEY_ACCOUNT_SETTINGS)
        return AccountSettings.__readSection(ads, BigWorld.player().name)

    @staticmethod
    def getFilter(name):
        return AccountSettings.__getValue(name, KEY_FILTERS)

    @staticmethod
    def setFilter(name, value):
        AccountSettings.__setValue(name, value, KEY_FILTERS)

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
                pass

            return DEFAULT_VALUES[type][name]
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
            AccountSettings.onSettingsChanging(name)
