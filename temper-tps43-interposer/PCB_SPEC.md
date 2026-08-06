# Temper TPS43 Interposer — PCB Design Specification

## Purpose

A thin (1.0mm) interposer PCB that sits between a nice!nano v2 (nRF52840) and
the Temper keyboard PCB. It passes through all 24 Pro Micro pins while tapping
4 unused GPIOs + VCC + GND to a 6-pin 0.5mm FFC connector for an Azoteq TPS43
trackpad. Two 0805 pull-up resistors are included for the I2C bus.

---

## 1. Mechanical

| Parameter | Value |
|-----------|-------|
| Width | 34.0 mm |
| Height | 44.0 mm |
| Thickness | 1.0 mm |
| Layers | 2 (F.Cu + B.Cu) |
| Substrate | FR-4, 1 oz copper |
| Surface finish | ENIG (required for 0.5mm FFC pads) |

The board outline is a simple rectangle: `(0, 0)` at the geometric centre.

### Pro Micro footprint placement

Two 1×12 pin headers, 2.54 mm pitch, 15.24 mm row spacing.

| Designator | X centre | Y centre (pin 1) | Orientation |
|-----------|----------|-------------------|-------------|
| JP1 (left row) | -7.62 mm | +12.70 mm | Pin 1 at top (Y+) |
| JP2 (right row) | +7.62 mm | +12.70 mm | Pin 1 at top (Y+) |

Pin 1 of each header is labelled on the silkscreen. The footprint used:

- **Footprint**: `Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical`
- **Attribute**: `exclude_from_pos_files exclude_from_bom`

The centre of each footprint is Y = (pin1_y - pin12_y) / 2 = 12.70 - 5.5×2.54 =
-1.27 mm.

### FFC connector placement

| Parameter | Value |
|-----------|-------|
| Designator | CON1 |
| X centre | 0 mm |
| Y centre | +15.70 mm |
| Rotation | 0° (cable exits toward +Y, toward thumb cluster) |
| Footprint | `temper-tps43-interposer:TPS43_FFC_06` (see §6) |
| Attribute | `smd` |

### Resistor placement

| Designator | X centre | Y centre | Rotation |
|-----------|----------|----------|----------|
| R1 | -3.62 mm | +20.70 mm | 90° (pads oriented along Y) |
| R2 | -3.62 mm | +18.20 mm | 90° (pads oriented along Y) |

- **Footprint**: `Resistor_SMD:R_0805_2012Metric`
- **Attribute**: `smd`
- **Note**: R1 is the top resistor (Y+), R2 is below it

### Component Y-offset summary

All component Y positions are shifted downward by 1.27 mm relative to the
header centres to centre them on the 44 mm board. The board Y extents are
-20.50 mm to +23.50 mm.

```
Y = +20.70  ───     R1 (0805 resistor)
Y = +18.20  ───     R2 (0805 resistor)
Y = +15.70  ───     CON1 (FFC connector, cable exits +Y)
Y = +12.70  ─── pin 1  ─┐
Y = +10.16  ─── pin 2   │
Y =  +7.62  ─── pin 3   │ JP1 & JP2
   ...                    │ (Pro Micro headers)
Y = -15.24  ─── pin 12 ─┘
```

---

## 2. Pin Mapping

### JP1 — Left row (facing nice!nano USB port away from you)

| Pin | Pro Micro label | nRF52840 | Net assigned |
|-----|----------------|----------|-------------|
| 1 | D1 / TX | P0.06 | unconnected (net 0) |
| 2 | D0 / RX | P0.03 | unconnected |
| 3 | GND | — | **GND** (net 1) |
| 4 | GND | — | **GND** (net 1) |
| 5 | D2 | P0.17 | unconnected |
| 6 | D3 | P0.20 | unconnected |
| 7 | D4 / A6 | P0.04 | unconnected |
| 8 | D5 | P0.05 | unconnected |
| 9 | D6 / A7 | P0.07 | unconnected |
| 10 | D7 | P0.08 | unconnected |
| 11 | **D8 / A8** | **P1.04** | **SDA (net 3)** |
| 12 | **D9 / A9** | **P0.09** | **SCL (net 4)** |

### JP2 — Right row

| Pin | Pro Micro label | nRF52840 | Net assigned |
|-----|----------------|----------|-------------|
| 1 | RAW | — | unconnected |
| 2 | GND | — | GND (net 1) |
| 3 | RST | P0.18 | unconnected |
| 4 | **VCC** | 3.3V | **VCC (net 2)** |
| 5 | D21 / A3 | P0.30 | unconnected |
| 6 | D20 / A2 | P0.28 | unconnected |
| 7 | D19 / A1 | P0.31 | unconnected |
| 8 | D18 / A0 | P0.29 | unconnected |
| 9 | D15 / SCK | P0.02 | unconnected |
| 10 | D14 / MISO | P0.03 or P0.28? | unconnected |
| 11 | **D16 / MOSI** | **P1.06** | **RST (net 6)** |
| 12 | **D10 / A10** | **P0.11** | **RDY (net 5)** |

### FFC connector (CON1) pinout

| FFC pin | Signal | Net | Connects to |
|---------|--------|-----|-------------|
| 1 | VDD (3.3V) | VCC (2) | JP2 pin 4, R1 pad 2, R2 pad 2 |
| 2 | SDA | SDA (3) | JP1 pin 11, R1 pad 1 |
| 3 | SCL | SCL (4) | JP1 pin 12, R2 pad 1 |
| 4 | RDY | RDY (5) | JP2 pin 12 |
| 5 | RST | RST (6) | JP2 pin 11 |
| 6 | GND | GND (1) | JP1 pin 3, JP1 pin 4, JP2 pin 2 |

### Resistive nets

| Resistor | Pad 1 net | Pad 2 net |
|----------|-----------|-----------|
| R1 (2.2 kΩ) | SDA (3) | VCC (2) |
| R2 (2.2 kΩ) | SCL (4) | VCC (2) |

---

## 3. Net List

| Net ID | Name | Description |
|--------|------|-------------|
| 0 | (unconnected) | All non-tapped Pro Micro pins |
| 1 | GND | Ground — JP1 pins 3,4; JP2 pin 2; CON1 pin 6 |
| 2 | VCC | 3.3V power — JP2 pin 4; CON1 pin 1; R1 pad 2; R2 pad 2 |
| 3 | SDA | I2C data — JP1 pin 11; CON1 pin 2; R1 pad 1 |
| 4 | SCL | I2C clock — JP1 pin 12; CON1 pin 3; R2 pad 1 |
| 5 | RDY | Trackpad interrupt — JP2 pin 12; CON1 pin 4 |
| 6 | RST | Trackpad reset — JP2 pin 11; CON1 pin 5 |

**Net assignment rule**: All pins NOT listed in the tapped list (D8, D9, D10,
D16, VCC, GND) receive net 0. Net 0 pads are plated through-holes but not
connected to any copper trace.

---

## 4. Routing Requirements

### Tracks to route (hand-routed or interactive router)

| From | To | Width | Notes |
|------|----|-------|-------|
| JP1 pin 11 (D8) | CON1 pin 2 (SDA) | 0.25 mm | Also connects to R1 pad 1 |
| JP1 pin 12 (D9) | CON1 pin 3 (SCL) | 0.25 mm | Also connects to R2 pad 1 |
| JP2 pin 12 (D10) | CON1 pin 4 (RDY) | 0.25 mm | Direct |
| JP2 pin 11 (D16) | CON1 pin 5 (RST) | 0.25 mm | Direct |
| JP2 pin 4 (VCC) | CON1 pin 1 (VDD) | 0.50 mm | Also connects to R1 pad 2, R2 pad 2 |
| JP1 pin 3 (GND) | CON1 pin 6 (GND) | 0.50 mm | Can use either JP1 pin 3 or JP1 pin 4 |

### Routing rules

- Minimum track width: 0.20 mm
- Preferred signal track width: 0.25 mm
- Power track width (VCC, GND): 0.50 mm
- Minimum clearance: 0.20 mm
- All routing on **F.Cu** (top layer) only
- No vias required (single-sided routing is sufficient)
- Tracks must stay within board outline with ≥0.4 mm edge clearance
- Avoid routing directly under the FFC connector body

### SDA pull-up topology

```
JP1 pin 11 ────┬──── R1 pad 1 ──── R1 pad 2 ──── VCC
               │
               └──── CON1 pin 2 (SDA)
```

### SCL pull-up topology

```
JP1 pin 12 ────┬──── R2 pad 1 ──── R2 pad 2 ──── VCC
               │
               └──── CON1 pin 3 (SCL)
```

---

## 5. Layer Stackup

| Layer ID | Name | Type | Content |
|----------|------|------|---------|
| 0 | F.Cu | signal | All copper traces, SMD pads for CON1/R1/R2, PTH pads |
| 1 | F.Mask | user | Solder mask openings |
| 2 | B.Cu | signal | PTH pads only (pass-through) |
| 3 | B.Mask | user | Solder mask openings |
| 5 | F.SilkS | user | Reference designators, pin labels, board title |
| 7 | B.SilkS | user | (optional) "Bottom: Temper" label |
| 13 | F.Paste | user | Solder paste for SMD components |
| 25 | Edge.Cuts | user | Board outline (34×44 mm rectangle) |
| 29 | B.CrtYd | user | Courtyard (optional) |
| 31 | F.CrtYd | user | Courtyard (optional) |
| 33 | B.Fab | user | Fabrication notes (optional) |
| 35 | F.Fab | user | Fabrication notes (optional) |

---

## 6. Custom Footprint — TPS43 FFC Connector

The board must include a project-specific footprint library entry for the
Molex 503480-0600 (or compatible) 6-position 0.5 mm FFC/FPC connector.

**Library**: `temper-tps43-interposer.pretty`
**Footprint name**: `TPS43_FFC_06`

### Pad dimensions

| Parameter | Value |
|-----------|-------|
| Number of pads | 6 |
| Pad type | SMD, rectangular |
| Pad size | 0.30 mm × 1.50 mm |
| Pad pitch | 0.50 mm |
| Pad row X range | -1.25 mm to +1.25 mm (centred) |
| Pad Y position | +1.00 mm from footprint origin |
| Pad layers | F.Cu, F.Paste, F.Mask |

### Mounting holes

Two non-plated through-holes for mechanical alignment, at (-4.50, +0.55) and
(+4.50, +0.55) relative to footprint origin. Hole diameter 0.70 mm.

### Silkscreen / Fab outline

- Body outline on F.SilkS and F.Fab: ~11.0 mm × 3.5 mm
- "Pin 1" marker on F.SilkS at the pad-1 side
- Courtyard on F.CrtYd: ~13.0 mm × 5.5 mm

### Connector orientation

The connector opening faces the **-Y direction** (cable inserts from the pin
header side, bends upward and exits toward +Y toward the thumb cluster).

---

## 7. Silkscreen Labels

| Text | Position (X, Y) | Size | Layer |
|------|-----------------|------|-------|
| "Temper TPS43 Interposer" | (0, +22.0) | 1.0×1.0 mm | F.SilkS |
| "v1.0" | (0, +20.7) | 0.8×0.8 mm | F.SilkS |
| "Top: nice!nano" | (0, -18.5) | 0.9×0.9 mm | F.SilkS |
| "JP1" | (-11.0, -1.27) | 1.0×1.0 mm | F.SilkS |
| "JP2" | (+2.0, -1.27) | 1.0×1.0 mm | F.SilkS |
| "CON1" | (0, +17.7) | 1.0×1.0 mm | F.SilkS |
| "R1" | (-4.6, +22.7) | 1.0×1.0 mm | F.SilkS |
| "R2" | (-4.6, +20.2) | 1.0×1.0 mm | F.SilkS |
| "SDA(2) SCL(3) RDY(4) RST(5)" | (0, +13.2) | 0.8×0.8 mm | F.SilkS |
| "VCC(1)                    GND(6)" | (0, +11.7) | 0.6×0.6 mm | F.SilkS |
| "D8" | (-10.1, -12.70) | 0.6×0.6 mm | F.SilkS |
| "D9" | (-10.1, -15.24) | 0.6×0.6 mm | F.SilkS |
| "D10" | (+10.1, -15.24) | 0.6×0.6 mm | F.SilkS |
| "D16" | (+10.1, -12.70) | 0.6×0.6 mm | F.SilkS |
| "VCC" | (+10.1, +5.08) | 0.6×0.6 mm | F.SilkS |
| "GND" | (-10.1, +7.62) | 0.6×0.6 mm | F.SilkS |

---

## 8. Bill of Materials

| Qty | Designator | Part | Footprint | Supplier |
|-----|-----------|------|-----------|----------|
| 2 | JP1, JP2 | Male pin header, 1×12, 2.54 mm, vertical | `PinHeader_1x12_P2.54mm_Vertical` | Digikey (Molex 0010897122) |
| 1 | CON1 | Molex 503480-0600 FFC connector, 6-pos, 0.5 mm | Custom: `TPS43_FFC_06` | Digikey |
| 2 | R1, R2 | 2.2 kΩ ±5% 0805 thick-film SMD | `R_0805_2012Metric` | Digikey |
| 2 | — | Female socket header, 1×12, 2.54 mm, low-profile (bottom side) | — | Digikey |
| 1 | — | 6-pos 0.5 mm FFC Type A cable, 51 mm | — | Digikey (Assmann AFFC-050-06-051-11) |
| 1 | — | TPS43-201A-S trackpad module | — | Digikey |

---

## 9. Assembly Notes

1. **Bottom side**: Solder two 12-pin female socket headers (low-profile Mill-Max
   or equivalent) on the BOTTOM of the board at JP1 and JP2 positions.
2. **Top side**: Solder two 12-pin male pin headers on the TOP at JP1 and JP2.
3. **Top side**: Solder CON1 (FFC connector) — opening faces downward (-Y),
   cable inserts from below and bends up.
4. **Top side**: Solder R1 and R2 (0805 resistors).
5. **Installation**: Remove nice!nano from Temper, plug interposer into
   Temper's female sockets (interposer bottom), plug nice!nano into
   interposer's male headers (interposer top).
6. Connect TPS43 trackpad to CON1 via 6-pin FFC cable (blue stiffener facing
   up/toward the nice!nano).

---

## 10. ZMK Firmware (Reference)

The interposer uses I2C1 on pins P1.04 (SDA) and P0.09 (SCL) — a separate
I2C bus from the default `&pro_micro_i2c` which is occupied by the nice!view
display's SPI pins (D2/MOSI, D3/SCK).

```dts
&pinctrl {
    i2c1_default: i2c1_default {
        group1 {
            psels = <NRF_PSEL(TWIM_SDA, 1, 4)>,
                    <NRF_PSEL(TWIM_SCL, 0, 9)>;
        };
    };
    i2c1_sleep: i2c1_sleep {
        group1 {
            psels = <NRF_PSEL(TWIM_SDA, 1, 4)>,
                    <NRF_PSEL(TWIM_SCL, 0, 9)>;
            low-power-enable;
        };
    };
};

&i2c1 {
    compatible = "nordic,nrf-twim";
    status = "okay";
    clock-frequency = <I2C_BITRATE_FAST>;
    pinctrl-0 = <&i2c1_default>;
    pinctrl-1 = <&i2c1_sleep>;
    pinctrl-names = "default", "sleep";

    tps43: trackpad@74 {
        compatible = "azoteq,tps43";
        reg = <0x74>;
        rdy-gpios = <&pro_micro 10 GPIO_ACTIVE_HIGH>;
        rst-gpios = <&pro_micro 16 GPIO_ACTIVE_HIGH>;
        enable-power-management;
        scroll;
        two-finger-tap;
        single-tap;
        press-and-hold;
    };
};
```

Kconfig: `CONFIG_INPUT_TPS43=y` `CONFIG_I2C=y` `CONFIG_ZMK_POINTING=y`

Driver module: `stelmakhdigital/zmk_driver_azoteq`
