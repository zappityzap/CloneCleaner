from typing import Union, List, Any

class State:
    enable: bool = False
    only_adetailer: bool = False
    gender:str  = "female"
    insert_start: bool = True
    declone_weight: Union[float, int] = 1.0
    use_main_seed: bool = True
    fixed_batch_seed: bool = False
    declone_seed: int = -1
    use_components: List[str] = ["name", "country", "hair length", "hair color", "hair style"]
    exclude_regions: List[str] = []
    exclude_hairlength: List[str] = []
    exclude_haircolor: List[str] = []
    exclude_hairstyle: List[str] = []


instance = State()
