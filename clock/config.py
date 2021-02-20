
# Sets brightness level. Default: 100. Range: 1..100
matrix_brightness = 100
# Daisy-chained boards. Default: 1.
matrix_chain_length = 1
# Panel columns. Typically 32 or 64. (Default: 32)
matrix_cols = 64
# Don't use hardware pin-pulse generation
matrix_disable_hardware_pulsing = True
# Don't drop privileges from 'root' after initializing the hardware.
matrix_drop_privileges = True
# Slow down writing to GPIO. Range: 0..4. Default: 1
matrix_gpio_slowdown = 2
# Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm
matrix_hardware_mapping = 'adafruit-hat'
# Switch if your matrix has led colors swapped. Default: RGB
matrix_led_rgb_sequence = 'RGB'
# Multiplexing type: 0=direct; 1=strip; 2=checker; 3=spiral; 4=ZStripe; 5=ZnMirrorZStripe; 6=coreman; 7=Kaler2Scan; 8=ZStripeUneven... (Default: 0)
matrix_multiplexing = 0
# Needed to initialize special panels. Supported: 'FM6126A'
matrix_panel_type = ''
# For Plus-models or RPi2: parallel chains. 1..3. Default: 1
matrix_parallel = 1
# Apply pixel mappers. e.g "Rotate:90"
matrix_pixel_mapper_config = ''
# Bits used for PWM. Something between 1..11. Default: 11
matrix_pwm_bits = 11
# Base time-unit for the on-time in the lowest significant bit in nanoseconds. Default: 130
matrix_pwm_lsb_nanoseconds = 130
# 0 = default; 1=AB-addressed panels; 2=row direct; 3=ABC-addressed panels; 4 = ABC Shift + DE direct
matrix_row_address_type = 0
# Display rows. 16 for 16x32, 32 for 32x32. Default: 32
matrix_rows = 32
# Progressive or interlaced scan. 0 Progressive, 1 Interlaced (default)
matrix_scan_mode = 1
# Shows the current refresh rate of the LED panel
matrix_show_refresh_rate = 1

