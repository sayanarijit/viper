# Viper Infrastructure Commander

Viper is a handy tool for easily running infrastructure management tasks and commands.

## Viper CLI Examples.


    ### Load hosts from file
    viper hosts:from_file tests/data/hosts.csv --indent 4
    viper hosts:from_file tests/data/hosts.json --loader viper.demo.loaders.json --indent 4

    ### Load hosts from Python object
    viper hosts:from_obj viper.demo.hosts.group1 --indent 4

    ### Let's save the hosts
    hosts=$(viper hosts:from_obj viper.demo.hosts.group1)

    ### Filter hosts
    echo $hosts | viper hosts:filter viper.demo.filters.ip_starts_with_2 --indent 4

    ### Assign tasks to the given hosts
    echo $hosts | viper hosts:task viper.demo.tasks.ping --indent 4

    ### Run assigned tasks
    echo $hosts | viper hosts:task viper.demo.tasks.ping | viper runners:run --indent 4
    echo $hosts | viper hosts:run_task viper.demo.tasks.ping --indent 4


