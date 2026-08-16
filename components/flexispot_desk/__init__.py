import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.components import uart
from esphome.const import CONF_ID

CODEOWNERS = ["@dimitri-vs"]
DEPENDENCIES = ["uart"]
AUTO_LOAD = ["sensor", "button", "binary_sensor"]
MULTI_CONF = False

CONF_FLEXISPOT_DESK_ID = "flexispot_desk_id"
CONF_WAKE_PIN = "wake_pin"
CONF_NUDGE_DURATION = "nudge_duration"
CONF_BOOT_MEMORY_COMMAND = "boot_memory_command"
CONF_ANSWER_ALL_POLLS = "answer_all_polls"
CONF_PRESET_GUARD = "preset_guard"
CONF_HEIGHT_VALID_TIMEOUT = "height_valid_timeout"
CONF_PRESET_HOLD = "preset_hold"

flexispot_ns = cg.esphome_ns.namespace("flexispot_desk")
FlexiSpotDesk = flexispot_ns.class_(
    "FlexiSpotDesk", cg.Component, uart.UARTDevice
)

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(FlexiSpotDesk),
            cv.Required(CONF_WAKE_PIN): pins.gpio_output_pin_schema,
            cv.Optional(
                CONF_NUDGE_DURATION, default="5000ms"
            ): cv.positive_time_period_milliseconds,
            cv.Optional(
                CONF_PRESET_HOLD, default="1000ms"
            ): cv.positive_time_period_milliseconds,
            cv.Optional(CONF_BOOT_MEMORY_COMMAND, default=True): cv.boolean,
            cv.Optional(CONF_ANSWER_ALL_POLLS, default=False): cv.boolean,
            cv.Optional(
                CONF_PRESET_GUARD, default="0ms"
            ): cv.positive_time_period_milliseconds,
            cv.Optional(
                CONF_HEIGHT_VALID_TIMEOUT, default="0ms"
            ): cv.positive_time_period_milliseconds,
        }
    )
    .extend(uart.UART_DEVICE_SCHEMA)
    .extend(cv.COMPONENT_SCHEMA)
)

FINAL_VALIDATE_SCHEMA = uart.final_validate_device_schema(
    "flexispot_desk",
    baud_rate=9600,
    require_tx=True,
    require_rx=True,
    data_bits=8,
    parity=None,
    stop_bits=1,
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    wake_pin = await cg.gpio_pin_expression(config[CONF_WAKE_PIN])
    cg.add(var.set_wake_pin(wake_pin))

    cg.add(var.set_nudge_duration(config[CONF_NUDGE_DURATION].total_milliseconds))
    cg.add(var.set_preset_hold(config[CONF_PRESET_HOLD].total_milliseconds))
    cg.add(var.set_boot_memory_command(config[CONF_BOOT_MEMORY_COMMAND]))
    cg.add(var.set_answer_all_polls(config[CONF_ANSWER_ALL_POLLS]))
    cg.add(var.set_preset_guard(config[CONF_PRESET_GUARD].total_milliseconds))
    cg.add(
        var.set_height_valid_timeout(
            config[CONF_HEIGHT_VALID_TIMEOUT].total_milliseconds
        )
    )
