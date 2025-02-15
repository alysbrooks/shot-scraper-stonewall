import urllib.parse
import pathlib
import sys
import os.path

def add_url(url):

    parsed_url = urllib.parse.urlparse(url)

    output = (pathlib.Path("./screenshots") /
              pathlib.Path(parsed_url.path).relative_to("/")).with_suffix(".png")

    with open("shots.yml", "a") as f:
        f.write(f""" - url: {url}
   output: {output}\n""")

def print_html_command(url):

    parsed_url = urllib.parse.urlparse(url)

    output = (pathlib.Path("html/") /
              pathlib.Path(parsed_url.path).relative_to("/"))

    print(f"shot-scraper html {url} {output}")


def process_args(args):
    for arg in args:
        if arg.startswith("http"):
            add_url(arg.strip())
            print_html_command(arg.strip())
        else:
            with open(arg) as f:
                for line in f.readlines():
                    add_url(line.strip())
                    print_html_command(line.strip())





if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("provide either")
    else:
        _command, *args = sys.argv

        process_args(args)
