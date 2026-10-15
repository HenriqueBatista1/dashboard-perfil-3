import pandas as pd
import streamlit as st

from data_loader import load_data
from plots import render_charts


st.set_page_config(
    page_title="Sono e bem-estar acadêmico",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SHORT_SLEEP_HOURS = 7
HIGH_FATIGUE_LEVEL = 3


st.markdown(
    """
    <style>
    :root {
        --ink: #263b34;
        --muted: #66766f;
        --paper: #f5f7f2;
        --line: #dce5dc;
        --green: #2d7053;
        --green-soft: #e6f0e8;
        --gold: #c89a37;
    }

    .stApp {
        background: var(--paper);
        color: var(--ink);
    }

    .block-container {
        max-width: 1440px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .page-kicker,
    .section-kicker {
        color: var(--green);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .page-title {
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
        font-size: 2.7rem;
        font-weight: 500;
        line-height: 1.12;
        margin: 0.35rem 0 0.45rem;
    }

    .page-subtitle {
        color: var(--muted);
        font-size: 1rem;
        max-width: 780px;
    }

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--line);
        border-top: 3px solid var(--green);
        border-radius: 6px;
        padding: 0.5rem 0.8rem;
        min-height: 80px;
    }

    [data-testid="stMetric"] label {
        color: var(--muted);
    }

    [data-testid="stMetricValue"] {
        color: var(--ink);
    }

    .context-note {
        border-left: 3px solid var(--gold);
        color: var(--muted);
        line-height: 1.6;
        margin-top: 1.5rem;
        padding: 0.25rem 0 0.25rem 1rem;
    }

    .context-note strong {
        color: var(--ink);
    }

    /* Seleções dos filtros em verde suave. */
    [data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background-color: #e6f0e8 !important;
        color: #263b34 !important;
        border: 1px solid #cbded0 !important;
    }

    [data-testid="stMultiSelect"] [data-baseweb="tag"] span {
        color: #263b34 !important;
    }

    [data-testid="stMultiSelect"] [data-baseweb="tag"] svg {
        color: #263b34 !important;
        fill: currentColor !important;
    }

    @media (max-width: 700px) {
        .block-container {
            padding: 1.2rem 1rem 2rem;
        }

        .page-title {
            font-size: 2.1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Carregando dados...")
def get_data() -> pd.DataFrame:
    return load_data()


st.markdown(
    '<div class="page-kicker">'
    'UNIFEI &nbsp;·&nbsp; ATIVIDADE 2 &nbsp;·&nbsp; PERFIL 03'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<h1 class="page-title">Sono e bem-estar acadêmico</h1>',
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="page-subtitle">'
    'Indicadores de sono e cansaço para apoiar a identificação de grupos '
    'que podem demandar atenção da assistência estudantil.'
    '</p>',
    unsafe_allow_html=True,
)


try:
    dados = get_data()
except (FileNotFoundError, ValueError) as erro:
    st.error(f"Não foi possível carregar a planilha: {erro}")
    st.stop()


periodos_ordenados = [
    "1º–2º",
    "3º–4º",
    "5º–6º",
    "7º ou mais",
]

cursos = sorted(
    dados["Curso"].dropna().unique().tolist()
)

periodos_disponiveis = (
    dados["Periodo_Curso"].dropna().unique().tolist()
)

periodos = [
    periodo
    for periodo in periodos_ordenados
    if periodo in periodos_disponiveis
]

periodos.extend(
    sorted(set(periodos_disponiveis) - set(periodos))
)


# Filtros no corpo do painel.
filtro_curso, filtro_periodo = st.columns(2)

cursos_selecionados = filtro_curso.multiselect(
    "Curso",
    cursos,
    default=cursos,
)

periodos_selecionados = filtro_periodo.multiselect(
    "Período do curso",
    periodos,
    default=periodos,
)


recorte = dados.loc[
    dados["Curso"].isin(cursos_selecionados)
    & dados["Periodo_Curso"].isin(periodos_selecionados)
]

st.markdown(
    '<div class="section-kicker">RESUMO DO RECORTE</div>',
    unsafe_allow_html=True,
)

if recorte.empty:
    st.info("Nenhum estudante corresponde aos filtros selecionados.")
    st.stop()


# Cálculos existentes preservados.
sono_medio = recorte["Horas_Sono"].mean()

sono_curto_pct = (
    recorte["Horas_Sono"].lt(SHORT_SLEEP_HOURS).mean() * 100
)

cansaco_alto_pct = (
    recorte["Cansaco_Durante_Dia_1a5"]
    .ge(HIGH_FATIGUE_LEVEL)
    .mean()
    * 100
)


coluna_total, coluna_sono, coluna_sono_curto, coluna_cansaco = (
    st.columns(4, gap="small")
)

coluna_total.metric(
    "Estudantes",
    f"{len(recorte):,}".replace(",", "."),
)

coluna_sono.metric(
    "Sono médio",
    f"{sono_medio:.1f} h",
)

coluna_sono_curto.metric(
    "Abaixo de 7 h de sono",
    f"{sono_curto_pct:.0f}%",
)

coluna_cansaco.metric(
    "Cansaço alto (3 ou mais)",
    f"{cansaco_alto_pct:.0f}%",
)


st.markdown(
    f'<div class="context-note"><strong>Base didática.</strong> '
    f'Os registros são fictícios. '
    f'Os indicadores descrevem o recorte selecionado e não representam '
    f'diagnóstico nem relações causais. '
    f'Os limites de {SHORT_SLEEP_HOURS} horas de sono e nível '
    f'{HIGH_FATIGUE_LEVEL} de cansaço são referências exploratórias.'
    f'</div>',
    unsafe_allow_html=True,
)


# Gráficos complementares usando o mesmo recorte.
render_charts(
    recorte,
    periodos,
    SHORT_SLEEP_HOURS,
    HIGH_FATIGUE_LEVEL,
)