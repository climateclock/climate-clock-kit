
# Sets brightness level. Default: 100. Range: 1..100
portable_pi_brightness = 100

# Daisy-chained boards. Default: 1.
portable_pi_chain_length = 3

# Panel columns. Typically 32 or 64. (Default: 32)
portable_pi_cols = 64

# Don't use hardware pin-pulse generation
portable_pi_disable_hardware_pulsing = True

# Don't drop privileges from 'root' after initializing the hardware.
portable_pi_drop_privileges = True

# Slow down writing to GPIO. Range: 0..4. Default: 1
portable_pi_gpio_slowdown = 2

# Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm
portable_pi_hardware_mapping = 'adafruit-hat'

# Switch if your matrix has led colors swapped. Default: RGB
portable_pi_led_rgb_sequence = 'RGB'

# Multiplexing type: 0=direct; 1=strip; 2=checker; 3=spiral; 4=ZStripe; 5=ZnMirrorZStripe; 6=coreman; 7=Kaler2Scan; 8=ZStripeUneven... (Default: 0)
portable_pi_multiplexing = 0

# Needed to initialize special panels. Supported: 'FM6126A'
portable_pi_panel_type = ''

# For Plus-models or RPi2: parallel chains. 1..3. Default: 1
portable_pi_parallel = 1

# Apply pixel mappers. e.g "Rotate:90"
portable_pi_pixel_mapper_config = ''

# Bits used for PWM. Something between 1..11. Default: 11
portable_pi_pwm_bits = 11

# Base time-unit for the on-time in the lowest significant bit in nanoseconds. Default: 130
portable_pi_pwm_lsb_nanoseconds = 130

# 0 = default; 1=AB-addressed panels; 2=row direct; 3=ABC-addressed panels; 4 = ABC Shift + DE direct
portable_pi_row_address_type = 0

# Display rows. 16 for 16x32, 32 for 32x32. Default: 32
portable_pi_rows = 32

# Progressive or interlaced scan. 0 Progressive, 1 Interlaced (default)
portable_pi_scan_mode = 1

# Shows the current refresh rate of the LED panel
portable_pi_show_refresh_rate = 1

