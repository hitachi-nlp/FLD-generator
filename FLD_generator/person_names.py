from typing import Optional, List
from names_dataset import NameDataset, NameWrapper
from functools import lru_cache

_ND: Optional[NameDataset] = None


@lru_cache(maxsize=100)
def get(country='US', top_n=1000) -> List[str]:
    global _ND
    if _ND is None:
        _ND = NameDataset(load_first_names=True, load_last_names=False)
    names = _ND.get_top_names(n=top_n, country_alpha2=country)
    male_names = names[country]['M']
    female_names = names[country]['F']
    return male_names + female_names
