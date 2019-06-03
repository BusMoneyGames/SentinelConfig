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
@click.option('--project_root', default="", help="path to the config overwrite folder")
@click.option('--skip_version', default=False, help="Skips output version")
@click.option('--debug', default=False, help="Turns on debug messages")
@click.pass_context
def cli(ctx, project_root, debug, skip_version):
    """Sentinel Unreal Component handles running commands interacting with unreal engine"""

    ctx.ensure_object(dict)
    ctx.obj['CONFIG_OVERWRITE'] = project_root
    ctx.obj['SKIP_VERSION'] = skip_version

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
        print("Generated config...")
    elif output == 'json':
        print(json.dumps({"message": "Generated Config"}, indent=4))


if __name__ == "__main__":
    cli()
