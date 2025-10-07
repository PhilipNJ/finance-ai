#!/usr/bin/env python3
import sqlite3
import sys

try:
    conn = sqlite3.connect('data/finance.db')
    cursor = conn.execute('SELECT COUNT(*) FROM transactions')
    total = cursor.fetchone()[0]
    print(f'\n✅ Total transactions in database: {total}')
    print('\n📊 Sample transactions:')
    print('='*80)
    cursor = conn.execute('SELECT date, description, amount, category FROM transactions ORDER BY date DESC LIMIT 10')
    for row in cursor:
        date, desc, amount, cat = row
        amount_str = f'${abs(amount):.2f}'
        symbol = '📉' if amount < 0 else '📈'
        print(f'{symbol} {date} | {desc[:35]:35} | {amount_str:>10} | {cat}')
    print('\n📊 Category breakdown:')
    print('='*80)
    cursor = conn.execute('''
        SELECT category, COUNT(*) as count, SUM(amount) as total 
        FROM transactions 
        GROUP BY category 
        ORDER BY total
    ''')
    for row in cursor:
        cat, count, total = row
        print(f'{cat:20} | {count:3} transactions | ${total:>10.2f}')
    conn.close()
    print('\n✅ Database query successful!')
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
