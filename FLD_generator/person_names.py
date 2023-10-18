from typing import Optional, List, Union, Dict
from names_dataset import NameDataset, NameWrapper
from functools import lru_cache

_ND: Optional[NameDataset] = None


@lru_cache(maxsize=100)
def get_person_names(country='US',
                     details=False) -> Union[List[str], Dict[str, str]]:
    top_n=1000  # we do not allow users to specify top_n to manage this parameter only here

    global _ND
    if _ND is None:
        _ND = NameDataset(load_first_names=True, load_last_names=False)
    names = _ND.get_top_names(n=top_n, country_alpha2=country)
    male_names = [_uppercase(name) for name in names[country]['M']]
    female_names = [_uppercase(name) for name in names[country]['F']]

    if details:
        return [{'name': name, 'gender': 'M'} for name in male_names]\
            + [{'name': name, 'gender': 'F'} for name in female_names]
    else:
        return male_names + female_names


def _uppercase(name: str) -> str:
    return name[0].upper() + name[1:]
