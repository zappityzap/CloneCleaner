import sys
from types import ModuleType
from typing import Optional
from modules import scripts
from lib_ccz.state import state, xyz_attrs
from scripts.clonecleanerz_logger import logger_clonecleanerz as logger

def patch():
    xyz_module = find_xyz_module()
    if xyz_module is None:
        logger.warning("XYZ module not found.")
        return
    MODULE = "[CCZ]"
    xyz_module.axis_options.extend([
        xyz_module.AxisOption(
            label=f"{MODULE} Enabled",
            type=str_to_bool,
            apply=apply_state("enable"),
            choices=choices_bool),
        xyz_module.AxisOption(
            label=f"{MODULE} Only ADetailer",
            type=str_to_bool,
            apply=apply_state("only_adetailer"),
            choices=choices_bool),
        xyz_module.AxisOption(
            label=f"{MODULE} Insert Start",
            type=str_to_bool,
            apply=apply_state("insert_start"),
            choices=choices_bool),
        xyz_module.AxisOption(
            label=f"{MODULE} Declone weight",
            type=int_or_float,
            apply=apply_state("declone_weight")),
        xyz_module.AxisOption(
            label=f"{MODULE} Use main seed",
            type=str_to_bool,
            apply=apply_state("use_main_seed"),
            choices=choices_bool),
        xyz_module.AxisOption(
            label=f"{MODULE} Fixed batch seed",
            type=str_to_bool,
            apply=apply_state("fixed_batch_seed"),
            choices=choices_bool),
        xyz_module.AxisOption(
            label=f"{MODULE} Declone seed",
            type=int_or_float,
            apply=apply_state("declone_seed")),
        xyz_module.AxisOption(
            label=f"{MODULE} Components",
            type=str,
            apply=apply_components("use_components"),
            choices=lambda: ["name", "country", "hair length", "hair color", "hair style"]),
        ])


def apply_state(k, key_map=None):
    def callback(_p, v, _vs):
        if key_map is not None:
            v = key_map[v]
        xyz_attrs[k] = v

    return callback

def apply_components(k, key_map=None):
    logger.debug(f"apply_components(): entered, k={k}, key_map={key_map}")
    def callback(_p, v, _vs):
        logger.debug(f"callback to apply_components(): entered, _p={_p}, v={v}, _vs={_vs}")
        if key_map is not None:
            v = key_map[v]
        xyz_attrs[k] = v

    return callback
        

def str_to_bool(string):
    string = str(string)
    if string in ["None", ""]:
        return None
    elif string.lower() in ["true", "1"]:
        return True
    elif string.lower() in ["false", "0"]:
        return False
    else:
        raise ValueError(f"Could not convert string to boolean: {string}")


def int_or_float(string):
    try:
        return int(string)
    except ValueError:
        return float(string)


def choices_bool():
    return ["False", "True"]



def find_xyz_module() -> Optional[ModuleType]:
    for data in scripts.scripts_data:
        if data.script_class.__module__ in {"xyz_grid.py", "xy_grid.py"} and hasattr(data, "module"):
            return data.module

    return None
