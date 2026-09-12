from langchain_core.tools import tool


@tool
def calculate(expression: str) -> str:
    """
    Calculate a mathematical expression.

    Use this tool when the user asks for calculations
    such as budget per person, total cost, percentages,
    or other mathematical operations.
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception:
        return "Unable to calculate the expression."