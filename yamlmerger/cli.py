#!/usr/bin/env python
import sys
from logging import getLogger
from pathlib import Path
from typing import List

import click
import yaml

from .merger import get_strategic_merger

log = getLogger(__name__)


@click.command()
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(),
)
@click.option(
    "-r",
    "--recursive",
    is_flag=True,
    type=bool,
    help="Traverse given directory",
)
@click.option(
    "-o",
    "--output",
    default=None,
    type=click.Path(),
    help="Output file. Defaults to the stdout.",
)
@click.option(
    "-k",
    "--key",
    default="name",
    type=str,
    help="Which key to use for strategy patch.",
    show_default=True,
)
@click.help_option("-h", "--help")
def cli(files: List[click.Path], recursive: bool, output: click.Path, key: str):
    merger = get_strategic_merger(keyname=key)
    result = {}
    if not files:
        log.error("No files given.")
        sys.exit(1)

    # if recursive, then files must be a directory
    if recursive:
        paths = [Path(f) for f in files]
        files = []
        for path in paths:
            if not path.is_dir():
                continue
            files += list(path.glob("**/*.yaml"))

    for file in files:
        file = Path(file)
        if not file.exists():
            log.warn("File {file} does not exist. Skipping.".format(file=file.name))
            continue

        log.debug("Opening file {file}".format(file=file.name))
        with open(file) as fp:
            buffer = yaml.load(fp, Loader=yaml.SafeLoader)

        result = merger.merge(result, buffer)

    if not output:
        print(yaml.safe_dump(result))
        return

    with open(output, "w") as fp:
        yaml.safe_dump(result, fp)


if __name__ == "__main__":
    cli()
