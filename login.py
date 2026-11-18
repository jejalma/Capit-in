import html

import streamlit as st

import config
from services import ServiceError, auth
from views.layout import brand_html
from views.session import login

DEMO_ACCOUNTS = [
    ('Admin (Bapak Salim)', *config.SEED_USERS[0][1:3]),
    ('Akuntan', *config.SEED_USERS[1][1:3]),
    ('Kasir', *config.SEED_USERS[2][1:3]),
]


def _hero() -> None:
    st.markdown(f'<div class="sia-hero" data-testid="login-hero">{brand_html(dark=True)}<div>'
                '<div class="big">Catat setiap<br/><span class="accent">panen</span>, kelola<br/>setiap rupiah.</div>'
                '<div class="loc">Morodemak, Bonang, Demak</div></div>'
                '<div class="ver">v1.0 · SIA-TKS · Tambak Kepiting Bapak Salim</div></div>', unsafe_allow_html=True)


def _fill(mail: str, pwd: str) -> None:
    st.session_state.update({'login-email': mail, 'login-password': pwd})
    st.session_state.pop('login-error', None)


def login_page() -> None:
    hero, form = st.columns([1, 1], gap='large')
    with hero:
        _hero()
    with form:
        st.markdown('<div style="height:70px"></div>', unsafe_allow_html=True)
        st.markdown('<h2 style="margin:0;font-weight:600">Masuk ke akun Anda</h2>'
                    '<p style="color:#6B7578;margin-top:2px">Gunakan email dan kata sandi dari admin tambak.</p>',
                    unsafe_allow_html=True)
        with st.form('login-form', border=False):
            email = st.text_input('Email', key='login-email')
            password = st.text_input('Kata Sandi', type='password', key='login-password')
            submitted = st.form_submit_button('Masuk', type='primary', width='stretch')
        if submitted:
            try:
                login(auth.authenticate(email, password))
                st.session_state.pop('login-error', None)
                st.rerun()
            except ServiceError as exc:
                st.session_state['login-error'] = str(exc)
        if st.session_state.get('login-error'):
            st.markdown(f'<p data-testid="login-error" style="color:#B3412E;font-size:.9rem">'
                        f'{html.escape(st.session_state["login-error"])}</p>', unsafe_allow_html=True)
        st.divider()
        st.markdown('<div class="sia-eyebrow">Akun demo — klik untuk isi otomatis</div>', unsafe_allow_html=True)
        for label, mail, pwd in DEMO_ACCOUNTS:
            slug = label.split()[0].lower()
            st.button(f'{label}  ·  {mail}', key=f'demo-account-{slug}', on_click=_fill, args=(mail, pwd),
                      width='stretch')
