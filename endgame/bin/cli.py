#! /usr/bin/env python
import click
from endgame import command
from endgame.bin.version import __version__


@click.group()
@click.version_option(version=__version__)
def endgame():
    """
    An AWS Pentesting tool that lets you use one-liner commands to backdoor an AWS account's resources with a rogue AWS account - or share the resources with the entire internet 😈
    """


endgame.add_command(command.list_resources.list_resources)
endgame.add_command(command.expose.expose)
endgame.add_command(command.smash.smash)


def main():
    """
    An AWS Pentesting tool that lets you use one-liner commands to backdoor an AWS account's resources with a rogue AWS account - or share the resources with the entire internet 😈
    """
    endgame()


if __name__ == "__main__":
    main()
