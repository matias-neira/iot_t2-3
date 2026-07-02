file(GLOB_RECURSE proto "proto/*.c")

idf_component_register(
    SRCS
        "esp32-sub.c"
        "${proto}"
    
    INCLUDE_DIRS
        "."
        "proto"
    
    PRIV_REQUIRES
        esp_wifi
        nvs_flash
        mqtt
        esp_netif
)
