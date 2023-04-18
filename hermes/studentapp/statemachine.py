from stmpy import Machine, Driver


t_initial = {'source': 'initial',
             'target': 'active'}

t_start = {'trigger': 'start',
    'source': 'idle',
    'target': 'active'
    }

# Change 1: effect is removed
t_stop = {'trigger': 'stop',
    'source': 'active',
    'target': 'idle'}

s_idle = {'name': 'idle',
        'entry': ''}

s_active = {'name': 'active',
        'entry': ''}


state_machine = Machine('my_machine', transitions=[t_initial, t_start, t_stop] , obj=None)


# Create a driver for the state machine
driver = Driver()
driver.add_machine(state_machine)

# Run the driver to start the state machine
driver.start()