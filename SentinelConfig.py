import argparse
import configelper

def main(raw_args=None):

    print(raw_args)
    parser = argparse.ArgumentParser(description='Runs sentinel tasks for Unreal Engine.',
                                     add_help=True,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-default", action='store_true')

    args = parser.parse_args(raw_args)

    if args.default:
        configelper.generate_default_config()
        print("default")


if __name__ == "__main__":
    main()
