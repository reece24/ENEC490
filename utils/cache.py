from __future__ import annotations

import streamlit as st


CACHE_TTL_SECONDS = 900


def cached_data(ttl: int = CACHE_TTL_SECONDS):
    return st.cache_data(ttl=ttl, show_spinner=False)
