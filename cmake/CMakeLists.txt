cmake_minimum_required(VERSION 3.22)

# Project name — matches the GitHub repo name
project([project-name] C CXX ASM)

# ── Toolchain ─────────────────────────────────────────────────────────────────
# Set via toolchain file: cmake -DCMAKE_TOOLCHAIN_FILE=cmake/arm-none-eabi.cmake
# Uncomment the line below if not using a separate toolchain file:
# set(CMAKE_C_COMPILER   arm-none-eabi-gcc)
# set(CMAKE_CXX_COMPILER arm-none-eabi-g++)
# set(CMAKE_ASM_COMPILER arm-none-eabi-gcc)

set(CMAKE_C_STANDARD   11)
set(CMAKE_CXX_STANDARD 17)

# ── Target MCU flags ──────────────────────────────────────────────────────────
# Set these to match your MCU family. Examples:
#   STM32L476: -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=hard
#   STM32F103: -mcpu=cortex-m3
#   RP2040:    handled by pico-sdk

set(MCU_FLAGS
    # -mcpu=cortex-m4
    # -mthumb
    # -mfpu=fpv4-sp-d16
    # -mfloat-abi=hard
)

# ── Build flags ───────────────────────────────────────────────────────────────
add_compile_options(
    ${MCU_FLAGS}
    -Wall
    -Wextra
    -fdata-sections
    -ffunction-sections
    # -DWDG_ENABLE
    # -DNDEBUG          # production build
)

add_link_options(
    ${MCU_FLAGS}
    -Wl,--gc-sections
    # -T${CMAKE_SOURCE_DIR}/linker/[target].ld    # linker script path
)

# ── Source files ──────────────────────────────────────────────────────────────
file(GLOB_RECURSE SOURCES
    src/*.c
    src/*.cpp
)

# ── Include directories ───────────────────────────────────────────────────────
include_directories(
    include/
    # Add HAL/CMSIS include paths here, e.g.:
    # Drivers/CMSIS/Include
    # Drivers/STM32L4xx_HAL_Driver/Inc
)

# ── Firmware binary ───────────────────────────────────────────────────────────
add_executable(${PROJECT_NAME}.elf ${SOURCES})

# Generate .hex and .bin from .elf
add_custom_command(TARGET ${PROJECT_NAME}.elf POST_BUILD
    COMMAND arm-none-eabi-objcopy -O ihex   $<TARGET_FILE:${PROJECT_NAME}.elf> ${PROJECT_NAME}.hex
    COMMAND arm-none-eabi-objcopy -O binary $<TARGET_FILE:${PROJECT_NAME}.elf> ${PROJECT_NAME}.bin
    COMMENT "Generating ${PROJECT_NAME}.hex and ${PROJECT_NAME}.bin"
)

# Print size after build
add_custom_command(TARGET ${PROJECT_NAME}.elf POST_BUILD
    COMMAND arm-none-eabi-size $<TARGET_FILE:${PROJECT_NAME}.elf>
)
