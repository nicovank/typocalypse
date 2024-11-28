import argparse
import os

from . import typocalypse


def process_file(args: argparse.Namespace, path: str) -> None:
    with open(path, "r") as file:
        code = file.read()
    code = typocalypse.transform(code, args.override_existing)
    with open(path, "w") as file:
        file.write(code)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--override-existing", action="store_true")
    parser.add_argument("path", type=str, help="path to a file or directory")
    args = parser.parse_args()

    if os.path.isfile(args.path):
        process_file(args, args.path)
    elif os.path.isdir(args.path):
        for root, _, files in os.walk(args.path):
            for file in files:
                if file.endswith(".py"):
                    process_file(args, os.path.join(root, file))
    else:
        raise ValueError(f"invalid path: {args.path}")


if __name__ == "__main__":
    main()
