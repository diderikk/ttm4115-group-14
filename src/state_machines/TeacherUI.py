import paho.mqtt.client as mqtt
import logging
from threading import Thread
import json
from appJar import gui

# TODO: choose proper MQTT broker address
MQTT_BROKER = 'localhost'
MQTT_PORT = 8081

# TODO: choose proper topics for communication
MQTT_TOPIC_INPUT = 'command'


class TeacherUI:
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
            print(command)
            self.mqtt_client.publish(MQTT_TOPIC_INPUT, payload=payload, qos=2)

        self.app.startLabelFrame('Teacher Actions:')
        self.app.addButton('Login', lambda:  publish_command("login"))
        self.app.addButton('Duty', lambda: publish_command("duty"))
        self.app.addButton('Task Published', lambda: publish_command("task_published"))
        self.app.addButton('Assistance Notification', lambda: publish_command("assistance_notification"))
        self.app.addButton('Complete Help', lambda: publish_command("complete_help"))
        self.app.stopLabelFrame()

        self.app.go()


    def stop(self):
        self.mqtt_client.loop_stop()


t = TeacherUI()