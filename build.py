#!/usr/bin/env python3
"""Build script for 阿沐的菜单 - injects menu data into template."""

import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))

def main():
    # Load data
    with open(os.path.join(BASE, 'data', 'menu.json'), 'r', encoding='utf-8') as f:
        menu_data = json.load(f)
    
    # Load template
    with open(os.path.join(BASE, 'template.html'), 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Inject data
    data_json = json.dumps(menu_data, ensure_ascii=False, indent=2)
    output = template.replace('__EMBED_DATA__', data_json)
    
    # Write output
    output_path = os.path.join(BASE, 'amumu.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    size_kb = os.path.getsize(output_path) / 1024
    print(f'Built amumu.html ({size_kb:.1f} KB)')
    
    # Count dishes
    total = sum(len(cat['dishes']) for cat in menu_data['categories'])
    print(f'Total dishes: {total}')
    for cat in menu_data['categories']:
        print(f'  {cat["icon"]} {cat["name"]}: {len(cat["dishes"])} dishes')

if __name__ == '__main__':
    main()
