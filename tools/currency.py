import requests
from langchain_core.tools import tool


@tool
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str
) -> str:
    """
    Convert an amount from one currency to another.

    Use this tool when the user asks to convert money
    between different currencies.
    """

    try:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        url = "https://api.frankfurter.app/latest"

        response = requests.get(
            url,
            params={
                "amount": amount,
                "from": from_currency,
                "to": to_currency
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        converted_amount = data["rates"][to_currency]

        return (
            f"{amount:.2f} {from_currency} = "
            f"{converted_amount:.2f} {to_currency}"
        )

    except requests.RequestException as e:
        return f"Currency API error: {str(e)}"

    except KeyError:
        return (
            f"Currency conversion from "
            f"{from_currency} to {to_currency} is unavailable."
        )

    except Exception as e:
        return f"Unexpected error: {str(e)}"