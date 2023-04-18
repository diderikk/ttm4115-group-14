import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread
import json

# TODO: choose proper MQTT broker address
MQTT_BROKER = 'ec2-13-53-46-117.eu-north-1.compute.amazonaws.com'
MQTT_PORT = 1883

# TODO: choose proper topics for communication
MQTT_TOPIC_INPUT = 'command'


class TeacherMachine:
    def __init__(self):
        self.initial_queue = [1, 2, 3]

        t_initial = {'source': 'initial',
            'target': 'authentication'}

        # Change 1: effect is removed
        t_login = {'trigger': 'login',
            'source': 'authentication',
            'function': lambda: self.login("test", "test")}
        

        # Change 2: effect is removed here, too
        t_duty = {'trigger': 'duty',
            'source': 'progression_view',
            'target': 'publish_task'}
        
        t_published_task = {'trigger': 'task_published',
            'source': 'publish_task',
            'target': 'progression_view'}
        
        t_assistance_notification = {'trigger': 'assistance_notification',
            'source': 'progression_view',
            'target': 'assist_group'}
        
        t_complete_help = {'trigger': 'complete_help',
            'source': 'assist_group',
            'function': lambda: self.complete_help()}
        
        
        authentication = {'name': 'authentication',
        'entry': 'print_state("authentication")'}
        
        progression_view = {'name': 'progression_view',
        'entry': 'print_state("progression_view")'}
        
        publish_task = {'name': 'publish_task',
        'entry': 'print_state("publish_task")'}
        
        assist_group = {'name': 'assist_group',
        'entry': 'print_state("assist_group")'}
        
        self.stm = stmpy.Machine(name="student_machine",
            transitions=[t_initial, t_login, t_duty, t_published_task, t_assistance_notification, t_complete_help], 
            states=[authentication, progression_view, publish_task, assist_group], 
            obj=self)

    def login(self, username: str, password: str) -> str:
        if(username == "test" and password == "test"):
            return 'progression_view'
        else:
            return 'authentication'
        
    def complete_help(self) -> str:
        self.initial_queue.pop(0)
        if(len(self.initial_queue) == 0):
            return "progression_view"
        else:
            return "assist_group"
    
    def print_state(self, name):
        print(f"ENTERED STATE {name}")
        


class TeacherDriver:
    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected
        print('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):
        unwrapped = json.loads(msg.payload)
        self.student_machine.send(unwrapped)


    def __init__(self):
        # get the logger object for the component
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set("mosquitto", "mosquitto")
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        # subscribe to proper topic(s) of your choice
        self.mqtt_client.subscribe(MQTT_TOPIC_INPUT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        # we start the stmpy driver, without any state machines for now
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        self.student_machine = TeacherMachine().stm
        self.stm_driver.add_machine(self.student_machine)


    def stop(self):
        self.mqtt_client.loop_stop()
        self.stm_driver.stop()


def main():
    t = TeacherDriver()


if __name__ == "__main__":
    main()
