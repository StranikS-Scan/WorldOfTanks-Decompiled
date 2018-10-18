# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/strings_entries/ingame_gui.py
from gui.impl.gen_utils import DynAccessor

class IngameGui(DynAccessor):
    __slots__ = ()

    class aim(DynAccessor):
        __slots__ = ()
        zoom = 1595

    class attackReason(DynAccessor):
        __slots__ = ()
        artilleryProtection = 1629
        artillery_sector = 1630
        bombers = 1631

    class battleEndWarning(DynAccessor):
        __slots__ = ()
        text = 1600

    class battleMessenger(DynAccessor):
        __slots__ = ()

        class toxic(DynAccessor):
            __slots__ = ()

            class blackList(DynAccessor):
                __slots__ = ()

                class ADD_IN_BLACKLIST(DynAccessor):
                    __slots__ = ()
                    body = 1606
                    header = 1605

                class CANT_ADD_IN_BLACKLIST(DynAccessor):
                    __slots__ = ()
                    body = 1608
                    header = 1607

                class REMOVE_FROM_BLACKLIST(DynAccessor):
                    __slots__ = ()
                    body = 1610
                    header = 1609

    class battleProgress(DynAccessor):
        __slots__ = ()

        class hint(DynAccessor):
            __slots__ = ()
            description = 1638
            noBindingKey = 1645
            press = 1637

    class chat_example(DynAccessor):
        __slots__ = ()
        attack = 1165
        attack_enemy = 1170
        attention_to_cell = 1169
        back_to_base = 1166
        follow_me = 1164

        class global_msg(DynAccessor):
            __slots__ = ()

            class atk(DynAccessor):
                __slots__ = ()
                focus_hq = 1152
                save_tanks = 1146
                time = 1147

            class c_def(DynAccessor):
                __slots__ = ()
                focus_hq = 1153
                save_tanks = 1144
                time = 1148

            class lane(DynAccessor):
                __slots__ = ()
                center = 1150
                east = 1151
                west = 1149

        help_me = 1162
        help_me_ex = 1163
        negative = 1168
        positive = 1167
        reloading_cassette = 1156
        reloading_gun = 1155
        reloading_ready = 1157
        reloading_ready_cassette = 1159
        reloading_unavailable = 1160
        spg_aim_area = 1171
        stop = 1161
        support_me_with_fire = 1154
        turn_back = 1158

    class chat_shortcuts(DynAccessor):
        __slots__ = ()
        attack = 1121
        attack_enemy = 1142
        attack_enemy_reloading = 1143
        attention_to_base_atk = 1131
        attention_to_base_def = 1132
        attention_to_cell = 1125
        attention_to_objective_atk = 1129
        attention_to_objective_def = 1130
        attention_to_position = 1128
        back_to_base = 1122
        follow_me = 1120

        class global_msg(DynAccessor):
            __slots__ = ()

            class atk(DynAccessor):
                __slots__ = ()
                focus_hq = 1140
                save_tanks = 1133
                time = 1135

            class c_def(DynAccessor):
                __slots__ = ()
                focus_hq = 1141
                save_tanks = 1134
                time = 1136

            class lane(DynAccessor):
                __slots__ = ()
                center = 1138
                east = 1139
                west = 1137

        help_me = 1118
        help_me_ex = 1119
        negative = 1124
        positive = 1123
        reloading_cassette = 1113
        reloading_gun = 1112
        reloading_ready = 1114
        reloading_ready_cassette = 1115
        reloading_unavailable = 1116
        spg_aim_area = 1126
        spg_aim_area_reloading = 1127
        stop = 1117
        support_me_with_fire = 1111
        turn_back = 1110

    class colorSettingsTipPanel(DynAccessor):
        __slots__ = ()
        btnLabel = 1639

    class consumables_panel(DynAccessor):
        __slots__ = ()

        class equipment(DynAccessor):
            __slots__ = ()
            cooldownSeconds = 1279

            class tooltip(DynAccessor):
                __slots__ = ()
                empty = 1278

    class countRibbons(DynAccessor):
        __slots__ = ()
        multiSeparator = 1540

    class cruise_ctrl(DynAccessor):
        __slots__ = ()
        speedMetric = 1277

    class damageIndicator(DynAccessor):
        __slots__ = ()
        multiplier = 1601

    class damageLog(DynAccessor):
        __slots__ = ()
        multiplier = 1564

        class shellType(DynAccessor):
            __slots__ = ()
            ARMOR_PIERCING = 1559
            ARMOR_PIERCING_CR = 1562
            ARMOR_PIERCING_HE = 1561
            HIGH_EXPLOSIVE = 1560
            HOLLOW_CHARGE = 1563

    class damage_panel(DynAccessor):
        __slots__ = ()

        class crew(DynAccessor):
            __slots__ = ()

            class commander(DynAccessor):
                __slots__ = ()
                destroyed = 1262
                normal = 1261

            class driver(DynAccessor):
                __slots__ = ()
                destroyed = 1264
                normal = 1263

            class gunner1(DynAccessor):
                __slots__ = ()
                destroyed = 1270
                normal = 1269

            class gunner2(DynAccessor):
                __slots__ = ()
                destroyed = 1272
                normal = 1271

            class loader1(DynAccessor):
                __slots__ = ()
                destroyed = 1274
                normal = 1273

            class loader2(DynAccessor):
                __slots__ = ()
                destroyed = 1276
                normal = 1275

            class radioman1(DynAccessor):
                __slots__ = ()
                destroyed = 1266
                normal = 1265

            class radioman2(DynAccessor):
                __slots__ = ()
                destroyed = 1268
                normal = 1267

        class devices(DynAccessor):
            __slots__ = ()

            class ammoBay(DynAccessor):
                __slots__ = ()
                critical = 1244
                destroyed = 1245
                normal = 1243

            class chassis(DynAccessor):
                __slots__ = ()
                critical = 1250
                destroyed = 1251
                normal = 1249

            class engine(DynAccessor):
                __slots__ = ()
                critical = 1238
                destroyed = 1239
                normal = 1237

            class fuelTank(DynAccessor):
                __slots__ = ()
                critical = 1256
                destroyed = 1257
                normal = 1255

            class gun(DynAccessor):
                __slots__ = ()
                critical = 1241
                destroyed = 1242
                normal = 1240

            class radio(DynAccessor):
                __slots__ = ()
                critical = 1253
                destroyed = 1254
                normal = 1252

            class surveyingDevice(DynAccessor):
                __slots__ = ()
                critical = 1259
                destroyed = 1260
                normal = 1258

            class track(DynAccessor):
                __slots__ = ()
                critical = 1247
                destroyed = 1248
                normal = 1246

            class turretRotator(DynAccessor):
                __slots__ = ()
                critical = 1235
                destroyed = 1236
                normal = 1234

    class devices(DynAccessor):
        __slots__ = ()
        ammo_bay = 1043
        chassis = 1051
        engine = 1042
        fuel_tank = 1044
        gun = 1048
        left_track = 1046
        radio = 1045
        right_track = 1047
        surveing_device = 1050
        turret_rotator = 1049

    class distance(DynAccessor):
        __slots__ = ()
        meters = 1596

    class dynamicSquad(DynAccessor):
        __slots__ = ()

        class ally(DynAccessor):
            __slots__ = ()
            add = 1586
            disabled = 1588
            received = 1593
            wasSent = 1590

        class enemy(DynAccessor):
            __slots__ = ()
            add = 1587
            disabled = 1589
            received = 1594
            wasSent = 1591

        invite = 1592

    class efficiencyRibbons(DynAccessor):
        __slots__ = ()
        armor = 1541
        assistByAbility = 1625
        assistSpot = 1550
        assistTrack = 1549
        burn = 1545
        capture = 1542
        crits = 1551
        damage = 1543
        defence = 1546
        defenderBonus = 1624
        destructibleDamaged = 1621
        destructibleDestroyed = 1622
        destructiblesDefended = 1623
        enemySectorCaptured = 1620
        kill = 1547
        ram = 1544
        receivedBurn = 1555
        receivedCrits = 1553
        receivedDamage = 1554
        receivedRam = 1556
        receivedWorldCollision = 1557
        spotted = 1548
        stun = 1565
        vehicleRecovery = 1558
        worldCollision = 1552

    class epic_players_panel(DynAccessor):
        __slots__ = ()

        class state(DynAccessor):
            __slots__ = ()

            class hidden(DynAccessor):
                __slots__ = ()
                body = 1309
                header = 1308
                note = 1310

            class medium_player(DynAccessor):
                __slots__ = ()
                body = 1315
                header = 1314
                note = 1316

            class medium_tank(DynAccessor):
                __slots__ = ()
                body = 1318
                header = 1317
                note = 1319

            class short(DynAccessor):
                __slots__ = ()
                body = 1312
                header = 1311
                note = 1313

            class toggle(DynAccessor):
                __slots__ = ()
                body = 1321
                header = 1320
                note = 1322

    class flagNotification(DynAccessor):
        __slots__ = ()
        flagAbsorbed = 1582
        flagCaptured = 1579
        flagDelivered = 1581
        flagInbase = 1580

    class flags(DynAccessor):
        __slots__ = ()
        timer = 1539

    class fortConsumables(DynAccessor):
        __slots__ = ()

        class timer(DynAccessor):
            __slots__ = ()
            postfix = 1538

    class hitMarker(DynAccessor):
        __slots__ = ()
        blocked = 1566
        critical = 1568
        ricochet = 1567

    class marker(DynAccessor):
        __slots__ = ()
        meters = 1145

    class personalMissions(DynAccessor):
        __slots__ = ()

        class tip(DynAccessor):
            __slots__ = ()
            additionalHeader = 1535
            mainHeader = 1534

            class noQuests(DynAccessor):
                __slots__ = ()
                battleType = 1537
                vehicleType = 1536

    class player_errors(DynAccessor):
        __slots__ = ()

        class cant_move(DynAccessor):
            __slots__ = ()
            chassis_damaged = 1059
            crew_inactive = 1057
            engine_damaged = 1058

        class cant_shoot(DynAccessor):
            __slots__ = ()
            crew_inactive = 1061
            gun_damaged = 1063
            gun_locked = 1065
            gun_reload = 1064
            no_ammo = 1062
            vehicle_destroyed = 1060

        class cant_switch(DynAccessor):
            __slots__ = ()
            engine_destroyed = 1066

        class equipment(DynAccessor):
            __slots__ = ()
            alreadyActivated = 1067

            class extinguisher(DynAccessor):
                __slots__ = ()
                doesNotActivated = 1073

            isInCooldown = 1068

            class medkit(DynAccessor):
                __slots__ = ()
                allTankmenAreSafe = 1070
                tankmanIsSafe = 1069

            class order(DynAccessor):
                __slots__ = ()
                notReady = 1074

            class repairkit(DynAccessor):
                __slots__ = ()
                allDevicesAreNotDamaged = 1072
                deviceIsNotDamaged = 1071

    class player_messages(DynAccessor):
        __slots__ = ()
        ALLY_HIT = 1087
        COMBAT_EQUIPMENT_READY_ARTILLERY = 1435
        COMBAT_EQUIPMENT_READY_BOMBER = 1436
        COMBAT_EQUIPMENT_READY_INSPIRE = 1439
        COMBAT_EQUIPMENT_READY_RECON = 1437
        COMBAT_EQUIPMENT_READY_SMOKE = 1438
        COMBAT_EQUIPMENT_USED_ARTILLERY = 1440
        COMBAT_EQUIPMENT_USED_BOMBER = 1441
        COMBAT_EQUIPMENT_USED_INSPIRE = 1444
        COMBAT_EQUIPMENT_USED_RECON = 1442
        COMBAT_EQUIPMENT_USED_SMOKE = 1443
        DEATH_FROM_ARTILLERY_ALLY_ALLY = 1397
        DEATH_FROM_ARTILLERY_ALLY_ENEMY = 1398
        DEATH_FROM_ARTILLERY_ALLY_SUICIDE = 1394
        DEATH_FROM_ARTILLERY_ENEMY_ALLY = 1400
        DEATH_FROM_ARTILLERY_ENEMY_ENEMY = 1399
        DEATH_FROM_ARTILLERY_ENEMY_SUICIDE = 1393
        DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN_ALLY = 1404
        DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN_ENEMY = 1403
        DEATH_FROM_BOMBER_ALLY_SUICIDE = 1396
        DEATH_FROM_BOMBER_ENEMY_SUICIDE = 1395
        DEATH_FROM_DEATH_ZONE_ALLY_ALLY = 1492
        DEATH_FROM_DEATH_ZONE_ALLY_ENEMY = 1493
        DEATH_FROM_DEATH_ZONE_ALLY_SELF = 1491
        DEATH_FROM_DEATH_ZONE_ALLY_SUICIDE = 1490
        DEATH_FROM_DEATH_ZONE_ENEMY_ALLY = 1496
        DEATH_FROM_DEATH_ZONE_ENEMY_ENEMY = 1497
        DEATH_FROM_DEATH_ZONE_ENEMY_SELF = 1495
        DEATH_FROM_DEATH_ZONE_ENEMY_SUICIDE = 1494
        DEATH_FROM_DEATH_ZONE_SELF_ALLY = 1488
        DEATH_FROM_DEATH_ZONE_SELF_ENEMY = 1489
        DEATH_FROM_DEATH_ZONE_SELF_SUICIDE = 1487
        DEATH_FROM_DEVICE_EXPLOSION_AT_FIRE = 1416
        DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT = 1414
        DEATH_FROM_DROWNING_ALLY_ALLY = 1429
        DEATH_FROM_DROWNING_ALLY_ENEMY = 1430
        DEATH_FROM_DROWNING_ALLY_SELF = 1428
        DEATH_FROM_DROWNING_ALLY_SUICIDE = 1427
        DEATH_FROM_DROWNING_ENEMY_ALLY = 1433
        DEATH_FROM_DROWNING_ENEMY_ENEMY = 1434
        DEATH_FROM_DROWNING_ENEMY_SELF = 1432
        DEATH_FROM_DROWNING_ENEMY_SUICIDE = 1431
        DEATH_FROM_DROWNING_SELF_ALLY = 1425
        DEATH_FROM_DROWNING_SELF_ENEMY = 1426
        DEATH_FROM_DROWNING_SELF_SUICIDE = 1424
        DEATH_FROM_GAS_ATTACK_ALLY_ALLY = 1501
        DEATH_FROM_GAS_ATTACK_ALLY_ENEMY = 1502
        DEATH_FROM_GAS_ATTACK_ALLY_SELF = 1500
        DEATH_FROM_GAS_ATTACK_ENEMY_ALLY = 1504
        DEATH_FROM_GAS_ATTACK_ENEMY_ENEMY = 1505
        DEATH_FROM_GAS_ATTACK_ENEMY_SELF = 1503
        DEATH_FROM_GAS_ATTACK_SELF_ALLY = 1498
        DEATH_FROM_GAS_ATTACK_SELF_ENEMY = 1499
        DEATH_FROM_INACTIVE_CREW = 1413
        DEATH_FROM_INACTIVE_CREW_AT_SHOT = 1411
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_ALLY = 1473
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_ENEMY = 1474
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF = 1472
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SUICIDE = 1471
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_ALLY = 1477
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_ENEMY = 1478
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF = 1476
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SUICIDE = 1475
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_ALLY = 1469
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_ENEMY = 1470
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE = 1468
        DEATH_FROM_OVERTURN_ALLY_ALLY = 1524
        DEATH_FROM_OVERTURN_ALLY_ENEMY = 1525
        DEATH_FROM_OVERTURN_ALLY_SELF = 1523
        DEATH_FROM_OVERTURN_ALLY_SUICIDE = 1522
        DEATH_FROM_OVERTURN_ENEMY_ALLY = 1528
        DEATH_FROM_OVERTURN_ENEMY_ENEMY = 1529
        DEATH_FROM_OVERTURN_ENEMY_SELF = 1527
        DEATH_FROM_OVERTURN_ENEMY_SUICIDE = 1526
        DEATH_FROM_OVERTURN_SELF_ALLY = 1520
        DEATH_FROM_OVERTURN_SELF_ENEMY = 1521
        DEATH_FROM_OVERTURN_SELF_SUICIDE = 1519
        DEATH_FROM_RAMMING_ALLY_ALLY = 1517
        DEATH_FROM_RAMMING_ALLY_ENEMY = 1518
        DEATH_FROM_RAMMING_ALLY_SELF = 1516
        DEATH_FROM_RAMMING_ALLY_SUICIDE = 1515
        DEATH_FROM_RAMMING_ENEMY_ALLY = 1532
        DEATH_FROM_RAMMING_ENEMY_ENEMY = 1533
        DEATH_FROM_RAMMING_ENEMY_SELF = 1531
        DEATH_FROM_RAMMING_ENEMY_SUICIDE = 1530
        DEATH_FROM_RAMMING_SELF_ALLY = 1513
        DEATH_FROM_RAMMING_SELF_ENEMY = 1514
        DEATH_FROM_RAMMING_SELF_SUICIDE = 1512
        DEATH_FROM_RECOVERY_ALLY_SUICIDE = 1402
        DEATH_FROM_RECOVERY_ENEMY_SUICIDE = 1401
        DEATH_FROM_SECTOR_BOMBERS_UNKNOWN_ALLY = 1408
        DEATH_FROM_SECTOR_BOMBERS_UNKNOWN_ENEMY = 1407
        DEATH_FROM_SECTOR_PROTECTION_UNKNOWN_ALLY = 1406
        DEATH_FROM_SECTOR_PROTECTION_UNKNOWN_ENEMY = 1405
        DEATH_FROM_SHOT_ALLY_ALLY = 1375
        DEATH_FROM_SHOT_ALLY_ALLY_ARTILLERY = 1376
        DEATH_FROM_SHOT_ALLY_ALLY_BOMBER = 1377
        DEATH_FROM_SHOT_ALLY_ENEMY = 1378
        DEATH_FROM_SHOT_ALLY_ENEMY_ARTILLERY = 1379
        DEATH_FROM_SHOT_ALLY_ENEMY_BOMBER = 1380
        DEATH_FROM_SHOT_ALLY_SUICIDE = 1381
        DEATH_FROM_SHOT_ALLY_SUICIDE_ARTILLERY = 1382
        DEATH_FROM_SHOT_ALLY_SUICIDE_BOMBER = 1383
        DEATH_FROM_SHOT_ENEMY_ALLY = 1387
        DEATH_FROM_SHOT_ENEMY_ALLY_ARTILLERY = 1388
        DEATH_FROM_SHOT_ENEMY_ALLY_BOMBER = 1389
        DEATH_FROM_SHOT_ENEMY_ENEMY = 1390
        DEATH_FROM_SHOT_ENEMY_ENEMY_ARTILLERY = 1391
        DEATH_FROM_SHOT_ENEMY_ENEMY_BOMBER = 1392
        DEATH_FROM_SHOT_ENEMY_SUICIDE = 1384
        DEATH_FROM_SHOT_ENEMY_SUICIDE_ARTILLERY = 1385
        DEATH_FROM_SHOT_ENEMY_SUICIDE_BOMBER = 1386
        DEATH_FROM_SHOT_SELF_ALLY = 1369
        DEATH_FROM_SHOT_SELF_ALLY_ARTILLERY = 1370
        DEATH_FROM_SHOT_SELF_ALLY_BOMBER = 1371
        DEATH_FROM_SHOT_SELF_ENEMY = 1372
        DEATH_FROM_SHOT_SELF_ENEMY_ARTILLERY = 1373
        DEATH_FROM_SHOT_SELF_ENEMY_BOMBER = 1374
        DEATH_FROM_WORLD_COLLISION_ALLY_ALLY = 1456
        DEATH_FROM_WORLD_COLLISION_ALLY_ENEMY = 1457
        DEATH_FROM_WORLD_COLLISION_ALLY_SELF = 1455
        DEATH_FROM_WORLD_COLLISION_ALLY_SUICIDE = 1454
        DEATH_FROM_WORLD_COLLISION_ENEMY_ALLY = 1460
        DEATH_FROM_WORLD_COLLISION_ENEMY_ENEMY = 1461
        DEATH_FROM_WORLD_COLLISION_ENEMY_SELF = 1459
        DEATH_FROM_WORLD_COLLISION_ENEMY_SUICIDE = 1458
        DEATH_FROM_WORLD_COLLISION_SELF_ALLY = 1452
        DEATH_FROM_WORLD_COLLISION_SELF_ENEMY = 1453
        DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE = 1451
        DESTRUCTIBLE_DESTROYED_ALLY = 1612
        DESTRUCTIBLE_DESTROYED_ENEMY = 1613
        DESTRUCTIBLE_DESTROYED_SELF = 1611
        DEVICE_CRITICAL_AT_FIRE = 1079
        DEVICE_CRITICAL_AT_SHOT = 1075
        DEVICE_DESTROYED_AT_FIRE = 1082
        DEVICE_DESTROYED_AT_SHOT = 1076
        DEVICE_REPAIRED = 1086
        DEVICE_REPAIRED_TO_CRITICAL = 1083
        DEVICE_STARTED_FIRE_AT_SHOT = 1077
        ENGINE_CRITICAL_AT_UNLIMITED_RPM = 1080
        ENGINE_DESTROYED_AT_UNLIMITED_RPM = 1081
        FIRE_STOPPED = 1084
        TANKMAN_HIT_AT_SHOT = 1078
        TANKMAN_RESTORED = 1085
        allied_team_name = 1095
        ally_base_captured_by_notification = 1091
        ally_base_captured_notification = 1088
        base_capture_blocked = 1094
        base_captured_by_notification = 1093
        base_captured_notification = 1090
        enemy_base_captured_by_notification = 1092
        enemy_base_captured_notification = 1089
        enemy_team_name = 1096
        halloweenBliss = 1648
        halloweenSalvation = 1647
        halloweenSin = 1646
        loader_intuition_was_used = 1109

        class postmortem_caption(DynAccessor):
            __slots__ = ()
            other = 1099
            self = 1098

        postmortem_caption_ = 1097
        postmortem_userNoHasAmmo = 1100
        replayControlsHelp1 = 1106
        replayControlsHelp2 = 1107
        replayControlsHelp3 = 1108
        replayFreeCameraActivated = 1102
        replayPaused = 1105
        replaySavedCameraActivated = 1103
        replaySpeedChange = 1104
        tank_in_fire = 1101

    class players_panel(DynAccessor):
        __slots__ = ()

        class state(DynAccessor):
            __slots__ = ()

            class large(DynAccessor):
                __slots__ = ()
                body = 1301
                header = 1300
                note = 1302

            class medium(DynAccessor):
                __slots__ = ()
                body = 1295
                header = 1294
                note = 1296

            class medium2(DynAccessor):
                __slots__ = ()
                body = 1298
                header = 1297
                note = 1299

            class none(DynAccessor):
                __slots__ = ()
                body = 1289
                header = 1288
                note = 1290

            class short(DynAccessor):
                __slots__ = ()
                body = 1292
                header = 1291
                note = 1293

        unknown_clan = 1307
        unknown_frags = 1305
        unknown_name = 1303
        unknown_vehicle = 1304
        unknown_vehicleState = 1306

    class postmortem(DynAccessor):
        __slots__ = ()

        class tips(DynAccessor):
            __slots__ = ()

            class exitHangar(DynAccessor):
                __slots__ = ()
                label = 1286
                text = 1287

            class observerMode(DynAccessor):
                __slots__ = ()
                label = 1284
                text = 1285

    class postmortem_messages(DynAccessor):
        __slots__ = ()
        DEATH_FROM_DEATH_ZONE_ALLY_SELF = 1484
        DEATH_FROM_DEATH_ZONE_ENEMY_SELF = 1482
        DEATH_FROM_DEATH_ZONE_SELF_SUICIDE = 1480
        DEATH_FROM_DEVICE_EXPLOSION_AT_FIRE = 1417
        DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT = 1415
        DEATH_FROM_DROWNING_ALLY_SELF = 1423
        DEATH_FROM_DROWNING_ENEMY_SELF = 1421
        DEATH_FROM_DROWNING_SELF_SUICIDE = 1419
        DEATH_FROM_FIRE = 1410
        DEATH_FROM_INACTIVE_CREW_AT_SHOT = 1412
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF = 1467
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF = 1465
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE = 1463
        DEATH_FROM_OVERTURN_ALLY_SELF = 1368
        DEATH_FROM_OVERTURN_ENEMY_SELF = 1367
        DEATH_FROM_OVERTURN_SELF_SUICIDE = 1366
        DEATH_FROM_RAMMING_ALLY_SELF = 1511
        DEATH_FROM_RAMMING_ENEMY_SELF = 1509
        DEATH_FROM_RAMMING_SELF_SUICIDE = 1507
        DEATH_FROM_SHOT = 1360
        DEATH_FROM_SHOT_ARTILLERY = 1364
        DEATH_FROM_SHOT_BOMBER = 1365
        DEATH_FROM_WORLD_COLLISION_ALLY_SELF = 1450
        DEATH_FROM_WORLD_COLLISION_ENEMY_SELF = 1448
        DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE = 1446
        DEATH_UNKNOWN = 1361

    class recovery(DynAccessor):
        __slots__ = ()
        cooldown = 1628
        hint1 = 1626
        hint2 = 1627

    class repairPoint(DynAccessor):
        __slots__ = ()
        title = 1598
        unavailable = 1599

    class respawnView(DynAccessor):
        __slots__ = ()
        additionalTip = 1570
        additionalTipLimited = 1571
        classNotAvailable = 1578
        cooldownLbl = 1572
        destroyedLbl = 1573
        disabledLbl = 1574
        emptySlotInfo = 1576
        emptySlotInfoTooltip = 1577
        nextVehicleName = 1575
        title = 1569

    class rewardWindow(DynAccessor):
        __slots__ = ()

        class base(DynAccessor):
            __slots__ = ()
            btnLabel = 1644
            descText = 1643
            headerText = 1642
            subHeaderText = 1641

        winHeaderText = 1640

    class scorePanel(DynAccessor):
        __slots__ = ()
        mySquadLbl = 1584
        playerScore = 1585
        squadLbl = 1583

    class shells_kinds(DynAccessor):
        __slots__ = ()
        ARMOR_PIERCING = 1229
        ARMOR_PIERCING_CR = 1231
        ARMOR_PIERCING_HE = 1230
        HIGH_EXPLOSIVE = 1228
        HOLLOW_CHARGE = 1227
        params = 1232
        stunParams = 1233

    class siegeMode(DynAccessor):
        __slots__ = ()

        class hint(DynAccessor):
            __slots__ = ()

            class forMode(DynAccessor):
                __slots__ = ()
                c_0 = 1615
                c_1 = 1616
                c_2 = 1617
                c_3 = 1618

            noBinding = 1619
            press = 1614

    class statistics(DynAccessor):
        __slots__ = ()
        exit = 1196

        class final(DynAccessor):
            __slots__ = ()
            heroes = 1219

            class lifeInfo(DynAccessor):
                __slots__ = ()
                alive = 1220
                dead = 1221

            class personal(DynAccessor):
                __slots__ = ()
                capturePoints = 1217
                damaged = 1212
                directHits = 1215
                directHitsReceived = 1216
                droppedCapturePoints = 1218
                killed = 1211
                postmortem = 1210
                shots = 1214
                spotted = 1213

            class reasons(DynAccessor):
                __slots__ = ()
                reason0 = 1200
                reason1lose = 1202
                reason1tie = 1203
                reason1win = 1201
                reason2 = 1204
                reason3 = 1205

            class stats(DynAccessor):
                __slots__ = ()
                credits = 1208
                experience = 1207
                multipliedExp = 1206
                repair = 1209

            class status(DynAccessor):
                __slots__ = ()
                lose = 1199
                tie = 1197
                win = 1198

        header = 1184

        class headers(DynAccessor):
            __slots__ = ()
            header0 = 1188
            header1 = 1189
            header2 = 1190
            header3 = 1191
            header4 = 1192

        class playerState(DynAccessor):
            __slots__ = ()
            c_0 = 1222
            c_1 = 1224
            c_2 = 1223
            c_3 = 1225
            c_4 = 1226

        class tab(DynAccessor):
            __slots__ = ()

            class line_up(DynAccessor):
                __slots__ = ()
                header = 1172
                title = 1173

            class progressTracing(DynAccessor):
                __slots__ = ()
                notAvailable = 1185

            class quests(DynAccessor):
                __slots__ = ()
                header = 1174

                class notAvailable(DynAccessor):
                    __slots__ = ()
                    title = 1183

                class nothingToPerform(DynAccessor):
                    __slots__ = ()
                    descr = 1181
                    title = 1180

                class status(DynAccessor):
                    __slots__ = ()
                    done = 1178
                    fullDone = 1179
                    inProgress = 1175
                    increaseResult = 1177
                    onPause = 1176

                class switchOff(DynAccessor):
                    __slots__ = ()
                    title = 1182

        class tabs(DynAccessor):
            __slots__ = ()
            group = 1193
            heroes = 1195
            personal = 1194

        team1title = 1186
        team2title = 1187

    class stun(DynAccessor):
        __slots__ = ()
        indicator = 1635
        seconds = 1636

    tabStatsHint = 1597

    class tankmen(DynAccessor):
        __slots__ = ()
        commander = 1052
        driver = 1053
        gunner = 1055
        loader = 1056
        radioman = 1054

    class timer(DynAccessor):
        __slots__ = ()
        battlePeriod = 1283
        started = 1282
        starting = 1281
        waiting = 1280

    class trajectoryView(DynAccessor):
        __slots__ = ()

        class hint(DynAccessor):
            __slots__ = ()
            alternateModeLeft = 1633
            alternateModeRight = 1634
            noBindingKey = 1632

    class vehicle_messages(DynAccessor):
        __slots__ = ()
        DEATH_FROM_DEATH_ZONE_ALLY_SELF = 1483
        DEATH_FROM_DEATH_ZONE_ENEMY_SELF = 1481
        DEATH_FROM_DEATH_ZONE_SELF_SUICIDE = 1479
        DEATH_FROM_DROWNING_ALLY_SELF = 1422
        DEATH_FROM_DROWNING_ENEMY_SELF = 1420
        DEATH_FROM_DROWNING_SELF_SUICIDE = 1418
        DEATH_FROM_FIRE = 1409
        DEATH_FROM_GAS_ATTACK_ALLY_SELF = 1486
        DEATH_FROM_GAS_ATTACK_ENEMY_SELF = 1485
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF = 1466
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF = 1464
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE = 1462
        DEATH_FROM_OVERTURN_ALLY_SELF = 1604
        DEATH_FROM_OVERTURN_ENEMY_SELF = 1603
        DEATH_FROM_OVERTURN_SELF_SUICIDE = 1602
        DEATH_FROM_RAMMING_ALLY_SELF = 1510
        DEATH_FROM_RAMMING_ENEMY_SELF = 1508
        DEATH_FROM_RAMMING_SELF_SUICIDE = 1506
        DEATH_FROM_SHOT = 1359
        DEATH_FROM_SHOT_ARTILLERY = 1362
        DEATH_FROM_SHOT_BOMBER = 1363
        DEATH_FROM_WORLD_COLLISION_ALLY_SELF = 1449
        DEATH_FROM_WORLD_COLLISION_ENEMY_SELF = 1447
        DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE = 1445
        DEVICE_CRITICAL_AT_RAMMING_ALLY_ALLY = 1340
        DEVICE_CRITICAL_AT_RAMMING_ALLY_SELF = 1337
        DEVICE_CRITICAL_AT_RAMMING_ALLY_SUICIDE = 1338
        DEVICE_CRITICAL_AT_RAMMING_ENEMY_ALLY = 1339
        DEVICE_CRITICAL_AT_RAMMING_ENEMY_SELF = 1336
        DEVICE_CRITICAL_AT_RAMMING_SELF_SUICIDE = 1335
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_ALLY = 1328
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_SELF = 1325
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_SUICIDE = 1326
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ENEMY_ALLY = 1327
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ENEMY_SELF = 1324
        DEVICE_CRITICAL_AT_WORLD_COLLISION_SELF_SUICIDE = 1323
        DEVICE_DESTROYED_AT_RAMMING_ALLY_ALLY = 1346
        DEVICE_DESTROYED_AT_RAMMING_ALLY_SELF = 1343
        DEVICE_DESTROYED_AT_RAMMING_ALLY_SUICIDE = 1344
        DEVICE_DESTROYED_AT_RAMMING_ENEMY_ALLY = 1345
        DEVICE_DESTROYED_AT_RAMMING_ENEMY_SELF = 1342
        DEVICE_DESTROYED_AT_RAMMING_SELF_SUICIDE = 1341
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_ALLY = 1334
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_SELF = 1331
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_SUICIDE = 1332
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ENEMY_ALLY = 1333
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ENEMY_SELF = 1330
        DEVICE_DESTROYED_AT_WORLD_COLLISION_SELF_SUICIDE = 1329
        DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_ALLY = 1352
        DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_SELF = 1349
        DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_SUICIDE = 1350
        DEVICE_STARTED_FIRE_AT_RAMMING_ENEMY_ALLY = 1351
        DEVICE_STARTED_FIRE_AT_RAMMING_ENEMY_SELF = 1348
        DEVICE_STARTED_FIRE_AT_RAMMING_SELF_SUICIDE = 1347
        TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_ALLY = 1358
        TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_SELF = 1355
        TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_SUICIDE = 1356
        TANKMAN_HIT_AT_WORLD_COLLISION_ENEMY_ALLY = 1357
        TANKMAN_HIT_AT_WORLD_COLLISION_ENEMY_SELF = 1354
        TANKMAN_HIT_AT_WORLD_COLLISION_SELF_SUICIDE = 1353
