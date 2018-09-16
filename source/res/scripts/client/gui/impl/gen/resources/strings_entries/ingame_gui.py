# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/strings_entries/ingame_gui.py
from gui.impl.gen_utils import DynAccessor

class IngameGui(DynAccessor):
    __slots__ = ()

    class aim(DynAccessor):
        __slots__ = ()
        zoom = 660

    class attackReason(DynAccessor):
        __slots__ = ()
        artillery_sector = 695
        artilleryProtection = 694
        bombers = 696

    class battleEndWarning(DynAccessor):
        __slots__ = ()
        text = 665

    class battleMessenger(DynAccessor):
        __slots__ = ()

        class toxic(DynAccessor):
            __slots__ = ()

            class blackList(DynAccessor):
                __slots__ = ()

                class ADD_IN_BLACKLIST(DynAccessor):
                    __slots__ = ()
                    body = 671
                    header = 670

                class CANT_ADD_IN_BLACKLIST(DynAccessor):
                    __slots__ = ()
                    body = 673
                    header = 672

                class REMOVE_FROM_BLACKLIST(DynAccessor):
                    __slots__ = ()
                    body = 675
                    header = 674

    class battleProgress(DynAccessor):
        __slots__ = ()

        class hint(DynAccessor):
            __slots__ = ()
            description = 703
            noBindingKey = 704
            press = 702

    class chat_example(DynAccessor):
        __slots__ = ()
        attack = 231
        attack_enemy = 236
        attention_to_cell = 235
        back_to_base = 232
        follow_me = 230

        class global_msg(DynAccessor):
            __slots__ = ()

            class atk(DynAccessor):
                __slots__ = ()
                focus_hq = 218
                save_tanks = 212
                time = 213

            class c_def(DynAccessor):
                __slots__ = ()
                focus_hq = 219
                save_tanks = 210
                time = 214

            class lane(DynAccessor):
                __slots__ = ()
                center = 216
                east = 217
                west = 215

        help_me = 228
        help_me_ex = 229
        negative = 234
        positive = 233
        reloading_cassette = 222
        reloading_gun = 221
        reloading_ready = 223
        reloading_ready_cassette = 225
        reloading_unavailable = 226
        spg_aim_area = 237
        stop = 227
        support_me_with_fire = 220
        turn_back = 224

    class chat_shortcuts(DynAccessor):
        __slots__ = ()
        attack = 187
        attack_enemy = 208
        attack_enemy_reloading = 209
        attention_to_base_atk = 197
        attention_to_base_def = 198
        attention_to_cell = 191
        attention_to_objective_atk = 195
        attention_to_objective_def = 196
        attention_to_position = 194
        back_to_base = 188
        follow_me = 186

        class global_msg(DynAccessor):
            __slots__ = ()

            class atk(DynAccessor):
                __slots__ = ()
                focus_hq = 206
                save_tanks = 199
                time = 201

            class c_def(DynAccessor):
                __slots__ = ()
                focus_hq = 207
                save_tanks = 200
                time = 202

            class lane(DynAccessor):
                __slots__ = ()
                center = 204
                east = 205
                west = 203

        help_me = 184
        help_me_ex = 185
        negative = 190
        positive = 189
        reloading_cassette = 179
        reloading_gun = 178
        reloading_ready = 180
        reloading_ready_cassette = 181
        reloading_unavailable = 182
        spg_aim_area = 192
        spg_aim_area_reloading = 193
        stop = 183
        support_me_with_fire = 177
        turn_back = 176

    class consumables_panel(DynAccessor):
        __slots__ = ()

        class equipment(DynAccessor):
            __slots__ = ()
            cooldownSeconds = 344

            class tooltip(DynAccessor):
                __slots__ = ()
                empty = 343

    class countRibbons(DynAccessor):
        __slots__ = ()
        multiSeparator = 605

    class cruise_ctrl(DynAccessor):
        __slots__ = ()
        speedMetric = 342

    class damage_panel(DynAccessor):
        __slots__ = ()

        class crew(DynAccessor):
            __slots__ = ()

            class commander(DynAccessor):
                __slots__ = ()
                destroyed = 327
                normal = 326

            class driver(DynAccessor):
                __slots__ = ()
                destroyed = 329
                normal = 328

            class gunner1(DynAccessor):
                __slots__ = ()
                destroyed = 335
                normal = 334

            class gunner2(DynAccessor):
                __slots__ = ()
                destroyed = 337
                normal = 336

            class loader1(DynAccessor):
                __slots__ = ()
                destroyed = 339
                normal = 338

            class loader2(DynAccessor):
                __slots__ = ()
                destroyed = 341
                normal = 340

            class radioman1(DynAccessor):
                __slots__ = ()
                destroyed = 331
                normal = 330

            class radioman2(DynAccessor):
                __slots__ = ()
                destroyed = 333
                normal = 332

        class devices(DynAccessor):
            __slots__ = ()

            class ammoBay(DynAccessor):
                __slots__ = ()
                critical = 309
                destroyed = 310
                normal = 308

            class chassis(DynAccessor):
                __slots__ = ()
                critical = 315
                destroyed = 316
                normal = 314

            class engine(DynAccessor):
                __slots__ = ()
                critical = 303
                destroyed = 304
                normal = 302

            class fuelTank(DynAccessor):
                __slots__ = ()
                critical = 321
                destroyed = 322
                normal = 320

            class gun(DynAccessor):
                __slots__ = ()
                critical = 306
                destroyed = 307
                normal = 305

            class radio(DynAccessor):
                __slots__ = ()
                critical = 318
                destroyed = 319
                normal = 317

            class surveyingDevice(DynAccessor):
                __slots__ = ()
                critical = 324
                destroyed = 325
                normal = 323

            class track(DynAccessor):
                __slots__ = ()
                critical = 312
                destroyed = 313
                normal = 311

            class turretRotator(DynAccessor):
                __slots__ = ()
                critical = 300
                destroyed = 301
                normal = 299

    class damageIndicator(DynAccessor):
        __slots__ = ()
        multiplier = 666

    class damageLog(DynAccessor):
        __slots__ = ()
        multiplier = 629

        class shellType(DynAccessor):
            __slots__ = ()
            ARMOR_PIERCING = 624
            ARMOR_PIERCING_CR = 627
            ARMOR_PIERCING_HE = 626
            HIGH_EXPLOSIVE = 625
            HOLLOW_CHARGE = 628

    class devices(DynAccessor):
        __slots__ = ()
        ammo_bay = 109
        chassis = 117
        engine = 108
        fuel_tank = 110
        gun = 114
        left_track = 112
        radio = 111
        right_track = 113
        surveing_device = 116
        turret_rotator = 115

    class distance(DynAccessor):
        __slots__ = ()
        meters = 661

    class dynamicSquad(DynAccessor):
        __slots__ = ()

        class ally(DynAccessor):
            __slots__ = ()
            add = 651
            disabled = 653
            received = 658
            wasSent = 655

        class enemy(DynAccessor):
            __slots__ = ()
            add = 652
            disabled = 654
            received = 659
            wasSent = 656

        invite = 657

    class efficiencyRibbons(DynAccessor):
        __slots__ = ()
        armor = 606
        assistByAbility = 690
        assistSpot = 615
        assistTrack = 614
        burn = 610
        capture = 607
        crits = 616
        damage = 608
        defence = 611
        defenderBonus = 689
        destructibleDamaged = 686
        destructibleDestroyed = 687
        destructiblesDefended = 688
        enemySectorCaptured = 685
        kill = 612
        ram = 609
        receivedBurn = 620
        receivedCrits = 618
        receivedDamage = 619
        receivedRam = 621
        receivedWorldCollision = 622
        spotted = 613
        stun = 630
        vehicleRecovery = 623
        worldCollision = 617

    class epic_players_panel(DynAccessor):
        __slots__ = ()

        class state(DynAccessor):
            __slots__ = ()

            class hidden(DynAccessor):
                __slots__ = ()
                body = 374
                header = 373
                note = 375

            class medium_player(DynAccessor):
                __slots__ = ()
                body = 380
                header = 379
                note = 381

            class medium_tank(DynAccessor):
                __slots__ = ()
                body = 383
                header = 382
                note = 384

            class short(DynAccessor):
                __slots__ = ()
                body = 377
                header = 376
                note = 378

            class toggle(DynAccessor):
                __slots__ = ()
                body = 386
                header = 385
                note = 387

    class flagNotification(DynAccessor):
        __slots__ = ()
        flagAbsorbed = 647
        flagCaptured = 644
        flagDelivered = 646
        flagInbase = 645

    class flags(DynAccessor):
        __slots__ = ()
        timer = 604

    class fortConsumables(DynAccessor):
        __slots__ = ()

        class timer(DynAccessor):
            __slots__ = ()
            postfix = 603

    class hitMarker(DynAccessor):
        __slots__ = ()
        blocked = 631
        critical = 633
        ricochet = 632

    class marker(DynAccessor):
        __slots__ = ()
        meters = 211

    class personalMissions(DynAccessor):
        __slots__ = ()

        class tip(DynAccessor):
            __slots__ = ()
            additionalHeader = 600
            mainHeader = 599

            class noQuests(DynAccessor):
                __slots__ = ()
                battleType = 602
                vehicleType = 601

    class player_errors(DynAccessor):
        __slots__ = ()

        class cant_move(DynAccessor):
            __slots__ = ()
            chassis_damaged = 125
            crew_inactive = 123
            engine_damaged = 124

        class cant_shoot(DynAccessor):
            __slots__ = ()
            crew_inactive = 127
            gun_damaged = 129
            gun_locked = 131
            gun_reload = 130
            no_ammo = 128
            vehicle_destroyed = 126

        class cant_switch(DynAccessor):
            __slots__ = ()
            engine_destroyed = 132

        class equipment(DynAccessor):
            __slots__ = ()
            alreadyActivated = 133

            class extinguisher(DynAccessor):
                __slots__ = ()
                doesNotActivated = 139

            isInCooldown = 134

            class medkit(DynAccessor):
                __slots__ = ()
                allTankmenAreSafe = 136
                tankmanIsSafe = 135

            class order(DynAccessor):
                __slots__ = ()
                notReady = 140

            class repairkit(DynAccessor):
                __slots__ = ()
                allDevicesAreNotDamaged = 138
                deviceIsNotDamaged = 137

    class player_messages(DynAccessor):
        __slots__ = ()
        allied_team_name = 161
        ally_base_captured_by_notification = 157
        ally_base_captured_notification = 154
        ALLY_HIT = 153
        base_capture_blocked = 160
        base_captured_by_notification = 159
        base_captured_notification = 156
        COMBAT_EQUIPMENT_READY_ARTILLERY = 500
        COMBAT_EQUIPMENT_READY_BOMBER = 501
        COMBAT_EQUIPMENT_READY_INSPIRE = 504
        COMBAT_EQUIPMENT_READY_RECON = 502
        COMBAT_EQUIPMENT_READY_SMOKE = 503
        COMBAT_EQUIPMENT_USED_ARTILLERY = 505
        COMBAT_EQUIPMENT_USED_BOMBER = 506
        COMBAT_EQUIPMENT_USED_INSPIRE = 509
        COMBAT_EQUIPMENT_USED_RECON = 507
        COMBAT_EQUIPMENT_USED_SMOKE = 508
        DEATH_FROM_ARTILLERY_ALLY_ALLY = 462
        DEATH_FROM_ARTILLERY_ALLY_ENEMY = 463
        DEATH_FROM_ARTILLERY_ALLY_SUICIDE = 459
        DEATH_FROM_ARTILLERY_ENEMY_ALLY = 465
        DEATH_FROM_ARTILLERY_ENEMY_ENEMY = 464
        DEATH_FROM_ARTILLERY_ENEMY_SUICIDE = 458
        DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN_ALLY = 469
        DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN_ENEMY = 468
        DEATH_FROM_BOMBER_ALLY_SUICIDE = 461
        DEATH_FROM_BOMBER_ENEMY_SUICIDE = 460
        DEATH_FROM_DEATH_ZONE_ALLY_ALLY = 557
        DEATH_FROM_DEATH_ZONE_ALLY_ENEMY = 558
        DEATH_FROM_DEATH_ZONE_ALLY_SELF = 556
        DEATH_FROM_DEATH_ZONE_ALLY_SUICIDE = 555
        DEATH_FROM_DEATH_ZONE_ENEMY_ALLY = 561
        DEATH_FROM_DEATH_ZONE_ENEMY_ENEMY = 562
        DEATH_FROM_DEATH_ZONE_ENEMY_SELF = 560
        DEATH_FROM_DEATH_ZONE_ENEMY_SUICIDE = 559
        DEATH_FROM_DEATH_ZONE_SELF_ALLY = 553
        DEATH_FROM_DEATH_ZONE_SELF_ENEMY = 554
        DEATH_FROM_DEATH_ZONE_SELF_SUICIDE = 552
        DEATH_FROM_DEVICE_EXPLOSION_AT_FIRE = 481
        DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT = 479
        DEATH_FROM_DROWNING_ALLY_ALLY = 494
        DEATH_FROM_DROWNING_ALLY_ENEMY = 495
        DEATH_FROM_DROWNING_ALLY_SELF = 493
        DEATH_FROM_DROWNING_ALLY_SUICIDE = 492
        DEATH_FROM_DROWNING_ENEMY_ALLY = 498
        DEATH_FROM_DROWNING_ENEMY_ENEMY = 499
        DEATH_FROM_DROWNING_ENEMY_SELF = 497
        DEATH_FROM_DROWNING_ENEMY_SUICIDE = 496
        DEATH_FROM_DROWNING_SELF_ALLY = 490
        DEATH_FROM_DROWNING_SELF_ENEMY = 491
        DEATH_FROM_DROWNING_SELF_SUICIDE = 489
        DEATH_FROM_GAS_ATTACK_ALLY_ALLY = 566
        DEATH_FROM_GAS_ATTACK_ALLY_ENEMY = 567
        DEATH_FROM_GAS_ATTACK_ALLY_SELF = 565
        DEATH_FROM_GAS_ATTACK_ENEMY_ALLY = 569
        DEATH_FROM_GAS_ATTACK_ENEMY_ENEMY = 570
        DEATH_FROM_GAS_ATTACK_ENEMY_SELF = 568
        DEATH_FROM_GAS_ATTACK_SELF_ALLY = 563
        DEATH_FROM_GAS_ATTACK_SELF_ENEMY = 564
        DEATH_FROM_INACTIVE_CREW = 478
        DEATH_FROM_INACTIVE_CREW_AT_SHOT = 476
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_ALLY = 538
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_ENEMY = 539
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF = 537
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SUICIDE = 536
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_ALLY = 542
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_ENEMY = 543
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF = 541
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SUICIDE = 540
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_ALLY = 534
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_ENEMY = 535
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE = 533
        DEATH_FROM_OVERTURN_ALLY_ALLY = 589
        DEATH_FROM_OVERTURN_ALLY_ENEMY = 590
        DEATH_FROM_OVERTURN_ALLY_SELF = 588
        DEATH_FROM_OVERTURN_ALLY_SUICIDE = 587
        DEATH_FROM_OVERTURN_ENEMY_ALLY = 593
        DEATH_FROM_OVERTURN_ENEMY_ENEMY = 594
        DEATH_FROM_OVERTURN_ENEMY_SELF = 592
        DEATH_FROM_OVERTURN_ENEMY_SUICIDE = 591
        DEATH_FROM_OVERTURN_SELF_ALLY = 585
        DEATH_FROM_OVERTURN_SELF_ENEMY = 586
        DEATH_FROM_OVERTURN_SELF_SUICIDE = 584
        DEATH_FROM_RAMMING_ALLY_ALLY = 582
        DEATH_FROM_RAMMING_ALLY_ENEMY = 583
        DEATH_FROM_RAMMING_ALLY_SELF = 581
        DEATH_FROM_RAMMING_ALLY_SUICIDE = 580
        DEATH_FROM_RAMMING_ENEMY_ALLY = 597
        DEATH_FROM_RAMMING_ENEMY_ENEMY = 598
        DEATH_FROM_RAMMING_ENEMY_SELF = 596
        DEATH_FROM_RAMMING_ENEMY_SUICIDE = 595
        DEATH_FROM_RAMMING_SELF_ALLY = 578
        DEATH_FROM_RAMMING_SELF_ENEMY = 579
        DEATH_FROM_RAMMING_SELF_SUICIDE = 577
        DEATH_FROM_RECOVERY_ALLY_SUICIDE = 467
        DEATH_FROM_RECOVERY_ENEMY_SUICIDE = 466
        DEATH_FROM_SECTOR_BOMBERS_UNKNOWN_ALLY = 473
        DEATH_FROM_SECTOR_BOMBERS_UNKNOWN_ENEMY = 472
        DEATH_FROM_SECTOR_PROTECTION_UNKNOWN_ALLY = 471
        DEATH_FROM_SECTOR_PROTECTION_UNKNOWN_ENEMY = 470
        DEATH_FROM_SHOT_ALLY_ALLY = 440
        DEATH_FROM_SHOT_ALLY_ALLY_ARTILLERY = 441
        DEATH_FROM_SHOT_ALLY_ALLY_BOMBER = 442
        DEATH_FROM_SHOT_ALLY_ENEMY = 443
        DEATH_FROM_SHOT_ALLY_ENEMY_ARTILLERY = 444
        DEATH_FROM_SHOT_ALLY_ENEMY_BOMBER = 445
        DEATH_FROM_SHOT_ALLY_SUICIDE = 446
        DEATH_FROM_SHOT_ALLY_SUICIDE_ARTILLERY = 447
        DEATH_FROM_SHOT_ALLY_SUICIDE_BOMBER = 448
        DEATH_FROM_SHOT_ENEMY_ALLY = 452
        DEATH_FROM_SHOT_ENEMY_ALLY_ARTILLERY = 453
        DEATH_FROM_SHOT_ENEMY_ALLY_BOMBER = 454
        DEATH_FROM_SHOT_ENEMY_ENEMY = 455
        DEATH_FROM_SHOT_ENEMY_ENEMY_ARTILLERY = 456
        DEATH_FROM_SHOT_ENEMY_ENEMY_BOMBER = 457
        DEATH_FROM_SHOT_ENEMY_SUICIDE = 449
        DEATH_FROM_SHOT_ENEMY_SUICIDE_ARTILLERY = 450
        DEATH_FROM_SHOT_ENEMY_SUICIDE_BOMBER = 451
        DEATH_FROM_SHOT_SELF_ALLY = 434
        DEATH_FROM_SHOT_SELF_ALLY_ARTILLERY = 435
        DEATH_FROM_SHOT_SELF_ALLY_BOMBER = 436
        DEATH_FROM_SHOT_SELF_ENEMY = 437
        DEATH_FROM_SHOT_SELF_ENEMY_ARTILLERY = 438
        DEATH_FROM_SHOT_SELF_ENEMY_BOMBER = 439
        DEATH_FROM_WORLD_COLLISION_ALLY_ALLY = 521
        DEATH_FROM_WORLD_COLLISION_ALLY_ENEMY = 522
        DEATH_FROM_WORLD_COLLISION_ALLY_SELF = 520
        DEATH_FROM_WORLD_COLLISION_ALLY_SUICIDE = 519
        DEATH_FROM_WORLD_COLLISION_ENEMY_ALLY = 525
        DEATH_FROM_WORLD_COLLISION_ENEMY_ENEMY = 526
        DEATH_FROM_WORLD_COLLISION_ENEMY_SELF = 524
        DEATH_FROM_WORLD_COLLISION_ENEMY_SUICIDE = 523
        DEATH_FROM_WORLD_COLLISION_SELF_ALLY = 517
        DEATH_FROM_WORLD_COLLISION_SELF_ENEMY = 518
        DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE = 516
        DESTRUCTIBLE_DESTROYED_ALLY = 677
        DESTRUCTIBLE_DESTROYED_ENEMY = 678
        DESTRUCTIBLE_DESTROYED_SELF = 676
        DEVICE_CRITICAL_AT_FIRE = 145
        DEVICE_CRITICAL_AT_SHOT = 141
        DEVICE_DESTROYED_AT_FIRE = 148
        DEVICE_DESTROYED_AT_SHOT = 142
        DEVICE_REPAIRED = 152
        DEVICE_REPAIRED_TO_CRITICAL = 149
        DEVICE_STARTED_FIRE_AT_SHOT = 143
        enemy_base_captured_by_notification = 158
        enemy_base_captured_notification = 155
        enemy_team_name = 162
        ENGINE_CRITICAL_AT_UNLIMITED_RPM = 146
        ENGINE_DESTROYED_AT_UNLIMITED_RPM = 147
        FIRE_STOPPED = 150
        loader_intuition_was_used = 175

        class postmortem_caption(DynAccessor):
            __slots__ = ()
            other = 165
            self = 164

        postmortem_caption_ = 163
        postmortem_userNoHasAmmo = 166
        replayControlsHelp1 = 172
        replayControlsHelp2 = 173
        replayControlsHelp3 = 174
        replayFreeCameraActivated = 168
        replayPaused = 171
        replaySavedCameraActivated = 169
        replaySpeedChange = 170
        tank_in_fire = 167
        TANKMAN_HIT_AT_SHOT = 144
        TANKMAN_RESTORED = 151

    class players_panel(DynAccessor):
        __slots__ = ()

        class state(DynAccessor):
            __slots__ = ()

            class large(DynAccessor):
                __slots__ = ()
                body = 366
                header = 365
                note = 367

            class medium(DynAccessor):
                __slots__ = ()
                body = 360
                header = 359
                note = 361

            class medium2(DynAccessor):
                __slots__ = ()
                body = 363
                header = 362
                note = 364

            class none(DynAccessor):
                __slots__ = ()
                body = 354
                header = 353
                note = 355

            class short(DynAccessor):
                __slots__ = ()
                body = 357
                header = 356
                note = 358

        unknown_clan = 372
        unknown_frags = 370
        unknown_name = 368
        unknown_vehicle = 369
        unknown_vehicleState = 371

    class postmortem(DynAccessor):
        __slots__ = ()

        class tips(DynAccessor):
            __slots__ = ()

            class exitHangar(DynAccessor):
                __slots__ = ()
                label = 351
                text = 352

            class observerMode(DynAccessor):
                __slots__ = ()
                label = 349
                text = 350

    class postmortem_messages(DynAccessor):
        __slots__ = ()
        DEATH_FROM_DEATH_ZONE_ALLY_SELF = 549
        DEATH_FROM_DEATH_ZONE_ENEMY_SELF = 547
        DEATH_FROM_DEATH_ZONE_SELF_SUICIDE = 545
        DEATH_FROM_DEVICE_EXPLOSION_AT_FIRE = 482
        DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT = 480
        DEATH_FROM_DROWNING_ALLY_SELF = 488
        DEATH_FROM_DROWNING_ENEMY_SELF = 486
        DEATH_FROM_DROWNING_SELF_SUICIDE = 484
        DEATH_FROM_FIRE = 475
        DEATH_FROM_INACTIVE_CREW_AT_SHOT = 477
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF = 532
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF = 530
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE = 528
        DEATH_FROM_OVERTURN_ALLY_SELF = 433
        DEATH_FROM_OVERTURN_ENEMY_SELF = 432
        DEATH_FROM_OVERTURN_SELF_SUICIDE = 431
        DEATH_FROM_RAMMING_ALLY_SELF = 576
        DEATH_FROM_RAMMING_ENEMY_SELF = 574
        DEATH_FROM_RAMMING_SELF_SUICIDE = 572
        DEATH_FROM_SHOT = 425
        DEATH_FROM_SHOT_ARTILLERY = 429
        DEATH_FROM_SHOT_BOMBER = 430
        DEATH_FROM_WORLD_COLLISION_ALLY_SELF = 515
        DEATH_FROM_WORLD_COLLISION_ENEMY_SELF = 513
        DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE = 511
        DEATH_UNKNOWN = 426

    class recovery(DynAccessor):
        __slots__ = ()
        cooldown = 693
        hint1 = 691
        hint2 = 692

    class repairPoint(DynAccessor):
        __slots__ = ()
        title = 663
        unavailable = 664

    class respawnView(DynAccessor):
        __slots__ = ()
        additionalTip = 635
        additionalTipLimited = 636
        classNotAvailable = 643
        cooldownLbl = 637
        destroyedLbl = 638
        disabledLbl = 639
        emptySlotInfo = 641
        emptySlotInfoTooltip = 642
        nextVehicleName = 640
        title = 634

    class rewardWindow(DynAccessor):
        __slots__ = ()

        class base(DynAccessor):
            __slots__ = ()
            btnLabel = 709
            descText = 708
            headerText = 707
            subHeaderText = 706

        winHeaderText = 705

    class scorePanel(DynAccessor):
        __slots__ = ()
        mySquadLbl = 649
        playerScore = 650
        squadLbl = 648

    class shells_kinds(DynAccessor):
        __slots__ = ()
        ARMOR_PIERCING = 294
        ARMOR_PIERCING_CR = 296
        ARMOR_PIERCING_HE = 295
        HIGH_EXPLOSIVE = 293
        HOLLOW_CHARGE = 292
        params = 297
        stunParams = 298

    class siegeMode(DynAccessor):
        __slots__ = ()

        class hint(DynAccessor):
            __slots__ = ()

            class forMode(DynAccessor):
                __slots__ = ()
                c_0 = 680
                c_1 = 681
                c_2 = 682
                c_3 = 683

            noBinding = 684
            press = 679

    class statistics(DynAccessor):
        __slots__ = ()
        exit = 261

        class final(DynAccessor):
            __slots__ = ()
            heroes = 284

            class lifeInfo(DynAccessor):
                __slots__ = ()
                alive = 285
                dead = 286

            class personal(DynAccessor):
                __slots__ = ()
                capturePoints = 282
                damaged = 277
                directHits = 280
                directHitsReceived = 281
                droppedCapturePoints = 283
                killed = 276
                postmortem = 275
                shots = 279
                spotted = 278

            class reasons(DynAccessor):
                __slots__ = ()
                reason0 = 265
                reason1lose = 267
                reason1tie = 268
                reason1win = 266
                reason2 = 269
                reason3 = 270

            class stats(DynAccessor):
                __slots__ = ()
                credits = 273
                experience = 272
                multipliedExp = 271
                repair = 274

            class status(DynAccessor):
                __slots__ = ()
                lose = 264
                tie = 262
                win = 263

        header = 249

        class headers(DynAccessor):
            __slots__ = ()
            header0 = 253
            header1 = 254
            header2 = 255
            header3 = 256
            header4 = 257

        class playerState(DynAccessor):
            __slots__ = ()
            c_0 = 287
            c_1 = 289
            c_2 = 288
            c_3 = 290
            c_4 = 291

        class tab(DynAccessor):
            __slots__ = ()

            class line_up(DynAccessor):
                __slots__ = ()
                header = 238
                title = 239

            class progressTracing(DynAccessor):
                __slots__ = ()
                notAvailable = 250

            class quests(DynAccessor):
                __slots__ = ()
                header = 240

                class notAvailable(DynAccessor):
                    __slots__ = ()
                    title = 248

                class nothingToPerform(DynAccessor):
                    __slots__ = ()
                    descr = 246
                    title = 245

                class status(DynAccessor):
                    __slots__ = ()
                    done = 243
                    fullDone = 244
                    increaseResult = 242
                    inProgress = 241

                class switchOff(DynAccessor):
                    __slots__ = ()
                    title = 247

        class tabs(DynAccessor):
            __slots__ = ()
            group = 258
            heroes = 260
            personal = 259

        team1title = 251
        team2title = 252

    class stun(DynAccessor):
        __slots__ = ()
        indicator = 700
        seconds = 701

    tabStatsHint = 662

    class tankmen(DynAccessor):
        __slots__ = ()
        commander = 118
        driver = 119
        gunner = 121
        loader = 122
        radioman = 120

    class timer(DynAccessor):
        __slots__ = ()
        battlePeriod = 348
        started = 347
        starting = 346
        waiting = 345

    class trajectoryView(DynAccessor):
        __slots__ = ()

        class hint(DynAccessor):
            __slots__ = ()
            alternateModeLeft = 698
            alternateModeRight = 699
            noBindingKey = 697

    class vehicle_messages(DynAccessor):
        __slots__ = ()
        DEATH_FROM_DEATH_ZONE_ALLY_SELF = 548
        DEATH_FROM_DEATH_ZONE_ENEMY_SELF = 546
        DEATH_FROM_DEATH_ZONE_SELF_SUICIDE = 544
        DEATH_FROM_DROWNING_ALLY_SELF = 487
        DEATH_FROM_DROWNING_ENEMY_SELF = 485
        DEATH_FROM_DROWNING_SELF_SUICIDE = 483
        DEATH_FROM_FIRE = 474
        DEATH_FROM_GAS_ATTACK_ALLY_SELF = 551
        DEATH_FROM_GAS_ATTACK_ENEMY_SELF = 550
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF = 531
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF = 529
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE = 527
        DEATH_FROM_OVERTURN_ALLY_SELF = 669
        DEATH_FROM_OVERTURN_ENEMY_SELF = 668
        DEATH_FROM_OVERTURN_SELF_SUICIDE = 667
        DEATH_FROM_RAMMING_ALLY_SELF = 575
        DEATH_FROM_RAMMING_ENEMY_SELF = 573
        DEATH_FROM_RAMMING_SELF_SUICIDE = 571
        DEATH_FROM_SHOT = 424
        DEATH_FROM_SHOT_ARTILLERY = 427
        DEATH_FROM_SHOT_BOMBER = 428
        DEATH_FROM_WORLD_COLLISION_ALLY_SELF = 514
        DEATH_FROM_WORLD_COLLISION_ENEMY_SELF = 512
        DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE = 510
        DEVICE_CRITICAL_AT_RAMMING_ALLY_ALLY = 405
        DEVICE_CRITICAL_AT_RAMMING_ALLY_SELF = 402
        DEVICE_CRITICAL_AT_RAMMING_ALLY_SUICIDE = 403
        DEVICE_CRITICAL_AT_RAMMING_ENEMY_ALLY = 404
        DEVICE_CRITICAL_AT_RAMMING_ENEMY_SELF = 401
        DEVICE_CRITICAL_AT_RAMMING_SELF_SUICIDE = 400
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_ALLY = 393
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_SELF = 390
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_SUICIDE = 391
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ENEMY_ALLY = 392
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ENEMY_SELF = 389
        DEVICE_CRITICAL_AT_WORLD_COLLISION_SELF_SUICIDE = 388
        DEVICE_DESTROYED_AT_RAMMING_ALLY_ALLY = 411
        DEVICE_DESTROYED_AT_RAMMING_ALLY_SELF = 408
        DEVICE_DESTROYED_AT_RAMMING_ALLY_SUICIDE = 409
        DEVICE_DESTROYED_AT_RAMMING_ENEMY_ALLY = 410
        DEVICE_DESTROYED_AT_RAMMING_ENEMY_SELF = 407
        DEVICE_DESTROYED_AT_RAMMING_SELF_SUICIDE = 406
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_ALLY = 399
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_SELF = 396
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_SUICIDE = 397
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ENEMY_ALLY = 398
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ENEMY_SELF = 395
        DEVICE_DESTROYED_AT_WORLD_COLLISION_SELF_SUICIDE = 394
        DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_ALLY = 417
        DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_SELF = 414
        DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_SUICIDE = 415
        DEVICE_STARTED_FIRE_AT_RAMMING_ENEMY_ALLY = 416
        DEVICE_STARTED_FIRE_AT_RAMMING_ENEMY_SELF = 413
        DEVICE_STARTED_FIRE_AT_RAMMING_SELF_SUICIDE = 412
        TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_ALLY = 423
        TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_SELF = 420
        TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_SUICIDE = 421
        TANKMAN_HIT_AT_WORLD_COLLISION_ENEMY_ALLY = 422
        TANKMAN_HIT_AT_WORLD_COLLISION_ENEMY_SELF = 419
        TANKMAN_HIT_AT_WORLD_COLLISION_SELF_SUICIDE = 418
