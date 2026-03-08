
from src.core import calculate_valuation
from src.utils import format_valuation

from rich.console import Console
from rich.table import Table



def track_portfolio(portfolio:list)->str:

    console=Console()

    raw_value:float=calculate_valuation(portfolio)
    formatted_value:str=format_valuation(raw_value)


    table=Table(title="[spring_green3]VANGUARD ASSET TRACKER[/spring_green3]")
    table.add_column("Asset",style="yellow2",justify="center")
    table.add_column("Value",style="deep_pink2",justify="right")

    for asset in portfolio:
        table.add_row(asset["name"],format_valuation(asset["value"]))

    console.print(f"[dark_cyan] Total Networth : [/dark_cyan] [green]{formatted_value}[/green]")

    console.print(table)


if __name__=="__main__":

    portfolio=[
        {
            "name":"Amazon",
            "value":191_600_000_000,
            "type":"Public Company"
        },
        {
            "name":"Washington Post",
            "value":250_000_000,
            "type":"Private Media Company"
        },
        {
            "name":"Seattle,Beverly Hills... etc",
            "value":500_000_000,
            "type":"Real Estate"
        },
        {
            "name":"Superyacht Y721",
            "value":500_000_000,
            "type":"Yacht"
        },
        {
            "name":"Bezos Expeditions",
            "value":107_800_000_000,
            "type":"Family Office"
        },
        {
            "name":"Gulfstream G700 & G650ER",
            "value":125_000_000,
            "type":"Private Jet"
        },
        {
            "name":"Blue Origin",
            "value":80_000_000_000,
            "type":"Private Aerospace Company"
        }
    ]

    track_portfolio(portfolio)

    



