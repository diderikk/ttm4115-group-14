import stmpy
import logging
from threading import Thread
import json
from .StudentMachineLogic import login as login_, logout, post_notification, post_notification_tech, alert_teacher, post_notification_without_description, complete_help
import paho.mqtt.client as mqtt


MQTT_BROKER = "ec2-13-53-46-117.eu-north-1.compute.amazonaws.com"
MQTT_PORT = 1883

MQTT_TOPIC_INPUT = "raspberrypi"

MQTT_PAYLOADS = {"ask": "assistance_requested", "cancel": "assistance_done", "send_notification": "assistance_requested"}


class StudentMachine:
    def __init__(self, uuid):
        t_initial = {"source": "initial", "target": "login"}

        t_login = {
            "trigger": "login",
            "source": "login",
            "function": login_,
        }

        t_task_selected = {
            "trigger": "task_selected",
            "source": "task_select",
            "target": "task_overview",
        }

        t_back = {"trigger": "back",
                  "source": "task_overview", "target": "task_select"}

        t_complete = {
            "trigger": "complete",
            "source": "task_overview",
            "function": alert_teacher
        }

        t_logout = {
            "trigger": "logout",
            "source": "task_select",
            "function": logout
        }

        t_ask = {
            "trigger": "ask",
            "source": "task_overview",
            "target": "write_help_description",
        }

        t_ask_tech = {
            "trigger": "ask",
            "source": "task_select",
            "target": "write_technical_error_description",
        }

        t_cancel_tech = {
            "trigger": "cancel",
            "source": "write_technical_error_description",
            "target": "task_select",
        }

        t_send_notification_tech = {
            "trigger": "send_notification",
            "source": "write_technical_error_description",
            "function": post_notification_tech
        }

        t_cancel = {
            "trigger": "cancel",
            "source": "write_help_description",
            "target": "task_overview",
        }

        t_send_notification = {
            "trigger": "send_notification",
            "source": "write_help_description",
            "function": post_notification
        }

        task_select = {"name": "task_select",
                       "entry": 'print_state("task_select")'}

        login = {"name": "login", "entry": 'print_state("login")'}

        task_overview = {
            "name": "task_overview",
            "entry": 'print_state("task_overview")',
        }

        write_help_description = {
            "name": "write_help_description",
            "entry": 'print_state("write_help_description")',
        }

        write_technical_error_description = {
            "name": "write_technical_error_description",
            "entry": 'print_state("write_technical_error_description")',
        }

        self.stm = stmpy.Machine(
            name=uuid,
            transitions=[
                t_initial,
                t_login,
                t_logout,
                t_task_selected,
                t_complete,
                t_back,
                t_cancel_tech,
                t_ask_tech,
                t_send_notification_tech,
                t_ask,
                t_cancel,
                t_send_notification,
            ],
            states=[
                task_select,
                login,
                task_overview,
                write_help_description,
                write_technical_error_description
            ],
            obj=self,
        )

    def print_state(self, name):
        print(f"ENTERED STATE {name}")


class StudentDriver:
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
        self.mqtt_client.subscribe(f"{MQTT_TOPIC_INPUT}/#")
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)

    def trigger(self, uuid, trigger, kwargs={}):
        self.stm_driver.send(trigger, uuid, [''], kwargs=kwargs)

    def trigger_send_notification(self, uuid, trigger, group_no, kwargs={}):
        self.send_notification_to_mqtt(trigger, group_no)
        self.stm_driver.send(trigger, uuid, [''], kwargs=kwargs)

    def send_notification_to_mqtt(self, trigger, group_no):
        if group_no is not None:
            self.mqtt_client.publish(f"{MQTT_TOPIC_INPUT}/{group_no}", json.dumps(MQTT_PAYLOADS[trigger]))

    def add_machine(self, uuid):
        student_machine = StudentMachine(uuid=uuid).stm
        self.stm_driver.add_machine(student_machine)

    def get_machine(self, uuid):
        return self.stm_driver._stms_by_id.get(uuid)
    
    def pop_machine(self, uuid):
        self.stm_driver._terminate_stm(uuid)

    def stop(self):
        self.mqtt_client.loop_stop()
        self.stm_driver.stop()

    def on_message(self, client, userdata, msg):
        unwrapped = json.loads(msg.payload)
        group_no = int(msg.topic.split("/")[-1])
        print(unwrapped)
        if unwrapped == MQTT_PAYLOADS["ask"]:
            post_notification_without_description(group_no)
        elif unwrapped == MQTT_PAYLOADS["cancel"]:
            complete_help(group_no)


    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected

        print("MQTT connected to {}".format(client))


def main():
    pass


if __name__ == "__main__":
    main()


s = StudentDriver()
