import inspect
from typing import Any, Iterable, Tuple, Union


def element_at(_iterable: Iterable[Any], index: int) -> Union[Any, None]:
    '''
    Returns the element at the specified index if it exists, and
    None if it doesn't
    '''
    try:
        return _iterable[index]
    except:
        return None


def first(_iterable, func):
    for item in _iterable:
        if func(item):
            return item


def validate_constant(constant_class, value: Any) -> bool:
    class_members = inspect.getmembers(
        constant_class, lambda x: not(inspect.isroutine(x)))

    class_attribs = [
        x[1] for x in class_members
        if not(x[0].startswith('__')
               and x[0].endswith('__'))]

    if value not in class_attribs:
        raise Exception(
            f'Member {value} does not exist in class {constant_class.__name__}')
    return True


def not_null(param: Any, name: str):

    if not param:
        raise Exception(f'{name} cannot be null')


def is_type(param: Any, name: str, _type: Union[type, Tuple[type]], null=True) -> bool:
    if not null:
        not_null(param, name)

    if null and param is None:
        return True

    if not isinstance(param, _type):
        _type_name = (', '.join(
            [x.__name__ for x in _type])
            if isinstance(_type, tuple)
            else _type.__name__)
        raise Exception(f"{name} must be of type '{_type_name}'")
    return True


def defined(param: Any):
    if param is not None:
        return True
    return False
