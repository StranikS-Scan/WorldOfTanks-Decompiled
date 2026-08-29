# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/aliases.py
from gui.impl.gen_utils import DynAccessor

class battle_modifiers(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Modifiers = DynAccessor(135377)

    shared = _shared(135378)


class battle_pass(DynAccessor):
    __slots__ = ()
    ChapterChoice = DynAccessor(135380)
    Progression = DynAccessor(135381)
    PostProgression = DynAccessor(135382)
    BuyPass = DynAccessor(135383)
    BuyPassRewards = DynAccessor(135384)
    BuyLevels = DynAccessor(135385)
    BuyLevelsRewards = DynAccessor(135386)
    HolidayFinal = DynAccessor(135387)
    FinalRewardPreview = DynAccessor(135388)
    TankmenScreen = DynAccessor(135389)


class battle_result(DynAccessor):
    __slots__ = ()
    none = DynAccessor(135391)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        User = DynAccessor(135392)
        Vehicle = DynAccessor(135393)

    contextMenu = _contextMenu(135394)


class battle_results(DynAccessor):
    __slots__ = ()

    class _progression(DynAccessor):
        __slots__ = ()
        DailyMissions = DynAccessor(135396)
        WeeklyMissions = DynAccessor(135397)
        PersonalMissions = DynAccessor(135398)
        BattlePass = DynAccessor(135399)
        Prestige = DynAccessor(135400)
        BattleMatters = DynAccessor(135401)
        ModuleVehicleUnlocks = DynAccessor(135402)
        CommonQuests = DynAccessor(135403)
        Challenges = DynAccessor(135404)

    progression = _progression(135405)


class common(DynAccessor):
    __slots__ = ()
    none = DynAccessor(135407)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(135408)

    contextMenu = _contextMenu(135409)

    class _tooltip(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(135410)
        Wulf = DynAccessor(135411)
        Param = DynAccessor(135412)

    tooltip = _tooltip(135413)

    class _popOver(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(135414)

    popOver = _popOver(135415)

    class _shared(DynAccessor):
        __slots__ = ()
        DynamicEconomics = DynAccessor(135416)

    shared = _shared(135417)


class hangar(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(135419)
        VehiclesStatistics = DynAccessor(135420)
        Consumables = DynAccessor(135421)
        Equipments = DynAccessor(135422)
        Instructions = DynAccessor(135423)
        Shells = DynAccessor(135424)
        Loadout = DynAccessor(135425)
        Crew = DynAccessor(135426)
        VehicleParams = DynAccessor(135427)
        ETEVehicleParams = DynAccessor(135428)
        CurrentVehicle = DynAccessor(135429)
        VehiclesInventory = DynAccessor(135430)
        MainMenu = DynAccessor(135431)
        VehicleMenu = DynAccessor(135432)
        LootboxEntryPoint = DynAccessor(135433)
        VehicleFilters = DynAccessor(135434)
        VehiclePlaylists = DynAccessor(135435)
        Teaser = DynAccessor(135436)
        OptionalDevicesAssistant = DynAccessor(135437)
        SpaceInteraction = DynAccessor(135438)
        HeroTank = DynAccessor(135439)
        UserMissions = DynAccessor(135440)
        ModeState = DynAccessor(135441)
        EasyTankEquip = DynAccessor(135442)
        PetEvent = DynAccessor(135443)
        PetObjectTooltip = DynAccessor(135444)
        Settings = DynAccessor(135445)
        KeyBindings = DynAccessor(135446)
        ManageableVehiclePlaylists = DynAccessor(135447)
        MainPlugins = DynAccessor(135448)

    shared = _shared(135449)


class lobby_footer(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Platoon = DynAccessor(135451)
        ContactsList = DynAccessor(135452)
        SessionStats = DynAccessor(135453)
        VehicleCompare = DynAccessor(135454)
        NotificationsCenter = DynAccessor(135455)
        Chats = DynAccessor(135456)
        ReferralProgram = DynAccessor(135457)
        ServerInfo = DynAccessor(135458)

    default = _default(135459)


class lobby_header(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        FightStart = DynAccessor(135461)
        NavigationBar = DynAccessor(135462)
        Prebattle = DynAccessor(135463)
        Wallet = DynAccessor(135464)
        AccountDashboard = DynAccessor(135465)
        HeaderState = DynAccessor(135466)
        UserAccount = DynAccessor(135467)
        ReservesEntryPoint = DynAccessor(135468)
        PremShop = DynAccessor(135469)
        CurrentVehicle = DynAccessor(135470)

    default = _default(135471)


class select_vehicle(DynAccessor):
    __slots__ = ()

    class _select_vehicle(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(135473)
        VehiclesInventory = DynAccessor(135474)
        VehiclesStatistics = DynAccessor(135475)
        VehicleFilters = DynAccessor(135476)
        VehiclePlaylists = DynAccessor(135477)

    select_vehicle = _select_vehicle(135478)


class states(DynAccessor):
    __slots__ = ()

    class _Hangar(DynAccessor):
        __slots__ = ()

        class _Loadout(DynAccessor):
            __slots__ = ()
            Equipment = DynAccessor(135480)
            Instructions = DynAccessor(135481)
            Shells = DynAccessor(135482)
            Consumables = DynAccessor(135483)

        Loadout = _Loadout(135484)
        Vehicles = DynAccessor(135485)

    Hangar = _Hangar(135486)


class user_missions(DynAccessor):
    __slots__ = ()

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        BattlePass = DynAccessor(135488)
        Events = DynAccessor(135489)
        Quests = DynAccessor(135490)
        PersonalMissions = DynAccessor(135491)
        EventMainInfoTip = DynAccessor(135492)

    hangarWidget = _hangarWidget(135493)

    class _hub(DynAccessor):
        __slots__ = ()

        class _basicMissions(DynAccessor):
            __slots__ = ()
            MainView = DynAccessor(135494)

            class _DailyMissionsSection(DynAccessor):
                __slots__ = ()
                MainView = DynAccessor(135495)
                DailyBlock = DynAccessor(135496)
                PremiumBlock = DynAccessor(135497)
                RewardProgressBlock = DynAccessor(135498)

            DailyMissionsSection = _DailyMissionsSection(135499)
            WeeklyMissions = DynAccessor(135500)
            PersonalMissions = DynAccessor(135501)

        basicMissions = _basicMissions(135502)

        class _challengeMissions(DynAccessor):
            __slots__ = ()
            MainView = DynAccessor(135503)

        challengeMissions = _challengeMissions(135504)

    hub = _hub(135505)


class vehicle_hub(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        VehicleParams = DynAccessor(135507)
        Wallet = DynAccessor(135508)
        VehicleInfo = DynAccessor(135509)
        ManageableVehiclePlaylists = DynAccessor(135510)
        VehiclesInfo = DynAccessor(135511)
        VehiclesStatistics = DynAccessor(135512)
        VehicleFilters = DynAccessor(135513)
        VehiclePlaylists = DynAccessor(135514)
        VehiclesInventory = DynAccessor(135515)

    default = _default(135516)


class vehicle_menu(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Customization = DynAccessor(135518)
        CrewAutoReturn = DynAccessor(135519)
        CrewRetrain = DynAccessor(135520)
        QuickTraining = DynAccessor(135521)
        CrewOut = DynAccessor(135522)
        CrewBack = DynAccessor(135523)
        EasyEquip = DynAccessor(135524)
        ArmorInspector = DynAccessor(135525)
        FieldModification = DynAccessor(135526)
        NationChange = DynAccessor(135527)
        Research = DynAccessor(135528)
        AboutVehicle = DynAccessor(135529)
        Compare = DynAccessor(135530)
        Repairs = DynAccessor(135531)
        VehSkillTree = DynAccessor(135532)
        ProBoost = DynAccessor(135533)

    default = _default(135534)


class white_tiger(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Carousel = DynAccessor(135536)
        ConsumablesPanel = DynAccessor(135537)
        Progression = DynAccessor(135538)
        Crewman = DynAccessor(135539)
        VehicleStats = DynAccessor(135540)
        ProgressionContent = DynAccessor(135541)
        ProgressionQuests = DynAccessor(135542)
        LootboxEntryPoint = DynAccessor(135543)

    shared = _shared(135544)


class battle_royale(DynAccessor):
    __slots__ = ()
    BattleSelector = DynAccessor(135546)
    UserMissions = DynAccessor(135547)
    VehiclesInventory = DynAccessor(135548)
    VehiclesFilter = DynAccessor(135549)
    AlertMessage = DynAccessor(135550)
    Header = DynAccessor(135551)
    LoadoutPanelContainer = DynAccessor(135552)
    Events = DynAccessor(135553)

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        Progression = DynAccessor(135554)
        EventShop = DynAccessor(135555)

    hangarWidget = _hangarWidget(135556)

    class _loadoutPanelContainer(DynAccessor):
        __slots__ = ()
        Loadout = DynAccessor(135557)
        Commander = DynAccessor(135558)

    loadoutPanelContainer = _loadoutPanelContainer(135559)


class comp7(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(135561)
        Schedule = DynAccessor(135562)
        SeasonModifier = DynAccessor(135563)
        RoleSkillSlot = DynAccessor(135564)
        UserMissions = DynAccessor(135565)
        EntryPoint = DynAccessor(135566)
        WeeklyQuestsWidget = DynAccessor(135567)
        BattleResultsWeeklyQuests = DynAccessor(135568)
        BattleResultsCustomizationQuests = DynAccessor(135569)

    shared = _shared(135570)


class comp7_light(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(135572)
        SeasonModifier = DynAccessor(135573)
        RoleSkillSlot = DynAccessor(135574)
        UserMissions = DynAccessor(135575)
        EntryPoint = DynAccessor(135576)
        Quests = DynAccessor(135577)
        BattleResultsProgressionQuests = DynAccessor(135578)

    shared = _shared(135579)


class frontline(DynAccessor):
    __slots__ = ()

    class _loadout(DynAccessor):
        __slots__ = ()
        BattleAbilities = DynAccessor(135581)

    loadout = _loadout(135582)

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(135583)
        AlertMessage = DynAccessor(135584)

    shared = _shared(135585)


class fun_random(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(135587)
        ProgressionEntryPoint = DynAccessor(135588)
        ProgressionQuests = DynAccessor(135589)

    shared = _shared(135590)


class last_stand(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Carousel = DynAccessor(135592)
        Difficulty = DynAccessor(135593)
        MoneyBalance = DynAccessor(135594)
        TeamStats = DynAccessor(135595)
        Meta = DynAccessor(135596)
        Keys = DynAccessor(135597)
        Quests = DynAccessor(135598)
        RewardPath = DynAccessor(135599)
        Shop = DynAccessor(135600)
        Gsw = DynAccessor(135601)
        Switcher = DynAccessor(135602)
        PresetsSwitcher = DynAccessor(135603)
        VehiclesDaily = DynAccessor(135604)
        BundleCard = DynAccessor(135605)
        DailyCard = DynAccessor(135606)
        Parallax = DynAccessor(135607)

    shared = _shared(135608)


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
