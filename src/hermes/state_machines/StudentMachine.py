import stmpy
import logging
from threading import Thread
import json
from .StudentMachineLogic import login as login_, logout, post_notification, alert_teacher


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
            "function": post_notification
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
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)

    def trigger(self, uuid, trigger, kwargs={}):
        self.stm_driver.send(trigger, uuid, [''], kwargs=kwargs)

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


s = StudentDriver()
