# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/aliases.py
from gui.impl.gen_utils import DynAccessor

class battle_modifiers(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Modifiers = DynAccessor(129025)

    shared = _shared(129026)


class battle_pass(DynAccessor):
    __slots__ = ()
    IntroVideo = DynAccessor(129028)
    ExtraVideo = DynAccessor(129029)
    Intro = DynAccessor(129030)
    ChapterChoice = DynAccessor(129031)
    Progression = DynAccessor(129032)
    PostProgression = DynAccessor(129033)
    BuyPass = DynAccessor(129034)
    BuyPassRewards = DynAccessor(129035)
    BuyLevels = DynAccessor(129036)
    BuyLevelsRewards = DynAccessor(129037)
    HolidayFinal = DynAccessor(129038)
    FinalRewardPreview = DynAccessor(129039)


class battle_result(DynAccessor):
    __slots__ = ()
    none = DynAccessor(129041)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        User = DynAccessor(129042)
        Vehicle = DynAccessor(129043)

    contextMenu = _contextMenu(129044)


class battle_results(DynAccessor):
    __slots__ = ()

    class _progression(DynAccessor):
        __slots__ = ()
        DailyMissions = DynAccessor(129046)
        WeeklyMissions = DynAccessor(129047)
        PersonalMissions = DynAccessor(129048)
        BattlePass = DynAccessor(129049)
        Prestige = DynAccessor(129050)
        BattleMatters = DynAccessor(129051)
        ModuleVehicleUnlocks = DynAccessor(129052)
        CommonQuests = DynAccessor(129053)

    progression = _progression(129054)


class common(DynAccessor):
    __slots__ = ()
    none = DynAccessor(129056)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(129057)

    contextMenu = _contextMenu(129058)

    class _tooltip(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(129059)
        Wulf = DynAccessor(129060)
        Param = DynAccessor(129061)

    tooltip = _tooltip(129062)

    class _popOver(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(129063)

    popOver = _popOver(129064)

    class _shared(DynAccessor):
        __slots__ = ()
        DynamicEconomics = DynAccessor(129065)

    shared = _shared(129066)


class hangar(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(129068)
        VehiclesStatistics = DynAccessor(129069)
        Consumables = DynAccessor(129070)
        Equipments = DynAccessor(129071)
        Instructions = DynAccessor(129072)
        Shells = DynAccessor(129073)
        Loadout = DynAccessor(129074)
        Crew = DynAccessor(129075)
        VehicleParams = DynAccessor(129076)
        ETEVehicleParams = DynAccessor(129077)
        CurrentVehicle = DynAccessor(129078)
        VehiclesInventory = DynAccessor(129079)
        MainMenu = DynAccessor(129080)
        VehicleMenu = DynAccessor(129081)
        LootboxEntryPoint = DynAccessor(129082)
        VehicleFilters = DynAccessor(129083)
        VehiclePlaylists = DynAccessor(129084)
        Teaser = DynAccessor(129085)
        OptionalDevicesAssistant = DynAccessor(129086)
        SpaceInteraction = DynAccessor(129087)
        HeroTank = DynAccessor(129088)
        UserMissions = DynAccessor(129089)
        ModeState = DynAccessor(129090)
        EasyTankEquip = DynAccessor(129091)
        PetEvent = DynAccessor(129092)
        PetObjectTooltip = DynAccessor(129093)
        Settings = DynAccessor(129094)
        KeyBindings = DynAccessor(129095)
        ManageableVehiclePlaylists = DynAccessor(129096)

    shared = _shared(129097)


class lobby_footer(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Platoon = DynAccessor(129099)
        ContactsList = DynAccessor(129100)
        SessionStats = DynAccessor(129101)
        VehicleCompare = DynAccessor(129102)
        NotificationsCenter = DynAccessor(129103)
        Chats = DynAccessor(129104)
        ReferralProgram = DynAccessor(129105)
        ServerInfo = DynAccessor(129106)

    default = _default(129107)


class lobby_header(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        FightStart = DynAccessor(129109)
        NavigationBar = DynAccessor(129110)
        Prebattle = DynAccessor(129111)
        Wallet = DynAccessor(129112)
        AccountDashboard = DynAccessor(129113)
        HeaderState = DynAccessor(129114)
        UserAccount = DynAccessor(129115)
        ReservesEntryPoint = DynAccessor(129116)
        PremShop = DynAccessor(129117)
        CurrentVehicle = DynAccessor(129118)

    default = _default(129119)


class select_vehicle(DynAccessor):
    __slots__ = ()

    class _select_vehicle(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(129121)
        VehiclesInventory = DynAccessor(129122)
        VehiclesStatistics = DynAccessor(129123)
        VehicleFilters = DynAccessor(129124)
        VehiclePlaylists = DynAccessor(129125)

    select_vehicle = _select_vehicle(129126)


class states(DynAccessor):
    __slots__ = ()

    class _Hangar(DynAccessor):
        __slots__ = ()

        class _Loadout(DynAccessor):
            __slots__ = ()
            Equipment = DynAccessor(129128)
            Instructions = DynAccessor(129129)
            Shells = DynAccessor(129130)
            Consumables = DynAccessor(129131)

        Loadout = _Loadout(129132)
        Vehicles = DynAccessor(129133)

    Hangar = _Hangar(129134)


class user_missions(DynAccessor):
    __slots__ = ()

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        BattlePass = DynAccessor(129136)
        Events = DynAccessor(129137)
        Quests = DynAccessor(129138)
        EventMainInfoTip = DynAccessor(129139)

    hangarWidget = _hangarWidget(129140)

    class _hub(DynAccessor):
        __slots__ = ()

        class _basicMissions(DynAccessor):
            __slots__ = ()
            MainView = DynAccessor(129141)

            class _DailyMissionsSection(DynAccessor):
                __slots__ = ()
                MainView = DynAccessor(129142)
                DailyBlock = DynAccessor(129143)
                PremiumBlock = DynAccessor(129144)
                RewardProgressBlock = DynAccessor(129145)

            DailyMissionsSection = _DailyMissionsSection(129146)
            WeeklyMissions = DynAccessor(129147)
            PersonalMissions = DynAccessor(129148)

        basicMissions = _basicMissions(129149)

    hub = _hub(129150)


class vehicle_hub(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        VehicleParams = DynAccessor(129152)
        Wallet = DynAccessor(129153)
        VehicleInfo = DynAccessor(129154)
        ManageableVehiclePlaylists = DynAccessor(129155)
        VehiclesInfo = DynAccessor(129156)
        VehiclesStatistics = DynAccessor(129157)
        VehicleFilters = DynAccessor(129158)
        VehiclePlaylists = DynAccessor(129159)
        VehiclesInventory = DynAccessor(129160)

    default = _default(129161)


class vehicle_menu(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Customization = DynAccessor(129163)
        CrewAutoReturn = DynAccessor(129164)
        CrewRetrain = DynAccessor(129165)
        QuickTraining = DynAccessor(129166)
        CrewOut = DynAccessor(129167)
        CrewBack = DynAccessor(129168)
        EasyEquip = DynAccessor(129169)
        ArmorInspector = DynAccessor(129170)
        FieldModification = DynAccessor(129171)
        NationChange = DynAccessor(129172)
        Research = DynAccessor(129173)
        AboutVehicle = DynAccessor(129174)
        Compare = DynAccessor(129175)
        Repairs = DynAccessor(129176)
        VehSkillTree = DynAccessor(129177)
        ProBoost = DynAccessor(129178)

    default = _default(129179)


class white_tiger(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Carousel = DynAccessor(129181)
        ConsumablesPanel = DynAccessor(129182)
        Progression = DynAccessor(129183)
        Crewman = DynAccessor(129184)
        VehicleStats = DynAccessor(129185)
        ProgressionContent = DynAccessor(129186)
        ProgressionQuests = DynAccessor(129187)
        LootboxEntryPoint = DynAccessor(129188)

    shared = _shared(129189)


class battle_royale(DynAccessor):
    __slots__ = ()
    BattleSelector = DynAccessor(129191)
    UserMissions = DynAccessor(129192)
    VehiclesInventory = DynAccessor(129193)
    VehiclesFilter = DynAccessor(129194)
    AlertMessage = DynAccessor(129195)
    Header = DynAccessor(129196)
    LoadoutPanelContainer = DynAccessor(129197)
    Events = DynAccessor(129198)

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        Progression = DynAccessor(129199)
        EventShop = DynAccessor(129200)

    hangarWidget = _hangarWidget(129201)

    class _loadoutPanelContainer(DynAccessor):
        __slots__ = ()
        Loadout = DynAccessor(129202)
        Commander = DynAccessor(129203)

    loadoutPanelContainer = _loadoutPanelContainer(129204)


class comp7(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(129206)
        Schedule = DynAccessor(129207)
        SeasonModifier = DynAccessor(129208)
        RoleSkillSlot = DynAccessor(129209)
        UserMissions = DynAccessor(129210)
        EntryPoint = DynAccessor(129211)
        WeeklyQuestsWidget = DynAccessor(129212)
        BattleResultsWeeklyQuests = DynAccessor(129213)
        BattleResultsCustomizationQuests = DynAccessor(129214)

    shared = _shared(129215)


class comp7_light(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(129217)
        SeasonModifier = DynAccessor(129218)
        RoleSkillSlot = DynAccessor(129219)
        UserMissions = DynAccessor(129220)
        EntryPoint = DynAccessor(129221)
        Quests = DynAccessor(129222)

    shared = _shared(129223)


class frontline(DynAccessor):
    __slots__ = ()

    class _loadout(DynAccessor):
        __slots__ = ()
        BattleAbilities = DynAccessor(129225)

    loadout = _loadout(129226)

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(129227)
        AlertMessage = DynAccessor(129228)

    shared = _shared(129229)


class fun_random(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(129231)
        ProgressionEntryPoint = DynAccessor(129232)

    shared = _shared(129233)


class last_stand(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Carousel = DynAccessor(129235)
        Difficulty = DynAccessor(129236)
        MoneyBalance = DynAccessor(129237)
        TeamStats = DynAccessor(129238)
        Meta = DynAccessor(129239)
        Keys = DynAccessor(129240)
        Quests = DynAccessor(129241)
        RewardPath = DynAccessor(129242)
        Shop = DynAccessor(129243)
        Gsw = DynAccessor(129244)
        Switcher = DynAccessor(129245)
        PresetsSwitcher = DynAccessor(129246)
        VehiclesDaily = DynAccessor(129247)
        BundleCard = DynAccessor(129248)
        DailyCard = DynAccessor(129249)
        Parallax = DynAccessor(129250)

    shared = _shared(129251)


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
