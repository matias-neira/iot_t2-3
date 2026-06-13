#include <stdio.h>
#include <string.h>
//#include <unistd.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
//#include <endian.h>
#include <math.h>
#include <inttypes.h>

#define ACCEL_RANGE_G 16.0f
#define ATTENUATION 0.70f /* ejes secundarios = 70 % del principal */
#define TEMP_MIN 20.0f
#define TEMP_MAX 30.0f

typedef struct {uint32_t timestamp; float ax, ay, az; } accel_sample_t;
typedef struct {uint32_t timestamp; float temp;} temp_sample_t;

accel_sample_t simulate_accel(void) {
    /* Eje principal: sinusoide + ruido uniforme */
    static float phase = 0.0f;
    phase += 0.01f; /* avance de fase por muestra a 1000 Hz */
    float main_val = ACCEL_RANGE_G * sinf(phase)
                    + ((float)rand() / RAND_MAX - 0.5f) * 1.0f;
    accel_sample_t s = {
        .timestamp = esp_timer_get_time() / 1000,
        .ax = main_val,
        .ay = main_val * ATTENUATION + ((float)rand()/RAND_MAX - 0.5f)*0.5f,
        .az = main_val * ATTENUATION + ((float)rand()/RAND_MAX - 0.5f)*0.5f,
    };
    return s;
}

temp_sample_t simulate_temperature(void) {
    static float temp = 25.0f;
    float delta = ((float)rand() / RAND_MAX - 0.5f) * 0.4f;
    temp += delta;
    if (temp < TEMP_MIN) temp = TEMP_MIN;
    if (temp > TEMP_MAX) temp = TEMP_MAX;
    
    temp_sample_t s = {
      .timestamp = esp_timer_get_time() / 1000,
      .temp = temp,
    };
    return s;
}

void app_main(void)
{

}
