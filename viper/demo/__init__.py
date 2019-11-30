"""## Viper CLI Examples.

### Initialize current workspace (creates a `viperdb.sqlite3` file)

    viper init

    # or remove or overwrite existing data with "-f" / "--force"

    viper init -f


### Load hosts from file

    viper hosts:from-file tests/data/hosts.csv --indent 4

    # or with a custom loader

    viper hosts:from-file tests/data/hosts.json --loader viper.demo.loaders.json --indent 4


### Load hosts from Python object

    viper hosts:from-obj viper.demo.hosts.group1 --indent 4


### Let's save the hosts

    viper hosts:from-obj viper.demo.hosts.group1 > /tmp/hosts.json


### Filter hosts

    cat /tmp/hosts.json | viper hosts:filter viper.demo.filters.ip_starts_with_2 --indent 4


### Assign tasks to the given hosts

    cat /tmp/hosts.json | viper hosts:task viper.demo.tasks.ping --indent 4


### Run the assigned tasks

    cat /tmp/hosts.json | viper hosts:task viper.demo.tasks.ping | viper task-runners:run --indent 4

    # or use a shortcut

    cat /tmp/hosts.json | viper hosts:run-task viper.demo.tasks.ping --indent 4


### Run tasks in parallel using multiple workers

    cat /tmp/hosts.json | viper hosts:run-task viper.demo.tasks.ping --max-workers 50 --indent 4


### Get the past task results of the hosts from DB

    cat /tmp/hosts.json | viper hosts:task-results --indent 4 --debug


### Or get the past task results by task

    viper task:from-obj viper.demo.tasks.ping | viper task-results:by-task -i 4

    # Or

    viper task:from-obj viper.demo.tasks.ping | viper task:results -i 4


### Let's save the result

    viper task:from-obj viper.demo.tasks.ping | viper task:results > /tmp/results.json


### Now filter the results by their status

    # success
    cat /tmp/results.json | viper task-results:filter viper.demo.filters.result_ok -i 4

    # failed
    cat /tmp/results.json | viper task-results:filter viper.demo.filters.result_errored -i 4


### Pipe the results to a custom handler

    cat /tmp/results.json | viper task-results:pipe viper.demo.handlers.print_status
"""
