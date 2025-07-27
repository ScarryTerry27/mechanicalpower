from typing import Literal, Optional

import streamlit as st


# BACKEND
def check_mechanical_power(
        vt: float,
        peep: float,
        rr: float,
        f: float = None,
        ppeak: float = None,
        del_p_din: float = None,
        module: Literal["vcv", "pcv"] = "vcv"
) -> Optional[float | None]:
    mp = 0
    if module == "vcv":
        mp = round(((vt / 1000) * (ppeak + peep + f / 6) * rr) / 20, 2)
    elif module == "pcv":
        mp = round((vt / 1000) * (del_p_din + peep) * rr * 0.098, 2)
    return mp


# front mai menu
def change_page(page: Literal["vcv", "pcv"]):
    st.session_state["page"] = page


def show_sidebar():
    st.sidebar.button("VCV", on_click=change_page, kwargs={"page": "vcv"}, disabled=st.session_state["page"] == "vcv")
    st.sidebar.button("PCV", on_click=change_page, kwargs={"page": "pcv"}, disabled=st.session_state["page"] == "pcv")


def show_mp_risk(mp):
    if mp >= 17:
        level = "КРАЙНЕ ВЫСОКИЙ"
        bg_color = "#8B0000"  # тёмно-красный (багровый)
    elif mp >= 15:
        level = "ВЫСОКИЙ"
        bg_color = "#FF0000"  # красный
    elif mp >= 10:
        level = "УМЕРЕННЫЙ"
        bg_color = "#FFD700"  # жёлтый
    else:
        level = "НИЗКИЙ"
        bg_color = "#008000"  # зелёный

    # Карточка с настраиваемым стилем
    st.markdown(
        f"""
                    <div style="background-color:{bg_color};margin-bottom: 0.5rem; padding: 1.5rem; border-radius: 0.75rem;">
                        <h3 style="color:white; margin-bottom: 0.5rem;">
                            Механическая мощность: {mp} дж./мин
                        </h3>
                        <p style="color:white; font-size: 20px; margin: 0;">
                            Риск вентилятор-ассоциированного повреждения лёгких: <strong>{level}</strong>
                        </p>
                    </div>
                    """,
        unsafe_allow_html=True
    )


# front vcv
def show_cols_vcv(vt: float, ppeak: float, peep: float, rr: float, f: float):
    col1, col2, col3 = st.columns(3, border=True)
    col1.metric("Vt", f"{vt} мл", f"{vt - st.session_state.vcv.get("vt", 0)} мл")
    col2.metric("Ppeak", f"{ppeak} смН2О", f"{ppeak - st.session_state.vcv.get("ppeak", 0)} смН2О")
    col3.metric("PEEP", f"{peep} смН2О", f"{peep - st.session_state.vcv.get("peep", 0)} смН2О")
    col4, col5 = st.columns(2, border=True)
    col4.metric("RR", f"{rr} /мин", f"{rr - st.session_state.vcv.get("rr", 0)} /мин")
    col5.metric("F", f"{f} л/мин", f"{f - st.session_state.vcv.get("f", 0)} л/мин")


def show_cols_pcv(vt: float, peep: float, rr: float, del_p_din: float):
    col1, col2 = st.columns(2, border=True)
    col1.metric("Vt", f"{vt} мл", f"{vt - st.session_state.vcv.get("vt", 0)} мл")
    col2.metric("delPdin", f"{del_p_din} смН2О", f"{del_p_din - st.session_state.vcv.get("del_p_din", 0)} смН2О")
    col3, col4 = st.columns(2, border=True)
    col3.metric("PEEP", f"{peep} смН2О", f"{peep - st.session_state.vcv.get("peep", 0)} смН2О")
    col4.metric("RR", f"{rr} /мин", f"{rr - st.session_state.vcv.get("rr", 0)} /мин")


def show_form_vcv():
    with st.form("VCV"):
        vt = st.slider("Дыхательный объем", min_value=100, max_value=1000, step=25)
        ppeak = st.slider("Пиковое давление", min_value=0, max_value=50, step=1)
        peep = st.slider("ПДКВ", min_value=0, max_value=30, step=1)
        rr = st.slider("Частота дыхания", min_value=0, max_value=30, step=1)
        f = st.slider("Поток", min_value=0, max_value=50, step=5)
        if st.form_submit_button("Посчитать"):
            mp = check_mechanical_power(vt=vt, ppeak=ppeak, peep=peep, rr=rr, f=f)
            show_mp_risk(mp)
            show_cols_vcv(vt, ppeak, peep, rr, f)

            st.session_state["vcv"] = {
                "vt": vt,
                "ppeak": ppeak,
                "peep": peep,
                "rr": rr,
                "f": f,
                "del_p_din": 0,
                "mp": mp
            }


def show_form_pcv():
    with st.form("PCV"):
        vt = st.slider("Дыхательный объем", min_value=100, max_value=1000, step=25)
        peep = st.slider("ПДКВ", min_value=0, max_value=30, step=1)
        rr = st.slider("Частота дыхания", min_value=0, max_value=30, step=1)
        del_p_din = st.slider("Динамическая дельта P", min_value=0, max_value=50, step=5)
        if st.form_submit_button("Посчитать"):
            mp = check_mechanical_power(vt=vt, peep=peep, rr=rr, del_p_din=del_p_din, module="pcv")
            show_mp_risk(mp)
            show_cols_pcv(vt, peep, rr, del_p_din)

            st.session_state["vcv"] = {
                "vt": vt,
                "ppeak": 0,
                "peep": peep,
                "rr": rr,
                "del_p_din": del_p_din,
                "f": 0,
                "mp": mp
            }


def start_settings():
    if "vcv" not in st.session_state:
        st.session_state["vcv"] = {
            "vt": 0,
            "ppeak": 0,
            "peep": 0,
            "rr": 0,
            "f": 0,
            "del_p_din": 0,
            "mp": 0
        }
    if "page" not in st.session_state:
        st.session_state["page"] = "vcv"


if __name__ == "__main__":
    st.set_page_config(
        page_title="Оценка риска вентилятор-ассоциированного повреждения легких",
        layout="wide"
    )
    start_settings()
    show_sidebar()
    pages = {
        "vcv": show_form_vcv,
        "pcv": show_form_pcv
    }
    pages[st.session_state["page"]]()
