#!/usr/bin/env python3
import asyncio
import os
from bleak import BleakScanner
import paho.mqtt.client as paho

# --- Config ---
TARGET_MAC = "f4:63:6b:d0:77:b9"  # BLE device
MQTT_BROKER = "172.20.10.2"       # Raspberry Pi's IP
MQTT_PORT = 1883

# MQTT Topics
TOPIC_NEW_DEVICE = "game/new_player"
TOPIC_DATA = "game/data"

client = None
seen_devices = set()
last_payloads = {}

# --- MQTT setup ---
def setup_mqtt():
    global client
    client = paho.Client(paho.CallbackAPIVersion.VERSION2)
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        print(f"✅ MQTT connected to {MQTT_BROKER}:{MQTT_PORT}")
        return True
    except Exception as e:
        print(f"❌ MQTT connect error: {e}")
        return False

def mqtt_send(topic, msg):
    if client and client.is_connected():
        client.publish(topic, msg, qos=1)
        print(f"📤 MQTT: {topic} → {msg}")
    else:
        print("❌ MQTT not connected")

# --- BLE callback ---
def detection_callback(device, advertisement_data):
    mac = device.address.lower()
    
    # Only process our target device
    if mac != TARGET_MAC:
        return

    # Check if this is a new detection
    if mac not in seen_devices:
        seen_devices.add(mac)
        print(f"🎯 TARGET DEVICE FOUND: {mac}")
        mqtt_send(TOPIC_NEW_DEVICE, mac)
    # Process all service data
    if advertisement_data.service_data:
        for uuid, data in advertisement_data.service_data.items():
            try:
                hex_data = data.hex()

                # Try to decode payload (skip first 3 bytes)
                if len(hex_data) >= 6:
                    payload = bytes.fromhex(hex_data[6:]).decode("ascii", errors="replace")
                    payload_clean = payload.split(';')[0].split('\x00')[0].strip()

                    # Only send if payload changed
                    if payload_clean and last_payloads.get(mac) != payload_clean:
                        last_payloads[mac] = payload_clean

                        # Create JSON message with additional data
                        message = {
                            "mac": mac,
                            "payload": payload_clean,
                            "raw_hex": hex_data
                        }

                        import json
                        mqtt_send(f"{TOPIC_DATA}/{mac}", json.dumps(message))
                        print(f"📡 BLE Data: {mac} → '{payload_clean}'")

            except Exception as e:
                print(f"❌ Decode error: {e}")

# --- BLE scanning loop ---
async def scan_ble_devices():
    scanner = BleakScanner(detection_callback=detection_callback)
    
    print("🔍 Starting BLE Scanner...")
    print(f"🎯 Targeting device: {TARGET_MAC}")
    print(f"📡 MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print("Press Ctrl+C to stop\n")
    
    await scanner.start()
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await scanner.stop()
        if client:
            client.loop_stop()
            client.disconnect()
        print("\n🛑 Scanner stopped.")
# --- Main ---
async def main():
    if setup_mqtt():
        await scan_ble_devices()
    else:
        print("❌ Failed to setup MQTT, exiting...")

if __name__ == "__main__":
    asyncio.run(main())
