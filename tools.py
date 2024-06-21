import inspect
from inspect import signature
from typing import List

from components.data_loaders.base import BaseDataLoader


def render_text_description(tools: List, ignored_parameters=None) -> str:
    """Render the tool name and description in plain text.

    Output will be in the format of:

    .. code-block:: markdown

        search: This tool is used for search
        calculator: This tool is used for math
    """
    descriptions = []
    for tool in tools:
        sig = signature(tool)
        new_params = {
            k: v for k, v in sig.parameters.items() if k not in ignored_parameters
        }
        new_sig = sig.replace(parameters=new_params.values())
        description = f"{tool.__name__}{new_sig} - {tool.__doc__}"
        descriptions.append(description)
    return "\n".join(descriptions)


def get_required_parameters(function):
    sig = inspect.signature(function)
    params = sig.parameters
    required_params = [
        name
        for name, param in params.items()
        if param.default == param.empty and name != "self"
    ]
    return required_params


def book_hotel_tool(id: int) -> str:
    """Book hotel by a provided id. Id can be obtained from search_hotels_mock."""
    return "successfully booked"


def search_hotels_tool(
    location: str,
    checkin_date: str,
    checkout_date: str,
    adults_number: int,
    data_loader: BaseDataLoader,
    children_number: int = 0,
    order_by: str = "popularity",
    min_rating=None,
    min_price=None,
    max_price=None,
) -> List:
    """Search for hotels in a given parameters."""
    return data_loader.load_with_filters(
        location=location,
        min_rating=min_rating,
        min_price=min_price,
        max_price=max_price,
        order_by=order_by,
        adults_number=adults_number,
        children_number=children_number,
        checkin_date=checkin_date,
        checkout_date=checkout_date,
    )
