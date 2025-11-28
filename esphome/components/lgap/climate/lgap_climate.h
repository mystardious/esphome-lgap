#include "../lgap.h"
#include "../lgap_device.h"

#include "esphome/components/climate/climate.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/number/number.h"
#include "esphome/components/button/button.h"

namespace esphome
{
  namespace lgap
  {
    class LGAPHVACClimate;

    // Timer duration number with automatic start/cancel
    class TimerDurationNumber : public number::Number
    {
      public:
        void set_parent(LGAPHVACClimate *parent) { this->parent_ = parent; }
        void control(float value) override;
      protected:
        LGAPHVACClimate *parent_{nullptr};
    };

    class LGAPHVACClimate : public LGAPDevice, public climate::Climate
    {
      public:
        void dump_config() override;       
        void setup() override;
        void set_temperature_publish_time(int temperature_publish_time) { this->temperature_publish_time_ = temperature_publish_time; }
        void set_pipe_in_sensor(sensor::Sensor *sensor) { this->pipe_in_sensor_ = sensor; }
        void set_pipe_out_sensor(sensor::Sensor *sensor) { this->pipe_out_sensor_ = sensor; }
        void set_error_code_sensor(sensor::Sensor *sensor) { this->error_code_sensor_ = sensor; }
        
        // Timer control
        void set_timer_duration_number(TimerDurationNumber *number) { 
          this->timer_duration_number_ = number; 
          number->set_parent(this);
        }
        void set_timer_remaining_sensor(sensor::Sensor *sensor) { this->timer_remaining_sensor_ = sensor; }
        void start_timer(float minutes);
        void cancel_timer();
        void loop() override;
        void set_zone_active_load_sensor(sensor::Sensor *sensor) { this->zone_active_load_sensor_ = sensor; }
        void set_zone_power_state_sensor(sensor::Sensor *sensor) { this->zone_power_state_sensor_ = sensor; }
        void set_zone_design_load_sensor(sensor::Sensor *sensor) { this->zone_design_load_sensor_ = sensor; }
        void set_odu_total_load_sensor(sensor::Sensor *sensor) { this->odu_total_load_sensor_ = sensor; }
        virtual esphome::climate::ClimateTraits traits() override;
        virtual void control(const esphome::climate::ClimateCall &call) override;
        


      protected:
        uint32_t temperature_publish_time_{300000};
        uint32_t temperature_last_publish_time_{0};

        uint8_t power_state_{0};
        uint8_t swing_{0};
        uint8_t mode_{0};
        uint8_t fan_speed_{0};

        float current_temperature_{0.0f};
        float target_temperature_{0.0f};
        
        // Timer state
        bool timer_active_{false};
        uint32_t timer_end_time_{0};  // millis() when timer expires
        uint32_t timer_last_update_{0};  // Last time we published remaining time
        
        sensor::Sensor *pipe_in_sensor_{nullptr};
        sensor::Sensor *pipe_out_sensor_{nullptr};
        sensor::Sensor *error_code_sensor_{nullptr};            // Byte 5 - Error code (0=OK, others=service codes)
        sensor::Sensor *zone_active_load_sensor_{nullptr};      // Byte 11 - LonWorks nvoLoadEstimate
        sensor::Sensor *zone_power_state_sensor_{nullptr};      // Byte 12 - LonWorks nvoOnOff
        sensor::Sensor *zone_design_load_sensor_{nullptr};      // Byte 13 - LonWorks nciRatedCapacity
        sensor::Sensor *odu_total_load_sensor_{nullptr};        // Byte 14 - LonWorks nvoThermalLoad
        
        // Timer components
        TimerDurationNumber *timer_duration_number_{nullptr};
        sensor::Sensor *timer_remaining_sensor_{nullptr};

        //todo: evaluate whether to use esppreferenceobject or not
        // ESPPreferenceObject power_state_preference_; //uint8_t
        // ESPPreferenceObject swing_preference_; //uint8_t
        // ESPPreferenceObject mode_preference_; //uint8_t
        // ESPPreferenceObject fan_speed_preference_; //uint8_t

        // optional<float> target_temperature_;
        // optional<float> current_temperature_;

        void handle_on_message_received(std::vector<uint8_t> &message) override;
        void handle_generate_lgap_request(std::vector<uint8_t> &message, uint8_t &request_id) override;
      };

  } // namespace lgap
} // namespace esphome