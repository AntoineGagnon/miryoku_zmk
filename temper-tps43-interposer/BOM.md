# TPS43 Trackpad — Shopping List (digikey.ca)

## Option A: Custom PCB Route (recommended)

| Qty | Part | digikey.ca Link | ~Price |
|-----|------|-----------------|--------|
| 1 | TPS43-201A-B trackpad module | https://www.digikey.ca/en/products/detail/azoteq-pty-ltd/TPS43-201A-B/7101305 | $18.50 |
| 1 | Molex 5034800600 FFC connector, 6-pos, 0.5mm, RA | https://www.digikey.ca/en/products/detail/molex/5034800600/2356622 | $0.75 |
| 1 | FFC cable: 6-pos, 0.5mm pitch, ~100mm, Type A *(see note)* | https://www.digikey.ca/en/products/filter/flat-flex-ribbon-jumpers-cables/458?s=N4IgTCBcDaIDYFMwHYCcBaADAUkgFkBaDEEAXQF8g | $3-5 |
| 2 | 12-pin female socket header, 2.54mm pitch | https://www.digikey.ca/en/products/detail/sullins-connector-solutions/PPPC121LFBN-RC/810200 | $2 |
| 2 | 12-pin male pin header, 2.54mm pitch | https://www.digikey.ca/en/products/detail/sullins-connector-solutions/PRPC012SAAN-RC/2775404 | $1 |
| 2 | 2.2kΩ 0805 SMD resistor | https://www.digikey.ca/en/products/detail/yageo/RC0805FR-072K2L/727829 | $0.10 |
| 5 | Custom PCBs (JLCPCB) | Upload `temper-tps43-interposer.kicad_pcb` | ~$5 |
| | | **Total** | **~$32** |

> **FFC cable requirements**: 6 positions, 0.5mm pitch, Type A (contacts on same side of cable at both ends), 50–150mm length.
> The TPS43 ships with an FFC cable in some kits — check before ordering a separate one. If buying from Digikey, use the filter link above and select: `Number of Conductors = 6`, `Pitch = 0.020" (0.50mm)`, `Length = 2.000" (50.80mm) to 6.000" (152.40mm)`.
>
> **JLCPCB specs**: 2 layers, 1.0mm thickness, ENIG finish (recommended for the fine-pitch FFC pads).

---

## Option B: Breadboard / Hand-Wired Route

No custom PCB required. Wire everything point-to-point on perfboard.

| Qty | Part | digikey.ca Link | ~Price |
|-----|------|-----------------|--------|
| 1 | TPS43-201A-B trackpad module | ^ same as above | $18.50 |
| 1 | Molex 5034800600 FFC connector | ^ same as above | $0.75 |
| 1 | FFC cable, 6-pos, 0.5mm, ~100mm, Type A | ^ see filter link above | $3-5 |
| 1 | Protoboard / perfboard (~50×70mm) | https://www.digikey.ca/en/products/detail/busboard-prototype-systems/ST3U/17439370 | $3 |
| 2 | 2.2kΩ through-hole resistor (1/4W) | https://www.digikey.ca/en/products/detail/yageo/CFR-25JB-52-2K2/2686 | $0.20 |
| 1 | Hookup wire, solid-core, 22-28 AWG | https://www.digikey.ca/en/products/detail/adafruit-industries-llc/1311/10094919 | $4 |
| — | Soldering iron + solder | Whatever you have | — |
| | | **Total** | **~$31** |

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
