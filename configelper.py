import pathlib
import CONSTANTS
import json
import logging

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


def assemble_config(config_dir):
    """
    Reads the config file and
    :param config_dir:
    :return:
    """

    L.debug(config_dir)
    L.debug("Reading Config from: %s", config_dir)
    config_dir = pathlib.Path(config_dir).resolve()

    default_config_path = get_default_config_path()

    if not config_dir.exists():
        print("Unable to find a run config directory at: %", str(config_dir))
    else:
        pass
        # print("Reading Config from directory: ", str(config_dir))

    run_config = {}
    asset_types = []
    for each_file in default_config_path.glob("**/*.json"):

        L.debug("Reading %s", each_file)

        # Skipping generated files
        if each_file.name.startswith("_"):
            continue

        overwrite_file = pathlib.Path(config_dir.joinpath(each_file.name))

        if overwrite_file.exists():
            file_to_read = overwrite_file
        else:
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

    env_category = run_config[CONSTANTS.ENVIRONMENT_CATEGORY]
    relative_project_path = pathlib.Path(env_category[CONSTANTS.UNREAL_PROJECT_ROOT])
    project_root = config_dir.joinpath(relative_project_path).resolve()

    L.info("Project Root: " + str(project_root))

    # Resolves all relative paths in the project structure to absolute paths
    for each_value in env_category.keys():
        if not each_value == CONSTANTS.UNREAL_PROJECT_ROOT:
            each_relative_path = env_category[each_value]
            abs_path = project_root.joinpath(each_relative_path).resolve()

            L.debug(each_value + " :" + str(abs_path) + " Exists:  " + str(abs_path.exists()))
            env_category[each_value] = str(abs_path)

    env_category[CONSTANTS.UNREAL_PROJECT_ROOT] = str(project_root)
    run_config[CONSTANTS.ENVIRONMENT_CATEGORY] = env_category

    _write_assembled_config(config_dir, run_config)

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


def generate_default_config():

    # Test config file
    current_dir = pathlib.Path(pathlib.Path(__file__)).parent
    output_path = current_dir.joinpath("..").resolve()

    path = current_dir.joinpath("defaultConfig").resolve()

    L.info("Generating default config at: %s", output_path)

    gen_config_file = output_path.joinpath("_sentinelConfig.json")

    config = assemble_config(path)
    f = open(gen_config_file, "w")
    f.write(json.dumps(config))
    f.close()

    return gen_config_file
