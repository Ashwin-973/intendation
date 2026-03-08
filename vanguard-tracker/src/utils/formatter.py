


def format_valuation(value:float)->str:
    if value>=1000_000_000:
        return f"${(value/1000_000_000):.2f}B"
    elif value>=1000_000:
        return f"${(value/1000_000):.2f}M"
    else:
        return f"${value}"
    
if __name__=="__main__":
    print(format_valuation(1300600000))