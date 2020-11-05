import argparse
import shutil
import tempfile
from pathlib import Path

from tqdm import tqdm

from .graph import Graph, Package, Contributor
from .utils import read_csv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename")
    parser.add_argument("output_path")
    parser.add_argument("--template-dir", default=str(Path(__file__).parent / "template"))
    parser.add_argument("--temp-dir", default=str(Path(tempfile.gettempdir()) / "repositories"))
    args = parser.parse_args()

    input_filename = args.input_filename
    # TODO: check if input_filename has needed columns

    output_path = Path(args.output_path)
    output_filename = output_path / "data" / "network.json"
    image_path = output_path / "static" / "img"

    templates_path = Path(args.template_dir)
    shutil.copytree(templates_path, output_path)

    temp_path = Path(args.temp_dir)

    graph = Graph()

    # First, add nodes and save contributors
    iterator = tqdm(read_csv(input_filename))
    for package_data in iterator:
        iterator.desc = f"Extracting repository data: {package_data['name']}"
        iterator.refresh()
        package_data.pop("depended_by")
        package_data["repository_path"] = temp_path / package_data["name"]
        package = Package(**package_data)
        graph.add_node(package.serialize())

        filename = output_path / "data" / f"{package.id}.json"
        if not filename.exists():
            package.save_contributors(filename, output_path, image_path)

    # Then, add edges
    iterator = tqdm(read_csv(input_filename))
    for package_data in iterator:
        iterator.desc = f"Adding dependencies: {package_data['name']}"
        iterator.refresh()
        depended_by = package_data.pop("depended_by")
        if depended_by:
            graph.add_edge(
                from_id=graph.get_node_by_name(depended_by)["id"],
                to_id=graph.get_node_by_name(package_data["name"])["id"],
                label="depends on",
                width=10,
                color="blue",
            )

    print("Exporting network JSON...", end="", flush=True)
    graph.save(output_filename)
    print()


if __name__ == "__main__":
    main()
