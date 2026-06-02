import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import button
from . import flexispot_ns, FlexiSpotDesk, CONF_FLEXISPOT_DESK_ID

CONF_STAND = "stand"
CONF_SIT = "sit"
CONF_PRESET_1 = "preset_1"
CONF_PRESET_2 = "preset_2"
CONF_UP = "up"
CONF_DOWN = "down"
CONF_MEMORY = "memory"

DeskButton = flexispot_ns.class_("DeskButton", button.Button, cg.Component)

BUTTON_SCHEMA = button.button_schema(DeskButton).extend(
    {
        cv.GenerateID(CONF_FLEXISPOT_DESK_ID): cv.use_id(FlexiSpotDesk),
    }
)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_FLEXISPOT_DESK_ID): cv.use_id(FlexiSpotDesk),
        cv.Optional(CONF_STAND): BUTTON_SCHEMA,
        cv.Optional(CONF_SIT): BUTTON_SCHEMA,
        cv.Optional(CONF_PRESET_1): BUTTON_SCHEMA,
        cv.Optional(CONF_PRESET_2): BUTTON_SCHEMA,
        cv.Optional(CONF_UP): BUTTON_SCHEMA,
        cv.Optional(CONF_DOWN): BUTTON_SCHEMA,
        cv.Optional(CONF_MEMORY): BUTTON_SCHEMA,
    }
)

BUTTON_TYPES = {
    CONF_STAND: 0,
    CONF_SIT: 1,
    CONF_PRESET_1: 2,
    CONF_PRESET_2: 3,
    CONF_UP: 4,
    CONF_DOWN: 5,
    CONF_MEMORY: 6,
}


async def to_code(config):
    parent = await cg.get_variable(config[CONF_FLEXISPOT_DESK_ID])

    for button_type, command_index in BUTTON_TYPES.items():
        if button_type in config:
            conf = config[button_type]
            var = await button.new_button(conf)
            await cg.register_component(var, conf)
            cg.add(var.set_parent(parent))
            cg.add(var.set_command_index(command_index))
