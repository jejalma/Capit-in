import html
import re
from typing import Callable

import streamlit as st

from services import ServiceError
from services.pdf import table_pdf
from views.theme import TONES

ALIGN = {'left': 'left', 'right': 'right', 'center': 'center'}


class Html(str):
    """String yang sudah berupa HTML aman (tidak di-escape)."""


def esc(value) -> str:
    return value if isinstance(value, Html) else html.escape(str(value if value is not None else ''))


def plain(value) -> str:
    return html.unescape(re.sub(r'<[^>]+>', '', str(value))) if isinstance(value, Html) else str(value or '')


def badge_html(text: str, tone: str = 'teal', testid: str | None = None) -> Html:
    bg, fg = TONES[tone]
    tid = f' data-testid="{testid}"' if testid else ''
    return Html(f'<span class="sia-badge" style="background:{bg};color:{fg}"{tid}>{html.escape(text)}</span>')


def badge(text: str, tone: str = 'teal', testid: str | None = None) -> None:
    st.markdown(badge_html(text, tone, testid), unsafe_allow_html=True)


def page_header(title: str, subtitle: str = '') -> None:
    st.markdown(f'<div class="sia-header" data-testid="page-header"><h1>{html.escape(title)}</h1>'
                f'<p>{html.escape(subtitle)}</p></div>', unsafe_allow_html=True)


def section_title(title: str, subtitle: str | None = None) -> None:
    sub = f'<p class="sia-section-sub">{html.escape(subtitle)}</p>' if subtitle else ''
    st.markdown(f'<p class="sia-section">{html.escape(title)}</p>{sub}', unsafe_allow_html=True)


def kpi(label: str, value: str, hint: str, tone: str, testid: str) -> None:
    _, fg = TONES[tone]
    st.markdown(f'<div class="sia-kpi" style="border-top:3px solid {fg}"><div class="label">{html.escape(label)}</div>'
                f'<div class="value" data-testid="{testid}">{html.escape(value)}</div>'
                f'<div class="hint">{html.escape(hint)}</div></div>', unsafe_allow_html=True)


def html_table(headers: list[tuple[str, str]], rows: list[tuple[list, str]], empty: str, testid: str) -> None:
    if not rows:
        st.markdown(f'<div class="sia-empty" data-testid="{testid}-empty">{html.escape(empty)}</div>',
                    unsafe_allow_html=True)
        return
    head = ''.join(f'<th style="text-align:{ALIGN[a]}">{html.escape(h)}</th>' for h, a in headers)
    body = []
    for cells, style in rows:
        tds = ''.join(f'<td class="{"num" if a == "right" else ""}" style="text-align:{ALIGN[a]}">{esc(c)}</td>'
                      for c, (_, a) in zip(cells, headers))
        body.append(f'<tr class="{style}">{tds}</tr>')
    st.markdown(f'<div class="sia-table-wrap"><table class="sia-table" data-testid="{testid}"><thead><tr>{head}'
                f'</tr></thead><tbody>{"".join(body)}</tbody></table></div>', unsafe_allow_html=True)


def data_table(headers: list[tuple[str, str]], rows: list[list], empty: str, testid: str) -> None:
    html_table(headers, [(r, '') for r in rows], empty, testid)


def report_block(*, title: str, subtitle: str, headers: list[tuple[str, str]], rows: list[tuple[list, str]],
                 widths: list[float], filename: str, testid: str, orientation: str = 'P') -> None:
    top = st.columns([4, 1], vertical_alignment='center')
    with top[0]:
        section_title(title, subtitle)
    pdf_rows = [([plain(c) for c in cells], style) for cells, style in rows]
    with top[1]:
        st.download_button('Unduh PDF', icon=':material/picture_as_pdf:', key=f'{testid}-pdf',
                           data=table_pdf(title, subtitle, [h for h, _ in headers], pdf_rows, widths,
                                          ''.join('R' if a == 'right' else 'L' for _, a in headers), orientation),
                           file_name=filename, mime='application/pdf', width='stretch')
    html_table(headers, rows, 'Tidak ada data pada periode ini.', testid)


def flash(message: str, kind: str = 'success') -> None:
    st.session_state.setdefault('_flash', []).append((kind, message))


def show_flash() -> None:
    icons = {'success': ':material/check_circle:', 'warning': ':material/warning:', 'error': ':material/error:'}
    for kind, message in st.session_state.pop('_flash', []):
        st.toast(message, icon=icons[kind])


def run_safely(action: Callable[[], object], success: str | None = None) -> bool:
    try:
        action()
    except ServiceError as exc:
        st.error(str(exc), icon=':material/error:')
        return False
    if success:
        flash(success)
    return True


@st.dialog('Konfirmasi')
def confirm(message: str, action: Callable[[], object], success: str) -> None:
    st.write(message)
    left, right = st.columns(2)
    if left.button('Batal', key='confirm-cancel', width='stretch'):
        st.rerun()
    if right.button('Ya, hapus', key='confirm-ok', type='primary', width='stretch'):
        if run_safely(action, success):
            st.rerun()
