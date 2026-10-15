
"""Comparações por grupo, sem alterar a base original."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# --------------------------------------------------
# CORES E CONFIGURAÇÕES
# --------------------------------------------------

INK = "#263b34"
GREEN = "#2d7053"


# --------------------------------------------------
# RESUMOS ESTATÍSTICOS
# --------------------------------------------------

def sleep_summary(data):
    """Calcula média de sono e quantidade de respostas válidas."""
    return (
        data.groupby("Curso", observed=True)["Horas_Sono"]
        .agg(media="mean", n="count")
        .dropna(subset=["media"])
        .reset_index()
        .sort_values(["media", "Curso"])
    )


def fatigue_summary(data, threshold):
    """Calcula a proporção que atinge o corte em cada grupo."""

    valid = data.dropna(
        subset=["Cansaco_Durante_Dia_1a5"]
    ).copy()

    valid["atinge_limite"] = (
        valid["Cansaco_Durante_Dia_1a5"].ge(threshold)
    )

    result = (
        valid.groupby(
            ["Curso", "Periodo_Curso"],
            observed=True,
        )["atinge_limite"]
        .agg(n="count", casos="sum")
        .reset_index()
    )

    result["percentual"] = (
        result["casos"] / result["n"] * 100
    )

    return result


# --------------------------------------------------
# ESTILO PADRÃO DOS GRÁFICOS
# --------------------------------------------------

def style_figure(fig, height):
    """Aplica o estilo comum aos gráficos."""

    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Arial",
            size=13,
            color=INK,
        ),
        margin=dict(
            l=10,
            r=25,
            t=25,
            b=35,
        ),
        separators=",.",
    )

    return fig


# --------------------------------------------------
# GRÁFICO 1: SONO MÉDIO POR CURSO
# --------------------------------------------------

def sleep_chart(summary, threshold):
    """Barras horizontais ordenadas da menor para a maior média."""

    fig = go.Figure(
        go.Bar(
            x=summary["media"],
            y=summary["Curso"],
            orientation="h",
            marker_color=GREEN,
            text=[
                f"{value:.1f} h".replace(".", ",")
                for value in summary["media"]
            ],
            textposition="outside",
            cliponaxis=False,
            customdata=summary[["n"]],
            hovertemplate=(
                "<b>%{y}</b>"
                "<br>Sono médio: %{x:.2f} h"
                "<br>Respostas válidas: %{customdata[0]}"
                "<extra></extra>"
            ),
        )
    )

    upper = max(
        float(summary["media"].max()),
        threshold,
    ) * 1.18

    fig.update_xaxes(
        title="Horas por noite",
        range=[0, upper],
        gridcolor="#dce5dc",
        zeroline=False,
    )

    fig.update_yaxes(
        autorange="reversed",
        title=None,
        automargin=True,
    )

    fig.add_vline(
        x=threshold,
        line_dash="dot",
        line_color="#66766f",
        annotation_text=f"Referência: {threshold} h",
        annotation_position="top right",
    )

    return style_figure(
        fig,
        max(300, len(summary) * 35 + 80),
    )


# --------------------------------------------------
# GRÁFICO 2: CANSAÇO POR CURSO E PERÍODO
# --------------------------------------------------

def fatigue_chart(summary, courses, periods):
    """Matriz de cansaço com escala sequencial em verde."""

    values = summary.pivot(
        index="Curso",
        columns="Periodo_Curso",
        values="percentual",
    ).reindex(index=courses, columns=periods)

    counts = summary.pivot(
        index="Curso",
        columns="Periodo_Curso",
        values="n",
    ).reindex(index=courses, columns=periods)

    cases = summary.pivot(
        index="Curso",
        columns="Periodo_Curso",
        values="casos",
    ).reindex(index=courses, columns=periods)

    details = [
        [
            [
                int(counts.iloc[i, j]),
                int(cases.iloc[i, j]),
            ]
            if pd.notna(values.iloc[i, j])
            else [None, None]
            for j in range(len(periods))
        ]
        for i in range(len(courses))
    ]

    colorscale = [
        [0.00, "#f0f5f1"],
        [0.25, "#c6ddcc"],
        [0.50, "#7cab90"],
        [0.75, "#427759"],
        [1.00, "#20513b"],
    ]

    fig = go.Figure(
        go.Heatmap(
            z=values.to_numpy(),
            x=periods,
            y=courses,
            customdata=details,
            zmin=0,
            zmax=100,
            colorscale=colorscale,
            xgap=3,
            ygap=3,
            hoverongaps=False,
            colorbar=dict(
                title="%",
                thickness=10,
                len=0.8,
                tickvals=[0, 25, 50, 75, 100],
                ticksuffix="%",
                outlinewidth=0,
            ),
            hovertemplate=(
                "<b>%{y} · %{x}</b>"
                "<br>%{z:.1f}% atingem o limite"
                "<br>%{customdata[1]} de "
                "%{customdata[0]} respostas válidas"
                "<extra></extra>"
            ),
        )
    )

    for i, course in enumerate(courses):
        for j, period in enumerate(periods):
            value = values.iloc[i, j]

            if pd.isna(value):
                text = "—"
                text_color = INK
            else:
                text = f"{value:.0f}%"
                text_color = (
                    "#ffffff"
                    if value >= 65
                    else "#172d23"
                )

            fig.add_annotation(
                x=period,
                y=course,
                text=text,
                showarrow=False,
                font=dict(
                    color=text_color,
                    size=13,
                ),
            )

    fig.update_xaxes(
        title="Período do curso",
        side="bottom",
        showgrid=False,
        zeroline=False,
        automargin=True,
    )

    fig.update_yaxes(
        autorange="reversed",
        title=None,
        showgrid=False,
        zeroline=False,
        automargin=True,
    )

    return style_figure(
        fig,
        max(300, len(courses) * 35 + 80),
    )


# --------------------------------------------------
# GRÁFICO 3: DISTRIBUIÇÃO DO CANSAÇO POR FAIXA DE SONO
# --------------------------------------------------

def sleep_fatigue_chart(data, sleep_threshold=7):
    """Distribuição percentual do cansaço em três faixas de sono."""

    valid = data.dropna(
        subset=["Horas_Sono", "Cansaco_Durante_Dia_1a5"]
    ).copy()

    grupos = [
        f"Menos de {sleep_threshold} h",
        f"{sleep_threshold} a menos de 8 h",
        "8 h ou mais",
    ]

    valid["grupo_sono"] = pd.cut(
        valid["Horas_Sono"],
        bins=[
            float("-inf"),
            sleep_threshold,
            8,
            float("inf"),
        ],
        labels=grupos,
        right=False,
    )

    valid["nivel"] = valid[
        "Cansaco_Durante_Dia_1a5"
    ].astype(int)

    contagem = pd.crosstab(
        valid["grupo_sono"],
        valid["nivel"],
    ).reindex(
        index=grupos,
        columns=[1, 2, 3, 4, 5],
        fill_value=0,
    )

    totais = contagem.sum(axis=1)

    percentuais = contagem.div(
        totais.replace(0, float("nan")),
        axis=0,
    ) * 100

    cores = [
        "#b9ddca",  # Nível 1
        "#7fb99b",  # Nível 2
        "#24a06b",  # Nível 3
        "#d7a64a",  # Nível 4
        "#c95b4a",  # Nível 5
    ]

    fig = go.Figure()

    for nivel, cor in zip(range(1, 6), cores):

        valores = percentuais[nivel]

        fig.add_trace(
            go.Bar(
                x=grupos,
                y=valores,
                name=f"Nível {nivel}",
                marker_color=cor,
                width=0.28,
                text=[
                    f"{valor:.0f}%"
                    if pd.notna(valor) and valor >= 8
                    else ""
                    for valor in valores
                ],
                textposition="inside",
                insidetextanchor="middle",
                customdata=contagem[nivel],
                hovertemplate=(
                    f"<b>Cansaço nível {nivel}</b>"
                    "<br>Faixa de sono: %{x}"
                    "<br>Percentual: %{y:.1f}%"
                    "<br>Estudantes: %{customdata}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        barmode="stack",
        bargap=0.60,
        legend=dict(
            title="Nível de cansaço",
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5,
            traceorder="normal",
        ),
        uniformtext_minsize=11,
        uniformtext_mode="hide",
    )

    # Quantidade de estudantes abaixo de cada coluna.
    rotulos = [
        f"{grupo}<br>(n={int(totais[grupo])})"
        if totais[grupo] > 0
        else f"{grupo}<br>(sem respostas)"
        for grupo in grupos
    ]

    fig.update_xaxes(
        title="Duração do sono",
        tickmode="array",
        tickvals=grupos,
        ticktext=rotulos,
        categoryorder="array",
        categoryarray=grupos,
        showgrid=False,
        zeroline=False,
    )

    fig.update_yaxes(
        title="Distribuição dos estudantes (%)",
        range=[0, 100],
        ticksuffix="%",
        dtick=20,
        gridcolor="#dce5dc",
        zeroline=False,
    )

    fig = style_figure(fig, 520)

    # Espaço adicional para os rótulos e a legenda.
    fig.update_layout(
        margin=dict(
            l=10,
            r=25,
            t=65,
            b=75,
        ),
    )

    return fig


# --------------------------------------------------
# RENDERIZAÇÃO DOS TRÊS GRÁFICOS
# --------------------------------------------------

def render_charts(
    data,
    periods,
    sleep_threshold=7,
    fatigue_threshold=3,
):
    """Exibe os três gráficos com os filtros já aplicados."""

    st.subheader(
        "Como sono e cansaço se distribuem entre os grupos?"
    )

    sono = sleep_summary(data)
    cansaco = fatigue_summary(data, fatigue_threshold)

    courses = sono["Curso"].tolist()

    # Inclui cursos sem horas de sono válidas.
    courses += sorted(
        set(data["Curso"].dropna()) - set(courses)
    )

    available_periods = set(
        data["Periodo_Curso"].dropna()
    )

    selected_periods = [
        period
        for period in periods
        if period in available_periods
    ]

    # ---------------------------------------
    # GRÁFICO 1: SONO MÉDIO POR CURSO
    # ---------------------------------------

    st.markdown("**Sono médio por curso**")

    st.caption(
        "Da menor para a maior média. Passe o cursor "
        "para ver o número de respostas."
    )

    if sono.empty:
        st.info(
            "Sem respostas válidas de horas de sono neste recorte."
        )
    else:
        st.plotly_chart(
            sleep_chart(sono, sleep_threshold),
            width="stretch",
            config={"displayModeBar": False},
            key="sono_por_curso",
        )

    # ---------------------------------------
    # GRÁFICO 2: CANSAÇO POR CURSO E PERÍODO
    # ---------------------------------------

    st.markdown(
        f"**Cansaço de nível {fatigue_threshold} ou mais "
        f"por curso e período**"
    )

    st.caption(
        "Tons mais escuros indicam maior proporção. "
        "Escala fixa de 0 a 100%; cursos na mesma ordem "
        "do gráfico acima."
    )

    if cansaco.empty:
        st.info(
            "Sem respostas válidas de cansaço neste recorte."
        )
    else:
        st.plotly_chart(
            fatigue_chart(
                cansaco,
                courses,
                selected_periods,
            ),
            width="stretch",
            config={"displayModeBar": False},
            key="cansaco_por_grupo",
        )

        st.caption(
            "— indica ausência de respostas, não 0%. "
            "Grupos pequenos exigem cautela; consulte o tamanho "
            "do grupo ao passar o cursor. "
            "O corte é exploratório, não um diagnóstico."
        )

    # ---------------------------------------
    # GRÁFICO 3: DISTRIBUIÇÃO DO CANSAÇO
    # ---------------------------------------

    st.markdown(
        "**Distribuição dos níveis de cansaço por duração do sono**"
    )

    st.caption(
        "Comparação da distribuição percentual dos níveis de cansaço "
        "entre estudantes que dormem menos de 7 horas, "
        "de 7 a menos de 8 horas e 8 horas ou mais. "
        "Cada coluna representa 100% dos estudantes da respectiva faixa."
    )

    dados_validos = data.dropna(
        subset=["Horas_Sono", "Cansaco_Durante_Dia_1a5"]
    )

    if dados_validos.empty:
        st.info(
            "Sem respostas válidas para analisar "
            "a distribuição do cansaço por duração do sono."
        )
    else:
        st.plotly_chart(
            sleep_fatigue_chart(
                dados_validos,
                sleep_threshold,
            ),
            width="stretch",
            config={"displayModeBar": False},
            key="relacao_sono_cansaco",
        )

        st.caption(
            "Os percentuais consideram apenas respostas válidas "
            "de sono e cansaço. Passe o cursor sobre as colunas "
            "para consultar a quantidade de estudantes em cada nível. "
            "Faixas sem respostas não apresentam percentuais. "
            "As associações observadas não estabelecem causalidade."
        )
