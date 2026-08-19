import random
import datetime


STORE_NAMES = [
    "QuickMart", "Fresh Foods", "TechHub Electronics", "Style Boutique",
    "Home Essentials", "Green Grocer", "Book Nook", "Pet Paradise",
    "Auto Parts Plus", "Sporting Goods Co", "Pharmacy First", "Office Supply Co"
]

ITEM_CATEGORIES = {
    "Groceries": ["Milk", "Bread", "Eggs", "Cheese", "Apples", "Bananas", "Chicken", "Rice", "Pasta", "Cereal"],
    "Electronics": ["USB Cable", "Phone Case", "Headphones", "Charger", "Memory Card", "Mouse", "Keyboard"],
    "Clothing": ["T-Shirt", "Jeans", "Socks", "Jacket", "Sweater", "Hat", "Scarf", "Gloves"],
    "Home": ["Detergent", "Paper Towels", "Trash Bags", "Light Bulbs", "Batteries", "Cleaner", "Sponge"],
    "Books": ["Novel", "Cookbook", "Magazine", "Notebook", "Planner", "Dictionary"],
    "Pet": ["Dog Food", "Cat Litter", "Pet Toy", "Treats", "Leash", "Bowl"],
}

PRICE_RANGES = {
    "Groceries": (1.50, 15.00),
    "Electronics": (5.00, 150.00),
    "Clothing": (10.00, 80.00),
    "Home": (2.00, 25.00),
    "Books": (5.00, 30.00),
    "Pet": (3.00, 40.00),
}


def _generate_receipt(num_items: int = None, store_name: str = None):
    if store_name is None:
        store_name = random.choice(STORE_NAMES)
    
    if num_items is None:
        num_items = random.randint(3, 12)
    
    items = []
    categories = list(ITEM_CATEGORIES.keys())
    
    for _ in range(num_items):
        cat = random.choice(categories)
        item_name = random.choice(ITEM_CATEGORIES[cat])
        min_price, max_price = PRICE_RANGES[cat]
        price = round(random.uniform(min_price, max_price), 2)
        qty = random.randint(1, 3)
        if qty > 1:
            item_name = f"{qty}x {item_name}"
            price = round(price * qty, 2)
        items.append((item_name, price))
    
    subtotal = round(sum(p for _, p in items), 2)
    tax_rate = round(random.uniform(0.05, 0.10), 3)
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax, 2)
    
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    receipt_num = f"{random.randint(100000, 999999)}"
    register = f"REG-{random.randint(1, 20):02d}"
    cashier = f"CSH-{random.randint(100, 999)}"
    
    return {
        "store": store_name,
        "date": date,
        "receipt_num": receipt_num,
        "register": register,
        "cashier": cashier,
        "items": items,
        "subtotal": subtotal,
        "tax_rate": tax_rate * 100,
        "tax": tax,
        "total": total,
    }


def _format_receipt(receipt: dict, width: int = 48) -> str:
    lines = []
    w = width
    
    def center(text):
        return text.center(w)
    
    def left_right(left, right):
        return f"{left:<{w-len(right)-1}} {right}"
    
    lines.append("=" * w)
    lines.append(center(receipt["store"].upper()))
    lines.append(center(f"Receipt #{receipt['receipt_num']}"))
    lines.append(center(f"{receipt['date']}"))
    lines.append(center(f"{receipt['register']}  {receipt['cashier']}"))
    lines.append("-" * w)
    lines.append(f"{'ITEM':<35} {'PRICE':>10}")
    lines.append("-" * w)
    
    for item, price in receipt["items"]:
        name = item[:34]
        lines.append(f"{name:<35} ${price:>9.2f}")
    
    lines.append("-" * w)
    lines.append(left_right("Subtotal", f"${receipt['subtotal']:.2f}"))
    lines.append(left_right(f"Tax ({receipt['tax_rate']:.1f}%)", f"${receipt['tax']:.2f}"))
    lines.append("=" * w)
    lines.append(left_right("TOTAL", f"${receipt['total']:.2f}"))
    lines.append("=" * w)
    lines.append(center("Thank you for shopping!"))
    lines.append(center("Come again soon!"))
    lines.append("=" * w)
    
    return "\n".join(lines)


def run(kevbin):
    kevbin.box_title("Fake Receipt Generator")
    kevbin.box_print("Generate realistic fake receipts with items, prices, tax, and totals")
    
    while True:
        kevbin.box_print("")
        num_input = kevbin.box_input("Number of items (3-20) [random]: ").strip()
        if num_input.lower() in ('q', 'quit', 'exit'):
            break
        
        num_items = None
        if num_input:
            try:
                num_items = int(num_input)
                if not 1 <= num_items <= 50:
                    kevbin.box_print("[red]Please enter 1-50[/red]")
                    continue
            except ValueError:
                kevbin.box_print("[red]Invalid number[/red]")
                continue
        
        store = kevbin.box_input("Store name (empty for random): ").strip()
        if not store:
            store = None
        
        receipt = _generate_receipt(num_items, store)
        formatted = _format_receipt(receipt)
        
        kevbin.box_code(formatted)
        
        save = kevbin.box_input("\nSave to file? (path or empty): ").strip().strip('"')
        if save:
            try:
                with open(save, 'w', encoding='utf-8') as f:
                    f.write(formatted)
                kevbin.box_print(f"[green]Saved to {save}[/green]")
            except Exception as e:
                kevbin.box_print(f"[red]Save error: {e}[/red]")
        
        another = kevbin.box_input("\nGenerate another? (y/n) [y]: ").strip().lower()
        if another in ('n', 'no'):
            break


if __name__ == "__main__":
    class MockKevbin:
        def box_title(self, t): print(f"\n=== {t} ===")
        def box_print(self, t): print(t)
        def box_input(self, t): return input(t + " ")
        def box_table(self, rows, title=""):
            if title: print(f"\n{title}")
            for row in rows:
                print(" | ".join(str(c) for c in row))
        def box_code(self, code, language=""): print(code)
    
    run(MockKevbin())