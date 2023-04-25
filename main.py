import time
import numpy as np
import brainflow
import serial
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

# Set up the OpenBCI Cyton board
params = BrainFlowInputParams()
#params.serial_port = 'COM_PORT'  # Replace with the appropriate COM port for your device
board_id = BoardIds.SYNTHETIC_BOARD
BoardShim.enable_dev_board_logger()
board = BoardShim(board_id, params)
board.prepare_session()
board.start_stream()

# Set up the Arduino
#arduino_serial = serial.Serial('COM_PORT', 9600)  # Replace with the appropriate COM port for your Arduino
#time.sleep(2)  # Give the Arduino time to initialize

# Define the EEG channels and LED pins
eeg_channels = [0, 1, 2, 3, 4, 5, 6, 7]
led_pins = [3, 5, 6, 9, 10, 11, 12, 13]  # PWM pins for the LEDs

try:
    while True:
        # Get the EEG data and calculate the absolute values
        data = board.get_board_data()
        eeg_data = data[eeg_channels]
        eeg_absolute = np.abs(eeg_data)

        # Normalize the EEG data to the range 0-255 for each channel separately
        eeg_normalized = []
        for channel_data in eeg_absolute:
            if channel_data.size > 0 and not np.isnan(channel_data).any():
                normalized_data = np.interp(channel_data, (channel_data.min(), channel_data.max()), (0, 255))
                eeg_normalized.append(normalized_data)

        # Send the brightness values to the Arduino
        if len(eeg_normalized) == len(led_pins):
            for i, pin in enumerate(led_pins):
                brightness = int(eeg_normalized[i][-1])  # Get the latest value in the normalized data array
                #arduino_serial.write(f'{pin}:{brightness}\n'.encode())
                print(f'{pin}:{brightness}\n'.encode())

        time.sleep(0.1)

except KeyboardInterrupt:
    # Stop the stream and clean up
    board.stop_stream()
    board.release_session()
    #arduino_serial.close()