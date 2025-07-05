import yaml
import re

def parse_price(price_str):
    if not price_str:
        return 0.0
    match = re.search(r'([\d,.]+)', str(price_str))
    if match:
        return float(match.group(1).replace('.', '').replace(',', '.'))
    return 0.0

def parse_weight(weight_str):
    if not weight_str:
        return 0.0
    match = re.search(r'([\d,.]+)', str(weight_str))
    if match:
        return float(match.group(1).replace(',', '.'))
    return 0.0

def extract_items(data, parent_key=''):
    items = []
    if isinstance(data, dict):
        for k, v in data.items():
            key = f"{parent_key}/{k}" if parent_key else k
            if isinstance(v, (dict, list)):
                items.extend(extract_items(v, key))
            else:
                # Only add leaf nodes with price or weight
                if k in ['price', 'Preis', 'weight', 'wight']:
                    items.append((parent_key, {k: v}))
    elif isinstance(data, list):
        for entry in data:
            items.extend(extract_items(entry, parent_key))
    return items

def summarize_parts(data):
    overview = {}
    def walk(node, path=''):
        if isinstance(node, dict):
            part = {}
            for k, v in node.items():
                if k in ['price', 'Preis']:
                    part['price'] = parse_price(v)
                if k in ['weight', 'wight']:
                    part['weight'] = parse_weight(v)
                if isinstance(v, (dict, list)):
                    walk(v, path + '/' + k if path else k)
            if part:
                overview[path] = overview.get(path, {'price': 0, 'weight': 0})
                overview[path]['price'] += part.get('price', 0)
                overview[path]['weight'] += part.get('weight', 0)
        elif isinstance(node, list):
            for item in node:
                walk(item, path)
    walk(data)
    return overview

def main():
    with open('teile-liste.yaml', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    overview = summarize_parts(data)
    total_price = sum(part['price'] for part in overview.values())
    total_weight = sum(part['weight'] for part in overview.values())

    print("Teile-Übersicht:")
    print(f"{'Teil':40} {'Preis (EUR)':>12} {'Gewicht (g)':>12}")
    print("-" * 68)
    for part, vals in overview.items():
        print(f"{part:40} {vals['price']:12.2f} {vals['weight']:12.1f}")
    print("-" * 68)
    print(f"{'Gesamt':40} {total_price:12.2f} {total_weight:12.1f}")

if __name__ == "__main__":
    main()