import argparse
import logging
import pathlib
import click
import json

if __package__ is None or __package__ == '':
    import configelper
else:
    from . import configelper

L = logging.getLogger()

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
        L.debug("Running with debug messages")
    else:
        L.setLevel(logging.ERROR)

@cli.command()
@click.option('-o','--output', type=click.Choice(['text', 'json']), default='text', help="Output type.")
@click.pass_context
def generate(ctx, output):
    """Generates a config file """

    config_path = ctx.obj['CONFIG_OVERWRITE']
    L.debug("Config Path: %s", config_path)
    
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
