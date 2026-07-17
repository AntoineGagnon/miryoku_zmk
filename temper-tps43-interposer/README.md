# Temper TPS43 Interposer PCB

PCB that sits between the nice!nano and Temper keyboard PCB, tapping
4 unused Pro Micro pins to connect an Azoteq TPS43 trackpad.

## Pin mapping

| Pro Micro label | nRF52840 | TPS43 signal | FFC pin |
|---|---|---|---|
| D8 | P1.04 | SDA (I2C data) | 2 |
| D9 | P0.09 | SCL (I2C clock) | 3 |
| D10 | P0.11 | RDY (interrupt) | 4 |
| D16 | P1.06 | RST (reset) | 5 |
| VCC | 3.3V | VDD | 1 |
| GND | GND | GND | 6 |

All 24 Pro Micro pins are passed through to the Temper PCB below.

## BOM

| Qty | Part | Supplier | ~Cost |
|-----|------|----------|-------|
| 2 | 12-pin female socket header (2.54mm, low profile) | LCSC C16053 | $1 |
| 2 | 12-pin male pin header (2.54mm) | LCSC C35890 | $1 |
| 1 | Molex 503480-0600 FFC connector | LCSC C293675 | $1 |
| 1 | 6-pin 0.5mm FFC cable (type A, 10cm) | LCSC C209187 | $1 |
| 2 | 2.2kΩ 0805 SMD resistor | LCSC C17534 | $0.10 |
| 1 | Azoteq TPS43-201A-B trackpad | Mouser / AliExpress | $15-25 |

## Assembly

1. Solder **female socket headers** to the **BOTTOM** of the interposer
   (the side facing the Temper PCB)
2. Solder **male pin headers** to the **TOP** of the interposer
   (the side facing the nice!nano)
3. Solder 0805 resistors to the TOP
4. Solder FFC connector to the TOP (opening faces upward, toward thumb keys)
5. Unplug nice!nano from Temper
6. Plug interposer into Temper's sockets
7. Plug nice!nano into interposer's male headers
8. Connect TPS43 via FFC cable (blue stiffener side up)

## PCB ordering

Upload `temper-tps43-interposer.kicad_pcb` to JLCPCB or PCBWay:
- Layers: 2
- Thickness: 1.0mm
- Surface finish: ENIG (recommended for FFC connector)
- Copper weight: 1oz

## ZMK firmware changes

After installing the interposer and TPS43 hardware, add these files to your
ZMK config (miryoku_zmk repo):

### `config/temper_right.conf`
```
CONFIG_INPUT_TPS43=y
CONFIG_I2C=y
CONFIG_ZMK_POINTING=y
```

### `config/temper_right.overlay`
```dts
#include "temper.dtsi"

&default_transform {
    col-offset = <5>;
};

&kscan0 {
    col-gpios
        = <&pro_micro 15 GPIO_ACTIVE_HIGH>
        , <&pro_micro 18 GPIO_ACTIVE_HIGH>
        , <&pro_micro 19 GPIO_ACTIVE_HIGH>
        , <&pro_micro 20 GPIO_ACTIVE_HIGH>
        , <&pro_micro 21 GPIO_ACTIVE_HIGH>
        ;
};

/* I2C on D8(SDA) / D9(SCL) - separate bus from the nice!view SPI */
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

/ {
    split_inputs {
        #address-cells = <1>;
        #size-cells = <0>;
        tps43_split: tps43_split@0 {
            compatible = "zmk,input-split";
            reg = <0>;
            device = <&tps43>;
        };
    };
};
```

### Build workflow
Add `stelmakhdigital/zmk_driver_azoteq` as an external module in your
GitHub Actions build workflow's `modules` matrix variable.

### Central (left) side
On the left `.overlay`, add an input listener referencing the split device:
```dts
/ {
    split_inputs {
        #address-cells = <1>;
        #size-cells = <0>;
        tps43_split: tps43_split@0 {
            compatible = "zmk,input-split";
            reg = <0>;
        };
    };
    tps43_listener: tps43_listener {
        compatible = "zmk,input-listener";
        device = <&tps43_split>;
        status = "okay";
    };
};
```
