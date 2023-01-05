import importlib
import importlib.util
import os
import os.path
from typing import Iterable

from datapipeline import DataPipeline


def load_next_pipeline(adapters_folder: str) -> Iterable[DataPipeline]:
    # module_already_loaded = set()
    for root, _, files in os.walk(adapters_folder):
        for file in files:
            if not file.endswith(".py"):
                continue
            module_name = os.path.basename(os.path.splitext(file)[0])
            if not (
                module_spec := importlib.util.spec_from_file_location(
                    module_name, root + "/" + file
                )
            ):
                continue
            if not (loader := module_spec.loader):
                continue
            module_loaded = importlib.util.module_from_spec(module_spec)
            loader.exec_module(module_loaded)
            #            if not (export := module_loaded.__dict__.get("export")):
            if not (export := getattr(module_loaded, "export", None)):
                del module_loaded
                continue
            # pipeline: DataPipeline
            # for pipeline in export:
            # if type(pipeline) in module_already_loaded:
            #     print(
            #         f"Data pipeline with type {type(pipeline)} already loaded. {pipeline} not accepted"
            #     )
            #     del pipeline
            #    continue
            # module_already_loaded.add(type(pipeline))
            yield from export


def load_list_pipeline(adapters_folder: str) -> list[DataPipeline]:
    return list(load_next_pipeline(adapters_folder))


if __name__ == "__main__":
    adapters = load_list_pipeline(os.getcwd() + "/adapters")
    for adapter in adapters:
        print(adapter)
