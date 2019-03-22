import argparse
import logging

if __package__ is None or __package__ == '':
    import configelper
else:
    from . import configelper

L = logging.getLogger()


def main(raw_args=None):

    parser = argparse.ArgumentParser(description='Runs sentinel tasks for Unreal Engine.',
                                     add_help=True,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-generate", action='store_true')
    parser.add_argument("-path", default="", help="Absolute or relative path to the config directory if other than default")

    args = parser.parse_args(raw_args)

    if args.generate and not args.path:
        L.info("Generating default config")
        configelper.generate_default_config()

    else:
        L.info("Reading config overwrite from: %s ", args.path)
        configelper.assemble_config(args.path)


if __name__ == "__main__":
    main()
