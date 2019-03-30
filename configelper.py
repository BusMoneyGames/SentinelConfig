import pathlib
import CONSTANTS
import json
import logging
import os

L = logging.getLogger()


def verify_environment(run_config):

    env_config = run_config[CONSTANTS.ENVIRONMENT_CATEGORY]
    print('\n')
    print("%-75s %-25s %4s" % ("Path", "Value", "Exists"))

    for each_env_config in env_config.keys():
        path = pathlib.Path(env_config[each_env_config])
        exists = path.exists()

        print("%-75s %-25s %4s" % (path, each_env_config, str(exists)))

    print('\n')


def reset_ue_repo(run_config):
    """
    cleans the git repo so that it is clean to run
    :return:
    """

    environment = run_config[CONSTANTS.ENVIRONMENT_CATEGORY]
    project_root = pathlib.Path(environment[CONSTANTS.UNREAL_PROJECT_ROOT])

    repo = git.Repo(str(project_root.parent))
    clean_result = repo.git.execute(["git", "clean", "-dfx"])
    L.debug(clean_result)

    reset_result = repo.git.execute(["git", "reset", "--hard"])
    L.debug(reset_result)


def assemble_config(sentinel_environment_config):
    """Assembles all the different config files into one """

    # Read environment config
    L.debug("Loading: %s - exists: %s", sentinel_environment_config, sentinel_environment_config.exists())

    f = open(sentinel_environment_config, "r")
    environment_config_data = json.load(f)
    f.close()

    L.debug("Reading environment from: %s", sentinel_environment_config)

    default_config_path = pathlib.Path(get_default_config_path())
    L.debug("Default config folder %s - Exists: %s", default_config_path, default_config_path.exists())

    run_config = {}
    asset_types = []
    for each_file in default_config_path.glob("**/*.json"):
        # Skipping generated files
        if each_file.name.startswith("_"):
            continue

        file_to_read = each_file

        f = open(str(file_to_read))
        json_data = json.load(f)
        f.close()

        # TODO fix it so that the default folder can have fewer types that the target folder since now we only try and
        # find an asset overview if it exists in the overwrite dir

        if "type_" in file_to_read.name:
            asset_types.append(json_data)
        else:
            run_config.update(json_data)

    run_config.update({"AssetTypes": asset_types})

    current_run_directory = pathlib.Path(os.getcwd())

    # Resolves all relative paths in the project structure to absolute paths
    for each_value in environment_config_data.keys():
        each_relative_path = environment_config_data[each_value]
        abs_path = current_run_directory.joinpath(each_relative_path).resolve()

        L.debug(each_value + " :" + str(abs_path) + " Exists:  " + str(abs_path.exists()))
        environment_config_data[each_value] = str(abs_path)

    run_config[CONSTANTS.ENVIRONMENT_CATEGORY] = environment_config_data

    _write_assembled_config(current_run_directory, run_config)

    return run_config


def _write_assembled_config(root_folder, assembled_config):

    gen_config_file = pathlib.Path(root_folder).joinpath("_sentinelConfig.json")
    f = open(gen_config_file, "w")
    f.write(json.dumps(assembled_config))
    f.close()


def get_default_config_path():

    # Test config file
    current_dir = pathlib.Path(pathlib.Path(__file__)).parent

    path = current_dir.joinpath("defaultConfig").resolve()
    L.debug("Default Config Path %s", current_dir)
    return path


def generate_config(environment_file):

    environment_file = pathlib.Path(environment_file)
    # Assembles the config into a single file
    config = assemble_config(environment_file)

    current_run_directory = pathlib.Path(environment_file.parent.joinpath(CONSTANTS.GENERATED_CONFIG_FILE_NAME))

    f = open(current_run_directory, "w")
    f.write(json.dumps(config, indent=4))
    f.close()

    return current_run_directory
