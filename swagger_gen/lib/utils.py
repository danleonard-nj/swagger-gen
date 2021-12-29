from typing import Any, Iterable, Union


def element_at(_iterable: Iterable[Any], index: int) -> Union[Any, None]:
    '''
    Returns the element at the specified index if it exists, and
    None if it doesn't
    '''
    try:
        return _iterable[index]
    except:
        return None


def empty(_iterable: Iterable) -> bool:
    '''
    Checks if the iterable contains no elements

    _iterable   :   the iterable to check
    '''

    if len(_iterable) == 0:
        return True
    return False
