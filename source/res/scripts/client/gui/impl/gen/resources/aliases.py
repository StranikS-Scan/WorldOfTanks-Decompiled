# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/aliases.py
from gui.impl.gen_utils import DynAccessor

class battle_modifiers(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Modifiers = DynAccessor(129264)

    shared = _shared(129265)


class battle_pass(DynAccessor):
    __slots__ = ()
    IntroVideo = DynAccessor(129267)
    ExtraVideo = DynAccessor(129268)
    Intro = DynAccessor(129269)
    ChapterChoice = DynAccessor(129270)
    Progression = DynAccessor(129271)
    PostProgression = DynAccessor(129272)
    BuyPass = DynAccessor(129273)
    BuyPassRewards = DynAccessor(129274)
    BuyLevels = DynAccessor(129275)
    BuyLevelsRewards = DynAccessor(129276)
    HolidayFinal = DynAccessor(129277)
    FinalRewardPreview = DynAccessor(129278)


class battle_result(DynAccessor):
    __slots__ = ()
    none = DynAccessor(129280)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        User = DynAccessor(129281)
        Vehicle = DynAccessor(129282)

    contextMenu = _contextMenu(129283)


class battle_results(DynAccessor):
    __slots__ = ()

    class _progression(DynAccessor):
        __slots__ = ()
        DailyMissions = DynAccessor(129285)
        WeeklyMissions = DynAccessor(129286)
        PersonalMissions = DynAccessor(129287)
        BattlePass = DynAccessor(129288)
        Prestige = DynAccessor(129289)
        BattleMatters = DynAccessor(129290)
        ModuleVehicleUnlocks = DynAccessor(129291)
        CommonQuests = DynAccessor(129292)

    progression = _progression(129293)


class common(DynAccessor):
    __slots__ = ()
    none = DynAccessor(129295)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(129296)

    contextMenu = _contextMenu(129297)

    class _tooltip(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(129298)
        Wulf = DynAccessor(129299)
        Param = DynAccessor(129300)

    tooltip = _tooltip(129301)

    class _popOver(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(129302)

    popOver = _popOver(129303)

    class _shared(DynAccessor):
        __slots__ = ()
        DynamicEconomics = DynAccessor(129304)

    shared = _shared(129305)


class hangar(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(129307)
        VehiclesStatistics = DynAccessor(129308)
        Consumables = DynAccessor(129309)
        Equipments = DynAccessor(129310)
        Instructions = DynAccessor(129311)
        Shells = DynAccessor(129312)
        Loadout = DynAccessor(129313)
        Crew = DynAccessor(129314)
        VehicleParams = DynAccessor(129315)
        ETEVehicleParams = DynAccessor(129316)
        CurrentVehicle = DynAccessor(129317)
        VehiclesInventory = DynAccessor(129318)
        MainMenu = DynAccessor(129319)
        VehicleMenu = DynAccessor(129320)
        LootboxEntryPoint = DynAccessor(129321)
        VehicleFilters = DynAccessor(129322)
        VehiclePlaylists = DynAccessor(129323)
        Teaser = DynAccessor(129324)
        OptionalDevicesAssistant = DynAccessor(129325)
        SpaceInteraction = DynAccessor(129326)
        HeroTank = DynAccessor(129327)
        UserMissions = DynAccessor(129328)
        ModeState = DynAccessor(129329)
        EasyTankEquip = DynAccessor(129330)
        PetEvent = DynAccessor(129331)
        PetObjectTooltip = DynAccessor(129332)
        Settings = DynAccessor(129333)
        KeyBindings = DynAccessor(129334)
        ManageableVehiclePlaylists = DynAccessor(129335)

    shared = _shared(129336)


class lobby_footer(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Platoon = DynAccessor(129338)
        ContactsList = DynAccessor(129339)
        SessionStats = DynAccessor(129340)
        VehicleCompare = DynAccessor(129341)
        NotificationsCenter = DynAccessor(129342)
        Chats = DynAccessor(129343)
        ReferralProgram = DynAccessor(129344)
        ServerInfo = DynAccessor(129345)

    default = _default(129346)


class lobby_header(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        FightStart = DynAccessor(129348)
        NavigationBar = DynAccessor(129349)
        Prebattle = DynAccessor(129350)
        Wallet = DynAccessor(129351)
        AccountDashboard = DynAccessor(129352)
        HeaderState = DynAccessor(129353)
        UserAccount = DynAccessor(129354)
        ReservesEntryPoint = DynAccessor(129355)
        PremShop = DynAccessor(129356)
        CurrentVehicle = DynAccessor(129357)

    default = _default(129358)


class select_vehicle(DynAccessor):
    __slots__ = ()

    class _select_vehicle(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(129360)
        VehiclesInventory = DynAccessor(129361)
        VehiclesStatistics = DynAccessor(129362)
        VehicleFilters = DynAccessor(129363)
        VehiclePlaylists = DynAccessor(129364)

    select_vehicle = _select_vehicle(129365)


class states(DynAccessor):
    __slots__ = ()

    class _Hangar(DynAccessor):
        __slots__ = ()

        class _Loadout(DynAccessor):
            __slots__ = ()
            Equipment = DynAccessor(129367)
            Instructions = DynAccessor(129368)
            Shells = DynAccessor(129369)
            Consumables = DynAccessor(129370)

        Loadout = _Loadout(129371)
        Vehicles = DynAccessor(129372)

    Hangar = _Hangar(129373)


class user_missions(DynAccessor):
    __slots__ = ()

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        BattlePass = DynAccessor(129375)
        Events = DynAccessor(129376)
        Quests = DynAccessor(129377)
        EventMainInfoTip = DynAccessor(129378)

    hangarWidget = _hangarWidget(129379)

    class _hub(DynAccessor):
        __slots__ = ()

        class _basicMissions(DynAccessor):
            __slots__ = ()
            MainView = DynAccessor(129380)

            class _DailyMissionsSection(DynAccessor):
                __slots__ = ()
                MainView = DynAccessor(129381)
                DailyBlock = DynAccessor(129382)
                PremiumBlock = DynAccessor(129383)
                RewardProgressBlock = DynAccessor(129384)

            DailyMissionsSection = _DailyMissionsSection(129385)
            WeeklyMissions = DynAccessor(129386)
            PersonalMissions = DynAccessor(129387)

        basicMissions = _basicMissions(129388)

    hub = _hub(129389)


class vehicle_hub(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        VehicleParams = DynAccessor(129391)
        Wallet = DynAccessor(129392)
        VehicleInfo = DynAccessor(129393)
        ManageableVehiclePlaylists = DynAccessor(129394)
        VehiclesInfo = DynAccessor(129395)
        VehiclesStatistics = DynAccessor(129396)
        VehicleFilters = DynAccessor(129397)
        VehiclePlaylists = DynAccessor(129398)
        VehiclesInventory = DynAccessor(129399)

    default = _default(129400)


class vehicle_menu(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Customization = DynAccessor(129402)
        CrewAutoReturn = DynAccessor(129403)
        CrewRetrain = DynAccessor(129404)
        QuickTraining = DynAccessor(129405)
        CrewOut = DynAccessor(129406)
        CrewBack = DynAccessor(129407)
        EasyEquip = DynAccessor(129408)
        ArmorInspector = DynAccessor(129409)
        FieldModification = DynAccessor(129410)
        NationChange = DynAccessor(129411)
        Research = DynAccessor(129412)
        AboutVehicle = DynAccessor(129413)
        Compare = DynAccessor(129414)
        Repairs = DynAccessor(129415)
        VehSkillTree = DynAccessor(129416)
        ProBoost = DynAccessor(129417)

    default = _default(129418)


class white_tiger(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Carousel = DynAccessor(129420)
        ConsumablesPanel = DynAccessor(129421)
        Progression = DynAccessor(129422)
        Crewman = DynAccessor(129423)
        VehicleStats = DynAccessor(129424)
        ProgressionContent = DynAccessor(129425)
        ProgressionQuests = DynAccessor(129426)
        LootboxEntryPoint = DynAccessor(129427)

    shared = _shared(129428)


class battle_royale(DynAccessor):
    __slots__ = ()
    BattleSelector = DynAccessor(129430)
    UserMissions = DynAccessor(129431)
    VehiclesInventory = DynAccessor(129432)
    VehiclesFilter = DynAccessor(129433)
    AlertMessage = DynAccessor(129434)
    Header = DynAccessor(129435)
    LoadoutPanelContainer = DynAccessor(129436)
    Events = DynAccessor(129437)

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        Progression = DynAccessor(129438)
        EventShop = DynAccessor(129439)

    hangarWidget = _hangarWidget(129440)

    class _loadoutPanelContainer(DynAccessor):
        __slots__ = ()
        Loadout = DynAccessor(129441)
        Commander = DynAccessor(129442)

    loadoutPanelContainer = _loadoutPanelContainer(129443)


class comp7(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(129445)
        Schedule = DynAccessor(129446)
        SeasonModifier = DynAccessor(129447)
        RoleSkillSlot = DynAccessor(129448)
        UserMissions = DynAccessor(129449)
        EntryPoint = DynAccessor(129450)
        WeeklyQuestsWidget = DynAccessor(129451)
        BattleResultsWeeklyQuests = DynAccessor(129452)
        BattleResultsCustomizationQuests = DynAccessor(129453)

    shared = _shared(129454)


class comp7_light(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(129456)
        SeasonModifier = DynAccessor(129457)
        RoleSkillSlot = DynAccessor(129458)
        UserMissions = DynAccessor(129459)
        EntryPoint = DynAccessor(129460)
        Quests = DynAccessor(129461)

    shared = _shared(129462)


class frontline(DynAccessor):
    __slots__ = ()

    class _loadout(DynAccessor):
        __slots__ = ()
        BattleAbilities = DynAccessor(129464)

    loadout = _loadout(129465)

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(129466)
        AlertMessage = DynAccessor(129467)

    shared = _shared(129468)


class fun_random(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(129470)
        ProgressionEntryPoint = DynAccessor(129471)

    shared = _shared(129472)


class last_stand(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Carousel = DynAccessor(129474)
        Difficulty = DynAccessor(129475)
        MoneyBalance = DynAccessor(129476)
        TeamStats = DynAccessor(129477)
        Meta = DynAccessor(129478)
        Keys = DynAccessor(129479)
        Quests = DynAccessor(129480)
        RewardPath = DynAccessor(129481)
        Shop = DynAccessor(129482)
        Gsw = DynAccessor(129483)
        Switcher = DynAccessor(129484)
        PresetsSwitcher = DynAccessor(129485)
        VehiclesDaily = DynAccessor(129486)
        BundleCard = DynAccessor(129487)
        DailyCard = DynAccessor(129488)
        Parallax = DynAccessor(129489)

    shared = _shared(129490)


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
