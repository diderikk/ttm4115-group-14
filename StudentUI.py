import paho.mqtt.client as mqtt
import logging
from threading import Thread
import json
from appJar import gui

# TODO: choose proper MQTT broker address
MQTT_BROKER = 'localhost'
MQTT_PORT = 8081

# TODO: choose proper topics for communication
MQTT_TOPIC_INPUT = 'ttm4115/command'
MQTT_TOPIC_OUTPUT = 'ttm4115/answer'


class TimerCommandSenderComponent:
    """
    The component to send voice commands.
    """

    def on_connect(self, client, userdata, flags, rc):
       	print('MQTT connected to {}'.format(client))

    def __init__(self):
        self.mqtt_client = mqtt.Client()
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        self.create_gui()

    def create_gui(self):
        self.app = gui()

        def publish_command(command):
            payload = json.dumps(command)
            self.mqtt_client.publish(MQTT_TOPIC_INPUT, payload=payload, qos=2)

        self.app.startLabelFrame('Student Actions:')
        def on_button_pressed_start(title):
            name = extract_timer_name(title)
            duration = extract_duration_seconds(title)
            command = {"command": "new_timer", "name": name, "duration": duration}
            publish_command(command)
            
          
        
        self.app.addButton('Login', lambda:  publish_command("login"))
        self.app.addButton('Task Selected', lambda: publish_command("task_selected"))
        self.app.addButton('Back', lambda: publish_command("back"))
        self.app.addButton('Ask', lambda: publish_command("ask"))
        self.app.addButton('Cancel', lambda: publish_command("cancel"))
        self.app.addButton('Send', lambda: publish_command("send_notification"))
        self.app.addButton('Finish', lambda: publish_command("finish"))
        self.app.stopLabelFrame()

        self.app.go()


    def stop(self):
        self.mqtt_client.loop_stop()


t = TimerCommandSenderComponent()