import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import climate, sensor
from esphome.const import (
    CONF_ID,
    CONF_NAME,
    UNIT_KILOWATT,
    DEVICE_CLASS_POWER,
    STATE_CLASS_MEASUREMENT,
)
from .. import (
    lgap_ns,
    LGAP,
    CONF_LGAP_ID
)

DEPENDENCIES = ["lgap"]
CODEOWNERS = ["@jourdant"]

LGAP_HVAC_Climate = lgap_ns.class_("LGAPHVACClimate", cg.Component, climate.Climate)

CONF_ZONE_NUMBER = "zone"
CONF_TEMPERATURE_PUBISH_TIME = "temperature_publish_time"
CONF_POWER_SENSOR = "power_sensor"
CONF_LOAD_BYTE_SENSOR = "load_byte_sensor"

CONFIG_SCHEMA = climate.CLIMATE_SCHEMA.extend(
    {
        cv.GenerateID(): cv.declare_id(LGAP_HVAC_Climate),
        cv.GenerateID(CONF_LGAP_ID): cv.use_id(LGAP),
        cv.Optional(CONF_ZONE_NUMBER, default=0): cv.All(cv.int_),
        cv.Optional(CONF_TEMPERATURE_PUBISH_TIME, default="300000ms"): cv.positive_time_period_milliseconds,
        cv.Optional(CONF_POWER_SENSOR): sensor.sensor_schema(
            unit_of_measurement=UNIT_KILOWATT,
            accuracy_decimals=2,
            device_class=DEVICE_CLASS_POWER,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        cv.Optional(CONF_LOAD_BYTE_SENSOR): sensor.sensor_schema(
            accuracy_decimals=0,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    #register against climate to make it available in home assistant
    await climate.register_climate(var, config)

    #retrieve parent lgap component and register climate device
    lgap = await cg.get_variable(config[CONF_LGAP_ID])
    cg.add(lgap.register_device(var))
    cg.add(var.set_parent(lgap))

    #set properties of the climate component
    cg.add(var.set_zone_number(config[CONF_ZONE_NUMBER]))
    cg.add(var.set_temperature_publish_time(config[CONF_TEMPERATURE_PUBISH_TIME]))
    
    #set power sensor - auto-generate name if not explicitly configured
    if CONF_POWER_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_POWER_SENSOR])
        cg.add(var.set_power_sensor(sens))
    else:
        # Auto-generate power sensor with name based on climate entity
        from esphome.core import ID
        power_id = ID(f"{config[CONF_ID].id}_power", is_manual=False, type=sensor.Sensor)
        power_config = {
            "unit_of_measurement": UNIT_KILOWATT,
            "accuracy_decimals": 2,
            "device_class": DEVICE_CLASS_POWER,
            "state_class": STATE_CLASS_MEASUREMENT,
        }
        # If climate has a name, use it to generate the sensor name
        if CONF_NAME in config:
            power_config[CONF_NAME] = f"{config[CONF_NAME]} Power"
        
        sens = cg.new_Pvariable(power_id)
        await sensor.register_sensor(sens, power_config)
        cg.add(var.set_power_sensor(sens))
    
    #set load byte sensor - auto-generate name if not explicitly configured
    if CONF_LOAD_BYTE_SENSOR in config:
        sens = await sensor.new_sensor(config[CONF_LOAD_BYTE_SENSOR])
        cg.add(var.set_load_byte_sensor(sens))
    else:
        # Auto-generate load byte sensor with name based on climate entity
        from esphome.core import ID
        load_byte_id = ID(f"{config[CONF_ID].id}_load_byte", is_manual=False, type=sensor.Sensor)
        load_byte_config = {
            "accuracy_decimals": 0,
            "state_class": STATE_CLASS_MEASUREMENT,
        }
        # If climate has a name, use it to generate the sensor name
        if CONF_NAME in config:
            load_byte_config[CONF_NAME] = f"{config[CONF_NAME]} Load Byte"
        
        sens = cg.new_Pvariable(load_byte_id)
        await sensor.register_sensor(sens, load_byte_config)
        cg.add(var.set_load_byte_sensor(sens))
    
