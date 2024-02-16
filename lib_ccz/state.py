from typing import Union, List, Any
from scripts.clonecleanerz_logger import logger_clonecleanerz as logger

class State:
    enable: bool = False
    only_adetailer: bool = False
    gender: str  = "female"
    insert_start: bool = True
    declone_weight: Union[float, int] = 1.0
    use_main_seed: bool = True
    fixed_batch_seed: bool = False
    declone_seed: int = -1
    components: List[str] = ["name", "country", "hair length", "hair color", "hair style"]
    exclude_regions: List[str] = []
    exclude_hairlength: List[str] = []
    exclude_haircolor: List[str] = []
    exclude_hairstyle: List[str] = []


state = State()
xyz_attrs: dict = {}

def apply_xyz():
    global state
    logger.debug("apply_xyz(): entered")
    for k, v in xyz_attrs.items():
        logger.debug(f"applying k={k}, v={v}")
        setattr(state, k, v)
