import logging
import pathlib
import click
import json
import os

if __package__ is None or __package__ == '':
    import configelper
else:
    from . import configelper

L = logging.getLogger()

CONFIG_SETTINGS_FILE_NAME = "_sentinelConfig.json"


def _load_environment_config(overwrite_path=""):
    """Finds the config file that contains the environment information"""

    if overwrite_path:
        L.debug("environment config read from none default location")
        L.debug("environment config read from: %s", overwrite_path)

    # Figure out where the script is run from
    current_run_directory = pathlib.Path(os.getcwd())
    L.debug("Current Directory: %s ", current_run_directory)

    config_file_path = current_run_directory.joinpath(overwrite_path, CONFIG_SETTINGS_FILE_NAME)
    L.debug("Searching for environment file at: %s", config_file_path)
    L.debug("environment file exists: %s ", config_file_path.exists())

    if config_file_path.exists():
        return config_file_path
    else:
        L.error("Unable to find config environment file")
        L.error("Expected Path: %s", config_file_path)
        quit(1)


@click.group()
@click.option('--path', default="", help="path to the config overwrite folder")
@click.option('--debug', default=False, help="Turns on debug messages")
@click.pass_context
def cli(ctx, path, debug):
    """Sentinel Unreal Component handles running commands interacting with unreal engine"""

    ctx.ensure_object(dict)
    ctx.obj['CONFIG_OVERWRITE'] = path

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
    sentinel_config = _load_environment_config(config_path)

    L.debug("Found Sentinel Config at: %s", sentinel_config)

    return
    if not config_path:
        L.debug("Generating default config")
        configelper.generate_default_config()

    else:
        path = pathlib.Path(config_path).resolve()

        if not path.exists():
            L.error("No config overwrite found at: %s", path.absolute())
            quit(1)

            configelper.assemble_config(path)

    #TODO output
    if output == 'text':
        print("Generated config...")
    elif output == 'json':
        print(json.dumps({"message":"Generated Config"}, indent=4))


if __name__ == "__main__":
    cli()
