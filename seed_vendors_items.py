import sqlite3

# Connect to the database
conn = sqlite3.connect("Data/invoice.db")
cursor = conn.cursor()

# Vendor data with associated items and item IDs
vendor_items = {
    "4-M Fruit": [
        ("40565", "Grapes Black Seedless"),
    ],
    "alphas produce": [
        ("15120", "Bok Choy Baby"),
        ("30110", "Basil 1lb"),
        ("30113", "Basil Thai"),
        ("10455", "Daikon Root 5#"),
        ("11020", "Pepper Serrano"),
        ("30140", "Chives Bulk"),
        ("30320", "Rosemary Bulk"),
        ("40470", "Dragon Fruit"),
        ("40650", "Mangoes Kent"),
    ],
    "Community": [
        ("11230", "Potatoes Yams"),
        ("11900", "Potatoes Bakers 90"),
        ("11020", "Potatoes Red A"),
        ("40500", "Limes 10ct"),
        ("40950", "Lemons 95ct"),
        ("40890", "Oranges 113 Navel"),
        ("40510", "Oranges Cara Cara"),
        ("40310", "Pomegranates"),
        ("10381", "Celery 30ct"),
        ("40500", "Grapefruit Pink 32ct"),
    ],
    "Condakes": [
        ("11290", "Radishes Bunch"),
        ("10220", "Beets Bunch"),
        ("10111", "Arugula Baby"),
        ("10290", "Cabbage Green"),
        ("10300", "Cabbage Red"),
        ("10430", "Cukes Dill"),
        ("10440", "Cukes Select"),
        ("10450", "Eggplant"),
        ("10460", "Escarole"),
        ("10540", "Kale"),
        ("11110", "Peppers Wholesale"),
        ("11970", "Peppers Jalapeno"),
        ("11310", "Scallions"),
        ("11482", "Swiss Chard Bright Lights"),
        ("30160", "Dill"),
        ("30300", "Parsley Plain"),
        ("10420", "Beans Green"),
        ("10403", "Collard Greens"),
        ("10450", "Cukes Super Select"),
    ],
    "Cooseman": [
        ("40602", "Lemon Juice"),
        ("40605", "Orange Juice"),
        ("11550", "Tomatoes Cluster"),
        ("11539", "Tomatoes Hot House Flats"),
    ],
    "D'Arrigo Bros": [
        ("41124", "Strawberries Driscoll 8-1"),
        ("40390", "Blueberries"),
        ("40190", "Raspberries"),
        ("40380", "Blackberries"),
        ("40500", "Lemons 95ct"),
        ("10340", "Carrots Bunch"),
        ("10382", "Celery Hearts"),
        ("10360", "Asparagus"),
        ("10210", "Broccolini"),
        ("11270", "Rabe AB 20#"),
        ("10200", "Radish Cello"),
        ("10320", "Carrots Baby Peeled"),
        ("10682", "Cukes Seedless English"),
        ("10620", "Lettuce Arcadian"),
        ("10598", "Lettuce Boston 24ct"),
        ("10599", "Lettuce Boston Hydro"),
        ("10600", "Lettuce Green Leaf"),
        ("10660", "Lettuce Mescutn"),
        ("10662", "Lettuce Romaine Hearts"),
        ("11339", "Spinach Baby"),
        ("11360", "Spinach Cello"),
        ("11350", "Spinach Popeye"),
        ("10596", "Lettuce Olivia Spring Mix"),
        ("10595", "Lettuce Olivia's Spinach"),
        ("10597", "Lettuce Olivia's Arugula"),
        ("10598", "Lettuce Olivia's 5050"),
        ("10594", "Lettuce OliviasBaby Lettuce"),
        ("10102", "Lettuce Olivia's Power Green"),
        ("10592", "Lettuce Olivia Kale"),
        ("10590", "Lettuce Olivis Spin 9oz"),
        ("10350", "Carrot Cello 1#/48ct"),
    ],
    "Maheras": [
        ("10880", "Onions Spanish White"),
        ("40465", "Dates Medjool"),
        ("11040", "Potatoes Fingerling"),
        ("11178", "Potatoes Creamer Yukon"),
    ],
    "Matarazzo Bro": [
        ("15100", "Beans French"),
        ("15130", "Carrots Crew Cut"),
        ("15131", "Carrots Crew Cut Tri Color"),
    ]
}

def add_vendor(name):
    cursor.execute("INSERT OR IGNORE INTO vendors (name) VALUES (?)", (name,))
    cursor.execute("SELECT id FROM vendors WHERE name = ?", (name,))
    return cursor.fetchone()[0]

def add_item(vendor_id, item_id, name):
    cursor.execute(
        "INSERT OR IGNORE INTO items (vendor_id, item_code, name) VALUES (?, ?, ?)",
        (vendor_id, item_id, name)
    )

# Insert vendors and items
for vendor, items in vendor_items.items():
    vendor_id = add_vendor(vendor)
    for item_id, item_name in items:
        add_item(vendor_id, item_id, item_name)

# Commit and close
conn.commit()
conn.close()
print("Vendors and items added successfully.")
