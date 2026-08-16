import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import binary_sensor
from esphome.const import ENTITY_CATEGORY_DIAGNOSTIC

from . import CONF_FLEXISPOT_DESK_ID, FlexiSpotDesk, flexispot_ns

DeskHeightValidBinarySensor = flexispot_ns.class_(
    "DeskHeightValidBinarySensor", binary_sensor.BinarySensor, cg.Component
)

CONFIG_SCHEMA = binary_sensor.binary_sensor_schema(
    DeskHeightValidBinarySensor,
    entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    icon="mdi:eye-check-outline",
).extend(
    {
        cv.GenerateID(CONF_FLEXISPOT_DESK_ID): cv.use_id(FlexiSpotDesk),
    }
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_FLEXISPOT_DESK_ID])
    var = await binary_sensor.new_binary_sensor(config)
    await cg.register_component(var, config)
    cg.add(parent.set_height_valid_sensor(var))
