#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ****        **** STAR TREK ****        ****
# **** SIMULATION OF A MISSION OF THE STARSHIP ENTERPRISE,
# **** AS SEEN ON THE STAR TREK TV SHOW.
# **** ORIGINAL PROGRAM BY MIKE MAYFIELD, MODIFIED VERSION
# **** PUBLISHED IN DEC'S "101 BASIC GAMES", BY DAVE AHL.
# **** MODIFICATIONS TO THE LATTER (PLUS DEBUGGING) BY BOB
# **** LEEDOM - APRIL & DECEMBER 1974,
# **** WITH A LITTLE HELP FROM HIS FRIENDS . . .
#
# Python translation by Jack Boyce - February 2021
#   Output is identical to BASIC version except for a few
#   fixes (as noted, search `bug`) and minor cleanup.
#
# Modified by Allyn Gibson - Summer 2026
#   Features added:
#   * Instructions (which were separate in the Leedom/Ahl
#     version)
#   * Marcus Aurelius quotes when certain triggers are
#     reached. This was an odd feature in a version of
#     Star Trek in code descended from the UTexas version
#     of the game. Can be disabled by uncommenting a line
#     in the marcus_aurelius() procedure. This does not
#     add *every* UTexas feature -- no Romulans, no
#     Tholians, no Faerie Queen, no Death Ray. It's still
#     the Leedom/Ahl game from Creative Computer, now
#     with bonus Stoicism.
#   * A "super" sector with 4 Klingons. If the initial
#     galaxy generation creates fewer than 15 Klingons,
#     the program will find an empty sector and add four
#     Klingons to bring the number up and add to the
#     challenge. A "boss fight," if you will.

import random
from math import sqrt


# -------------------------------------------------------------------------
#  Utility functions
# -------------------------------------------------------------------------


def fnr():
    # Generate a random integer from 0 to 7 inclusive.
    return random.randint(0, 7)


def quadrant_name(row, col, region_only=False):
    # Return quadrant name visible on scans, etc.
    region1 = ['ANTARES', 'RIGEL', 'PROCYON', 'VEGA', 'CANOPUS', 'ALTAIR',
               'SAGITTARIUS', 'POLLUX']
    region2 = ['SIRIUS', 'DENEB', 'CAPELLA', 'BETELGEUSE', 'ALDEBARAN',
               'REGULUS', 'ARCTURUS', 'SPICA']
    modifier = ['I', 'II', 'III', 'IV']

    quadrant = region1[row] if col < 4 else region2[row]

    if not region_only:
        quadrant += ' ' + modifier[col % 4]

    return quadrant


def insert_marker(row, col, marker):
    # Insert a marker into a given position in the quadrant string `qs`. The
    # contents of a quadrant (Enterprise, stars, etc.) are stored in `qs`.
    global qs

    if len(marker) != 3:
        print('ERROR')
        exit()

    pos = round(col) * 3 + round(row) * 24
    qs = qs[0:pos] + marker + qs[(pos + 3):192]


def compare_marker(row, col, test_marker):
    # Check whether the position in the current quadrant is occupied with a
    # given marker.
    pos = round(col) * 3 + round(row) * 24
    return qs[pos:(pos + 3)] == test_marker


def find_empty_place():
    # Find an empty location in the current quadrant.
    while True:
        row, col = fnr(), fnr()
        if compare_marker(row, col, '   '):
            return row, col


# -------------------------------------------------------------------------
#  Functions for individual player commands
# -------------------------------------------------------------------------


def navigation():
    # Take navigation input and move the Enterprise.
    global d, s, e, k, qs, t, q1, q2, s1, s2

    while True:
        c1s = input("COURSE (1-9)? ")
        if len(c1s) > 0:
            c1 = float(c1s)
            break
    if c1 == 9:
        c1 = 1
    if c1 < 1 or c1 >= 9:
        print("   LT. SULU REPORTS, 'INCORRECT COURSE DATA, SIR!'")
        return

    while True:
        warps = input(f"WARP FACTOR (0-{'0.2' if d[0] < 0 else '8'})? ")
        if len(warps) > 0:
            warp = float(warps)
            break
    if d[0] < 0 and warp > 0.2:
        print("WARP ENGINES ARE DAMAGED. MAXIMUM SPEED = WARP 0.2")
        return
    if warp == 0:
        return
    if warp < 0 or warp > 8:
        print("   CHIEF ENGINEER SCOTT REPORTS 'THE ENGINES WON'T TAKE "
              f"WARP {warp}!'")
        return

    n = round(warp * 8)
    if e < n:
        print("ENGINEERING REPORTS   'INSUFFICIENT ENERGY AVAILABLE")
        print(f"                       FOR MANEUVERING AT WARP {warp}!'")
        if s >= n - e and d[6] >= 0:
            print(f"DEFLECTOR CONTROL ROOM ACKNOWLEDGES {s} UNITS OF ENERGY")
            print("                         PRESENTLY DEPLOYED TO SHIELDS.")
        return

    # klingons move and fire
    for i in range(4):
        if k[i][2] != 0:
            insert_marker(k[i][0], k[i][1], '   ')
            k[i][0], k[i][1] = find_empty_place()
            insert_marker(k[i][0], k[i][1], '+K+')

    klingons_fire()

    # repair damaged devices and print damage report
    line = ''
    for i in range(8):
        if d[i] < 0:
            d[i] += min(warp, 1)
            if -0.1 < d[i] < 0:
                d[i] = -0.1
            elif d[i] >= 0:
                if len(line) == 0:
                    line = "DAMAGE CONTROL REPORT:"
                line += '   ' + devices[i] + ' REPAIR COMPLETED\n'
    if len(line) > 0:
        print(line)
    if random.random() <= 0.2:
        r1 = fnr()
        if random.random() < 0.6:
            d[r1] -= random.random() * 5 + 1
            print(f"DAMAGE CONTROL REPORT:   {devices[r1]} DAMAGED\n")
        else:
            d[r1] += random.random() * 3 + 1
            print(f"DAMAGE CONTROL REPORT:   {devices[r1]} STATE OF "
                  "REPAIR IMPROVED\n")

    # begin moving starship
    insert_marker(int(s1), int(s2), '   ')
    ic1 = int(c1)
    x1 = c[ic1 - 1][0] + (c[ic1][0] - c[ic1 - 1][0]) * (c1 - ic1)
    x2 = c[ic1 - 1][1] + (c[ic1][1] - c[ic1 - 1][1]) * (c1 - ic1)
    q1_start, q2_start = q1, q2
    x, y = s1, s2

    for _ in range(n):
        s1 += x1
        s2 += x2

        if s1 < 0 or s1 > 7 or s2 < 0 or s2 > 7:
            # exceeded quadrant limits; calculate final position
            x += 8 * q1 + n * x1
            y += 8 * q2 + n * x2
            q1, q2 = int(x / 8), int(y / 8)
            s1, s2 = int(x - q1 * 8), int(y - q2 * 8)
            if s1 < 0:
                q1 -= 1
                s1 = 7
            if s2 < 0:
                q2 -= 1
                s2 = 7

            hit_edge = False
            if q1 < 0:
                hit_edge = True
                q1 = s1 = 0
            if q1 > 7:
                hit_edge = True
                q1 = s1 = 7
            if q2 < 0:
                hit_edge = True
                q2 = s2 = 0
            if q2 > 7:
                hit_edge = True
                q2 = s2 = 7
            if hit_edge:
                print("LT. UHURA REPORTS MESSAGE FROM STARFLEET COMMAND:")
                print("  'PERMISSION TO ATTEMPT CROSSING OF GALACTIC "
                      "PERIMETER")
                print("  IS HEREBY *DENIED*. SHUT DOWN YOUR ENGINES.'")
                print("CHIEF ENGINEER SCOTT REPORTS  'WARP ENGINES SHUT DOWN")
                print(f"  AT SECTOR {s1 + 1} , {s2 + 1} OF QUADRANT "
                      f"{q1 + 1} , {q2 + 1}.'")
                if t > t0 + t9:
                    end_game(won=False, quit=False)
                    return

            if q1 == q1_start and q2 == q2_start:
                break
            t += 1
            maneuver_energy(n)
            new_quadrant()
            return
        else:
            pos = int(s1) * 24 + int(s2) * 3
            if qs[pos:(pos + 2)] != '  ':
                s1, s2 = int(s1 - x1), int(s2 - x2)
                print("WARP ENGINES SHUT DOWN AT SECTOR "
                      f"{s1 + 1} , {s2 + 1} DUE TO BAD NAVAGATION")
                break
    else:
        s1, s2 = int(s1), int(s2)

    insert_marker(int(s1), int(s2), '<*>')
    maneuver_energy(n)

    t += 0.1 * int(10 * warp) if warp < 1 else 1
    if t > t0 + t9:
        end_game(won=False, quit=False)
        return

    short_range_scan()


def maneuver_energy(n):
    # Deduct the energy for navigation from energy/shields.
    global e, s

    e -= n + 10

    if e <= 0:
        print("SHIELD CONTROL SUPPLIES ENERGY TO COMPLETE THE MANEUVER.")
        s += e
        e = 0
        s = max(0, s)


def short_range_scan():
    # Print a short range scan.
    global docked, e, p, s, m1, m2, command

    if command == 'SRS':
        m2 = m2 + 1
    if m2 > 3:
        m1 = 8
        marcus_aurelius()

    docked = False
    for i in (s1 - 1, s1, s1 + 1):
        for j in (s2 - 1, s2, s2 + 1):
            if 0 <= i <= 7 and 0 <= j <= 7:
                if compare_marker(i, j, '>!<'):
                    docked = True
                    cs = 'DOCKED'
                    e, p = e0, p0
                    print("SHIELDS DROPPED FOR DOCKING PURPOSES")
                    s = 0
                    break
        else:
            continue
        break
    else:
        if k3 > 0:
            cs = '*RED*'
        elif e < e0 * 0.1:
            cs = 'YELLOW'
        else:
            cs = 'GREEN'

    if d[1] < 0:
        print("\n*** SHORT RANGE SENSORS ARE OUT ***\n")
        return

    sep = '---------------------------------'
    print(sep)
    for i in range(8):
        line = ''
        for j in range(8):
            pos = i * 24 + j * 3
            line = line + ' ' + qs[pos:(pos + 3)]

        if i == 0:
            line += f'        STARDATE           {round(int(t * 10) * 0.1, 1)}'
        elif i == 1:
            line += f'        CONDITION          {cs}'
        elif i == 2:
            line += f'        QUADRANT           {q1 + 1} , {q2 + 1}'
        elif i == 3:
            line += f'        SECTOR             {s1 + 1} , {s2 + 1}'
        elif i == 4:
            line += f'        PHOTON TORPEDOES   {int(p)}'
        elif i == 5:
            line += f'        TOTAL ENERGY       {int(e + s)}'
        elif i == 6:
            line += f'        SHIELDS            {int(s)}'
        else:
            line += f'        KLINGONS REMAINING {k9}'

        print(line)
    print(sep)


def long_range_scan():
    # Print a long range scan.
    global z

    if d[2] < 0:
        print("LONG RANGE SENSORS ARE INOPERABLE")
        return

    print(f"LONG RANGE SCAN FOR QUADRANT {q1 + 1} , {q2 + 1}")
    sep = '-------------------'
    print(sep)
    for i in (q1 - 1, q1, q1 + 1):
        n = [-1, -2, -3]

        for j in (q2 - 1, q2, q2 + 1):
            if 0 <= i <= 7 and 0 <= j <= 7:
                n[j - q2 + 1] = g[i][j]
                z[i][j] = g[i][j]

        line = ': '
        for l in range(3):
            if n[l] < 0:
                line += '*** : '
            else:
                line += str(n[l] + 1000).rjust(4, ' ')[-3:] + ' : '
        print(line)
        print(sep)


def phaser_control():
    # Take phaser control input and fire phasers.
    global e, k, g, z, k3, k9

    if d[3] < 0:
        print("PHASERS INOPERATIVE")
        return

    if k3 <= 0:
        print("SCIENCE OFFICER SPOCK REPORTS  'SENSORS SHOW NO ENEMY SHIPS")
        print("                                IN THIS QUADRANT'")
        return

    if d[7] < 0:
        print("COMPUTER FAILURE HAMPERS ACCURACY")

    print(f"PHASERS LOCKED ON TARGET;  ENERGY AVAILABLE = {e} UNITS")
    x = 0
    while True:
        while True:
            xs = input("NUMBER OF UNITS TO FIRE? ")
            if len(xs) > 0:
                try:
                    x = int(xs)
                except:
                    continue
                break
        if x <= 0:
            return
        if e >= x:
            break
        print(f"ENERGY AVAILABLE = {e} UNITS")

    e -= x
    if d[7] < 0:  # bug in original, was d[6]
        x *= random.random()

    h1 = int(x / k3)
    for i in range(4):
        if k[i][2] <= 0:
            continue

        h = int((h1 / fnd(i)) * (random.random() + 2))
        if h <= 0.15 * k[i][2]:
            print("SENSORS SHOW NO DAMAGE TO ENEMY AT "
                  f"{k[i][0] + 1} , {k[i][1] + 1}")
        else:
            k[i][2] -= h
            print(f" {h} UNIT HIT ON KLINGON AT SECTOR "
                  f"{k[i][0] + 1} , {k[i][1] + 1}")
            if k[i][2] <= 0:
                print("*** KLINGON DESTROYED ***")
                k3 -= 1
                k9 -= 1
                insert_marker(k[i][0], k[i][1], '   ')
                k[i][2] = 0
                g[q1][q2] -= 100
                z[q1][q2] = g[q1][q2]
                if k9 <= 0:
                    end_game(won=True, quit=False)
                    return
            else:
                print(f"   (SENSORS SHOW {round(k[i][2],6)} UNITS REMAINING)")

    klingons_fire()


def photon_torpedoes():
    # Take photon torpedo input and process firing of torpedoes.
    global e, p, k3, k9, k, b3, b9, docked, g, z

    if p <= 0:
        print("ALL PHOTON TORPEDOES EXPENDED")
        return
    if d[4] < 0:
        print("PHOTON TUBES ARE NOT OPERATIONAL")
        return

    while True:
        c1s = input("PHOTON TORPEDO COURSE (1-9)? ")
        if len(c1s) > 0:
            c1 = float(c1s)
            break
    if c1 == 9:
        c1 = 1
    if c1 < 1 or c1 >= 9:
        print("ENSIGN CHEKOV REPORTS, 'INCORRECT COURSE DATA, SIR!'")
        return

    ic1 = int(c1)
    x1 = c[ic1 - 1][0] + (c[ic1][0] - c[ic1 - 1][0]) * (c1 - ic1)
    e -= 2
    p -= 1
    x2 = c[ic1 - 1][1] + (c[ic1][1] - c[ic1 - 1][1]) * (c1 - ic1)
    x, y = s1, s2
    x3, y3 = x, y
    print("TORPEDO TRACK:")
    while True:
        x += x1
        y += x2
        x3, y3 = round(x), round(y)
        if x3 < 0 or x3 > 7 or y3 < 0 or y3 > 7:
            print("TORPEDO MISSED")
            klingons_fire()
            return
        print(f"                {x3 + 1} , {y3 + 1}")
        if not compare_marker(x3, y3, '   '):
            break

    if compare_marker(x3, y3, '+K+'):
        print("*** KLINGON DESTROYED ***")
        k3 -= 1
        k9 -= 1
        if k9 <= 0:
            end_game(won=True, quit=False)
            return
        for i in range(4):
            if x3 == k[i][0] and y3 == k[i][1]:
                k[i][2] = 0
    elif compare_marker(x3, y3, ' * '):
        print(f"STAR AT {x3 + 1} , {y3 + 1} ABSORBED TORPEDO ENERGY.")
        klingons_fire()
        return
    elif compare_marker(x3, y3, '>!<'):
        print("*** STARBASE DESTROYED ***")
        b3 -= 1
        b9 -= 1
        if b9 == 0 and k9 <= t - t0 - t9:
            print("THAT DOES IT, CAPTAIN!! YOU ARE HEREBY RELIEVED OF COMMAND")
            print("AND SENTENCED TO 99 STARDATES AT HARD LABOR ON CYGNUS 12!!")
            end_game(won=False)
            return
        else:
            print("STARFLEET COMMAND REVIEWING YOUR RECORD TO CONSIDER")
            print("COURT MARTIAL!")
            docked = False

    insert_marker(x3, y3, '   ')
    g[q1][q2] = k3 * 100 + b3 * 10 + s3
    z[q1][q2] = g[q1][q2]
    klingons_fire()


def fnd(i):
    # Find distance between Enterprise and i'th Klingon warship.
    return sqrt((k[i][0] - s1)**2 + (k[i][1] - s2)**2)


def klingons_fire():
    # Process nearby Klingons firing on Enterprise.
    global s, k, d

    if k3 <= 0:
        return
    if docked:
        print("STARBASE SHIELDS PROTECT THE ENTERPRISE")
        return

    for i in range(4):
        if k[i][2] <= 0:
            continue

        h = int((k[i][2] / fnd(i)) * (random.random() + 2))
        s -= h
        k[i][2] /= (random.random() + 3)
        print(f" {h} UNIT HIT ON ENTERPRISE FROM SECTOR "
              f"{k[i][0] + 1} , {k[i][1] + 1}")
        if s <= 0:
            end_game(won=False, quit=False, enterprise_killed=True)
            return
        print(f"      <SHIELDS DOWN TO {s} UNITS>")
        if h >= 20 and random.random() < 0.60 and h / s > 0.02:
            r1 = fnr()
            d[r1] -= h / s + 0.5 * random.random()
            print(f"DAMAGE CONTROL REPORTS  '{devices[r1]} DAMAGED "
                  "BY THE HIT'")


def shield_control():
    # Raise or lower the shields.
    global e, s

    if d[6] < 0:
        print("SHIELD CONTROL INOPERABLE")
        return

    while True:
        xs = input(f"ENERGY AVAILABLE = {e + s} NUMBER OF UNITS TO SHIELDS? ")
        if len(xs) > 0:
            try:
                x = int(xs)
            except:
                continue
            break

    if x < 0 or s == x:
        print("<SHIELDS UNCHANGED>")
        return

    if x > e + s:
        print("SHIELD CONTROL REPORTS  'THIS IS NOT THE FEDERATION "
              "TREASURY.'\n"
              "<SHIELDS UNCHANGED>")
        return

    e += s - x
    s = x
    print("DEFLECTOR CONTROL ROOM REPORT:")
    print(f"  'SHIELDS NOW AT {s} UNITS PER YOUR COMMAND.'")


def damage_control():
    # Print a damage control report.
    global d, t

    if d[5] < 0:
        print('DAMAGE CONTROL REPORT NOT AVAILABLE')
    else:
        print('\nDEVICE             STATE OF REPAIR')
        for r1 in range(8):
            print(f"{devices[r1].ljust(26, ' ')}{int(d[r1] * 100) * 0.01:g}")
        print()

    if not docked:
        return

    d3 = sum(0.1 for i in range(8) if d[i] < 0)
    if d3 == 0:
        return

    d3 += d4
    if d3 >= 1:
        d3 = 0.9
    print("\nTECHNICIANS STANDING BY TO EFFECT REPAIRS TO YOUR SHIP;")
    print("ESTIMATED TIME TO REPAIR: "
          f"{round(0.01 * int(100 * d3), 2)} STARDATES")
    if input("WILL YOU AUTHORIZE THE "
             "REPAIR ORDER (Y/N)? ").upper().strip() != 'Y':
        return

    for i in range(8):
        if d[i] < 0:
            d[i] = 0
    t += d3 + 0.1


def computer():
    # Perform the various functions of the library computer.
    global d, z, k9, t0, t9, t, b9, s1, s2, b4, b5

    if d[7] < 0:
        print("COMPUTER DISABLED")
        return

    while True:
        coms = input("COMPUTER ACTIVE AND AWAITING COMMAND? ")
        if len(coms) == 0:
            com = 6
        else:
            try:
                com = int(coms)
            except:
                com = 6
        if com < 0:
            return

        print()

        if com == 0 or com == 5:
            if com == 5:
                print("                        THE GALAXY")
            else:
                print("\n        COMPUTER RECORD OF GALAXY FOR "
                      f"QUADRANT {q1 + 1} , {q2 + 1}\n")

            print("       1     2     3     4     5     6     7     8")
            sep = "     ----- ----- ----- ----- ----- ----- ----- -----"
            print(sep)

            for i in range(8):
                line = ' ' + str(i + 1) + ' '

                if com == 5:
                    g2s = quadrant_name(i, 0, True)
                    line += (' ' * int(12 - 0.5 * len(g2s))) + g2s
                    g2s = quadrant_name(i, 4, True)
                    line += (' ' * int(39 - 0.5 * len(g2s) - len(line))) + g2s
                else:
                    for j in range(8):
                        line += '   '
                        if z[i][j] == 0:
                            line += '***'
                        else:
                            line += str(z[i][j] + 1000)[-3:]

                print(line)
                print(sep)

            print()
            return
        elif com == 1:
            print("   STATUS REPORT:")
            print(f"KLINGON{'S' if k9 > 1 else ''} LEFT: {k9}")
            print("MISSION MUST BE COMPLETED IN "
                  f"{round(0.1 * int((t0+t9-t) * 10), 1)} STARDATES")

            if b9 == 0:
                print("YOUR STUPIDITY HAS LEFT YOU ON YOUR OWN IN")
                print("  THE GALAXY -- YOU HAVE NO STARBASES LEFT!")
            else:
                print(f"THE FEDERATION IS MAINTAINING {b9} "
                      f"STARBASE{'S' if b9 > 1 else ''} IN THE GALAXY")

            damage_control()
            return
        elif com == 2:
            if k3 <= 0:
                print("SCIENCE OFFICER SPOCK REPORTS  'SENSORS SHOW NO ENEMY "
                      "SHIPS\n"
                      "                                IN THIS QUADRANT'")
                return

            print("FROM ENTERPRISE TO KLINGON BATTLE "
                  f"CRUISER{'S' if k3 > 1 else ''}")

            for i in range(4):
                if k[i][2] > 0:
                    print_direction(s1, s2, k[i][0], k[i][1])
            return
        elif com == 3:
            if b3 == 0:
                print("MR. SPOCK REPORTS,  'SENSORS SHOW NO STARBASES IN THIS "
                      "QUADRANT.'")
                return

            print("FROM ENTERPRISE TO STARBASE:")
            print_direction(s1, s2, b4, b5)
            return
        elif com == 4:
            print("DIRECTION/DISTANCE CALCULATOR:")
            print(f"YOU ARE AT QUADRANT {q1+1} , {q2+1} SECTOR "
                  f"{s1+1} , {s2+1}")
            print("PLEASE ENTER")
            while True:
                ins = input("  INITIAL COORDINATES (X,Y)? ").split(',')
                if len(ins) == 2:
                    from1, from2 = int(ins[0]) - 1, int(ins[1]) - 1
                    if 0 <= from1 <= 7 and 0 <= from2 <= 7:
                        break
            while True:
                ins = input("  FINAL COORDINATES (X,Y)? ").split(',')
                if len(ins) == 2:
                    to1, to2 = int(ins[0]) - 1, int(ins[1]) - 1
                    if 0 <= to1 <= 7 and 0 <= to2 <= 7:
                        break
            print_direction(from1, from2, to1, to2)
            return
        else:
            print("FUNCTIONS AVAILABLE FROM LIBRARY-COMPUTER:\n"
                  "   0 = CUMULATIVE GALACTIC RECORD\n"
                  "   1 = STATUS REPORT\n"
                  "   2 = PHOTON TORPEDO DATA\n"
                  "   3 = STARBASE NAV DATA\n"
                  "   4 = DIRECTION/DISTANCE CALCULATOR\n"
                  "   5 = GALAXY 'REGION NAME' MAP\n")


def print_direction(from1, from2, to1, to2):
    # Print direction and distance between two locations in the grid.
    delta1 = -(to1 - from1)  # flip so positive is up (heading = 3)
    delta2 = to2 - from2

    if delta2 > 0:
        if delta1 < 0:
            base = 7
        else:
            base = 1
            delta1, delta2 = delta2, delta1
    else:
        if delta1 > 0:
            base = 3
        else:
            base = 5
            delta1, delta2 = delta2, delta1

    delta1, delta2 = abs(delta1), abs(delta2)

    if delta1 > 0 or delta2 > 0:  # bug in original; no check for divide by 0
        if delta1 >= delta2:
            print(f"DIRECTION = {round(base + delta2 / delta1, 6)}")
        else:
            print(f"DIRECTION = {round(base + 2 - delta1 / delta2, 6)}")

    print(f"DISTANCE = {round(sqrt(delta1 ** 2 + delta2 ** 2), 6)}")


# -------------------------------------------------------------------------
#  Game transitions
# -------------------------------------------------------------------------


def startup():
    # Initialize the game variables and map, and print startup messages.
    global g, z, d, t, t0, t9, docked, e, e0, p, p0, s, k9, b9, s9, c 
    global devices, q1, q2, s1, s2, k7
    # For Marcus Aurelius quotes
    global ma, m1, m2, command

    print("\n\n\n\n\n\n\n\n\n\n\n"
          "                                    ,------*------,\n"
          "                    ,-------------   '---  ------'\n"
          "                     '-------- --'      / /\n"
          "                         ,---' '-------/ /--,\n"
          "                          '----------------'\n\n"
          "                    THE USS ENTERPRISE --- NCC-1701\n"
          "\n\n\n\n")

    if input("DO YOU NEED INSTRUCTIONS (Y/N)? ").upper().strip()[:1] == 'Y':
        instructions()

    # set up global game variables
    g = [[0] * 8 for _ in range(8)]         # galaxy map
    z = [[0] * 8 for _ in range(8)]         # charted galaxy map
    d = [0] * 8                             # damage stats for devices
    t = t0 = 100 * random.randint(20, 39)   # stardate (current, initial)
    t9 = random.randint(25, 34)             # mission duration (stardates)
    docked = False                          # true when docked at starbase
    e = e0 = 3000                           # energy (current, initial)
    p = p0 = 10                             # torpedoes (current, initial)
    s = 0                                   # shields
    k9, b9 = 0, 0                           # total Klingons, bases in galaxy
    # ^ bug in original, was b9 = 2
    k4, b4 = 0, 0                           # will a quadrant have 4 Klingons?
    s9 = 200                                # avg. Klingon shield strength
    command = ''                            # string for command
    ma = [0] * 13                           # Marcus Aurelius display flag
    m1 = 0                                  # Marcus Aurelius pointer
    m2 = 0                                  # counter for SRS command (Marcus Aurelius)

    c = [[0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1],
         [1, 0], [1, 1], [0, 1]]            # vectors in cardinal directions

    devices = ['WARP ENGINES', 'SHORT RANGE SENSORS', 'LONG RANGE SENSORS',
               'PHASER CONTROL', 'PHOTON TUBES', 'DAMAGE CONTROL',
               'SHIELD CONTROL', 'LIBRARY-COMPUTER']

    # initialize Enterprise's position
    q1, q2 = fnr(), fnr()                   # Enterprise's quadrant
    s1, s2 = fnr(), fnr()                   # ...and sector

    # initialize contents of galaxy
    for i in range(8):
        for j in range(8):
            k3 = 0
            r1 = random.random()

            if r1 > 0.98:
                k3 = 3
            elif r1 > 0.95:
                k3 = 2
            elif r1 > 0.80:
                k3 = 1
            k9 += k3

            b3 = 0
            if random.random() > 0.96:
                b3 = 1
                b9 += 1
            g[i][j] = k3 * 100 + b3 * 10 + fnr() + 1

    if k9 > t9:
        t9 = k9 + 1

    # if 15 or fewer Klingons, one quadrant will have 4
    if k9 < 16:
        while k4 == 0:
            q1, q2 = random.randint(2, 5), random.randint(2, 5)
            if g[q1][q2] < 100:
                g[q1][q2] += 400
                k9 += 4
                # Add a starbase nearby
                while b4 == 0:
                    q3, q4 = (q1+1-random.randint(0, 2)), (q2+1-random.randint(0, 2))
                    b4 = (g[q3][q4] // 10) % 10
                    # If the random nearby sector doesn't have a starbase
                    if b4 == 0:  
                        g[q3][q4] += 10
                        b9 += 1
                        b4 = 1
                    # If the random nearby sector has one already, try again
                    else:
                        b4 = 0
                k4 = 1
            q1, q2 = fnr(), fnr()  # Reset the Enterprise's starting position

    if b9 == 0:  # original has buggy extra code here
        b9 = 1
        g[q1][q2] += 10
        q1, q2 = fnr(), fnr()

    k7 = k9                                 # Klingons at start of game

    print("YOUR ORDERS ARE AS FOLLOWS:\n"
          f"     DESTROY THE {k9} KLINGON WARSHIPS WHICH HAVE INVADED\n"
          "   THE GALAXY BEFORE THEY CAN ATTACK FEDERATION HEADQUARTERS\n"
          f"   ON STARDATE {t0+t9}. THIS GIVES YOU {t9} DAYS. THERE "
          f"{'IS' if b9 == 1 else 'ARE'}\n"
          f"   {b9} STARBASE{'' if b9 == 1 else 'S'} IN THE GALAXY FOR "
          "RESUPPLYING YOUR SHIP.\n")


def new_quadrant():
    # Enter a new quadrant: populate map and print a short range scan.
    global z, k3, b3, s3, d4, k, qs, b4, b5, m1

    k3 = b3 = s3 = 0                        # Klingons, bases, stars in quad.
    d4 = 0.5 * random.random()              # extra delay in repairs at base
    z[q1][q2] = g[q1][q2]

    if 0 <= q1 <= 7 and 0 <= q2 <= 7:
        quad = quadrant_name(q1, q2, False)
        if t == t0:
            print("\nYOUR MISSION BEGINS WITH YOUR STARSHIP LOCATED")
            print(f"IN THE GALACTIC QUADRANT, '{quad}'.\n")
        else:
            print(f"\nNOW ENTERING {quad} QUADRANT . . .\n")

        k3 = g[q1][q2] // 100
        b3 = g[q1][q2] // 10 - 10 * k3
        s3 = g[q1][q2] - 100 * k3 - 10 * b3

        # Marcus Aurelius trigger
        if k3 > 3:
            m1 = 12
        elif k3 > 2:
            m1 = 5
        elif k3 > 0:
            m1 = 6

        if k3 != 0:
            marcus_aurelius()
            print("COMBAT AREA      CONDITION RED")
            if s <= 200:
                print("   SHIELDS DANGEROUSLY LOW")

    k = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]   # Klingons in current quadrant
    qs = ' ' * 192                          # quadrant string

    # build quadrant string
    insert_marker(s1, s2, '<*>')
    for i in range(k3):
        r1, r2 = find_empty_place()
        insert_marker(r1, r2, '+K+')
        k[i] = [r1, r2, s9 * (0.5 + random.random())]
    if b3 > 0:
        b4, b5 = find_empty_place()         # position of starbase (sector)
        insert_marker(b4, b5, '>!<')
    for i in range(s3):
        r1, r2 = find_empty_place()
        insert_marker(r1, r2, ' * ')

    short_range_scan()

def instructions():
    print("\n\n")
    print("     INSTRUCTIONS FOR 'SUPER STAR TREK'")
    print("\n")
    print("1. WHEN YOU SEE \\COMMAND ?\\ PRINTED, ENTER ONE OF THE LEGAL")
    print("     COMMANDS (NAV, SRS, LRS, PHA, TOR, SHE, DAM, COM, OR XXX).")
    print("2. IF YOU SHOULD TYPE IN AN ILLEGAL COMMAND, YOU'LL GET A SHORT")
    print("     LIST OF THE LEGAL COMMANDS PRINTED OUT.")
    print("3. SOME COMMANDS REQUIRE YOU TO ENTER DATA (FOR EXAMPLE THE")
    print("     'NAV' COMMAND COMES BACK WITH COURSE (1-9) ?'.) IF YOU")
    print("     TYPE IN ILLEGAL DATA (LIKE NEGATIVE NUMBERS), THAT COMMAND")
    print("     WILL BE ABORTED")
    print("\n")
    print("     THE GALAXY IS DIVIDED INTO AN 8 X 8 QUADRANT GRID,")
    print("AND EACH QUADRANT IS FURTHER DIVIDED INTO AN 8 X 8 SECTOR GRID.")
    print("\n")
    print("     YOU WILL BE ASSIGNED A STARTING POINT SOMEWHERE IN THE")
    print("GALAXY TO BEGIN A TOUR OF DUTY AS COMMANDER OF THE STARSHIP")
    print("\\ENTERPRISE\\; YOUR MISSION: TO SEEK AND DESTROY THE FLEET OF")
    print("KLINGON WARSHIPS WHICH ARE MENACING THE UNITED FEDERATION OF")
    print("PLANETS.")
    input("CONTINUE...")
    print("\x1b[2J\033[H")
    print("     YOU HAVE THE FOLLOWING COMMANDS AVAILABLE TO YOU AS CAPTAIN")
    print("OF THE STARSHIP ENTERPRISE:")
    print("\n")
    print("\\NAV\\ COMMAND = WARP ENGINE CONTROL --")
    print("     COURSE 15 IN A CIRCULAR NUMERICAL      4  3  2")
    print("     VECTOR ARRANGEMENT AS SHOWN.            . . .")
    print("     INTEGER AND REAL VALUES MAY BE           ...")
    print("     USED. (THUS COURSE 1.5 IS HALF-      5 ---*--- 1")
    print("     WAY BETWEEN 1 AND 2.                     ...")
    print("                                             . . .")
    print("     VALUES MAY APPROACH 9.0. WHICH         6  7  8")
    print("     ITSELF IS EQUIVALENT TO 1.0.")
    print("                                             COURSE")
    print("     ONE WARP FACTOR IS THE SIZE OF")
    print("     ONE QUADRANT.  THEREFORE, TO GET") 
    print("     FROM QUADRANT 6,5 TO 5,5, YOU WOULD")
    print("     USE COURSE 3. WARP FACTOR 1.")
    input("CONTINUE...")
    print("\x1b[2J\033[H")
    print("\\SRS\\ COMMAND = SHORT RANGE SENSOR SCAN --")
    print("     SHOWS YOU A SCAN OF YOUR PRESENT QUADRANT.")
    print("\n")
    print("     SYMBOLOGY ON YOUR SENSOR SCREEN IS AS FOLLOWS:")
    print("        <*> = YOUR STARSHIP'S POSITION")
    print("        +K+ = KLINGON BATTLE CRUISER")
    print("        >!< = FEDERATION STARBASE (REFUEL/REPAIR/RE-ARM HERE!)")
    print("         *  = STAR")
    print("\n")
    print("     A CONDENSED 'STATUS REPORT' WILL ALSO BE PRESENTED.")
    input("CONTINUE...")
    print("\x1b[2J\033[H")
    print("\\LRS\\ COMMAND = LONG RANGE SENSOR SCAN --")
    print("     SHOWS CONDITIONS IN SPACE FOR ONE QUADRANT ON EACH SIDE")
    print("     OF THE ENTERPRISE (WHICH IS IN THE MIDDLE OF THE SCAN)")
    print("     THE SCAN IS CODED IN THE FORM \\###\\, WHERE THE UNITS DIGIT")
    print("     IS THE NUMBER OF STARS. THE TENS DIGIT IS THE NUMBER OF")
    print("     STARBASES, AND THE HUNDRESDS DIGIT IS THE NUMBER OF")
    print("     KLINGONS.")
    print("\n")
    print("     EXAMPLE - 207 - 2 KLINGONS, NO STARBASES, & 7 STARS.")
    input("CONTINUE...")
    print("\x1b[2J\033[H")
    print("\\PHA\\ COMMAND = PHASER CONTROL --")
    print("     ALLOWS YOU TO DESTROY THE KLINGON BATTLE CRUISERS BY ")
    print("     ZAPPING THEM WITH SUITABLY LARGE UNITS OF ENERGY TO")
    print("     DEPLETE THEIR SHIELD POWER. (REMEMBER, KLINGONS HAVE")
    print("     PHASERS, T00!)")
    print("\n")
    print("\\TOR\\ COMMAND = PHOTON TORPEDO CONTROL --")
    print("     TORPEDO COURSE IS THE SAME AS USED IN WARP ENGINE CONTROL")
    print("     IF YOU HIT THE KLINGON VESSEL. HE IS DESTROYED AND CANNOT")
    print("     FIRE BACK AT YOU. IF YOU MISS. YOU ARE SUBJECT TO HIS")
    print("     PHASER FIRE.  IN EITHER CASE, YOU ARE ALSO SUBJECT TO")
    print("     THE PHASER FIRE OF ALL OTHER KLINGONS IN THE QUADRANT.")
    print("\n")
    print("     THE LIBRARY-COMPUTER (\\COM\\ COMMAND) HAS AN OPTION TO ")
    print("     COMPUTE TORPEDO TRAJECTORY FOR YOU (OPTION 2).")
    input("CONTINUE...")
    print("\x1b[2J\033[H")
    print("\\SHE\\ COMMAND = SHIELD CONTROL --")
    print("     DEFINES THE NUMBER OF ENERGY UNITS TO BE ASSIGNED TO THE")
    print("     SHIELDS. ENERGY IS TAKEN FROM TOTAL SHIP'S ENERGY. NOTE")
    print("     THAT THE STATUS DISPLAY TOTAL ENERGY INCLUDES SHIELD ENERGY.")
    print("\n")
    print("\\DAM\\ COMMAND = DAMAGE CONTROL REPORT --")
    print("     GIVES THE STATE OF REPAIR OF ALL DEVICES. WHERE A NEGATIVE")
    print("     'STATE OF REPAIR' SHOWS THAT THE DEVICE IS TEMPORARILY")
    print("     DAMAGED.")
    input("CONTINUE...")
    print("\x1b[2J\033[H")
    print("\\COM\\ COMMAND = LIBRARY-COMPUTER --")
    print("     THE LIBRARY-COMPUTER CONTAINS SIX OPTIONS:")
    print("     OPTION 0 = CUMULATIVE GALACTIC RECORD")
    print("        THIS OPTION SHOWS COMPUTER MEMORY OF THE RESULTS OF ALL")
    print("        PREVIOUS SHORT AND LONG RANGE SENSOR SCANS")
    print("     OPTION 1 = STATUS REPORT")
    print("        THIS OPTION SHOWS THE NUMBER OF KLINGONS. STARDATES,")
    print("        AND STARBASES REMAINING IN THE GAME.")
    print("     OPTION 2 = PHOTON TORPEDO DATA")
    print("        WHICH GIVES DIRECTIONS AND DISTANCE FROM THE ENTERPRISE")
    print("        TO ALL KLINGONS IN YOUR QUADRANT")
    print("     OPTION 3 = STARBASE NAV DATA")
    print("        THIS OPTION GIVES DIRECTION AND DISTANCE TO ANY ")
    print("        STARBASE WITHIN YOUR QUADRANT")
    print("     OPTION 4 = DIRECTION/DISTANCE CALCULATOR")
    print("        THIS OPTION ALLOWS YOU TO ENTER COORDINATES FOR")
    print("        DIRECTION/DISTANCE CALCULATIONS")
    print("     OPTION 5 = CALACTIC /REGION NAME/ MAP")
    print("        THIS OPTION PRINTS THE NAMES OF THE SIXTEEN MAJOR ")
    print("        GALACTIC REGIONS REFERRED TO IN THE GAME.")
    input("CONTINUE...")
    print("\n\n")

def marcus_aurelius():
    global ma, m1
    # In the Star Trek line of descent from the University of
    # Texas Fortran code, there's a strange version that spits
    # out quotes from The Meditations of Marcus Aurelius,
    # specifically, the George Long translation.
    # This routine implements the Marcus Aurelius quotes
    # for the Bob Leedom/David H. Ahl version of Super Star Trek
    # from Creative Computing/101 BASIC Computer Games of
    # the late 1970s.

    # return
    # Uncomment line above to disable the Marcus Aurelius quotes
    if ma[m1] == 1:
        return()
    else:
        ma[m1] = 1

    print("\n")
    if m1 == 1:
        # Time-based: more than 25 stardates into the mission
        print("   ALL THINGS ARE FAMILIAR TO US; BUT THE")
        print("   DISTRIBUTION OF THEM STILL REMAINS THE")
        print("   SAME.")
        print("         --- MARCUS AURELIUS, VIII.6")
    elif m1 == 2:
        # Time-based: more than 18 stardates into the mission
        print("   THINK OF THE UNIVERSAL SUBSTANCE, OF WHICH")
        print("   THOU HAST A VERY SMALL PORTION; AND OF")
        print("   UNIVERSAL TIME, OF WHICH A SHORT AND")
        print("   INDIVISIBLE INTERVAL HAS BEEN ASSIGNED TO")
        print("   THEE; AND OF THAT WHICH IS FIXED BY DESTINY,")
        print("   AND HOW SMALL A PART OF IT THOU ART.")
        print("         --- MARCUS AURELIUS, V.24")
    elif m1 == 3:
        # Time-based: more than 10 stardates into the mission
        print("   BE NOT PERTURBED, FOR ALL THINGS ARE")
        print("   ACCORDING TO THE NATURE OF THE UNIVERSE;")
        print("   AND IN A LITTLE TIME THOU WILT BE NOBODY")
        print("   AND NOWHERE.")
        print("         --- MARCUS AURELIUS, VIII.5")
    elif m1 == 4:
        # Time-based: more than 5 stardates into the mission
        print("   IF HE IS A STRANGER TO THE UNIVERSE WHO")
        print("   DOES NOT KNOW WHAT IS IN IT, NO LESS IS HE")
        print("   A STRANGER WHO DOES NOT KNOW WHAT IS GOING")
        print("   ON IN IT.")
        print("         --- MARCUS AURELIUS, IV.29")
    elif m1 == 5:
        # Klingon-based: 3 Klingons in the quadrant
        print("   TO SEEK WHAT IS IMPOSSIBLE IS MADNESS; AND")
        print("   IT IS IMPOSSIBLE THAT THE BAD SHOULD NOT DO")
        print("   SOMETHING OF THIS KIND.")
        print("         --- MARCUS AURELIUS, V.17")
    elif m1 == 6:
        # Klingon-based: At least 1 Klingon in the quadrant
        print("   LET NO ACT BE DONE WITHOUT PURPOSE, NOR")
        print("   OTHERWISE THAN ACCORDING TO THE PERFECT")
        print("   PRINCIPLES OF ART.")
        print("         --- MARCUS AURELIUS, IV.2")
    elif m1 == 7:
        # Enterprise destroyed
        print("   CONSIDER EVERYTHING WHICH HAPPENS, HAPPENS")
        print("   JUSTLY, AND IF THOU OBSERVEST CAREFULLY,")
        print("   THOU WILT FIND IT TO BE SO.")
        print("         --- MARCUS AURELIUS, IV.10")
    elif m1 == 8:
        # Too many short-range scans in a single sector
        print("   TO THE AIDS WHICH HAVE BEEN MENTIONED, LET")
        print("   THIS ONE STILL BE ADDED:  MAKE FOR THYSELF A")
        print("   DEFINITION OR DESCRIPTION OF THE THING WHICH")
        print("   IS PRESENTED TO THEE, SO AS TO SEE DISTINCTLY WHAT")
        print("   KIND OF THING IT IS IN ITS SUBSTANCE, IN ITS")
        print("   NUDITY, IN ITS COMPLETE ENTIRETY; AND TELL THYSELF")
        print("   ITS PROPER NAME, AND THE NAMES OF THE THINGS OF")
        print("   WHICH IT HAS BEEN COMPOUNDED, AND INTO WHICH IT")
        print("   WILL BE RESOLVED.")
        print("         --- MARCUS AURELIUS, III.11")
    elif m1 == 9:
        # Enterprise defeates the Klingons
        print("   EVERYTHING WHICH IS IN ANY WAY BEAUTIFUL IS")
        print("   BEAUTIFUL IN ITSELF AND TERMINATES IN ITSELF,")
        print("   NOT HAVING PRAISE AS PART OF ITSELF.  NEITHER")
        print("   WORSE, THEN, NOR BETTER IS A THING MADE BY BEING")
        print("   PRAISED.")
        print("         --- MARCUS AURELIUS, IV.20")
    elif m1 == 10:
        # Energy-based: Enterprise with less than 150 energy
        print("   THAT WHICH HAS DIED FALLS NOT OUT OF THE")
        print("   UNIVERSE.  IF IT STAYS HERE, IT ALSO CHANGES")
        print("   HERE, AND IS DISSOLVED INTO ITS PROPER PARTS,")
        print("   WHICH ARE ELEMENTS OF THE UNIVERSE AND OF")
        print("   THYSELF.")
        print("         --- MARCUS AURELIUS, VIII.18")
    elif m1 == 11:
        # Energy-based: Enterprise with no energy
        print("   THERE IS NO MAN SO FORTUNATE THAT THERE SHALL ")
        print("   NOT BE BY HIM WHEN HE IS DYING SOME WHO ARE ")
        print("   PLEASED WITH WHAT IS GOING TO HAPPEN.")
        print("         --- MARCUS AURELIUS, X.36")
    elif m1 == 12:
        # Klingon-based: 4 Klingons in the quadrant
        print("   SEE THAT THOU SECURE THIS PRESENT TIME TO THYSELF;")
        print("   FOR THOSE WHO RATHER PURSUE POSTHUMOUS FAME DO NOT")
        print("   CONSIDER THAT THE MEN OF AFTER TIME WILL BE")
        print("   EXACTLY SUCH AS THOSE WHOM THEY CANNOT BEAR NOW;")
        print("   AND BOTH ARE MORTAL. AND WHAT IS IT IN ANY WAY TO")
        print("   THEE IF THESE MEN OF AFTER TIME UTTER THIS OR THAT")
        print("   SOUND, OR HAVE THIS OR THAT OPINION ABOUT THEE?")
        print("         --- MARCUS AURELIUS, VIII.44")
    else:
        print("")
    print("\n")

def end_game(won=False, quit=True, enterprise_killed=False):
    # Handle end-of-game situations.
    global restart

    if won:
        m1 = 9
        marcus_aurelius()
        print("CONGRATULATIONS, CAPTAIN! THE LAST KLINGON BATTLE CRUISER")
        print("MENACING THE FEDERATION HAS BEEN DESTROYED.\n")
        print("YOUR EFFICIENCY RATING IS "
              f"{round(1000 * (k7 / (t - t0))**2, 4)}\n\n")
    else:
        if not quit:
            if enterprise_killed:
                m1 = 7
                marcus_aurelius()
                print("\nTHE ENTERPRISE HAS BEEN DESTROYED. THE FEDERATION "
                      "WILL BE CONQUERED.")
            print(f"IT IS STARDATE {round(t, 1)}")

        print(f"THERE WERE {k9} KLINGON BATTLE CRUISERS LEFT AT")
        print(f"THE END OF YOUR MISSION.\n\n")

        if b9 == 0:
            exit()

    print("THE FEDERATION IS IN NEED OF A NEW STARSHIP COMMANDER")
    print("FOR A SIMILAR MISSION -- IF THERE IS A VOLUNTEER,")
    if input("LET HIM STEP FORWARD AND "
             "ENTER 'AYE'? ").upper().strip() != 'AYE':
        exit()
    restart = True


# -------------------------------------------------------------------------
#  Entry point and main game loop
# -------------------------------------------------------------------------


def main():
    global restart, command, ma, m1

    f = {'NAV': navigation, 'SRS': short_range_scan, 'LRS': long_range_scan,
         'PHA': phaser_control, 'TOR': photon_torpedoes, 'SHE': shield_control,
         'DAM': damage_control, 'COM': computer, 'XXX': end_game}

    order = ''

    while True:
        startup()
        new_quadrant()
        restart = False

        while not restart:
            # Marcus Aurelius quotes
            # Time-based triggers
            m1 = t - t0
            if m1 < 5:
                m1 = 0
            elif m1 < 10:
                m1 = 4
            elif m1 < 18:
                m1 = 3
            elif m1 < 25:
                m1 = 2
            else:
                m1 = 1

            # Energy-based triggers
            if s + e <= 150 or (e <= 150 and d[6] != 0):
                # Energy bwlow 150; Enterprise at risk
                m1 = 10

            if s + e <= 10 or (e <= 10 and d[6] != 0):
                # Energy bwlow 10; Enterprise stranded in space
                print("\n** FATAL ERROR **   YOU'VE JUST STRANDED YOUR SHIP "
                      "IN SPACE.\nYOU HAVE INSUFFICIENT MANEUVERING ENERGY, "
                      "AND SHIELD CONTROL\nIS PRESENTLY INCAPABLE OF CROSS-"
                      "CIRCUITING TO ENGINE ROOM!!")
                m1 = 11

            if m1 > 0:
                marcus_aurelius()

            command = input('COMMAND? ').upper().strip()

            if command in f:
                f[command]()
            else:
                print("ENTER ONE OF THE FOLLOWING:\n"
                      "  NAV  (TO SET COURSE)\n"
                      "  SRS  (FOR SHORT RANGE SENSOR SCAN)\n"
                      "  LRS  (FOR LONG RANGE SENSOR SCAN)\n"
                      "  PHA  (TO FIRE PHASERS)\n"
                      "  TOR  (TO FIRE PHOTON TORPEDOES)\n"
                      "  SHE  (TO RAISE OR LOWER SHIELDS)\n"
                      "  DAM  (FOR DAMAGE CONTROL REPORTS)\n"
                      "  COM  (TO CALL ON LIBRARY-COMPUTER)\n"
                      "  XXX  (TO RESIGN YOUR COMMAND)\n")


if __name__ == "__main__":
    main()
