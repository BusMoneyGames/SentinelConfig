import argparse
import logging
import pathlib
if __package__ is None or __package__ == '':
    import configelper
else:
    from . import configelper

L = logging.getLogger()


def main(raw_args=None):

    parser = argparse.ArgumentParser(description='Runs sentinel tasks for Unreal Engine.',
                                     add_help=True,
                                     formatter_class=argparse.RawTextHelpFormatter)

    global_settings = parser.add_argument_group('Global Settings')
    global_settings.add_argument("-config", default="", help="Absolute or relative path to"
                                                             " the config directory if other than default")
    global_settings.add_argument("-debug", action='store_true', help="Enables detailed logging")

    parser.add_argument("-generate", action='store_true')
    parser.add_argument("-path", default="", help="Absolute or relative path to the config directory if other than default")

    args = parser.parse_args(raw_args)

    if args.debug:
        print("Running in debug mode!")
        FORMAT = '%(levelname)s - %(funcName)s - %(message)s'
        logging.basicConfig(format=FORMAT)
        L.setLevel(logging.DEBUG)
    else:
        FORMAT = '%(levelname)s - %(message)s'
        logging.basicConfig(format=FORMAT)
        L.setLevel(logging.DEBUG)

    if args.generate and not args.path:
        L.info("Generating default config")
        configelper.generate_default_config()

    else:

        path = pathlib.Path(args.path).resolve()

        if not path.exists():
            L.error("No config overwrite found at: %s", path.absolute())
            quit(1)

        L.info("Reading config overwrite from: %s ", args.path)
        configelper.assemble_config(args.path)


if __name__ == "__main__":
    main()
