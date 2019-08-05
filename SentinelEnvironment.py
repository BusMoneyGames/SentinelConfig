import logging
import pathlib
import click
import json
import os
import configelper
import config_constants

L = logging.getLogger()


def _load_environment_config(overwrite_path=""):
    """Finds the config file that contains the environment information"""
    # Figure out where the script is run from
    current_run_directory = pathlib.Path(os.getcwd())
    L.debug("Current Directory: %s ", current_run_directory)

    if overwrite_path:
        L.debug("environment config read from none default location")
        L.debug("relative environment path is: %s", overwrite_path)
    else:
        overwrite_path = ".."
        L.debug("Using the default relative path that resolves to:  %s", overwrite_path)

    config_file_name = config_constants.CONFIG_SETTINGS_FILE_NAME
    config_file_path = current_run_directory.joinpath(overwrite_path, config_file_name).resolve()
    L.debug("Searching for environment file at: %s", config_file_path)
    L.debug("environment file exists: %s ", config_file_path.exists())

    if config_file_path.exists():
        return config_file_path
    else:
        L.error("Unable to find config environment file")
        L.error("Expected Path: %s", config_file_path)
        quit(1)


@click.group()
@click.option('--project_root', default="", help="Path to the config overwrite folder")
@click.option('--output', type=click.Choice(['text', 'json']), default='text', help="Output type.")
@click.option('--no_version', type=click.Choice(['true', 'false']), default='true', help="Skips output version")
@click.option('--debug', type=click.Choice(['true', 'false']), default='false',  help="Verbose logging")
@click.pass_context
def cli(ctx, project_root, debug, output, no_version):
    """Sentinel Unreal Component handles running commands interacting with unreal engine"""

    ctx.ensure_object(dict)
    ctx.obj['CONFIG_OVERWRITE'] = project_root
    ctx.obj['SKIP_VERSION'] = no_version

    print("Got here")
    if debug:
        L.setLevel(logging.DEBUG)
        message_format = '%(levelname)s - %(message)s '
    else:
        message_format = '%(levelname)s %(message)s '
        L.setLevel(logging.ERROR)

    logging.basicConfig(format=message_format)


@cli.command()
@click.option('-o', '--output', type=click.Choice(['text', 'json']), default='text', help="Output type.")
@click.pass_context
def generate(ctx, output):
    """Generates a config file """

    config_path = ctx.obj['CONFIG_OVERWRITE']
    skip_version_flag = ctx.obj["SKIP_VERSION"]

    sentinel_environment_config = _load_environment_config(config_path)
    configelper.generate_config(sentinel_environment_config, skip_version_flag)

    # TODO output
    if output == 'text':
        print("Config Refreshed!")
    elif output == 'json':
        print(json.dumps({"message": "Generated Config"}, indent=4))


@cli.command()
@click.option('--project_name', default="", help="Name of the project")
@click.option('--engine_path', default="", help="Relative Path to the engine")
@click.option('--config_path', default="", help="Path to a custom config folder")
@click.option('--version_control_root', default="", help="Path to the version control root")
@click.option('--artifacts_root', default="", help="Path to the artifacts root")
@click.option('--s3_data_base_location', default="", help="Path to the database")
@click.option('--sentinel_database', default="", help="Path to the sentinel database")
@click.option('--cache_path', default="", help="Path to the sentinel cache")
@click.pass_context
def make_default_config(ctx, project_name,
                        engine_path,
                        config_path,
                        version_control_root,
                        artifacts_root,
                        sentinel_database,
                        s3_data_base_location,
                        cache_path):

    """Generate the default config for an unreal project"""

    L.info("Generating default config")

    default_config_path = pathlib.Path(ctx.obj['CONFIG_OVERWRITE']).joinpath("_sentinel_root.json")

    if not project_name:
        project_name = ""
    if not engine_path:
        engine_path = "UnrealEngine/"
    if not config_path:
        config_path = "SentinelConfig/"
    if not version_control_root:
        version_control_root = ""
    if not artifacts_root:
        artifacts_root = "SentinelArtifacts/"
    if not sentinel_database:
        sentinel_database = "SentinelDB/"
    if not cache_path:
        cache_path = "SentinelCache/"
    if not s3_data_base_location:
        s3_data_base_location = "Not Set"

    config = {"project_root_path": project_name,
              "engine_root_path": engine_path,
              "sentinel_config_root_path": config_path,
              "version_control_root": version_control_root,
              "sentinel_artifacts_path": artifacts_root,
              "sentinel_database": sentinel_database,
              "sentinel_cache_path": cache_path,
              "s3_data_base_location": s3_data_base_location}

    f = open(default_config_path, "w")
    f.write(json.dumps(config, indent=4))
    f.close()


if __name__ == "__main__":
    cli()
