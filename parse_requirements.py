import re
from pathlib import Path

REGEXP_PACKAGE_NAME_VERSION = re.compile("[ ><=,]")


# TODO: search inside setup.py files (`install_requires`)
# TODO: search inside Pipfile files


def parse_all_requirements(path):
    """Yield each Python requirement inside any requirements file in a path

    Will search recursively for files like:
    - `requirements.txt`
    - `dev-requirements.txt`
    - `requirements-dev.txt`
    and for each of them, yield each package
    """

    if not isinstance(path, Path):  # str
        path = Path(path)
    for filename in path.glob("**/*.txt"):
        if "requirements" in filename.name.lower():
            for package in parse_requirements(filename):
                yield filename, package


def parse_requirements(filename):
    """Yield each package name inside a requirements.txt filename"""

    with open(filename) as fobj:
        for line in fobj:
            package = parse_requirements_line(line)
            if package is not None:  # None when empty line or comment
                yield package


def parse_requirements_line(line):
    """
    >>> repr(parse_requirements_line(''))
    'None'
    >>> repr(parse_requirements_line('# Hello, comment!'))
    'None'
    >>> parse_requirements_line('rows ')
    'rows'
    >>> parse_requirements_line('rows >= 0.4.0')
    'rows'
    >>> parse_requirements_line('rows==0.4.2')
    'rows'
    >>> parse_requirements_line('https://github.com/turicas/rows/archive/develop.zip')
    'https://github.com/turicas/rows/archive/develop.zip'
    """

    line = line.strip()
    if not line or line.startswith("#") or line.startswith("-"):
        return None

    elif line.startswith("http:") or line.startswith("https:"):
        return line
    else:
        return REGEXP_PACKAGE_NAME_VERSION.split(line)[0]


def print_status(text):
    """Print a status text message, cleaning the last printed line"""

    if not hasattr(print_status, "last_status_len"):
        print_status.last_status_len = 0
    print("\r" + " " * print_status.last_status_len, end="", flush=True)
    print("\r" + text, end="", flush=True)
    print_status.last_status_len = len(text)


if __name__ == "__main__":
    import argparse
    import csv

    parser = argparse.ArgumentParser()
    parser.add_argument("output_filename")
    parser.add_argument("path", nargs="+")
    args = parser.parse_args()
    current_path = Path(".").absolute()

    with open(args.output_filename, mode="w") as fobj:
        writer = csv.DictWriter(fobj, fieldnames=["repository_path", "requirements_filename", "package"])
        writer.writeheader()
        total_found = 0
        last_status_len = 0
        for path in args.path:
            path = Path(path).absolute()
            repository_path = str(path.relative_to(current_path))
            for found_inside_package, (filename, package) in enumerate(parse_all_requirements(path), start=1):
                writer.writerow({"repository_path": repository_path, "requirements_filename": filename.name, "package": package})
                total_found += 1
                print_status(f"Searching {repository_path}...  {found_inside_package:02d} found (total: {total_found:03d})")
        print_status(f"Done! Check {args.output_filename} for results.\n")
