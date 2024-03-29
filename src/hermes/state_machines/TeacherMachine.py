import stmpy
import logging
from threading import Thread
import json
from .TeacherMachineLogic import login as login_, logout, delete_notification, update_assignee, create_task

class TeacherMachine:
    def __init__(self, uuid):

        t_initial = {"source": "initial", "target": "authentication"}

        # Change 1: effect is removed
        t_login = {
            "trigger": "login",
            "source": "authentication",
            "function": login_,
        }

        # Change 2: effect is removed here, too
        t_duty = {
            "trigger": "duty",
            "source": "progression_view",
            "target": "write_task",
        }

        t_publish_task = {
            "trigger": "publish_task",
            "source": "write_task",
            "function": create_task,
        }
        
        t_cancel = {
            "trigger": "cancel",
            "source": "write_task",
            "target": "progression_view",
        }

        
        t_logout = {
            "trigger": "logout",
            "source": "progression_view",
            "function": logout
        }
        

        t_start_assistance = {
            "trigger": "start_assistance",
            "source": "progression_view",
            "function": update_assignee,
        }

        t_complete_help = {
            "trigger": "complete_help",
            "source": "assist_group",
            "function": delete_notification,
        }

        authentication = {
            "name": "authentication",
            "entry": 'print_state("authentication")',
        }

        progression_view = {
            "name": "progression_view",
            "entry": 'print_state("progression_view")',
        }

        write_task = {"name": "write_task", "entry": 'print_state("write_task")'}

        assist_group = {"name": "assist_group", "entry": 'print_state("assist_group")'}

        self.stm = stmpy.Machine(
            name=uuid,
            transitions=[
                t_initial,
                t_login,
                t_logout,
                t_duty,
                t_cancel,
                t_publish_task,
                t_start_assistance,
                t_complete_help,
            ],
            states=[authentication, progression_view, write_task, assist_group],
            obj=self,
        )

    def print_state(self, name):
        print(f"ENTERED STATE {name}")


class TeacherDriver:
    def __init__(self):
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)

    def trigger(self, uuid, trigger, kwargs={}):
        self.stm_driver.send(trigger, uuid, [''], kwargs=kwargs)

    def add_machine(self, uuid):
        student_machine = TeacherMachine(uuid=uuid).stm
        self.stm_driver.add_machine(student_machine)
        
    def get_machine(self, uuid):
        return self.stm_driver._stms_by_id.get(uuid)
    
    def pop_machine(self, uuid):
        self.stm_driver._terminate_stm(uuid)
    
    def stop(self):
        self.stm_driver.stop()


def main():
    pass


if __name__ == "__main__":
    main()

t = TeacherDriver()