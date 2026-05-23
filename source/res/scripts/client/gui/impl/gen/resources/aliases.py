# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/aliases.py
from gui.impl.gen_utils import DynAccessor

class battle_modifiers(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Modifiers = DynAccessor(129632)

    shared = _shared(129633)


class battle_pass(DynAccessor):
    __slots__ = ()
    ChapterChoice = DynAccessor(129635)
    Progression = DynAccessor(129636)
    PostProgression = DynAccessor(129637)
    BuyPass = DynAccessor(129638)
    BuyPassRewards = DynAccessor(129639)
    BuyLevels = DynAccessor(129640)
    BuyLevelsRewards = DynAccessor(129641)
    HolidayFinal = DynAccessor(129642)
    FinalRewardPreview = DynAccessor(129643)
    TankmenScreen = DynAccessor(129644)


class battle_result(DynAccessor):
    __slots__ = ()
    none = DynAccessor(129646)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        User = DynAccessor(129647)
        Vehicle = DynAccessor(129648)

    contextMenu = _contextMenu(129649)


class battle_results(DynAccessor):
    __slots__ = ()

    class _progression(DynAccessor):
        __slots__ = ()
        DailyMissions = DynAccessor(129651)
        WeeklyMissions = DynAccessor(129652)
        PersonalMissions = DynAccessor(129653)
        BattlePass = DynAccessor(129654)
        Prestige = DynAccessor(129655)
        BattleMatters = DynAccessor(129656)
        ModuleVehicleUnlocks = DynAccessor(129657)
        CommonQuests = DynAccessor(129658)

    progression = _progression(129659)


class common(DynAccessor):
    __slots__ = ()
    none = DynAccessor(129661)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(129662)

    contextMenu = _contextMenu(129663)

    class _tooltip(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(129664)
        Wulf = DynAccessor(129665)
        Param = DynAccessor(129666)

    tooltip = _tooltip(129667)

    class _popOver(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(129668)

    popOver = _popOver(129669)

    class _shared(DynAccessor):
        __slots__ = ()
        DynamicEconomics = DynAccessor(129670)

    shared = _shared(129671)


class hangar(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(129673)
        VehiclesStatistics = DynAccessor(129674)
        Consumables = DynAccessor(129675)
        Equipments = DynAccessor(129676)
        Instructions = DynAccessor(129677)
        Shells = DynAccessor(129678)
        Loadout = DynAccessor(129679)
        Crew = DynAccessor(129680)
        VehicleParams = DynAccessor(129681)
        ETEVehicleParams = DynAccessor(129682)
        CurrentVehicle = DynAccessor(129683)
        VehiclesInventory = DynAccessor(129684)
        MainMenu = DynAccessor(129685)
        VehicleMenu = DynAccessor(129686)
        LootboxEntryPoint = DynAccessor(129687)
        VehicleFilters = DynAccessor(129688)
        VehiclePlaylists = DynAccessor(129689)
        Teaser = DynAccessor(129690)
        OptionalDevicesAssistant = DynAccessor(129691)
        SpaceInteraction = DynAccessor(129692)
        HeroTank = DynAccessor(129693)
        UserMissions = DynAccessor(129694)
        ModeState = DynAccessor(129695)
        EasyTankEquip = DynAccessor(129696)
        PetEvent = DynAccessor(129697)
        PetObjectTooltip = DynAccessor(129698)
        Settings = DynAccessor(129699)
        KeyBindings = DynAccessor(129700)
        ManageableVehiclePlaylists = DynAccessor(129701)

    shared = _shared(129702)


class lobby_footer(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Platoon = DynAccessor(129704)
        ContactsList = DynAccessor(129705)
        SessionStats = DynAccessor(129706)
        VehicleCompare = DynAccessor(129707)
        NotificationsCenter = DynAccessor(129708)
        Chats = DynAccessor(129709)
        ReferralProgram = DynAccessor(129710)
        ServerInfo = DynAccessor(129711)

    default = _default(129712)


class lobby_header(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        FightStart = DynAccessor(129714)
        NavigationBar = DynAccessor(129715)
        Prebattle = DynAccessor(129716)
        Wallet = DynAccessor(129717)
        AccountDashboard = DynAccessor(129718)
        HeaderState = DynAccessor(129719)
        UserAccount = DynAccessor(129720)
        ReservesEntryPoint = DynAccessor(129721)
        PremShop = DynAccessor(129722)
        CurrentVehicle = DynAccessor(129723)

    default = _default(129724)


class select_vehicle(DynAccessor):
    __slots__ = ()

    class _select_vehicle(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(129726)
        VehiclesInventory = DynAccessor(129727)
        VehiclesStatistics = DynAccessor(129728)
        VehicleFilters = DynAccessor(129729)
        VehiclePlaylists = DynAccessor(129730)

    select_vehicle = _select_vehicle(129731)


class states(DynAccessor):
    __slots__ = ()

    class _Hangar(DynAccessor):
        __slots__ = ()

        class _Loadout(DynAccessor):
            __slots__ = ()
            Equipment = DynAccessor(129733)
            Instructions = DynAccessor(129734)
            Shells = DynAccessor(129735)
            Consumables = DynAccessor(129736)

        Loadout = _Loadout(129737)
        Vehicles = DynAccessor(129738)

    Hangar = _Hangar(129739)


class user_missions(DynAccessor):
    __slots__ = ()

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        BattlePass = DynAccessor(129741)
        Events = DynAccessor(129742)
        Quests = DynAccessor(129743)
        EventMainInfoTip = DynAccessor(129744)

    hangarWidget = _hangarWidget(129745)

    class _hub(DynAccessor):
        __slots__ = ()

        class _basicMissions(DynAccessor):
            __slots__ = ()
            MainView = DynAccessor(129746)

            class _DailyMissionsSection(DynAccessor):
                __slots__ = ()
                MainView = DynAccessor(129747)
                DailyBlock = DynAccessor(129748)
                PremiumBlock = DynAccessor(129749)
                RewardProgressBlock = DynAccessor(129750)

            DailyMissionsSection = _DailyMissionsSection(129751)
            WeeklyMissions = DynAccessor(129752)
            PersonalMissions = DynAccessor(129753)

        basicMissions = _basicMissions(129754)

    hub = _hub(129755)


class vehicle_hub(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        VehicleParams = DynAccessor(129757)
        Wallet = DynAccessor(129758)
        VehicleInfo = DynAccessor(129759)
        ManageableVehiclePlaylists = DynAccessor(129760)
        VehiclesInfo = DynAccessor(129761)
        VehiclesStatistics = DynAccessor(129762)
        VehicleFilters = DynAccessor(129763)
        VehiclePlaylists = DynAccessor(129764)
        VehiclesInventory = DynAccessor(129765)

    default = _default(129766)


class vehicle_menu(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Customization = DynAccessor(129768)
        CrewAutoReturn = DynAccessor(129769)
        CrewRetrain = DynAccessor(129770)
        QuickTraining = DynAccessor(129771)
        CrewOut = DynAccessor(129772)
        CrewBack = DynAccessor(129773)
        EasyEquip = DynAccessor(129774)
        ArmorInspector = DynAccessor(129775)
        FieldModification = DynAccessor(129776)
        NationChange = DynAccessor(129777)
        Research = DynAccessor(129778)
        AboutVehicle = DynAccessor(129779)
        Compare = DynAccessor(129780)
        Repairs = DynAccessor(129781)
        VehSkillTree = DynAccessor(129782)
        ProBoost = DynAccessor(129783)

    default = _default(129784)


class white_tiger(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Carousel = DynAccessor(129786)
        ConsumablesPanel = DynAccessor(129787)
        Progression = DynAccessor(129788)
        Crewman = DynAccessor(129789)
        VehicleStats = DynAccessor(129790)
        ProgressionContent = DynAccessor(129791)
        ProgressionQuests = DynAccessor(129792)
        LootboxEntryPoint = DynAccessor(129793)

    shared = _shared(129794)


class battle_royale(DynAccessor):
    __slots__ = ()
    BattleSelector = DynAccessor(129796)
    UserMissions = DynAccessor(129797)
    VehiclesInventory = DynAccessor(129798)
    VehiclesFilter = DynAccessor(129799)
    AlertMessage = DynAccessor(129800)
    Header = DynAccessor(129801)
    LoadoutPanelContainer = DynAccessor(129802)
    Events = DynAccessor(129803)

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        Progression = DynAccessor(129804)
        EventShop = DynAccessor(129805)

    hangarWidget = _hangarWidget(129806)

    class _loadoutPanelContainer(DynAccessor):
        __slots__ = ()
        Loadout = DynAccessor(129807)
        Commander = DynAccessor(129808)

    loadoutPanelContainer = _loadoutPanelContainer(129809)


class comp7(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(129811)
        Schedule = DynAccessor(129812)
        SeasonModifier = DynAccessor(129813)
        RoleSkillSlot = DynAccessor(129814)
        UserMissions = DynAccessor(129815)
        EntryPoint = DynAccessor(129816)
        WeeklyQuestsWidget = DynAccessor(129817)
        BattleResultsWeeklyQuests = DynAccessor(129818)
        BattleResultsCustomizationQuests = DynAccessor(129819)

    shared = _shared(129820)


class comp7_light(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(129822)
        SeasonModifier = DynAccessor(129823)
        RoleSkillSlot = DynAccessor(129824)
        UserMissions = DynAccessor(129825)
        EntryPoint = DynAccessor(129826)
        Quests = DynAccessor(129827)

    shared = _shared(129828)


class frontline(DynAccessor):
    __slots__ = ()

    class _loadout(DynAccessor):
        __slots__ = ()
        BattleAbilities = DynAccessor(129830)

    loadout = _loadout(129831)

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(129832)
        AlertMessage = DynAccessor(129833)

    shared = _shared(129834)


class fun_random(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(129836)
        ProgressionEntryPoint = DynAccessor(129837)
        ProgressionQuests = DynAccessor(129838)

    shared = _shared(129839)


class last_stand(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Carousel = DynAccessor(129841)
        Difficulty = DynAccessor(129842)
        MoneyBalance = DynAccessor(129843)
        TeamStats = DynAccessor(129844)
        Meta = DynAccessor(129845)
        Keys = DynAccessor(129846)
        Quests = DynAccessor(129847)
        RewardPath = DynAccessor(129848)
        Shop = DynAccessor(129849)
        Gsw = DynAccessor(129850)
        Switcher = DynAccessor(129851)
        PresetsSwitcher = DynAccessor(129852)
        VehiclesDaily = DynAccessor(129853)
        BundleCard = DynAccessor(129854)
        DailyCard = DynAccessor(129855)
        Parallax = DynAccessor(129856)

    shared = _shared(129857)


class Aliases(DynAccessor):
    __slots__ = ()
    battle_modifiers = battle_modifiers()
    battle_pass = battle_pass()
    battle_result = battle_result()
    battle_results = battle_results()
    common = common()
    hangar = hangar()
    lobby_footer = lobby_footer()
    lobby_header = lobby_header()
    select_vehicle = select_vehicle()
    states = states()
    user_missions = user_missions()
    vehicle_hub = vehicle_hub()
    vehicle_menu = vehicle_menu()
    white_tiger = white_tiger()
    battle_royale = battle_royale()
    comp7 = comp7()
    comp7_light = comp7_light()
    frontline = frontline()
    fun_random = fun_random()
    last_stand = last_stand()
