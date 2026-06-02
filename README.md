# flexispot-esphome

ESPHome component for FlexiSpot standing desks (E7 Pro / E7 Pro Plus / LoctekMotion). Full programmatic control - presets, up/down, height sensor - via the desk's RJ45 serial interface.

Built for the **XIAO ESP32C6** with a bi-directional logic level shifter. Targets the E7 Pro's HS13M-1C0 controller, which has known issues with existing community integrations.

> **Status:** Working. Height sensor, preset commands (Stand/Sit/1/2), and manual Up/Down all tested on E7 Pro Plus + HS13M-1C0 + CB38M2L.

## What's Different

Existing projects ([iMicknl/LoctekMotion_IoT](https://github.com/iMicknl/LoctekMotion_IoT), forks) often report that E7 Pro desks read height but ignore movement commands. Root causes identified through deep research:

1. **Wake timing** - Controller requires PIN 20 held HIGH for 1 full second (not 200ms)
2. **Poll/response protocol** - Controller sends `0x11` polls every ~40ms expecting `0x02` button-state replies. Fire-and-forget commands get ignored.
3. **Voltage levels** - ESP32's 3.3V output may not register as HIGH on the desk's 5V CMOS logic

This component addresses all three with proper wake sequencing, a poll-aware state machine, and a level shifter in the reference design.

## Hardware

### Bill of Materials

| Part | Price | Source |
|------|-------|--------|
| Seeed Studio XIAO ESP32C6 | ~$7 | [Seeed Studio](https://www.seeedstudio.com) |
| SparkFun Logic Level Converter (BOB-12009) | ~$5 | [SparkFun](https://www.sparkfun.com/sparkfun-logic-level-converter-bi-directional.html) / Amazon |
| Cat 6 Ethernet cable (any length) | ~$3 | Any retailer |
| RJ45 pass-through connector | ~$0.10 | Amazon (bulk packs) |

**Tools needed:** Soldering iron, RJ45 crimper, wire strippers

**Total cost:** ~$15

### Wiring

Open [`docs/images/wiring-diagram.html`](docs/images/wiring-diagram.html) in a browser for the full color-coded diagram.

#### Quick Reference

```
XIAO ESP32C6 Level Shifter (BOB-12009) Desk RJ45 (T568B)
───────────── ─────────────────────── ─────────────────
3V3 ───────► LV (ref)
GND ───────► GND (LV) GND (HV) ◄─────── Pin 7 Wht-Brown GND
 HV (ref) ◄─────── Pin 8 Brown +5V
D6 / GPIO16 ───────► LV1 ─── ch1 ── HV1 ───────► Pin 6 Green Commands IN
D7 / GPIO17 ◄─────── LV2 ─── ch2 ── HV2 ◄─────── Pin 5 Wht-Blue Height OUT
D2 / GPIO2 ───────► LV3 ─── ch3 ── HV3 ───────► Pin 4 Blue PIN 20 Wake
5V (deploy) ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ► Pin 8 Brown +5V
```

**Signal directions:** Arrows show data flow. Commands go from ESP to desk (Pin 6). Height data comes from desk to ESP (Pin 5). Wake goes from ESP to desk (Pin 4).

**Unused wires:** Pins 1 (White-Orange), 2 (Orange), 3 (White-Green) - cut short and insulate.

**Power during testing:** Leave the 5V line disconnected; power the XIAO via USB-C. Connect 5V for permanent deployment only.

### Assembly

1. Crimp an RJ45 plug on one end of the Cat 6 cable
2. Cut the other end, strip ~2cm of jacket, expose the 5 needed wires
3. Solder the 5 desk wires to the HV side of the level shifter (see table below)
4. Solder 5 short wires from the XIAO's castellated pads to the LV side
5. Connect XIAO 3V3 to the LV reference pin

| Level Shifter Pad | Desk Wire (HV side) | XIAO Pad (LV side) |
|--------------------|---------------------|---------------------|
| HV / LV (ref) | Pin 8 - Brown (+5V) | 3V3 |
| GND | Pin 7 - White-Brown | GND |
| HV1 / LV1 | Pin 6 - Green | D6 (GPIO16, TX) |
| HV2 / LV2 | Pin 5 - White-Blue | D7 (GPIO17, RX) |
| HV3 / LV3 | Pin 4 - Blue | D2 (GPIO2) |

## Installation

### 1. Flash ESPHome

```bash
pip install esphome
cd esphome/
cp secrets.yaml.example secrets.yaml
# Edit secrets.yaml with your WiFi credentials
esphome compile office-desk.yaml
esphome upload office-desk.yaml --device COM5  # or /dev/ttyACM0
```

### 2. Connect to Home Assistant

The device auto-discovers via mDNS. Go to **Settings > Devices > Add Integration > ESPHome** and enter the encryption key from your `secrets.yaml`.

### 3. Plug In

Insert the RJ45 cable into the desk control box's **spare port** (not the one the keypad uses).

## Configuration

### Height Unit

The height sensor reads the display digits directly, so it reports whatever unit your desk is set to. The component defaults to `cm`. If your desk displays inches, override it in your YAML:

```yaml
sensor:
  - platform: flexispot_desk
    name: "Desk Height"
    unit_of_measurement: "in"  # for desks set to inches
```

### Available Entities

| Entity | Type | Description |
|--------|------|-------------|
| Desk Height | Sensor | Current height from the 7-segment display |
| Stand | Button | Move to standing preset |
| Sit | Button | Move to sitting preset |
| Preset 1 | Button | Move to memory preset 1 |
| Preset 2 | Button | Move to memory preset 2 |
| Up | Button | Nudge up (~5 seconds) |
| Down | Button | Nudge down (~5 seconds) |
| Memory | Button | Enter memory/save mode |

Up/Down are short nudges, not continuous hold. The physical keypad always works for manual control and can override any programmatic command.

## Example Use Cases

- **Health break enforcement** - pair with a timer automation to auto-raise the desk after prolonged sitting
- **Scene integration** - raise to standing when "work mode" activates, lower for "meeting mode"
- **Sit/stand tracking** - log height over time to track daily standing ratio

## Compatibility

**Tested on:**
- FlexiSpot E7 Pro Plus (HS13M-1C0 keypad, CB38M2L control box)

**Should work with:**
- FlexiSpot E7, E7 Pro, E7Q, E5, E6, E8 and other LoctekMotion-based desks
- Any desk with the standard `9B ... 9D` packet protocol on 9600 baud RJ45

**ESP32 boards:** Designed for XIAO ESP32C6 but adaptable to any ESP32 variant. Adjust pin assignments in the YAML config. If using a 5V-tolerant board (some ESP32 DevKits), the level shifter may be optional, though it's recommended for reliability.

## How It Works

The component implements a 5-state machine that emulates a keypad on the desk's spare RJ45 port:

1. **BOOT** - 10s delay for controller startup, then sends M command to get initial height
2. **IDLE** - Sends periodic "no buttons pressed" packets to maintain bus presence
3. **WAKING_LOW** - Pulls PIN 20 LOW for 100ms to create a rising edge
4. **WAKING_HIGH** - Holds PIN 20 HIGH for 1.1s (required by E7 Pro before accepting commands)
5. **ACTIVE** - Responds to controller's `0x11` polls with button-state packets encoding the requested command

Commands are only sent as responses to controller polls, not fire-and-forget. This matches the keypad scan conversation the controller expects. The physical keypad on the primary port continues to work normally.

## Protocol Reference

The desk uses a proprietary UART protocol at 9600 baud (8N1) over RJ45.

### Packet Format

```
[0x9B] [length] [type] [payload...] [CRC16] [0x9D]
```

### Packet Types (observed)

| Type | Direction | Purpose |
|------|-----------|---------|
| `0x11` | Controller -> Keypad | Status poll (~40ms interval) |
| `0x12` | Controller -> Keypad | Height display data (3 bytes, 7-segment encoded) |
| `0x02` | Keypad -> Controller | Button state response |

### Command Bytes

| Command | Full Packet |
|---------|-------------|
| No buttons | `9B 06 02 00 00 6C A1 9D` |
| Up | `9B 06 02 01 00 FC A0 9D` |
| Down | `9B 06 02 02 00 0C A0 9D` |
| Preset 1 | `9B 06 02 04 00 AC A3 9D` |
| Preset 2 | `9B 06 02 08 00 AC A6 9D` |
| Stand | `9B 06 02 10 00 AC AC 9D` |
| Sit | `9B 06 02 00 01 AC 60 9D` |
| Memory (M) | `9B 06 02 20 00 AC B8 9D` |

## Project Structure

```
flexispot-esphome/
├── components/
│   └── flexispot_desk/       # ESPHome external component
│       ├── __init__.py        # Component registration
│       ├── sensor.py          # Height sensor platform
│       ├── button.py          # Button platform (7 commands)
│       ├── flexispot_desk.h   # State machine, packets, constants
│       └── flexispot_desk.cpp # Implementation
├── esphome/
│   ├── office-desk.yaml       # Example config (XIAO ESP32C6)
│   ├── office-desk-debug.yaml # UART debug config (raw hex logging)
│   └── secrets.yaml.example
├── docs/
│   └── images/
│       └── wiring-diagram.html
└── README.md
```

## References

- [iMicknl/LoctekMotion_IoT](https://github.com/iMicknl/LoctekMotion_IoT) - Original reverse engineering project
- [NelsonBrandao/flexispot-e7-esphome](https://github.com/NelsonBrandao/flexispot-e7-esphome) - 3-state polling machine
- [takahashikenichi/flexispot-e7pro-nesson1](https://github.com/takahashikenichi/flexispot-e7pro-nesson1) - Confirmed E7 Pro + HS13M-1C0 control
- [Ideal Reality E7 Pro Analysis](https://ideal-reality.com) - Poll/response protocol documentation
- [PR #139](https://github.com/iMicknl/LoctekMotion_IoT/pull/139) - Wake-before-action fix for newer desks

## License

MIT
