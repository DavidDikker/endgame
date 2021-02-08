#! /usr/bin/env python
import click
from endgame import command
from endgame.bin.version import __version__


@click.group()
@click.version_option(version=__version__)
def endgame():
    """
    Expose AWS resources automagically
    """


endgame.add_command(command.list_resources.list_resources)
endgame.add_command(command.expose.expose)
endgame.add_command(command.smash.smash)


def main():
    """Expose AWS resources automagically"""
    endgame()


if __name__ == "__main__":
    main()
