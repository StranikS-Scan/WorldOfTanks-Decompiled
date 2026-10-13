# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/aliases.py
from gui.impl.gen_utils import DynAccessor

class battle_modifiers(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Modifiers = DynAccessor(135719)

    shared = _shared(135720)


class battle_pass(DynAccessor):
    __slots__ = ()
    ChapterChoice = DynAccessor(135722)
    Progression = DynAccessor(135723)
    PostProgression = DynAccessor(135724)
    BuyPass = DynAccessor(135725)
    BuyPassRewards = DynAccessor(135726)
    BuyLevels = DynAccessor(135727)
    BuyLevelsRewards = DynAccessor(135728)
    HolidayFinal = DynAccessor(135729)
    FinalRewardPreview = DynAccessor(135730)
    TankmenScreen = DynAccessor(135731)


class battle_result(DynAccessor):
    __slots__ = ()
    none = DynAccessor(135733)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        User = DynAccessor(135734)
        Vehicle = DynAccessor(135735)

    contextMenu = _contextMenu(135736)


class battle_results(DynAccessor):
    __slots__ = ()

    class _progression(DynAccessor):
        __slots__ = ()
        DailyMissions = DynAccessor(135738)
        WeeklyMissions = DynAccessor(135739)
        PersonalMissions = DynAccessor(135740)
        BattlePass = DynAccessor(135741)
        Prestige = DynAccessor(135742)
        BattleMatters = DynAccessor(135743)
        ModuleVehicleUnlocks = DynAccessor(135744)
        CommonQuests = DynAccessor(135745)
        Challenges = DynAccessor(135746)

    progression = _progression(135747)


class common(DynAccessor):
    __slots__ = ()
    none = DynAccessor(135749)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(135750)

    contextMenu = _contextMenu(135751)

    class _tooltip(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(135752)
        Wulf = DynAccessor(135753)
        Param = DynAccessor(135754)

    tooltip = _tooltip(135755)

    class _popOver(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(135756)

    popOver = _popOver(135757)

    class _shared(DynAccessor):
        __slots__ = ()
        DynamicEconomics = DynAccessor(135758)

    shared = _shared(135759)


class hangar(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(135761)
        VehiclesStatistics = DynAccessor(135762)
        Consumables = DynAccessor(135763)
        Equipments = DynAccessor(135764)
        Instructions = DynAccessor(135765)
        Shells = DynAccessor(135766)
        Loadout = DynAccessor(135767)
        Crew = DynAccessor(135768)
        VehicleParams = DynAccessor(135769)
        ETEVehicleParams = DynAccessor(135770)
        CurrentVehicle = DynAccessor(135771)
        VehiclesInventory = DynAccessor(135772)
        MainMenu = DynAccessor(135773)
        VehicleMenu = DynAccessor(135774)
        LootboxEntryPoint = DynAccessor(135775)
        VehicleFilters = DynAccessor(135776)
        VehiclePlaylists = DynAccessor(135777)
        Teaser = DynAccessor(135778)
        OptionalDevicesAssistant = DynAccessor(135779)
        SpaceInteraction = DynAccessor(135780)
        HeroTank = DynAccessor(135781)
        UserMissions = DynAccessor(135782)
        ModeState = DynAccessor(135783)
        EasyTankEquip = DynAccessor(135784)
        PetEvent = DynAccessor(135785)
        PetObjectTooltip = DynAccessor(135786)
        Settings = DynAccessor(135787)
        KeyBindings = DynAccessor(135788)
        ManageableVehiclePlaylists = DynAccessor(135789)
        MainPlugins = DynAccessor(135790)

    shared = _shared(135791)


class lobby_footer(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Platoon = DynAccessor(135793)
        ContactsList = DynAccessor(135794)
        SessionStats = DynAccessor(135795)
        VehicleCompare = DynAccessor(135796)
        NotificationsCenter = DynAccessor(135797)
        Chats = DynAccessor(135798)
        ReferralProgram = DynAccessor(135799)
        ServerInfo = DynAccessor(135800)

    default = _default(135801)


class lobby_header(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        FightStart = DynAccessor(135803)
        NavigationBar = DynAccessor(135804)
        Prebattle = DynAccessor(135805)
        Wallet = DynAccessor(135806)
        AccountDashboard = DynAccessor(135807)
        HeaderState = DynAccessor(135808)
        UserAccount = DynAccessor(135809)
        ReservesEntryPoint = DynAccessor(135810)
        PremShop = DynAccessor(135811)
        CurrentVehicle = DynAccessor(135812)

    default = _default(135813)


class select_vehicle(DynAccessor):
    __slots__ = ()

    class _select_vehicle(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(135815)
        VehiclesInventory = DynAccessor(135816)
        VehiclesStatistics = DynAccessor(135817)
        VehicleFilters = DynAccessor(135818)
        VehiclePlaylists = DynAccessor(135819)

    select_vehicle = _select_vehicle(135820)


class states(DynAccessor):
    __slots__ = ()

    class _Hangar(DynAccessor):
        __slots__ = ()

        class _Loadout(DynAccessor):
            __slots__ = ()
            Equipment = DynAccessor(135822)
            Instructions = DynAccessor(135823)
            Shells = DynAccessor(135824)
            Consumables = DynAccessor(135825)

        Loadout = _Loadout(135826)
        Vehicles = DynAccessor(135827)

    Hangar = _Hangar(135828)


class user_missions(DynAccessor):
    __slots__ = ()

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        BattlePass = DynAccessor(135830)
        Events = DynAccessor(135831)
        Quests = DynAccessor(135832)
        PersonalMissions = DynAccessor(135833)
        EventMainInfoTip = DynAccessor(135834)

    hangarWidget = _hangarWidget(135835)

    class _hub(DynAccessor):
        __slots__ = ()

        class _basicMissions(DynAccessor):
            __slots__ = ()
            MainView = DynAccessor(135836)

            class _DailyMissionsSection(DynAccessor):
                __slots__ = ()
                MainView = DynAccessor(135837)
                DailyBlock = DynAccessor(135838)
                PremiumBlock = DynAccessor(135839)
                RewardProgressBlock = DynAccessor(135840)

            DailyMissionsSection = _DailyMissionsSection(135841)
            WeeklyMissions = DynAccessor(135842)
            PersonalMissions = DynAccessor(135843)

        basicMissions = _basicMissions(135844)

        class _challengeMissions(DynAccessor):
            __slots__ = ()
            MainView = DynAccessor(135845)

        challengeMissions = _challengeMissions(135846)

    hub = _hub(135847)


class vehicle_hub(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        VehicleParams = DynAccessor(135849)
        Wallet = DynAccessor(135850)
        VehicleInfo = DynAccessor(135851)
        ManageableVehiclePlaylists = DynAccessor(135852)
        VehiclesInfo = DynAccessor(135853)
        VehiclesStatistics = DynAccessor(135854)
        VehicleFilters = DynAccessor(135855)
        VehiclePlaylists = DynAccessor(135856)
        VehiclesInventory = DynAccessor(135857)

    default = _default(135858)


class vehicle_menu(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Customization = DynAccessor(135860)
        CrewAutoReturn = DynAccessor(135861)
        CrewRetrain = DynAccessor(135862)
        QuickTraining = DynAccessor(135863)
        CrewOut = DynAccessor(135864)
        CrewBack = DynAccessor(135865)
        EasyEquip = DynAccessor(135866)
        ArmorInspector = DynAccessor(135867)
        FieldModification = DynAccessor(135868)
        NationChange = DynAccessor(135869)
        Research = DynAccessor(135870)
        AboutVehicle = DynAccessor(135871)
        Compare = DynAccessor(135872)
        Repairs = DynAccessor(135873)
        VehSkillTree = DynAccessor(135874)
        ProBoost = DynAccessor(135875)

    default = _default(135876)


class white_tiger(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Carousel = DynAccessor(135878)
        ConsumablesPanel = DynAccessor(135879)
        Progression = DynAccessor(135880)
        Crewman = DynAccessor(135881)
        VehicleStats = DynAccessor(135882)
        ProgressionContent = DynAccessor(135883)
        ProgressionQuests = DynAccessor(135884)
        LootboxEntryPoint = DynAccessor(135885)

    shared = _shared(135886)


class battle_royale(DynAccessor):
    __slots__ = ()
    BattleSelector = DynAccessor(135888)
    UserMissions = DynAccessor(135889)
    VehiclesInventory = DynAccessor(135890)
    VehiclesFilter = DynAccessor(135891)
    AlertMessage = DynAccessor(135892)
    Header = DynAccessor(135893)
    LoadoutPanelContainer = DynAccessor(135894)
    Events = DynAccessor(135895)

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        Progression = DynAccessor(135896)
        EventShop = DynAccessor(135897)

    hangarWidget = _hangarWidget(135898)

    class _loadoutPanelContainer(DynAccessor):
        __slots__ = ()
        Loadout = DynAccessor(135899)
        Commander = DynAccessor(135900)

    loadoutPanelContainer = _loadoutPanelContainer(135901)


class comp7(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(135903)
        Schedule = DynAccessor(135904)
        SeasonModifier = DynAccessor(135905)
        RoleSkillSlot = DynAccessor(135906)
        UserMissions = DynAccessor(135907)
        EntryPoint = DynAccessor(135908)
        WeeklyQuestsWidget = DynAccessor(135909)
        BattleResultsWeeklyQuests = DynAccessor(135910)
        BattleResultsCustomizationQuests = DynAccessor(135911)

    shared = _shared(135912)


class comp7_light(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(135914)
        SeasonModifier = DynAccessor(135915)
        RoleSkillSlot = DynAccessor(135916)
        UserMissions = DynAccessor(135917)
        EntryPoint = DynAccessor(135918)
        Quests = DynAccessor(135919)
        BattleResultsProgressionQuests = DynAccessor(135920)

    shared = _shared(135921)


class frontline(DynAccessor):
    __slots__ = ()

    class _loadout(DynAccessor):
        __slots__ = ()
        BattleAbilities = DynAccessor(135923)

    loadout = _loadout(135924)

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(135925)
        AlertMessage = DynAccessor(135926)

    shared = _shared(135927)


class fun_random(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(135929)
        ProgressionEntryPoint = DynAccessor(135930)
        ProgressionQuests = DynAccessor(135931)

    shared = _shared(135932)


class last_stand(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Carousel = DynAccessor(135934)
        Difficulty = DynAccessor(135935)
        MoneyBalance = DynAccessor(135936)
        TeamStats = DynAccessor(135937)
        Meta = DynAccessor(135938)
        Keys = DynAccessor(135939)
        Quests = DynAccessor(135940)
        RewardPath = DynAccessor(135941)
        Shop = DynAccessor(135942)
        Gsw = DynAccessor(135943)
        Switcher = DynAccessor(135944)
        PresetsSwitcher = DynAccessor(135945)
        VehiclesDaily = DynAccessor(135946)
        BundleCard = DynAccessor(135947)
        DailyCard = DynAccessor(135948)
        Parallax = DynAccessor(135949)

    shared = _shared(135950)


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
