"""Miniature utility to create database.


"""

import pathlib
import os
import sqlite3
import typing
import itertools
import datetime

import click
import rich.console
import rich.progress
import git

BATCH_SIZE = 100

T = typing.TypeVar("T")

def batched(iterable: typing.Iterable[T], n: int) -> typing.Iterator[typing.Collection[T]]:
    """Rough code from documentation.

    Python 3.12 adds this to the standard itertools module, so this is a
    backport, more or less. Note that CPython actually implements this in C.

    Example: batched('ABCDEFG', 3) → ABC DEF G"""
    if n < 1:
        raise ValueError('n must be at least one')
    iterator = iter(iterable)
    batch = tuple(itertools.islice(iterator, n))
    while batch:
        yield batch
        batch = tuple(itertools.islice(iterator, n))

cli = click.Group()

def create_database_schema(path: pathlib.Path):

    database = sqlite3.connect(path)


    page_schema = """CREATE TABLE pages
    (page_id INTEGER PRIMARY KEY,
     url TEXT,
     status_code INTEGER)
    """

    database.execute(page_schema)

    html_snapshot = """CREATE TABLE html_snapshots
    (html_shapshot_id INTEGER PRIMARY KEY,
     date INTEGER, --date
     path TEXT,
     contents TEXT)
    """

    database.execute(html_snapshot)

    image_snapshots = """CREATE TABLE image_snapshots
    (image_shapshot_id INTEGER PRIMARY KEY,
     date INTEGER, --date
     path TEXT,
     contents BLOB)
    """

    database.execute(image_snapshots)


@cli.command()
@click.argument("REPOSITORY")
@click.argument("DATABASE")
def create_database(repository, database):
    console = rich.console.Console()

    console.print(f"Creating database from {repository}.")


    create_database_schema(pathlib.Path(database))


    with rich.progress.Progress() as p:
        task = p.add_task("counting files...", total=2)

        screenshots_dir = pathlib.Path("screenshots/")

        screenshots = [pathlib.Path(root) / file for root, dirs, files in os.walk(screenshots_dir)
                       for file in files]

        p.update(task, advance=1)

        html_dir = pathlib.Path("html/")

        html = [pathlib.Path(root) / file for root, dirs, files in os.walk(html_dir)
                       for file in files]
        p.update(task, advance=1)

    console.print(f"Found {len(screenshots)} screenshots and {len(html)} HTML files.")

    repo = git.Repo(repository)

    database = sqlite3.connect(database)

    with rich.progress.Progress() as progress:
        task = progress.add_task("Inserting pages...", total=len(html))
        for html_batch in batched(html, BATCH_SIZE):

            database.executemany("""INSERT INTO pages (url) VALUES (:url)""",
                                 [{"url": f" https://www.nps.gov/{pathlib.Path(file_name).relative_to('html')}"} 
                                  for file_name in html])

            progress.update(task, advance=len(html_batch))


        

    for commit in rich.progress.track(list(repo.iter_commits())):
        # console.print(commit.hexsha)
        for entry in commit.tree.traverse():
            if entry.type == "blob":
                # console.print(entry.name, len(entry.data_stream.read()))
                # console.print(entry.name)
                if entry.name.endswith(".png"):
                    database.execute("""INSERT INTO image_snapshots (date, path, contents)
                                     VALUES (:date, :path, :contents) 
                                     """, {"date": datetime.datetime.fromtimestamp(commit.committed_date),
                                           "path": entry.name,
                                           "contents": entry.data_stream.read()})
                elif ".htm" in entry.name:
                    database.execute("""INSERT INTO html_snapshots (date, path, contents)
                                     VALUES (:date, :path, :contents) 
                                     """, {"date": datetime.datetime.fromtimestamp(commit.committed_date),
                                           "path": entry.name,
                                           "contents": entry.data_stream.read().decode("utf8")})

    database.commit()


if __name__ == "__main__":
    cli()
