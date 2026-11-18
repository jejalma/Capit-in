import hashlib
import hmac
import time

import streamlit as st
import streamlit.components.v1 as components

import config
from services import auth

COOKIE = 'sia_session'
MAX_AGE = 7 * 24 * 3600


def _sign(payload: str) -> str:
    return hmac.new(config.STORAGE_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()


def _make_token(uid: int) -> str:
    payload = f'{uid}.{int(time.time()) + MAX_AGE}'
    return f'{payload}.{_sign(payload)}'


def _read_token(token: str | None) -> int | None:
    try:
        uid, expiry, sig = (token or '').split('.')
    except ValueError:
        return None
    if not hmac.compare_digest(sig, _sign(f'{uid}.{expiry}')) or int(expiry) < time.time():
        return None
    return int(uid)


def _write_cookie(value: str, max_age: int) -> None:
    components.html(f"<script>parent.document.cookie='{COOKIE}={value}; path=/; max-age={max_age}; "
                    "SameSite=Lax';</script>", height=0)


def current_user() -> dict | None:
    state = st.session_state
    if 'uid' not in state and not state.get('_logged_out'):
        state['uid'] = _read_token(st.context.cookies.get(COOKIE))
    user = auth.get_user(state.get('uid'))
    if state.get('_logged_out'):
        _write_cookie('', 0)
    elif user and state.pop('_set_cookie', False):
        _write_cookie(_make_token(user['id']), MAX_AGE)
    return user


def login(user: dict) -> None:
    st.session_state.update(uid=user['id'], _set_cookie=True, _logged_out=False)


def logout() -> None:
    st.session_state.clear()
    st.session_state['_logged_out'] = True
