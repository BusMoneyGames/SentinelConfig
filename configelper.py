import pathlib
import config_constants
import json
import logging
import os
L = logging.getLogger()


def add_engine_information(run_config):
    """Checks if the engine is pre-intalled and compiled or is cloned from git"""

    # TODO Change this so that it checks the the actual registry

    engine_path = run_config["environment"]["engine_root_path"]

    for each_file in os.listdir(engine_path):
        if "generateprojectfiles" in each_file.lower():

            # TODO make sure that the unreal engine structure entry actually exists before trying to add to it
            run_config["unreal_engine_structure"]["is_installed"] = False
            return run_config

    run_config["unreal_engine_structure"]["is_installed"] = True

    return run_config

def verify_environment(run_config):

    env_config = run_config[config_constants.ENVIRONMENT_CATEGORY]
    print('\n')
    print("%-75s %-25s %4s" % ("Path", "Value", "Exists"))

    for each_env_config in env_config.keys():
        path = pathlib.Path(env_config[each_env_config])
        exists = path.exists()

        print("%-75s %-25s %4s" % (path, each_env_config, str(exists)))

    print('\n')


def merge_dicts(original, update):
    """
    Recursively update a dict.
    Subdict's won't be overwritten but also updated.
    """

    for key, value in original.items():
        if key not in update:
            update[key] = value
        elif isinstance(value, dict):
            merge_dicts(value, update[key])
    return update


def _assemble_config(sentinel_environment_config, skip_versioning="False"):
    """Assembles all the different config files into one """

    L.debug("Loading: %s - exists: %s", sentinel_environment_config, sentinel_environment_config.exists())

    f = open(sentinel_environment_config, "r")
    environment_config_data = json.load(f)
    f.close()

    root_dir = sentinel_environment_config.parent
    L.debug("Reading environment from: %s", sentinel_environment_config)

    default_config_path = pathlib.Path(get_default_config_path())
    L.debug("Default config folder %s - Exists: %s", default_config_path, default_config_path.exists())

    default_config = _read_configs_from_directory(default_config_path)

    # Read the overwrite config
    overwrite_config_path = environment_config_data["sentinel_config_root_path"]
    overwrite_config_path = root_dir.joinpath(overwrite_config_path).resolve()
    overwrite_config = _read_configs_from_directory(overwrite_config_path)

    # Combine the run config and overwrite from the overwrite config folder
    run_config = merge_dicts(default_config, overwrite_config)

    environment_config_data = convert_environment_paths_to_abs(environment_config_data, root_dir)

    if skip_versioning.lower() == "false":
        environment_config_data = add_version_to_artifact_path(run_config, environment_config_data)

    run_config[config_constants.ENVIRONMENT_CATEGORY] = environment_config_data

    # Add information about the engine
    run_config = add_engine_information(run_config)

    return run_config


def add_version_to_artifact_path(run_config, environment_config_data):

    # TODO read this from a constant
    artifacts_path = environment_config_data["sentinel_artifacts_path"]
    path = pathlib.Path(artifacts_path)

    if "gen_version_control" in run_config.keys():
        commit_id = run_config["gen_version_control"]["commit_id"]
        environment_config_data["sentinel_artifacts_path"] = path.joinpath(commit_id).as_posix()
    else:
        computer_name = os.getenv('COMPUTERNAME')
        environment_config_data["sentinel_artifacts_path"] = path.joinpath(computer_name).as_posix()

    return environment_config_data


def convert_environment_paths_to_abs(environment_config_data, root_dir):
    # Resolves all relative paths in the project structure to absolute paths
    for each_value in environment_config_data.keys():
        each_relative_path = environment_config_data[each_value]
        if each_relative_path.endswith("/") or each_relative_path == "":
            value = root_dir.joinpath(each_relative_path).resolve()
            L.debug(each_value + " :" + str(value) + " Exists:  " + str(value.exists()))
        else:
            value = each_relative_path

        environment_config_data[each_value] = str(value)

    return environment_config_data


def _read_configs_from_directory(default_config_path):
    """Creates a config file from a directory that has folders and json files"""

    run_config = {}
    temp_config_files = []
    temp_config_folders = []
    for each_entry in default_config_path.glob("*/"):
        # category
        json_data = {}
        if each_entry.is_dir():

            # Check if its a temp config folder and mark it for delete
            if each_entry.name.startswith("_"):
                temp_config_folders.append(each_entry)

            category_name = each_entry.name

            # Finding the values into the dict
            category_dict = {}

            entries = each_entry.glob("**/*.json")

            for each_sub_value in entries:

                # Reading the json file
                f = open(str(each_sub_value))
                json_data = json.load(f)
                f.close()

                # Check if its a temp config and add it to the delete list if so
                if each_sub_value.name.startswith("gen_"):
                    temp_config_files.append(each_sub_value)

                name = each_sub_value.with_suffix('').name

                category_dict[name] = json_data

            # If there was only one entry then we skip the file name and just add the category
            if len(os.listdir(each_entry)) == 1:
                run_config[category_name] = json_data
            else:
                run_config[category_name] = category_dict

    for each_temp_config in temp_config_files:
        os.remove(each_temp_config)

    for each_temp_config_folder in temp_config_folders:
        os.rmdir(each_temp_config_folder)

    return run_config


def get_default_config_path():
    """Return the directory containing the default config folder"""
    # Test config file
    current_dir = pathlib.Path(pathlib.Path(__file__)).parent

    path = current_dir.joinpath("defaultConfig").resolve()
    L.debug("Default Config Path %s", current_dir)
    return path


def generate_config(environment_file, skip_versioning=False):
    """Generate the assembled config based on the environment file"""

    environment_file = pathlib.Path(environment_file)

    # Assembles the config into a single file
    assembled_config_data = _assemble_config(environment_file, str(skip_versioning))

    # Generate output directory
    current_run_directory = pathlib.Path(environment_file.parent.joinpath(config_constants.GENERATED_CONFIG_FILE_NAME))

    # Writing it to disk
    f = open(current_run_directory, "w")
    f.write(json.dumps(assembled_config_data, indent=4))
    f.close()

    return current_run_directory
