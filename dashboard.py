from datetime import date

import altair as alt
import pandas as pd
import streamlit as st

from services import master, reports
from services.transactions import TYPES, list_transactions
from views.components import badge_html, data_table, kpi, page_header, section_title
from views.fmt import kg, rp, tgl

TYPE_TONES = {'PENJUALAN': 'moss', 'PENERIMAAN_PIUTANG': 'moss', 'MODAL': 'teal', 'PAKAN': 'ember', 'GAJI': 'ember',
              'OPERASIONAL': 'ember', 'PRIVE': 'rose'}


def type_badge(tx_type: str):
    return badge_html(TYPES[tx_type][0], TYPE_TONES[tx_type])


def _opening_warning(status: dict) -> None:
    if status['balanced']:
        return
    st.markdown(f'<div class="sia-warning" data-testid="dashboard-opening-warning">Saldo awal Bagan Akun belum '
                f'seimbang (selisih {rp(status["diff"])}). Neraca tidak akan seimbang sampai saldo awal debit = '
                f'kredit. Periksa menu <b>Bagan Akun</b>.</div>', unsafe_allow_html=True)


def _chart(series: list[dict]) -> None:
    df = pd.DataFrame([{'Bulan': s['label'], 'Pendapatan': round(s['revenue'] / 1000),
                        'Beban': round(s['expense'] / 1000), 'order': i} for i, s in enumerate(series)])
    x = alt.X('Bulan:N', sort=alt.SortField('order'), title=None)
    bars = alt.Chart(df).mark_bar(color='#0F4C5C', cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=26).encode(
        x=x, y=alt.Y('Pendapatan:Q', title='ribu Rp'), tooltip=['Bulan', 'Pendapatan', 'Beban'])
    line = alt.Chart(df).mark_line(color='#E07A3F', point=True, interpolate='monotone').encode(
        x=x, y='Beban:Q', tooltip=['Bulan', 'Pendapatan', 'Beban'])
    st.altair_chart((bars + line).properties(height=280), width='stretch', key='dashboard-chart')
    st.caption('Batang: Pendapatan · Garis: Beban')


def _entities() -> None:
    counts = master.entity_counts()
    rows = [['Pengepul Terdaftar', counts['collectors']], ['Karyawan Aktif', counts['employees']],
            ['Produk Kepiting', counts['products']], ['Total Transaksi', counts['transactions']]]
    data_table([('Entitas', 'left'), ('Jumlah', 'right')], rows, '-', 'entity-counts')


def render(user: dict) -> None:
    data = reports.dashboard(date.today())
    page_header('Ringkasan Keuangan', f'Periode: {tgl(data["start"])} — {tgl(data["end"])}')
    _opening_warning(data['opening'])
    cols = st.columns(5)
    items = [('Pendapatan', rp(data['revenue']), 'Penjualan kepiting bulan ini', 'moss', 'kpi-revenue'),
             ('Beban', rp(data['expense']), 'Pakan, gaji, operasional', 'ember', 'kpi-expense'),
             ('Laba Bersih', rp(data['net_income']), f'Margin {data["margin"]:.1f}%',
              'teal' if data['net_income'] >= 0 else 'rose', 'kpi-net-income'),
             ('Saldo Kas & Bank', rp(data['cash']), f'Piutang {rp(data["receivable"])}', 'teal', 'kpi-cash'),
             ('Nilai Stok', rp(data['stock_value']), f'{kg(data["stock_kg"])} total', 'sand', 'kpi-stock')]
    for col, item in zip(cols, items):
        with col:
            kpi(*item)
    left, right = st.columns([2, 1])
    with left, st.container(border=True):
        section_title('Pendapatan vs Beban (6 Bulan)', 'Pergerakan arus bulanan, dalam ribuan rupiah')
        _chart(data['series'])
    with right, st.container(border=True):
        section_title('Ringkasan Entitas')
        _entities()
    with st.container(border=True):
        section_title('Transaksi Terbaru')
        rows = [[tgl(t['date']), t['ref_no'], type_badge(t['type']), t['description'], rp(t['amount'])]
                for t in list_transactions(limit=8)]
        data_table([('Tanggal', 'left'), ('No. Ref', 'left'), ('Jenis', 'left'), ('Keterangan', 'left'),
                    ('Nilai', 'right')], rows, 'Belum ada transaksi. Mulai dari menu Transaksi.', 'recent-transactions')
