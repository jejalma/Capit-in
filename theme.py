import streamlit as st

PALETTE = {
    'primary': '#0F4C5C',
    'secondary': '#E07A3F',
    'accent': '#2A7F62',
    'positive': '#2A7F62',
    'negative': '#B3412E',
    'warning': '#C98A2B',
    'info': '#0F4C5C',
    'ink': '#1F2A2E',
    'muted': '#6B7578',
    'cream': '#F6F3EC',
    'sand': '#EFE9DC',
    'line': '#E6E1D6',
    'teal_soft': '#E3EEEE',
    'ember_soft': '#FBEADF',
    'moss_soft': '#E4F1EA',
    'rose_soft': '#F7E2DE',
}

HEX = dict(PALETTE)

TONES = {
    'teal': (PALETTE['teal_soft'], PALETTE['primary']),
    'moss': (PALETTE['moss_soft'], PALETTE['accent']),
    'ember': (PALETTE['ember_soft'], '#B8602C'),
    'rose': (PALETTE['rose_soft'], PALETTE['negative']),
    'sand': (PALETTE['sand'], '#7A6A4F'),
}

_CSS = """
<style>
#MainMenu, footer, [data-testid="stToolbar"] [data-testid="stAppDeployButton"] {display: none !important;}
.block-container {padding-top: 2.2rem; max-width: 1400px;}
[data-testid="stSidebar"] {border-right: 1px solid %(line)s;}
h1, h2, h3 {letter-spacing: -0.01em;}
.sia-eyebrow {font-size: 10px; letter-spacing: .18em; text-transform: uppercase; color: %(muted)s;}
.sia-header h1 {font-size: 2rem; font-weight: 400; color: %(ink)s; margin: 0; padding: 0;}
.sia-header p {color: %(muted)s; margin: .15rem 0 0 0; font-size: .92rem;}
.sia-section {font-weight: 600; color: %(ink)s; font-size: 1rem; margin: 0;}
.sia-section-sub {color: %(muted)s; font-size: .78rem; margin: 0 0 .4rem 0;}
.sia-badge {display: inline-block; font-size: 10.5px; letter-spacing: .06em; padding: 2px 8px; border-radius: 4px;
            font-weight: 500; white-space: nowrap;}
.sia-kpi {background: #fff; border: 1px solid %(line)s; border-radius: 12px; padding: 16px 18px; height: 100%%;}
.sia-kpi .label {font-size: 10px; letter-spacing: .16em; text-transform: uppercase; color: %(muted)s;}
.sia-kpi .value {font-family: 'Roboto Mono', ui-monospace, monospace; font-size: 1.35rem; color: %(ink)s;
                 margin-top: 6px; white-space: nowrap;}
.sia-kpi .hint {font-size: .75rem; color: %(muted)s; margin-top: 2px;}
.sia-table-wrap {overflow-x: auto; width: 100%%;}
table.sia-table {width: 100%%; border-collapse: collapse; font-size: .86rem; background: transparent; border: none !important;
                 margin: 0;}
table.sia-table th, table.sia-table td {border-left: none !important; border-right: none !important;
                 border-top: none !important;}
table.sia-table tr {background: transparent;}
table.sia-table th {font-size: 10px; letter-spacing: .14em; text-transform: uppercase; color: %(muted)s;
                    font-weight: 500; padding: 10px 10px; border-bottom: 1px solid %(line)s; white-space: nowrap;}
table.sia-table td {padding: 9px 10px; border-bottom: 1px solid %(line)s; color: %(ink)s; vertical-align: middle;}
table.sia-table tr.bold td {font-weight: 600; background: %(sand)s;}
table.sia-table tr.section td {font-weight: 600; background: %(teal_soft)s; color: %(primary)s;}
table.sia-table tr.muted td {color: %(muted)s; font-style: italic; font-size: .8rem;}
table.sia-table td.num {font-family: 'Roboto Mono', ui-monospace, monospace; white-space: nowrap;}
.sia-empty {color: %(muted)s; font-size: .88rem; padding: 18px 4px;}
.sia-panel {display: flex; align-items: center; gap: 28px; border-radius: 12px; padding: 12px 18px; flex-wrap: wrap;}
.sia-panel .k {font-size: 10px; letter-spacing: .12em; text-transform: uppercase; color: %(muted)s;}
.sia-panel .v {font-family: 'Roboto Mono', ui-monospace, monospace; color: %(ink)s;}
.sia-panel .grow {flex: 1;}
.sia-warning {border: 1px solid %(warning)s; background: %(ember_soft)s; border-radius: 12px; padding: 12px 16px;
              font-size: .88rem; color: %(ink)s;}
.sia-hero {background: %(primary)s; color: #fff; border-radius: 16px; padding: 40px; min-height: 560px;
           display: flex; flex-direction: column; justify-content: space-between;}
.sia-hero .big {font-size: 3rem; font-weight: 600; line-height: 1.15;}
.sia-hero .accent {color: %(secondary)s;}
.sia-hero .loc {color: rgba(255,255,255,.7); font-size: .88rem; margin-top: 14px;}
.sia-hero .ver {font-family: ui-monospace, monospace; font-size: .75rem; color: rgba(255,255,255,.5);}
.sia-brand {display: flex; align-items: center; gap: 12px;}
.sia-brand img {width: 40px; height: 40px; border-radius: 8px; object-fit: cover;}
.sia-brand .t1 {font-size: 10px; letter-spacing: .18em;}
.sia-brand .t2 {font-weight: 600;}
.sia-preview {background: %(cream)s; border-radius: 10px; padding: 14px 16px;}
.sia-preview .total {font-family: 'Roboto Mono', ui-monospace, monospace; font-size: 1.5rem; color: %(ink)s;}
.sia-line {display: flex; justify-content: space-between; font-size: .86rem; padding: 2px 0;}
.sia-stock-card {background: #fff; border: 1px solid %(line)s; border-radius: 12px; padding: 14px 18px;}
.sia-stock-card .name {font-size: .85rem; color: %(muted)s;}
.sia-stock-card .kg {font-family: 'Roboto Mono', ui-monospace, monospace; font-size: 1.5rem; color: %(ink)s;}
.sia-stock-card .meta {font-size: .75rem; color: %(muted)s;}
.sia-user {text-align: right; line-height: 1.2;}
.sia-user .n {font-weight: 500; font-size: .9rem;}
.sia-user .r {font-size: .75rem; color: %(muted)s;}
</style>
""" % PALETTE


def apply() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
