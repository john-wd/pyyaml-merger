#!/usr/bin/env python
from typing import List
import click
from logging import getLogger
from pathlib import Path
from .merger import get_strategic_merger
import yaml

log = getLogger(__name__)


@click.command()
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(),
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
def cli(files: List[click.Path], output: click.Path, key: str):
    merger = get_strategic_merger(keyname=key)
    result = {}
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
