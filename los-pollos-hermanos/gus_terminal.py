from rich import print
from inventory_manager import add_stock,company_insider,audit_inventory,dispatch_shipment

while True:
    menu:str=(
        f"[cyan]1. Add Stock[/cyan]\n"
        f"[green]2. Company Insider[/green]\n"
        f"[orange]3. Audit Inventory[/orange]\n"
        f"[black]4. Dispatch Shipment[/black]\n"
        f"[bright_red]5. Exit[/bright_red]\n"
    )
    print(menu)

    user_input:int=int(input("Enter your Choice : "))
    
    print(f"you chose {user_input}")

    if user_input==1:
        add_stock()
    elif user_input==2:
        company_insider()
    elif user_input==3:
        audit_inventory()
    elif user_input==4:
        dispatch_shipment()
    elif user_input==5:
        break
    else:
        print(f"{user_input} is invalid , it's not on the menu")





