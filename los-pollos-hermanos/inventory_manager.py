
meth_lab : dict = {
    "Albuquerque Central":[
        {
            "name":"Heisenberg",
            "quantity":200,
            "item":"Blue Sky",
            "is_Legit":False
        },
        {
            "name":"Capn Cook",
            "quantity":30,
            "item":"Chilli Meth",
            "is_Legit":False
        }
    ],
    "Madrigal Electromotives":[
        {
            "name":"Gustavo Fring",
            "quantity":16,
            "item":"los pollos hermanos",
            "is_Legit":True
        },
        {
            "name":"Peter Schuler",
            "quantity":13000000,
            "item":"money laundering",
            "is_Legit":False
        }
    ],
    "Las Cruces":[
        {
            "name":"Don Eladio",
            "quantity":40,
            "item":"Cheap Meth",
            "is_Legit":False
        }
    ]
}

def add_stock():
    for location,data in meth_lab.items():
        if location=="Albuquerque Central":
            data[0]["quantity"]=data[0]["quantity"]+50
            print(f"{data[0]["name"]}'s meth quantity is now {data[0]["quantity"]}")
            data[1]["quantity"]=data[1]["quantity"]+10
            print(f"{data[1]["name"]}'s meth quantity is now {data[1]["quantity"]}")


def company_insider():
    for location,data in meth_lab.items():
        if location=="Madrigal Electromotives":
            for i in data:
                if i["name"]=="Gustavo Fring":
                    print(f"{i["name"]} holds {i["quantity"]} fast food chains across US called the {i["item"]}")
                if i["name"]=="Peter Schuler":
                    print(f"{i["name"]} the executive of {location} has done {i["quantity"]} in cash through {i["item"]}")

def dispatch_shipment():
    print(f"the meth is now ready to go!!!")
    meth_lab["Albuquerque Central"][0]["quantity"]=0
    meth_lab["Albuquerque Central"][1]["quantity"]=0

def audit_inventory():
    meth_producers=meth_lab["Albuquerque Central"]
    for producer in meth_producers:
        if producer["quantity"]<10:
            print(f"{producer["name"]} has only {producer["quantity"]} pounds of {producer["item"]} [LOW STOCK ALERT!!]")

    #flag illegal items
    for location,data in meth_lab.items():
        for producer in data:
            if not producer["is_Legit"]:
                print(f"{producer["name"]} is in posession of illegal items")


if __name__=="__main__":
    print(f"testing stock addition")
    add_stock()
