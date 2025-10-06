"""Local Personal Finance Dashboard.

An offline Dash application for managing personal finances by uploading and parsing
bank statements (CSV/PDF), categorizing transactions, and visualizing spending patterns.
"""
import base64
import datetime as dt
import hashlib
import io
import os
import re
import sqlite3
from pathlib import Path
from typing import List

import dash
from dash import Dash, dcc, html, Input, Output, State, dash_table
import pandas as pd
import plotly.express as px

from finance_db import init_db, insert_document, insert_transactions, read_transactions_df, get_mem_labels, upsert_mem_label, get_conn
from parsers import parse_csv, parse_pdf_to_rows, categorize
from utils import unique_filename

# Project paths & ensure upload dir exists
ROOT = Path(__file__).parent
DATA_DIR = ROOT / 'data'
UPLOAD_DIR = DATA_DIR / 'uploads'
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize DB
init_db()

app: Dash = dash.Dash(__name__, suppress_callback_exceptions=True, title="Local Finance Dashboard")
server = app.server

categories = [
    'Income','Groceries','Dining','Transport','Housing','Utilities','Healthcare','Entertainment','Subscriptions','Adjustments','Savings','Uncategorized'
]

app.layout = html.Div([
    dcc.Tabs(className='tabs', value='tab-upload', children=[
        dcc.Tab(label='Upload', value='tab-upload', children=[
            html.Div(className='card', children=[
                html.H3('Upload Statements (CSV or PDF)'),
                dcc.Upload(
                    id='upload-data',
                    className='upload',
                    children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                    multiple=True
                ),
                html.Div(id='upload-status', style={'marginTop':'10px', 'color':'#2563eb'})
            ])
        ]),
        dcc.Tab(label='Transactions', value='tab-transactions', children=[
            html.Div(className='card', children=[
                html.H3('All Transactions'),
                html.Div(id='transactions-table-container')
            ])
        ]),
        dcc.Tab(label='Dashboard', value='tab-dashboard', children=[
            html.Div(className='card', children=[
                html.H3('Overview'),
                html.Div(id='kpi-cards', style={'display':'grid','gridTemplateColumns':'repeat(3, 1fr)','gap':'12px'})
            ]),
            html.Div(style={'height':'12px'}),
            html.Div(className='card', children=[
                html.H3('Spending by Category'),
                dcc.Graph(id='pie-category')
            ]),
            html.Div(style={'height':'12px'}),
            html.Div(className='card', children=[
                html.H3('Monthly Cashflow'),
                dcc.Graph(id='line-cashflow')
            ])
        ])
    ]),
    dcc.Interval(id='refresh-interval', interval=5*1000, n_intervals=0)  # soft refresh
], style={'padding':'16px'})


# -----------------------------
# Callbacks: Upload handling
# -----------------------------
@app.callback(
    Output('upload-status', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def handle_upload(list_of_contents, list_of_names):
    if not list_of_contents:
        return ''
    messages = []
    for content_str, name in zip(list_of_contents, list_of_names):
        try:
            header, b64 = content_str.split(',')
            content = base64.b64decode(b64)
            # unique filename
            safe_name = unique_filename(name, content)
            dest = UPLOAD_DIR / safe_name
            with open(dest, 'wb') as f:
                f.write(content)
            doc_id = insert_document(safe_name)
            # parse
            ext = os.path.splitext(name)[1].lower()
            if ext == '.csv':
                df = parse_csv(content)
            elif ext == '.pdf':
                df = parse_pdf_to_rows(content)
            else:
                # try csv as default
                try:
                    df = parse_csv(content)
                except Exception:
                    df = pd.DataFrame(columns=['date','amount','description'])
            # categorize
            mem = get_mem_labels()
            if not df.empty:
                df['category'] = [categorize(r['description'], r['amount'], mem) for _, r in df.iterrows()]
                rows = [(r['date'] or '', float(r['amount'] or 0), r['description'] or '', r['category'] or 'Uncategorized') for _, r in df.iterrows()]
                insert_transactions(doc_id, rows)
            messages.append(f"Processed {name} -> {len(df)} rows")
        except Exception as e:
            messages.append(f"Error processing {name}: {e}")
    return html.Ul([html.Li(m) for m in messages])


# -----------------------------
# Callbacks: Transactions table
# -----------------------------
@app.callback(
    Output('transactions-table-container', 'children'),
    Input('refresh-interval', 'n_intervals')
)
def refresh_table(_):
    df = read_transactions_df()
    if df.empty:
        return html.Div('No transactions yet.')
    # Prepare editable dropdown for category
    columns=[
        {'name':'ID','id':'id','editable':False},
        {'name':'Date','id':'date','editable':False},
        {'name':'Amount','id':'amount','type':'numeric','editable':False},
        {'name':'Description','id':'description','editable':False},
        {'name':'Category','id':'category','presentation':'dropdown'},
    ]
    dropdowns={ 'category': {'options':[{'label':c,'value':c} for c in categories]} }
    return dash_table.DataTable(
        id='transactions-table',
        columns=columns,
        data=df[['id','date','amount','description','category']].to_dict('records'),
        editable=True,
        row_deletable=False,
        filter_action='native',
        sort_action='native',
        page_size=20,
        style_table={'overflowX':'auto'},
        dropdown=dropdowns,
    )


@app.callback(
    Output('kpi-cards', 'children'),
    Output('pie-category', 'figure'),
    Output('line-cashflow', 'figure'),
    Input('refresh-interval', 'n_intervals')
)
def update_dashboard(_):
    df = read_transactions_df()
    if df.empty:
        cards = [
            html.Div(className='card', children=[html.Div('0.00', className='value'), html.Div('Income (total)', className='label')]),
            html.Div(className='card', children=[html.Div('0.00', className='value'), html.Div('Spend (total)', className='label')]),
            html.Div(className='card', children=[html.Div('0.00', className='value'), html.Div('Net Balance', className='label')]),
        ]
        return cards, px.scatter(title='No data'), px.scatter(title='No data')

    # totals
    income = df.loc[df['amount'] > 0, 'amount'].sum()
    spend = -df.loc[df['amount'] < 0, 'amount'].sum()
    net = income - spend
    cards = [
        html.Div(className='card', children=[html.Div(f"{income:,.2f}", className='value'), html.Div('Income (total)', className='label')]),
        html.Div(className='card', children=[html.Div(f"{spend:,.2f}", className='value'), html.Div('Spend (total)', className='label')]),
        html.Div(className='card', children=[html.Div(f"{net:,.2f}", className='value'), html.Div('Net Balance', className='label')]),
    ]

    # pie by category (expenses only)
    exp_df = df[df['amount'] < 0].copy()
    if not exp_df.empty:
        pie = px.pie(exp_df, names='category', values=exp_df['amount'].abs(), title='Expenses by Category')
    else:
        pie = px.pie(values=[1], names=['No expenses'])

    # monthly cashflow
    df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
    df['year_month'] = df['date_parsed'].dt.to_period('M').astype(str)
    monthly = df.groupby('year_month')['amount'].sum().reset_index()
    line = px.line(monthly, x='year_month', y='amount', markers=True, title='Monthly Net Cashflow')
    line.update_traces(line_shape='hv')

    return cards, pie, line


@app.callback(
    Output('transactions-table', 'data'),
    Input('transactions-table', 'data_timestamp'),
    State('transactions-table', 'data'),
    State('transactions-table', 'data_previous'),
    prevent_initial_call=True
)
def on_table_edit(ts, data, data_prev):
    # Detect category edits and update DB + memory
    if data is None or data_prev is None:
        raise dash.exceptions.PreventUpdate
    changed = []
    prev_map = {row['id']: row for row in data_prev}
    for row in data:
        rid = row['id']
        prev = prev_map.get(rid)
        if prev and row.get('category') != prev.get('category'):
            changed.append((rid, row.get('category') or 'Uncategorized', row.get('description') or ''))
    if not changed:
        raise dash.exceptions.PreventUpdate

    con = get_conn()
    try:
        cur = con.cursor()
        for rid, new_cat, desc in changed:
            cur.execute("UPDATE transactions SET category=? WHERE id=?", (new_cat, rid))
            # save keyword memory: simple split words longer than 3 chars
            for tok in set(re.findall(r"[A-Za-z]{4,}", desc.lower())):
                upsert_mem_label(tok, new_cat)
        con.commit()
    finally:
        con.close()

    # reload latest
    df = read_transactions_df()
    return df[['id','date','amount','description','category']].to_dict('records')


# Placeholder for future LLM hooks:
# - During parsing/categorization, you can call a local LLM via llama.cpp/GPT4All to suggest categories or summaries.
# - You could embed descriptions and use FAISS for nearest-neighbor category lookup.


if __name__ == '__main__':
    app.run_server(debug=True)
