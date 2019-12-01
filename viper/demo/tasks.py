from viper import Task
from viper.demo.callbacks import log_command
from viper.demo.callbacks import log_status
from viper.demo.commands import df_command
from viper.demo.commands import ping_command


def ping() -> Task:
    return Task(
        "Ping",
        ping_command,
        timeout=5,
        retry=1,
        pre_run=log_command,
        post_run=log_status,
    )


def disk_usage() -> Task:
    return Task(
        "Disk Usage",
        df_command,
        timeout=5,
        retry=1,
        pre_run=log_command,
        post_run=log_status,
    )
