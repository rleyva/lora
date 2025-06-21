"""
 _           _____         _____      _             
| |         |  __ \       |  __ \    | |            
| |     ___ | |__) |__ _  | |__) |___| | __ _ _   _ 
| |    / _ \|  _  // _` | |  _  // _ \ |/ _` | | | |
| |___| (_) | | \ \ (_| | | | \ \  __/ | (_| | |_| |
|______\___/|_|  \_\__,_| |_|  \_\___|_|\__,_|\__, |
                                               __/ |
                                              |___/ 

Hardware
--------
The Adafruit LoRa bonnet consists of the following bits of hardware:
    - RFM96W LoRa radio (915 mhz)
    - SSD1306 OLED controller
    - Three press-buttons

We intend to run this on the following compute:
    - Raspberry Pi Zero 2W

Goals
-------
Deliver data in a bi-directional manner between two of the hardware units
described above.

Things that would be cool:
    - Relay GPS information from one device to the other
    - Host web-page that allows one to type messages in
    - Determine the max number of bytes that can be transmitted
    - Play with encryption?

Issues
---------
TBD.

Licensing
---------
    - SPDX-FileCopyrightText: 2018 Brent Rubell for Adafruit Industries
    - SPDX-License-Identifier: MIT
"""

import adafruit_rfm9x
import adafruit_ssd1306
import board
import busio
import logging
import socket
import time

from digitalio import DigitalInOut, Direction, Pull


class LoraBonnet:
    # Identifier for the unit
    identifier = None

    # Three buttons present on the bonnet
    button_a = None
    button_b = None
    button_c = None

    # Comms/Pins
    i2c = None
    spi = None
    CS = None
    RESET = None

    # Display
    reset_pin = None
    display = None
    width = None
    height = None

    rfm9x = None
    prev_packet = None

def setup() -> LoraBonnet:
    bonnet = LoraBonnet()


    # Let's determine some identifying information for the unit
    bonnet.identifier = socket.gethostname()

    # Buttons
    #
    # There are three buttons provided on the bonnet, we'll go ahead
    # and set them up below.

    # Button A
    bonnet.button_a = DigitalInOut(board.D5)
    bonnet.button_a.direction = Direction.INPUT
    bonnet.button_a.pull = Pull.UP
    
    # Button B
    bonnet.button_b = DigitalInOut(board.D6)
    bonnet.button_b.direction = Direction.INPUT
    bonnet.button_b.pull = Pull.UP
    
    # Button C
    bonnet.button_c = DigitalInOut(board.D12)
    bonnet.button_c.direction = Direction.INPUT
    bonnet.button_c.pull = Pull.UP
    
    # Create the I2C interface.
    bonnet.i2c = busio.I2C(board.SCL, board.SDA)
    
    # 128x32 OLED Display
    bonnet.reset_pin = DigitalInOut(board.D4)
    bonnet.display = adafruit_ssd1306.SSD1306_I2C(128, 32, bonnet.i2c, reset=bonnet.reset_pin)
    
    # Clear the display.
    bonnet.display.fill(0)
    bonnet.display.show()
    
    bonnet.width = bonnet.display.width
    bonnet.height = bonnet.display.height
    
    # Configure RFM9x LoRa Radio
    bonnet.CS = DigitalInOut(board.CE1)
    bonnet.RESET = DigitalInOut(board.D25)
    
    bonnet.spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

    bonnet.rfm9x = adafruit_rfm9x.RFM9x(bonnet.spi, bonnet.CS, bonnet.RESET, 915.0)
    bonnet.rfm9x.tx_power = 23

    return bonnet


def run(bonnet: LoraBonnet):
    if not LoraBonnet:
        raise ValueError("LoraBonnet was not properly initialized")

    while True:
        bonnet.display.fill(0) 
        bonnet.display.text(f'{bonnet.identifier}', 35, 0, 1)

        # check for packet rx
        packet = bonnet.rfm9x.receive()
        
        if packet is None:
            bonnet.display.show()
            bonnet.display.text('- Waiting for PKT -', 15, 20, 1)
        else:
            # Display the packet text and rssi
            bonnet.display.fill(0)
            
            bonnet.prev_packet = packet
            packet_text = str(bonnet.prev_packet, "utf-8")
            
            bonnet.display.text('RX: ', 0, 0, 1)
            bonnet.display.text(packet_text, 25, 0, 1)
            
            logging.info(f"Received: {packet_text}")
            time.sleep(1)

        if not bonnet.button_a.value:
            # Send Button A
            bonnet.display.fill(0)
            
            button_a_data = bytes("Button A!\r\n","utf-8")
            bonnet.rfm9x.send(button_a_data)
            
            bonnet.display.text('Sent Button A!', 25, 15, 1)
            logging.info(f"Sent: {str(button_a_data, 'utf-8')}")

        elif not bonnet.button_b.value:
            # Send Button B
            bonnet.display.fill(0)
            
            button_b_data = bytes("Button B!\r\n","utf-8")
            bonnet.rfm9x.send(button_b_data)
            
            bonnet.display.text('Sent Button B!', 25, 15, 1)
            logging.info(f"Sent: {str(button_b_data, 'utf-8')}")
        
        elif not bonnet.button_c.value:
            # Send Button C
            bonnet.display.fill(0)
            
            button_c_data = bytes("Button C!\r\n","utf-8")
            bonnet.rfm9x.send(button_c_data)
            
            bonnet.display.text('Sent Button C!', 25, 15, 1)
            logging.info(f"Sent: {str(button_c_data, 'utf-8')}")

        bonnet.display.show()
        time.sleep(0.1)


if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    bonnet = setup()
    run(bonnet)
