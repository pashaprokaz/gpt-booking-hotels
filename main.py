from datetime import datetime, timezone
from typing import List

from langchain_core.language_models.chat_models import (
    BaseChatModel,
)
from langchain_core.prompts import ChatPromptTemplate

from chat_models.chat_unsloth import ChatUnsloth
from components.data_loaders.base import BaseDataLoader
from components.data_loaders.mock import MockDataLoader
from tools import (
    book_hotel_tool,
    get_required_parameters,
    render_text_description,
    search_hotels_tool,
)
from utils import str_to_json

days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


search_hotels_system_prompt = """
Current time: {current_time} UTC ({week_day})
You are an assistant who can search and book a hotel for a user.
Hotel search and reservations are made through the use of the following tools:

{rendered_tools}

 Here is a list of possible parameters and their values:
-location: str -> often just the name of the city
-checkin_date: str -> format: YYYY-MM-DD
-checkout_date: str -> format: YYYY-MM-DD
-adults_number: int
-children_number: int
-min_rating: int -> must be in the range from 0 to 10
-min_price: int
-max_price: int
-order_by: str -> possible values: popularity, price, rating
-id: int -> it is used exclusively when booking, when the search has already been called

Given the user input, return the name and input of the tool to use. Return your response as a JSON blob with 'name' and 'arguments' keys.

The `arguments` should be a dictionary, with keys corresponding to the argument names and the values corresponding to the requested values.
If the user has not provided some important information, you still need to send a json blob.
Don't make up the argument values yourself! Take only what the user specified!
"""


def format_hotels_json(hotels_json) -> str:
    result_str = ""
    for hotel in hotels_json:
        for key, value in hotel.items():
            result_str += f"{key}: {value}\n"
        result_str += "\n"

    return result_str


def book_hotel_with_llm(
    llm: BaseChatModel,
    tools: List,
    data_loader: BaseDataLoader = None,
):
    ignored_parameters = ["data_loader"]
    required_parameters_for_book = get_required_parameters(book_hotel_tool)
    required_parameters_for_search = get_required_parameters(search_hotels_tool)
    required_parameters_for_book = set(required_parameters_for_book) - set(
        ignored_parameters
    )
    required_parameters_for_search = set(required_parameters_for_search) - set(
        ignored_parameters
    )

    if data_loader is None:
        data_loader = MockDataLoader()

    history_messages = [("ai", "Tell me which hotel you want to book: ")]
    while True:
        rendered_tools = render_text_description(
            tools, ignored_parameters=["data_loader"]
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", search_hotels_system_prompt),
                *history_messages,
                ("user", "{input}"),
            ]
        )

        query = input(history_messages[-1][1])

        chain = prompt | llm
        llm_output = chain.invoke(
            {
                "input": query,
                "rendered_tools": rendered_tools,
                "current_time": datetime.now(timezone.utc).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "week_day": days[datetime.now(timezone.utc).weekday()],
            }
        ).content
        llm_json_output = str_to_json(llm_output)

        if llm_json_output["name"] == search_hotels_tool.__name__:
            missing_parameters = []
            for key, value in llm_json_output["arguments"].items():
                if value is None and key in required_parameters_for_search:
                    missing_parameters.append(key)
            for key in required_parameters_for_search:
                if key not in llm_json_output["arguments"]:
                    missing_parameters.append(key)

            if missing_parameters:
                clarifying_message = (
                    "Can you provide me with the missing booking parameters: "
                    + ", ".join(missing_parameters)
                    + "?: "
                )
                history_messages.append(("user", query))
                history_messages.append(("ai", clarifying_message))
                continue

            print("searching...")
            tools = [search_hotels_tool, book_hotel_tool]
            history_messages.append(("user", query))
            hotels = search_hotels_tool(
                **llm_json_output["arguments"], data_loader=data_loader
            )
            hotels_message = "Here are the hotels:\n" + format_hotels_json(hotels)
            print(hotels_message)
            history_messages.append(("ai", hotels_message))
            history_messages.append(("ai", "Please, choose a hotel to book: "))
        elif llm_json_output["name"] == book_hotel_tool.__name__:
            missing_parameters = []
            for key, value in llm_json_output["arguments"].items():
                if value is None and key in required_parameters_for_book:
                    missing_parameters.append(key)

            for key in required_parameters_for_book:
                if key not in llm_json_output["arguments"]:
                    missing_parameters.append(key)

            if missing_parameters:
                print("an error occurred when booking")
                return "invalid id"

            print("booking...")
            book_response = book_hotel_tool(**llm_json_output["arguments"])

            return book_response
        else:
            print("error while invoking tool")
            return "unknown tool"


if __name__ == "__main__":
    tools = [search_hotels_tool]

    llm = ChatUnsloth(model_path="pashaprokaz/qwen-7b-instruct-hotel-booking-4bit-v2")

    print(book_hotel_with_llm(llm, tools))
