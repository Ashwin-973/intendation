


def format_valuation(value:float)->str:
    if value>=1000_000_000:
        return f"${value/1000_000_000}:.2f"
    elif value>=1000_000:
        return f"${value/1000_000}:.2f"
    else:
        return f"${value}"
    
