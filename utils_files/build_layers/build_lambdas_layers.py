""" Build Layer script for AWS Lambdas """

import os
import sys
import subprocess
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="Path to librairy folder", required=True)
    path = parser.parse_args().path

    # Don't hardcode path to give flexibility with layers building
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../", path)

    print(f"Creating layers in {path}")
    dirs_list = os.listdir(path)

    requirements_files_list = [
        req for req in dirs_list if ".".join(req.split(".")[1:]) == "requirements.txt"
    ]

    for req in requirements_files_list:
        layer = req.split(".")[0]
        req_path = os.path.join(path, req)
        layer_path = os.path.join(path, layer, "python")

        if layer not in dirs_list:
            print(f"Creating layer {layer}")
            os.mkdir(os.path.join(path, layer))

        subprocess.call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "-r",
                req_path,
                "-t",
                layer_path,
            ]
        )
