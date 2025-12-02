#!/usr/bin/env python3
from flask import Flask, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import threading
import json
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# MQTT Configuration
MQTT_BROKER = "172.20.10.2"
MQTT_PORT = 1883

# Game Configuration - Sequential actions
GAME_ACTIONS = [
    {"id": "hello", "name": "Say Hi 👋", "instruction": "Wave and say Hello!", "completed": False, "emoji": "👋"},
    {"id": "raise", "name": "Raise Hand 🙋", "instruction": "Raise your hand up high!", "completed": False, "emoji": "🙋"},
    {"id": "circle", "name": "Make a Circle 🔄", "instruction": "Draw a circle in the air!", "completed": False, "emoji": "🔄"},
    {"id": "rotate", "name": "Rotate Your Body 🌪️", "instruction": "Spin around once!", "completed": False, "emoji": "🌪️"},
    {"id": "jump", "name": "Jump Up! ⬆️", "instruction": "Jump up and down!", "completed": False, "emoji": "⬆️"}
]

# Initial game state template
def create_initial_game_state():
    return {
        "actions": [action.copy() for action in GAME_ACTIONS],
        "current_action": 0,
        "completed_actions": 0,
        "total_actions": len(GAME_ACTIONS),
        "player_connected": False,
        "player_mac": None,
        "game_completed": False
    }

# Current game state
game_state = create_initial_game_state()

@app.route('/')
def index():
    return render_template('game_ui.html', game_state=game_state)

# SocketIO event for resetting the game
@socketio.on('reset_game')
def handle_reset_game():
    global game_state
    game_state = create_initial_game_state()
    print("🔄 Game state reset!")
    # Send the reset state to all clients
    socketio.emit('game_reset', game_state)

# MQTT Callbacks
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"✅ MQTT Connected to {MQTT_BROKER}")
    client.subscribe("game/#")

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode()
        
        print(f"📨 MQTT Received: {topic} -> {payload}")
        
        if topic == "game/new_player":
            # New player connected
            mac = payload
            game_state["player_mac"] = mac
            game_state["player_connected"] = True
            socketio.emit('player_connected', {"mac": mac})
            print(f"🎯 Player connected: {mac}")
            
        elif topic.startswith("game/data/"):
            # Data received - parse the JSON format
            try:
                data = json.loads(payload)
                mac = data.get("mac")
                payload_text = data.get("payload", "").lower().strip()
                
                print(f"📦 Raw data from {mac}: '{payload_text}'")
                
                # Map the incoming data to game actions
                action_mapping = {
                    "hello": "hello",
                    "raise": "raise", 
                    "circle": "circle",
                    "rotate": "rotate",
                    "jump": "jump"
                }
                
                # Check if payload matches any game action
                action = action_mapping.get(payload_text)
                if action:
                    # Get current action info
                    current_action_info = game_state["actions"][game_state["current_action"]]
                    
                    # Only accept the action if it matches the current expected action
                    if current_action_info["id"] == action and not current_action_info["completed"]:
                        current_action_info["completed"] = True
                        game_state["completed_actions"] += 1
                        
                        socketio.emit('action_completed', {
                            "action": action,
                            "action_name": current_action_info["name"],
                            "mac": mac
                        })
                        print(f"🎮 Action completed: {action} by {mac}")
                        
                        # Check if game is completed
                        if game_state["completed_actions"] == game_state["total_actions"]:
                            game_state["game_completed"] = True
                            socketio.emit('game_completed')
                            print("🎉 Game completed!")
                        else:
                            # Move to next action in sequence
                            game_state["current_action"] += 1
                            socketio.emit('next_action', {
                                "action_index": game_state["current_action"],
                                "action_name": game_state["actions"][game_state["current_action"]]["name"]
                            })
                            print(f"➡️ Moving to next action: {game_state['actions'][game_state['current_action']]['name']}")
                    else:
                        # Wrong action - give feedback
                        if current_action_info["id"] != action:
                            socketio.emit('wrong_action', {
                                "expected": current_action_info["name"],
                                "received": action_mapping.get(payload_text, payload_text)
                            })
                            print(f"⚠️ Wrong action! Expected: {current_action_info['id']}, Received: {action}")
                        else:
                            print(f"ℹ️ Action {action} already completed")
                else:
                    print(f"⚠️ Unknown payload: '{payload_text}' - not a game action")
                        
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
            except Exception as e:
                print(f"❌ Error processing data: {e}")
                
    except Exception as e:
        print(f"❌ Error processing MQTT message: {e}")

def start_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print(f"🔗 Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
        client.loop_forever()
    except Exception as e:
        print(f"❌ MQTT connection failed: {e}")

if __name__ == '__main__':
    # Start MQTT in a separate thread
    mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
    mqtt_thread.start()
    
    print("🚀 Starting Sequential Motion Game...")
    print("📍 Game UI: http://localhost:5000")
    print("🎮 Game Actions (Sequential): Hi → Raise Hand → Circle → Rotate → Jump")
    print("📡 Listening for MQTT messages on game/#")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
