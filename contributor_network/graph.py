import hashlib
import json
import shlex
import subprocess
import tempfile
from collections import Counter
from dataclasses import dataclass
from email.utils import getaddresses
from pathlib import Path
from urllib.request import urlopen

from .utils import transform


BASE_PATH = Path(__file__).parent
DATA_PATH = BASE_PATH / "data"
IMAGE_PATH = DATA_PATH / "img"


def list_contributors(repository_type, repository_url, path):
    if repository_type not in ("git", "hg"):
        raise NotImplementedError(f"Unknown repository type: {repr(repository_type)}")

    save_path = (Path(path) / Path(repository_url).name).absolute()
    if not save_path.parent.exists():
        save_path.parent.mkdir(parents=True)

    if not save_path.exists():  # clone repository
        command = f'{repository_type} clone "{repository_url}" "{save_path}"'
        subprocess.check_output(shlex.split(command), stderr=subprocess.PIPE)

    lines = subprocess.check_output(
        shlex.split(f"{repository_type} log"), cwd=save_path, encoding="utf-8",
    ).splitlines()
    c = Counter()
    if repository_type == "git":
        author_key = "Author:"
    elif repository_type == "hg":
        author_key = "user:"

    names = {}
    for line in lines:
        if not line.startswith(author_key) or "@" not in line:
            continue
        name, email = getaddresses([line[len(author_key) :].strip()])[0]
        email = email.strip().lower()
        names[email] = name
        c[email] += 1
    for email, commits in c.most_common():
        yield (names.get(email, email), email, commits)


@dataclass
class Package:
    name: str
    repository_type: str
    repository_url: str
    repository_path: str

    @property
    def id(self):
        return f"package:{self.name}"

    def serialize(self):
        return {
            "group": "package",
            "id": self.id,
            "label": self.name,
            "name": self.name,
            "shape": "circle",
        }

    def contributors(self):
        if not hasattr(self, "_contributors"):
            iterator = list_contributors(
                self.repository_type, self.repository_url, self.repository_path
            )
            self._contributors = [
                Contributor(name=name, email=email, commits=commits, package=self)
                for name, email, commits in iterator
            ]
        yield from self._contributors

    @property
    def min_commits(self):
        if not hasattr(self, "_min_commits"):
            self._min_commits = min(contributor.commits for contributor in self.contributors())
        return self._min_commits

    @property
    def max_commits(self):
        if not hasattr(self, "_max_commits"):
            self._max_commits = max(contributor.commits for contributor in self.contributors())
        return self._max_commits

    @property
    def commits(self):
        if not hasattr(self, "_commits"):
            self._commits = sum(contributor.commits for contributor in self.contributors())
        return self._commits

    def save_contributors(self, filename, base_path, image_path):
        image_path = Path(image_path)
        graph = Graph()
        for contributor in self.contributors():
            node = contributor.serialize()
            if "image" in node and (
                    node.get("image", "").startswith("http://") or
                    node.get("image", "").startswith("https://")
                ):
                image_filename = image_path / str(node["id"])
                if not image_filename.exists():
                    if not image_filename.parent.exists():
                        image_filename.parent.mkdir(parents=True)
                    response = urlopen(node["image"])
                    node["image"] = str(image_filename.relative_to(base_path))
                    with open(image_filename, mode="wb") as fobj:
                        fobj.write(response.read())
            graph.add_node(node)
            graph.add_edge(
                from_id=contributor.id,
                to_id=contributor.package.id,
                label="contributed to",
                width=contributor.commit_weight,
            )

        graph.save(filename)


@dataclass
class Contributor:
    name: str
    email: str
    commits: int
    package: Package

    @property
    def email_hash(self):
        return hashlib.md5(self.email.strip().lower().encode("utf-8")).hexdigest()

    @property
    def id(self):
        return f"person:{self.email_hash}"

    @property
    def avatar_url(self):
        return f"https://www.gravatar.com/avatar/{self.email_hash}"

    @property
    def commit_weight(self):
        return transform(self.commits, self.package.min_commits, self.package.max_commits, 1, 10)

    def serialize(self):
        return {
            "group": "person",
            "id": self.id,
            "image": self.avatar_url,
            "label": self.name,
            "shape": "circularImage",
        }


class Graph:

    def __init__(self):
        self.__nodes_by_id = {}
        self.__nodes_by_name = {}
        self.__edges = []

    def add_node(self, node):
        self.__nodes_by_id[node["id"]] = node
        if "name" in node:
            self.__nodes_by_name[node["name"]] = node

    def get_node_by_name(self, name):
        return self.__nodes_by_name[name]

    def add_edge(self, from_id, to_id, label, width=1, color="black"):
        self.__edges.append(
            {
                "from": from_id,
                "label": label,
                "to": to_id,
                "width": width,
                "color": color,
            }
        )

    def save(self, filename):
        filename = Path(filename)
        if not filename.parent.exists():
            filename.parent.mkdir(parents=True)
        with open(filename, mode="w") as fobj:
            json.dump(
                {
                    "nodes": list(self.__nodes_by_id.values()),
                    "edges": self.__edges,
                },
                fobj,
            )
