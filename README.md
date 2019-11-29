# Viper Infrastructure Commander

Viper is a handy tool for easily running infrastructure management tasks and commands.

## Viper CLI Examples.

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

    hosts=$(viper hosts:from-obj viper.demo.hosts.group1)


### Filter hosts

    echo $hosts | viper hosts:filter viper.demo.filters.ip_starts_with_2 --indent 4


### Assign tasks to the given hosts

    echo $hosts | viper hosts:task viper.demo.tasks.ping --indent 4


### Run the assigned tasks

    echo $hosts | viper hosts:task viper.demo.tasks.ping | viper task-runners:run --indent 4

    # or use a shortcut

    echo $hosts | viper hosts:run-task viper.demo.tasks.ping --indent 4


### Run tasks in parallel using multiple workers

    echo $hosts | viper hosts:run-task viper.demo.tasks.ping --max-workers 50 --indent 4


### Get the past task results of the hosts from DB

    echo $hosts | viper hosts:task-results --indent 4 --debug


### Or get the past task results by task

    viper task:from-obj viper.demo.tasks.ping | viper task-results:by-task -i 4


### Let's save the result

    results=$(viper task:from-obj viper.demo.tasks.ping | viper task-results:by-task)


### Now filter the results by their status

    # success
    echo $results | viper task-results:filter viper.demo.filters.result_ok -i 4

    # failed
    echo $results | viper task-results:filter viper.demo.filters.result_errored -i 4


