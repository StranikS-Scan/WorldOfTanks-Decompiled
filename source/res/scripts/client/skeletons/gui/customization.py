# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/customization.py
from Event import Event

class ICustomizationService(object):
    onRegionHighlighted = None
    onRemoveItems = None
    onCarouselFilter = None
    onOutfitChanged = None
    onPropertySheetShow = None

    def init(self):
        """ Initialization of service.
        """
        raise NotImplementedError

    def fini(self):
        """ Finalization of service
        """
        raise NotImplementedError

    def startHighlighter(self, mode):
        """ Start customization highlighting mode.
        
        In this mode vehicle parts will be highlighted on hover, a special
        event onRegionHighlighted will be fired on click.
        """
        raise NotImplementedError

    def stopHighlighter(self):
        """ Stop customization highlighting mode.
        """
        raise NotImplementedError

    def suspendHighlighter(self):
        """ Suspends highlighter if it's active.
        """
        raise NotImplementedError

    def resumeHighlighter(self):
        """ Resumes highlighter if it was active.
        """
        raise NotImplementedError

    def getSelectionMode(self):
        """Gets the selection mode of the highlighter ( determines what regions get highlighted )
        """
        raise NotImplementedError

    def getPointForRegionLeaderLine(self, areaId):
        """ Get a central point (in world space) for the given ApplyArea.
        
        :param areaId: one of the ApplyArea.USER_PAINT_ALLOWED_REGIONS
        """
        raise NotImplementedError

    def getPointForAnchorLeaderLine(self, areaId, slotId, regionId):
        """ Get a central point (in world space) for the given slot.
        
        :param areaId: The tank area of a slot for example Area.TURRET
        :param slotId: The type of items supported by a slot one of GUI_ITEM_TYPE
        :param regionId: The region index of an outfit slot
        """
        raise NotImplementedError

    def getNormalForAnchorLeaderLine(self, areaId, slotId, regionId):
        """ Get the normal for a point (in world space) for the given slot.
        
        :param areaId: The tank area of a slot for example Area.TURRET
        :param slotId: The type of items supported by a slot one of GUI_ITEM_TYPE
        :param regionId: The region index of an outfit slot
        """
        raise NotImplementedError

    def getHightlighter(self):
        """ Get an instance of highlight helper.
        """
        raise NotImplementedError

    def getItems(self, itemTypeID, vehicle=None, criteria=None):
        """ Get available customization items.
        
        :param itemTypeID: type of item (one of GUI_ITEM_TYPE).
        :param vehicle: if provided, get only items applicable for the vehicle.
        :param criteria: if provided, apply additional criteria while fetching items.
        :return: ItemsCollection with appropriate items.
        """
        raise NotImplementedError

    def getPaints(self, vehicle=None, criteria=None):
        """ Get available paints.
        
        :param vehicle: if provided, get only items applicable for the vehicle.
        :param criteria: if provided, apply additional criteria while fetching items.
        :return: ItemsCollection with appropriate items.
        """
        raise NotImplementedError

    def getCamouflages(self, vehicle=None, criteria=None):
        """ Get available camouflages.
        
        :param vehicle: if provided, get only items applicable for the vehicle.
        :param criteria: if provided, apply additional criteria while fetching items.
        :return: ItemsCollection with appropriate items.
        """
        raise NotImplementedError

    def getModifications(self, vehicle=None, criteria=None):
        """ Get available modifications.
        
        :param vehicle: if provided, get only items applicable for the vehicle.
        :param criteria: if provided, apply additional criteria while fetching items.
        :return: ItemsCollection with appropriate items.
        """
        raise NotImplementedError

    def getDecals(self, vehicle=None, criteria=None):
        """ Get available decals (emblems and inscriptions).
        
        :param vehicle: if provided, get only items applicable for the vehicle.
        :param criteria: if provided, apply additional criteria while fetching items.
        :return: ItemsCollection with appropriate items.
        """
        raise NotImplementedError

    def getEmblems(self, vehicle=None, criteria=None):
        """ Get available emblems.
        
        :param vehicle: if provided, get only items applicable for the vehicle.
        :param criteria: if provided, apply additional criteria while fetching items.
        :return: ItemsCollection with appropriate items.
        """
        raise NotImplementedError

    def getInscriptions(self, vehicle=None, criteria=None):
        """ Get available inscriptions.
        
        :param vehicle: if provided, get only items applicable for the vehicle.
        :param criteria: if provided, apply additional criteria while fetching items.
        :return: ItemsCollection with appropriate items.
        """
        raise NotImplementedError

    def getStyles(self, vehicle=None, criteria=None):
        """ Get available styles (i.e. predefined outfits).
        
        :param vehicle: if provided, get only items applicable for the vehicle.
        :param criteria: if provided, apply additional criteria while fetching items.
        :return: ItemsCollection with appropriate items.
        """
        raise NotImplementedError

    def getItemByID(self, itemTypeID, itemID):
        """ Get an item by it's type and id.
        
        :param itemTypeID: type of item (one of GUI_ITEM_TYPE).
        :param itemID: id of item.
        :return: instance of Customization.
        """
        raise NotImplementedError

    def getEmptyOutfit(self):
        """ Get an empty outfit to work with.
        """
        raise NotImplementedError

    def tryOnOutfit(self, outfit):
        """ Try on outfit on the current vehicle without buying anything.
        """
        raise NotImplementedError

    def getOutfit(self, season):
        """ Get outfit from the current vehicle.
        
        :param season: season type (one of SeasonType).
        """
        raise NotImplementedError

    def getCustomOutfit(self, season):
        """ Get a custom outfit from the current vehicle.
        
        :param season: season type (one of SeasonType).
        """
        raise NotImplementedError

    def getCurrentStyle(self):
        """ Get a style from the current vehicle.
        """
        raise NotImplementedError

    def buyItems(self, items, vehicle=None):
        """ Buy customization items.
        
        :param items: list of customizations to buy.
        :param vehicle: if provided, bound bound-only items to the given vehicle.
        """
        raise NotImplementedError

    def sellItem(self, item, count, vehicle=None):
        """ Sell single customization item.
        
        :param item: item to sell.
        :param count: specify a number of items to sell (i.e. how many of its inventoryCount).
        :param vehicle: if provided, unbound bound-only items from the given vehicle.
        """
        raise NotImplementedError

    def buyAndEquipOutfit(self, outfit, season, vehicle=None):
        """ Buy and equip an outfit for the given vehicle/season.
        
        :param outfit: an instance of Outfit to buy.
        :param season: apply outfit for the given season.
        :param vehicle: if provided, put outfit on given vehicle (current vehicle otherwise).
        """
        raise NotImplementedError

    def buyAndEquipStyle(self, style, vehicle=None):
        """ Buy (or rent) and equip a style for the given vehicle/season.
        
        Rent-only styles will be rented, buy-only styles will be bought.
        No other options are available.
        
        :param style: an instance of Style.
        :param vehicle: if provided, put outfit on given vehicle (current vehicle otherwise).
        """
        raise NotImplementedError

    def setSelectHighlighting(self, value):
        """
        Set value for enable highlighting when selecting
        :param value:
        :return:
        """
        raise NotImplementedError
