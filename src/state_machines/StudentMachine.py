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


class StudentMachine:
    def __init__(self):
        self.tmp_int = 0

        t_initial = {'source': 'initial',
            'target': 'login'}

        # Change 1: effect is removed
        t_login = {'trigger': 'login',
            'source': 'login',
            'function': lambda: self.login("test", "test")}
        

        # Change 2: effect is removed here, too
        t_task_selected = {'trigger': 'task_selected',
            'source': 'task_select',
            'target': 'task_overview'}
        
        t_back = {'trigger': 'back',
            'source': 'task_overview',
            'target': 'task_select'}
        
        t_ask = {'trigger': 'ask',
            'source': 'task_overview',
            'target': 'write_help_description'}
        
        t_cancel = {'trigger': 'cancel',
            'source': 'write_help_description',
            'target': 'task_overview'}
        
        t_send_notification = {'trigger': 'send_notification',
            'source': 'write_help_description',
            'target': 'task_overview'}
        
        t_finish = {'trigger': 'finish',
            'source': 'task_overview',
            'function': lambda: self.finish()}
        
        
        task_select = {'name': 'task_select',
        'entry': 'print_state("task_select")'}
        
        login = {'name': 'login',
        'entry': 'print_state("login")'}
        
        task_overview = {'name': 'task_overview',
        'entry': 'print_state("task_overview")'}
        
        write_help_description = {'name': 'write_help_description',
        'entry': 'print_state("write_help_description")'}
        
        finished_work = {'name': 'finished_work',
        'entry': 'print_state("finished_work")'}
        
        self.stm = stmpy.Machine(name="student_machine",
            transitions=[t_initial, t_login, t_task_selected, t_back, t_ask, t_cancel, t_send_notification, t_finish], 
            states=[task_select, login, task_overview, write_help_description, finished_work], 
            obj=self)

    def login(self, username: str, password: str) -> str:
        if(username == "test" and password == "test"):
            return 'task_select'
        else:
            return 'login'
        
    def finish(self) -> str:
        self.tmp_int += 1
        if(self.tmp_int >= 3):
            return "finished_work"
        else:
            return "task_overview"
    
    def print_state(self, name):
        print(f"ENTERED STATE {name}")
        


class StudentDriver:
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
        self.student_machine = StudentMachine().stm
        self.stm_driver.add_machine(self.student_machine)


    def stop(self):
        self.mqtt_client.loop_stop()
        self.stm_driver.stop()


def main():
    t = StudentDriver()


if __name__ == "__main__":
    main()