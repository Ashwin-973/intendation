

def calculate_valuation(assets:list)->float:
    tot_value : float=0.0
    for asset in assets:
        if asset["type"]=="Private Jet":
            tot_value+=asset["value"]*0.9
        elif asset["type"]=="Collectible":
            tot_value+=asset["value"]*1.05
        else:
            tot_value+=asset["value"]  

    return tot_value


if __name__=="__main__":
    print(calculate_valuation([
        {
            "name":"Amazon",
            "value":191_600_000_000,
            "type":"Public Company"
        },
        {
            "name":"Washington Post",
            "value":250_000_000,
            "type":"Private Company"
        }
    ]))

