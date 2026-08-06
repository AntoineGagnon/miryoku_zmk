# TPS43 Trackpad, shopping list (digikey.ca)

## Interposer PCB build

| Qty | Designator | Part | Where | ~Price |
|-----|-----------|------|-------|--------|
| 1 | - | TPS43-201A-S trackpad module | https://www.digikey.ca/en/products/detail/azoteq-pty-ltd/TPS43-201A-S/7164940 | $18.50 |
| 1 | CON1 | Hirose FH12-6S-0.5SH(55), 6-pos 0.5 mm FFC, right angle | search Digikey for `FH12-6S-0.5SH(55)` | $1.00 |
| 1 | - | FFC jumper cable, 6-pos, 0.5 mm, 51 mm (see note on type) | https://www.digikey.ca/en/products/detail/assmann-wsw-components/AFFC-050-06-051-11/6570241 | $4.00 |
| 24 | JP1, JP2 | **Mill-Max pins** for the bottom side (Mill-Max 3320 series or the pins sold with MCU socket kits) | search Digikey for `3320-0-00-15-00-00-08-0` | $3.00 |
| 24 | JP1, JP2 | **Mill-Max 310 series machine sockets** for the top side | search Digikey for `310-93-112-41-105000` | $4.00 |
| 2 | R1, R2 | 2.2 kOhm 0805 SMD resistor | https://www.digikey.ca/en/products/detail/yageo/RC0805FR-072K2P/17018916 | $0.10 |
| 5 | - | PCBs (JLCPCB), 2 layer, 1.0 mm, ENIG, 1 oz, 20 x 40 mm | upload `output/temper-tps43-interposer-gerbers.zip` | ~$5.00 |
| | | | **Total** | **~$36** |

### Notes

**CON1 changed.** Earlier revisions specified the Molex 503480-0600. That part is dropped: its
land pattern was never checked against the datasheet, and the hand-drawn footprint used with it
had non-plated mounting holes, so the connector had no solder retention. The Hirose
FH12-6S-0.5SH is a drop-in functional equivalent with two SMT solder tabs, and KiCad ships a
datasheet-derived footprint for it in `Connector_FFC-FPC`, so nothing has to be hand-drawn.
Any 6-position 0.5 mm right-angle FFC connector with a matching land pattern will work, but if
you substitute, change `FP_FFC` in `gen_interposer.py` and re-run `./build.sh` so the escape
routing is re-verified against the new pad geometry.

**FFC cable, the one thing that can ruin the board.** CON1 is wired as the mirror of the
trackpad's connector, i.e. **CON1 pin N must reach TPS43 J1 pin 7−N**. The trackpad's J1 is
`1:RDY 2:NRST 3:GND 4:VDDHI 5:SCL 6:SDA` (datasheet rev 1.06, August 2025).

Do not order by the Type letter. The naming is not standardised: DigiKey and Molex call same-side
contacts Type A and opposite-side Type D, while other vendors call the same thing Type B, Type 1
or Type 2. FH12-6S-0.5SH is bottom-contact, so at the interposer end the conductors face the
board, but that alone does not determine the mapping.

**Ring the cable out before fabbing the PCB.** Lay it out as it will actually run and check
continuity from conductor 1 at one end. If it reaches conductor 6 at the other end, the cable is
reversed and this board is correct. If it reaches conductor 1, it is straight-through: the board
needs re-laying out (see `PCB_SPEC.md` section 11) before you order it. Getting this wrong drives
3.3 V onto the trackpad's RDY output and shorts SCL to ground.

The Assmann part linked above is a 51 mm 6-position 0.5 mm jumper; confirm its mapping on the
vendor drawing, or just measure it.

**Headers: do not use ordinary breakaway headers.** Temper is built with Mill-Max 310 series
machine sockets, and its assembly guide has you solder Mill-Max pins directly to the nice!nano.
Those sockets take ~0.5 mm round pins; a standard 2.54 mm header pin is 0.64 mm square, will not
enter, and wrecks the socket if forced. So:

- **Top of the interposer:** Mill-Max 310 sockets, to receive the pins on your nice!nano.
- **Bottom of the interposer:** Mill-Max pins, to plug into Temper's existing sockets.

The 1.0 mm plated holes in this design suit both. Buying one extra MCU socket kit is usually the
cheapest way to get 48 pins and sockets.

**Resistors.** Any 0805 2.2 kOhm thick-film part. Tolerance is irrelevant for an I2C pull-up;
the +/-1% part is linked only because it was in stock.

**Fab settings.** 20 x 40 mm, 2 layers, 1.0 mm thickness, ENIG finish, 1 oz copper. The board
needs 0.20 mm minimum track and clearance and a 0.30 mm minimum drill, which every budget fab
meets. The south edge is notched, so the outline is not a plain rectangle: check the fab renders
the Edge.Cuts layer rather than assuming a bounding box.

---

## Alternative: hand-wired, no PCB

Cheaper to start but you lose the pass-through, so the nice!nano is no longer freely
unpluggable. Same total cost once you account for the perfboard, so this is only worth it if you
want to test the trackpad before committing to a PCB order.

| Qty | Part | Where | ~Price |
|-----|------|-------|--------|
| 1 | TPS43-201A-S trackpad module | as above | $18.50 |
| 1 | 6-pos 0.5 mm FFC connector | as above | $1.00 |
| 1 | 6-pos 0.5 mm FFC cable, 51 mm | as above | $4.00 |
| 1 | Protoboard, ~50x70 mm | https://www.digikey.ca/en/products/detail/busboard-prototype-systems/ST3U/17439370 | $3.00 |
| 2 | 2.2 kOhm through-hole resistor, 1/4 W | https://www.digikey.ca/en/products/detail/yageo/CFR-25JB-52-2K2/2686 | $0.20 |
| 1 | Hookup wire, solid core, 22-28 AWG | https://www.digikey.ca/en/products/detail/adafruit-industries-llc/1311/10094919 | $4.00 |
| | | **Total** | **~$31** |

1. Solder the FFC connector to the perfboard.
2. Solder the two 2.2 kOhm resistors between VCC-SDA and VCC-SCL.
3. Run six wires from your connector's pads to the nice!nano castellations. Hand-wiring means
   you can match the trackpad pin for pin and ignore the cable mapping question entirely, as long
   as you trace which connector pad ends up on which TPS43 pin:

   | TPS43 J1 pin | Signal | nice!nano |
   |---|---|---|
   | 1 | RDY | D10 |
   | 2 | NRST | D16 |
   | 3 | GND | GND |
   | 4 | VDDHI | VCC |
   | 5 | SCL | D9 |
   | 6 | SDA | D8 |

4. Connect the TPS43 with the FFC cable.
5. Mount the perfboard alongside the nice!nano with tape or a printed bracket.
