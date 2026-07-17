# TPS43 Trackpad — Shopping List (Digikey)

## Option A: Custom PCB Route (recommended)

| Qty | Part | Digikey PN | Link | ~Price |
|-----|------|-----------|------|--------|
| 1 | TPS43-201A-B trackpad module | 1790-1015-ND | https://www.digikey.com/en/products/detail/azoteq-pty-ltd/TPS43-201A-B/7101305 | $18.50 |
| 1 | Molex 503480-0600 FFC connector, 6-pin, 0.5mm, RA | WM14219CT-ND | https://www.digikey.com/en/products/detail/molex/5034800600/2356622 | $0.75 |
| 1 | FFC cable, 6-pin, 0.5mm, 100mm, Type A (same-side contacts) | WM14348-ND | https://www.digikey.com/en/products/detail/molex/0151660603/3888092 | $2.50 |
| 2 | 12-pin female socket header, 2.54mm | S7008-ND | https://www.digikey.com/en/products/detail/sullins-connector-solutions/PPPC121LFBN-RC/810200 | $1.80 |
| 2 | 12-pin male pin header, 2.54mm | S2011E-12-ND | https://www.digikey.com/en/products/detail/sullins-connector-solutions/PRPC012SAAN-RC/2775404 | $0.60 |
| 2 | 2.2kΩ 0805 SMD resistor | 311-2.20KARCT-ND | https://www.digikey.com/en/products/detail/yageo/RC0805FR-072K2L/727829 | $0.10 |
| 5 | Custom PCBs (JLCPCB) | — | Upload `temper-tps43-interposer.kicad_pcb` | ~$5 |
| | | | **Total** | **~$30** |

> **Note on FFC cable**: The linked Molex 0151660603 is a 152mm cable. Any 6-pin 0.5mm Type A (same-side contacts) FFC cable 50-150mm long works.
> For JLCPCB PCB ordering: 2 layers, 1.0mm thickness, ENIG finish.

---

## Option B: Breadboard / Hand-Wired Route

No custom PCB required. You wire everything point-to-point on perfboard.

| Qty | Part | Digikey PN | Link | ~Price |
|-----|------|-----------|------|--------|
| 1 | TPS43-201A-B trackpad module | 1790-1015-ND | ^ same as above | $18.50 |
| 1 | Molex 503480-0600 FFC connector, 6-pin, 0.5mm, RA | WM14219CT-ND | ^ same as above | $0.75 |
| 1 | FFC cable, 6-pin, 0.5mm, 100mm, Type A | WM14348-ND | ^ same as above | $2.50 |
| 1 | Protoboard / perfboard (50×70mm) | V2018-ND | https://www.digikey.com/en/products/detail/vector-electronics/8016/1358063 | $5.00 |
| 2 | 2.2kΩ through-hole resistor (1/4W) | 2.20KXBK-ND | https://www.digikey.com/en/products/detail/yageo/CFR-25JB-52-2K2/2686 | $0.20 |
| 1 | Hookup wire, 28AWG, assorted (solid core) | 1528-1877-ND | https://www.digikey.com/en/products/detail/adafruit-industries-llc/3173/10238156 | $4.00 |
| 1 | Soldering iron + solder | — | Whatever you have | — |
| | | | **Total** | **~$31** |

### Hand-wiring approach

1. Solder the FFC connector onto the perfboard
2. Solder the two 2.2kΩ resistors on the perfboard between VCC-SDA and VCC-SCL
3. Solder 6 wires from the perfboard FFC pads to the nice!nano castellations:
   - FFC pin 1 (VDD) → nice!nano VCC
   - FFC pin 2 (SDA) → nice!nano D8
   - FFC pin 3 (SCL) → nice!nano D9
   - FFC pin 4 (RDY) → nice!nano D10
   - FFC pin 5 (RST) → nice!nano D16
   - FFC pin 6 (GND) → nice!nano GND
4. Connect TPS43 via FFC cable
5. Mount the perfboard alongside the nice!nano (tape or 3D-printed bracket)

**Downside vs PCB**: Messier, less reliable, harder to unplug. The PCB route adds pass-through so you can still socket/unplug the nice!nano freely.
