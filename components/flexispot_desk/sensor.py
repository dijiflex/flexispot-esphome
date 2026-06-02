import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import (
    DEVICE_CLASS_DISTANCE,
    ICON_ARROW_EXPAND_VERTICAL,
    STATE_CLASS_MEASUREMENT,
)
from . import flexispot_ns, FlexiSpotDesk, CONF_FLEXISPOT_DESK_ID

DeskHeightSensor = flexispot_ns.class_(
    "DeskHeightSensor", sensor.Sensor, cg.Component
)

CONFIG_SCHEMA = sensor.sensor_schema(
    DeskHeightSensor,
    unit_of_measurement="cm",
    icon=ICON_ARROW_EXPAND_VERTICAL,
    accuracy_decimals=1,
    state_class=STATE_CLASS_MEASUREMENT,
    device_class=DEVICE_CLASS_DISTANCE,
).extend(
    {
        cv.GenerateID(CONF_FLEXISPOT_DESK_ID): cv.use_id(FlexiSpotDesk),
    }
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_FLEXISPOT_DESK_ID])
    var = await sensor.new_sensor(config)
    await cg.register_component(var, config)
    cg.add(parent.set_height_sensor(var))
