from sys import argv
import yaml
from os import system

config_file = argv[1]
with open(config_file) as f:
    data = yaml.load(f, yaml.SafeLoader)
    target_directory = data["application_directory"]
    cmd = "sudo mkdir -p {}".format(target_directory)
    system(cmd)
    cmd2 = "sudo chmod 777 {}".format(target_directory)
    system(cmd2)

    buffer_directory = "{}/key_store".format(target_directory)
    cmd = "sudo mkdir -p {}".format(buffer_directory)
    system(cmd)
    log_directory = data["logs_directory"]
    cmd = "sudo mkdir -p {}".format(log_directory)
    system(cmd)
    cmd2 = "sudo chmod 777 {}".format(log_directory)
    system(cmd2)
    print(target_directory)