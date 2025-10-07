"""Local Personal Finance Dashboard.

An offline Dash application for managing personal finances by automatically processing
bank statements (CSV/PDF) from a watched directory, categorizing transactions, and visualizing spending patterns.

Features an intelligent multi-agent workflow for enhanced data extraction and organization.
Auto-processes new files on startup with persistent memory to avoid duplicates.
"""
import os
from pathlib import Path
import re

import dash
from dash import Dash, dcc, html, Input, Output, State, dash_table
import pandas as pd
import plotly.express as px

from finance_db import init_db, read_transactions_df, upsert_mem_label, get_conn
from utils import unique_filename
from agents import AgentWorkflow
from llm_handler import is_llm_available
from file_scanner import FileScanner

# Project paths & ensure directories exist
ROOT = Path(__file__).parent
DATA_DIR = ROOT / 'data'
WATCH_DIR = ROOT / 'test_files'  # Directory to watch for new files
TEMP_DIR = DATA_DIR / 'temp'
PROCESSED_FILE = DATA_DIR / 'processed_files.json'  # Track processed files
DATA_DIR.mkdir(parents=True, exist_ok=True)
WATCH_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Initialize DB
init_db()

# AI-First Startup Check
print("\n" + "="*70)
print("🤖 Finance AI Dashboard - Starting Up")
print("="*70)

if not is_llm_available():
    print("\n❌ CRITICAL ERROR: LLM dependencies not available!")
    print("\nThis app requires llama-cpp-python to function.")
    print("\nInstall with:")
    print("  macOS (Apple Silicon): CMAKE_ARGS=\"-DLLAMA_METAL=on\" pip install llama-cpp-python")
    print("  Other systems: pip install llama-cpp-python")
    print("\nOr run: ./setup.sh")
    print("\n" + "="*70 + "\n")
    raise SystemExit("LLM dependencies required. Please install llama-cpp-python.")

print("✅ LLM dependencies available")

# Initialize Agent Workflow (AI-first approach)
USE_AGENT_WORKFLOW = True  # AI workflow is always enabled
print("🔧 Initializing AI agent workflow...")

try:
    agent_workflow = AgentWorkflow(TEMP_DIR)
    print("✅ AI agents ready!")
except Exception as e:
    print(f"\n❌ Failed to initialize AI agents: {e}")
    print("\nPlease check:")
    print("  1. Model file exists: mistral-7b-instruct-v0.1.Q5_0.gguf")
    print("  2. llama-cpp-python is properly installed")
    print("\n" + "="*70 + "\n")
    raise

# Initialize File Scanner
print("🔍 Initializing file scanner...")
file_scanner = FileScanner(WATCH_DIR, PROCESSED_FILE)
stats = file_scanner.get_stats()
print(f"📁 Watching directory: {stats['watch_directory']}")
print(f"📊 Previously processed files: {stats['total_processed']}")

# Scan for new files on startup
print("🔎 Scanning for new files...")
new_files = file_scanner.scan_for_new_files()

if new_files:
    print(f"📄 Found {len(new_files)} new file(s) to process")
    for file_path, file_hash in new_files:
        print(f"\n🤖 Processing: {file_path.name}")
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                content = f.read()
            
            ext = file_path.suffix.lower()
            
            # Process with AI agents
            success, message, num_records = agent_workflow.process_file(
                file_path.name, content, ext
            )
            
            if success:
                print(f"✅ {file_path.name}: {num_records} records processed 🤖")
                file_scanner.mark_as_processed(file_hash)
            else:
                print(f"❌ {file_path.name}: {message}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
            import traceback
            traceback.print_exc()
else:
    print("✓ No new files to process")

print("="*70)
print("✅ Finance AI Dashboard ready!")
print("="*70 + "\n")

app: Dash = dash.Dash(__name__, suppress_callback_exceptions=True, title="Finance AI Dashboard 🤖")
server = app.server

categories = [
    'Income','Groceries','Dining','Transport','Housing','Utilities','Healthcare','Entertainment','Subscriptions','Adjustments','Savings','Uncategorized'
]

app.layout = html.Div([
    # Header with AI branding
    html.Div(className='card', style={'marginBottom': '20px', 'textAlign': 'center'}, children=[
        html.H1('🤖 Finance AI Dashboard', style={'margin': '10px 0'}),
        html.P('Powered by Multi-Agent AI • 100% Offline • Privacy-First • Auto-Processing', 
               style={'color': '#666', 'fontSize': '14px', 'margin': '5px 0'}),
        html.Div([
            html.Span('🔍 Agent 1: Extractor', style={'margin': '0 10px', 'fontSize': '12px'}),
            html.Span('📊 Agent 2: Organizer', style={'margin': '0 10px', 'fontSize': '12px'}),
            html.Span('💾 Agent 3: DB Expert', style={'margin': '0 10px', 'fontSize': '12px'}),
        ], style={'color': '#888', 'fontSize': '12px'})
    ]),
    
    # Info card about auto-processing
    html.Div(className='card', style={'marginBottom': '20px', 'backgroundColor': '#f0f9ff'}, children=[
        html.H3('📁 Auto-Processing Active', style={'margin': '10px 0', 'color': '#0369a1'}),
        html.P(f'Monitoring: {WATCH_DIR}', style={'fontSize': '14px', 'margin': '5px 0', 'fontFamily': 'monospace'}),
        html.P('Drop new files into this directory and restart the app to process them automatically.', 
               style={'fontSize': '14px', 'color': '#666', 'margin': '5px 0'}),
        html.Div(id='scanner-stats', style={'marginTop': '10px'})
    ]),
    
    dcc.Tabs(className='tabs', value='tab-dashboard', children=[
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
# Callbacks: Scanner stats
# -----------------------------
@app.callback(
    Output('scanner-stats', 'children'),
    Input('refresh-interval', 'n_intervals')
)
def update_scanner_stats(_):
    stats = file_scanner.get_stats()
    return html.Div([
        html.Span(f"📊 Total files processed: {stats['total_processed']}", 
                 style={'fontSize': '14px', 'fontWeight': 'bold', 'color': '#059669'}),
        html.Br(),
        html.Span("💡 Tip: Add new files to test_files/ and restart the app", 
                 style={'fontSize': '12px', 'color': '#888', 'fontStyle': 'italic'})
    ])





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
