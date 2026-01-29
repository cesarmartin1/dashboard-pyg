"""
Sección de Balance de Situación del Dashboard.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List
from utils.formatters import format_currency, calculate_variation


def render_balance(balance_kpis: Dict, activo_detalle: Dict, pasivo_detalle: Dict,
                   years: List[str], year_selected: str, compare_year: str):
    """Renderiza la sección de Balance de Situación."""

    st.markdown("## 📋 Balance de Situación")

    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        activo = balance_kpis.get('total_activo', {}).get(year_selected, 0)
        activo_ant = balance_kpis.get('total_activo', {}).get(compare_year, 0)
        var = calculate_variation(activo, activo_ant)
        st.metric(
            "Total Activo",
            format_currency(activo),
            f"{var:+.1f}% vs {compare_year}"
        )

    with col2:
        patrimonio = balance_kpis.get('patrimonio_neto', {}).get(year_selected, 0)
        patrimonio_ant = balance_kpis.get('patrimonio_neto', {}).get(compare_year, 0)
        var = calculate_variation(patrimonio, patrimonio_ant)
        st.metric(
            "Patrimonio Neto",
            format_currency(patrimonio),
            f"{var:+.1f}% vs {compare_year}"
        )

    with col3:
        pasivo_nc = balance_kpis.get('pasivo_no_corriente', {}).get(year_selected, 0)
        pasivo_c = balance_kpis.get('pasivo_corriente', {}).get(year_selected, 0)
        pasivo_total = pasivo_nc + pasivo_c
        st.metric(
            "Pasivo Total",
            format_currency(pasivo_total)
        )

    with col4:
        activo_c = balance_kpis.get('activo_corriente', {}).get(year_selected, 0)
        fondo_maniobra = activo_c - pasivo_c
        st.metric(
            "Fondo de Maniobra",
            format_currency(fondo_maniobra),
            "Positivo" if fondo_maniobra > 0 else "Negativo",
            delta_color="normal" if fondo_maniobra > 0 else "inverse"
        )

    st.markdown("---")

    # Gráficos de estructura
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### 📊 Estructura del Activo ({year_selected})")

        activo_nc = balance_kpis.get('activo_no_corriente', {}).get(year_selected, 0)
        activo_c = balance_kpis.get('activo_corriente', {}).get(year_selected, 0)

        fig = go.Figure(data=[go.Pie(
            labels=['Activo No Corriente', 'Activo Corriente'],
            values=[activo_nc, activo_c],
            hole=0.4,
            marker_colors=['#1f77b4', '#2ca02c'],
            textinfo='percent+label',
            textposition='outside'
        )])

        total = activo_nc + activo_c
        fig.update_layout(
            height=350,
            annotations=[dict(text=f'Total<br>{format_currency(total)}', x=0.5, y=0.5, font_size=12, showarrow=False)],
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"### 📊 Estructura del Pasivo ({year_selected})")

        patrimonio = balance_kpis.get('patrimonio_neto', {}).get(year_selected, 0)
        pasivo_nc = balance_kpis.get('pasivo_no_corriente', {}).get(year_selected, 0)
        pasivo_c = balance_kpis.get('pasivo_corriente', {}).get(year_selected, 0)

        fig = go.Figure(data=[go.Pie(
            labels=['Patrimonio Neto', 'Pasivo No Corriente', 'Pasivo Corriente'],
            values=[patrimonio, pasivo_nc, pasivo_c],
            hole=0.4,
            marker_colors=['#2ca02c', '#ff7f0e', '#d62728'],
            textinfo='percent+label',
            textposition='outside'
        )])

        total = patrimonio + pasivo_nc + pasivo_c
        fig.update_layout(
            height=350,
            annotations=[dict(text=f'Total<br>{format_currency(total)}', x=0.5, y=0.5, font_size=12, showarrow=False)],
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    # Evolución temporal
    st.markdown("---")
    st.markdown("### 📈 Evolución del Balance")

    data_balance = {
        'Año': years,
        'Activo No Corriente': [balance_kpis.get('activo_no_corriente', {}).get(y, 0) for y in years],
        'Activo Corriente': [balance_kpis.get('activo_corriente', {}).get(y, 0) for y in years],
        'Patrimonio Neto': [balance_kpis.get('patrimonio_neto', {}).get(y, 0) for y in years],
        'Pasivo No Corriente': [balance_kpis.get('pasivo_no_corriente', {}).get(y, 0) for y in years],
        'Pasivo Corriente': [balance_kpis.get('pasivo_corriente', {}).get(y, 0) for y in years],
    }
    df_balance = pd.DataFrame(data_balance)

    # Crear gráfico de barras apiladas
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Activo', 'Pasivo y Patrimonio'))

    # Activo
    fig.add_trace(go.Bar(
        name='Activo No Corriente',
        x=df_balance['Año'],
        y=df_balance['Activo No Corriente'],
        marker_color='#1f77b4'
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        name='Activo Corriente',
        x=df_balance['Año'],
        y=df_balance['Activo Corriente'],
        marker_color='#2ca02c'
    ), row=1, col=1)

    # Pasivo
    fig.add_trace(go.Bar(
        name='Patrimonio Neto',
        x=df_balance['Año'],
        y=df_balance['Patrimonio Neto'],
        marker_color='#2ca02c'
    ), row=1, col=2)

    fig.add_trace(go.Bar(
        name='Pasivo No Corriente',
        x=df_balance['Año'],
        y=df_balance['Pasivo No Corriente'],
        marker_color='#ff7f0e'
    ), row=1, col=2)

    fig.add_trace(go.Bar(
        name='Pasivo Corriente',
        x=df_balance['Año'],
        y=df_balance['Pasivo Corriente'],
        marker_color='#d62728'
    ), row=1, col=2)

    fig.update_layout(
        height=400,
        barmode='stack',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.05),
        yaxis_tickformat=',.0f',
        yaxis2_tickformat=',.0f'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detalle del Activo
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### 🏗️ Composición del Inmovilizado ({year_selected})")

        if activo_detalle:
            activo_filtered = {k: v[year_selected] for k, v in activo_detalle.items() if v.get(year_selected, 0) > 0}

            if activo_filtered:
                fig = go.Figure(data=[go.Bar(
                    x=list(activo_filtered.values()),
                    y=list(activo_filtered.keys()),
                    orientation='h',
                    marker_color='#1f77b4',
                    text=[format_currency(v) for v in activo_filtered.values()],
                    textposition='outside'
                )])
                fig.update_layout(height=400, xaxis_tickformat=',.0f')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos detallados de activo disponibles")

    with col2:
        st.markdown(f"### 💰 Composición del Activo Corriente ({year_selected})")

        ac_data = {
            'Existencias': balance_kpis.get('existencias', {}).get(year_selected, 0),
            'Deudores': balance_kpis.get('deudores', {}).get(year_selected, 0),
            'Efectivo': balance_kpis.get('efectivo', {}).get(year_selected, 0)
        }

        ac_filtered = {k: v for k, v in ac_data.items() if v > 0}

        if ac_filtered:
            fig = go.Figure(data=[go.Pie(
                labels=list(ac_filtered.keys()),
                values=list(ac_filtered.values()),
                hole=0.3,
                marker_colors=['#ff6b6b', '#4ecdc4', '#45b7d1']
            )])
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Tabla resumen
    st.markdown("---")
    st.markdown("### 📋 Resumen del Balance")

    resumen = [
        {'Partida': 'ACTIVO NO CORRIENTE', **{y: balance_kpis.get('activo_no_corriente', {}).get(y, 0) for y in years}},
        {'Partida': '  - Inmovilizado Intangible', **{y: balance_kpis.get('inmovilizado_intangible', {}).get(y, 0) for y in years}},
        {'Partida': '  - Inmovilizado Material', **{y: balance_kpis.get('inmovilizado_material', {}).get(y, 0) for y in years}},
        {'Partida': 'ACTIVO CORRIENTE', **{y: balance_kpis.get('activo_corriente', {}).get(y, 0) for y in years}},
        {'Partida': '  - Existencias', **{y: balance_kpis.get('existencias', {}).get(y, 0) for y in years}},
        {'Partida': '  - Deudores', **{y: balance_kpis.get('deudores', {}).get(y, 0) for y in years}},
        {'Partida': '  - Efectivo', **{y: balance_kpis.get('efectivo', {}).get(y, 0) for y in years}},
        {'Partida': 'TOTAL ACTIVO', **{y: balance_kpis.get('total_activo', {}).get(y, 0) for y in years}},
        {'Partida': '', **{y: '' for y in years}},
        {'Partida': 'PATRIMONIO NETO', **{y: balance_kpis.get('patrimonio_neto', {}).get(y, 0) for y in years}},
        {'Partida': '  - Capital', **{y: balance_kpis.get('capital', {}).get(y, 0) for y in years}},
        {'Partida': '  - Reservas', **{y: balance_kpis.get('reservas', {}).get(y, 0) for y in years}},
        {'Partida': '  - Resultado del Ejercicio', **{y: balance_kpis.get('resultado_ejercicio_balance', {}).get(y, 0) for y in years}},
        {'Partida': 'PASIVO NO CORRIENTE', **{y: balance_kpis.get('pasivo_no_corriente', {}).get(y, 0) for y in years}},
        {'Partida': 'PASIVO CORRIENTE', **{y: balance_kpis.get('pasivo_corriente', {}).get(y, 0) for y in years}},
        {'Partida': 'TOTAL PASIVO + PN', **{y: balance_kpis.get('total_pasivo_patrimonio', {}).get(y, 0) for y in years}},
    ]

    df_resumen = pd.DataFrame(resumen)

    # Formatear números
    format_dict = {y: '{:,.0f} €' for y in years}

    st.dataframe(
        df_resumen.style.format(format_dict, na_rep=''),
        use_container_width=True,
        hide_index=True
    )


def render_ratios_financieros(ratios: Dict, years: List[str], year_selected: str, compare_year: str):
    """Renderiza la sección de Ratios Financieros."""

    st.markdown("## 📐 Ratios Financieros")

    # KPIs principales
    year_ratios = ratios.get(year_selected, {})
    compare_ratios = ratios.get(compare_year, {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        roe = year_ratios.get('roe', 0)
        roe_ant = compare_ratios.get('roe', 0)
        st.metric(
            "ROE (Rentabilidad)",
            f"{roe:.1f}%",
            f"{roe - roe_ant:+.1f} pp"
        )

    with col2:
        roa = year_ratios.get('roa', 0)
        roa_ant = compare_ratios.get('roa', 0)
        st.metric(
            "ROA (Rent. Activos)",
            f"{roa:.1f}%",
            f"{roa - roa_ant:+.1f} pp"
        )

    with col3:
        liquidez = year_ratios.get('ratio_liquidez', 0)
        liquidez_ant = compare_ratios.get('ratio_liquidez', 0)
        st.metric(
            "Ratio Liquidez",
            f"{liquidez:.2f}",
            f"{liquidez - liquidez_ant:+.2f}"
        )

    with col4:
        endeudamiento = year_ratios.get('ratio_endeudamiento', 0) * 100
        endeudamiento_ant = compare_ratios.get('ratio_endeudamiento', 0) * 100
        st.metric(
            "Endeudamiento",
            f"{endeudamiento:.1f}%",
            f"{endeudamiento - endeudamiento_ant:+.1f} pp",
            delta_color="inverse"
        )

    st.markdown("---")

    # Secciones de ratios
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💧 Ratios de Liquidez")

        liquidez_data = []
        for year in years:
            yr = ratios.get(year, {})
            liquidez_data.append({
                'Año': year,
                'Liquidez General': yr.get('ratio_liquidez', 0),
                'Acid Test': yr.get('ratio_acid_test', 0),
                'Tesorería': yr.get('ratio_tesoreria', 0)
            })

        df_liq = pd.DataFrame(liquidez_data)

        fig = go.Figure()
        for col in ['Liquidez General', 'Acid Test', 'Tesorería']:
            fig.add_trace(go.Scatter(
                x=df_liq['Año'],
                y=df_liq[col],
                name=col,
                mode='lines+markers',
                line=dict(width=3),
                marker=dict(size=10)
            ))

        fig.add_hline(y=1, line_dash="dash", line_color="red", annotation_text="Mínimo recomendado")
        fig.update_layout(height=350, yaxis_title='Ratio', hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

        # Interpretación
        liq = year_ratios.get('ratio_liquidez', 0)
        if liq >= 1.5:
            st.success(f"✅ Liquidez óptima ({liq:.2f}): La empresa puede cubrir sus deudas a corto plazo")
        elif liq >= 1:
            st.warning(f"⚠️ Liquidez ajustada ({liq:.2f}): Capacidad justa para cubrir deudas CP")
        else:
            st.error(f"❌ Liquidez insuficiente ({liq:.2f}): Riesgo de no poder cubrir deudas CP")

    with col2:
        st.markdown("### 📊 Ratios de Rentabilidad")

        rent_data = []
        for year in years:
            yr = ratios.get(year, {})
            rent_data.append({
                'Año': year,
                'ROE': yr.get('roe', 0),
                'ROA': yr.get('roa', 0),
                'Margen Neto': yr.get('margen_neto', 0)
            })

        df_rent = pd.DataFrame(rent_data)

        fig = go.Figure()
        colors = ['#2ca02c', '#1f77b4', '#ff7f0e']
        for i, col in enumerate(['ROE', 'ROA', 'Margen Neto']):
            fig.add_trace(go.Bar(
                name=col,
                x=df_rent['Año'],
                y=df_rent[col],
                marker_color=colors[i],
                text=[f"{v:.1f}%" for v in df_rent[col]],
                textposition='outside'
            ))

        fig.update_layout(height=350, barmode='group', yaxis_title='Porcentaje (%)')
        st.plotly_chart(fig, use_container_width=True)

        # Interpretación
        roe = year_ratios.get('roe', 0)
        if roe >= 15:
            st.success(f"✅ ROE excelente ({roe:.1f}%): Alta rentabilidad para los accionistas")
        elif roe >= 8:
            st.info(f"ℹ️ ROE aceptable ({roe:.1f}%): Rentabilidad moderada")
        else:
            st.warning(f"⚠️ ROE bajo ({roe:.1f}%): Rentabilidad por debajo de lo esperado")

    # Segunda fila
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏦 Ratios de Endeudamiento")

        end_data = []
        for year in years:
            yr = ratios.get(year, {})
            end_data.append({
                'Año': year,
                'Endeudamiento': yr.get('ratio_endeudamiento', 0) * 100,
                'Autonomía': yr.get('ratio_autonomia', 0) * 100,
                'Apalancamiento': yr.get('ratio_apalancamiento', 0)
            })

        df_end = pd.DataFrame(end_data)

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Bar(
            name='Endeudamiento %',
            x=df_end['Año'],
            y=df_end['Endeudamiento'],
            marker_color='#d62728'
        ), secondary_y=False)

        fig.add_trace(go.Bar(
            name='Autonomía %',
            x=df_end['Año'],
            y=df_end['Autonomía'],
            marker_color='#2ca02c'
        ), secondary_y=False)

        fig.add_trace(go.Scatter(
            name='Apalancamiento',
            x=df_end['Año'],
            y=df_end['Apalancamiento'],
            mode='lines+markers',
            line=dict(color='#ff7f0e', width=3)
        ), secondary_y=True)

        fig.update_layout(height=350, barmode='group')
        fig.update_yaxes(title_text="Porcentaje (%)", secondary_y=False)
        fig.update_yaxes(title_text="Ratio", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

        # Interpretación
        end = year_ratios.get('ratio_endeudamiento', 0) * 100
        if end <= 50:
            st.success(f"✅ Endeudamiento conservador ({end:.1f}%): Bajo riesgo financiero")
        elif end <= 70:
            st.warning(f"⚠️ Endeudamiento moderado ({end:.1f}%): Vigilar la evolución")
        else:
            st.error(f"❌ Endeudamiento elevado ({end:.1f}%): Alto riesgo financiero")

    with col2:
        st.markdown("### 🔄 Fondo de Maniobra")

        fm_data = []
        for year in years:
            yr = ratios.get(year, {})
            fm_data.append({
                'Año': year,
                'Fondo de Maniobra': yr.get('fondo_maniobra', 0),
                '% sobre Activo': yr.get('capital_circulante_ratio', 0) * 100
            })

        df_fm = pd.DataFrame(fm_data)

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Bar(
            name='Fondo de Maniobra (€)',
            x=df_fm['Año'],
            y=df_fm['Fondo de Maniobra'],
            marker_color='#1f77b4',
            text=[format_currency(v) for v in df_fm['Fondo de Maniobra']],
            textposition='outside'
        ), secondary_y=False)

        fig.add_trace(go.Scatter(
            name='% sobre Activo',
            x=df_fm['Año'],
            y=df_fm['% sobre Activo'],
            mode='lines+markers',
            line=dict(color='#ff7f0e', width=3)
        ), secondary_y=True)

        fig.update_layout(height=350)
        fig.update_yaxes(title_text="Euros (€)", tickformat=',.0f', secondary_y=False)
        fig.update_yaxes(title_text="Porcentaje (%)", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

        # Interpretación
        fm = year_ratios.get('fondo_maniobra', 0)
        if fm > 0:
            st.success(f"✅ Fondo de maniobra positivo ({format_currency(fm)}): Buena salud financiera a corto plazo")
        else:
            st.error(f"❌ Fondo de maniobra negativo ({format_currency(fm)}): Riesgo de tensiones de liquidez")

    # Tabla resumen de ratios
    st.markdown("---")
    st.markdown("### 📋 Tabla Resumen de Ratios")

    tabla_ratios = []
    for year in years:
        yr = ratios.get(year, {})
        tabla_ratios.append({
            'Año': year,
            'Liquidez': f"{yr.get('ratio_liquidez', 0):.2f}",
            'Acid Test': f"{yr.get('ratio_acid_test', 0):.2f}",
            'Tesorería': f"{yr.get('ratio_tesoreria', 0):.2f}",
            'ROE (%)': f"{yr.get('roe', 0):.1f}%",
            'ROA (%)': f"{yr.get('roa', 0):.1f}%",
            'Endeudamiento (%)': f"{yr.get('ratio_endeudamiento', 0) * 100:.1f}%",
            'Solvencia': f"{yr.get('ratio_solvencia', 0):.2f}",
            'Fondo Maniobra': format_currency(yr.get('fondo_maniobra', 0))
        })

    df_ratios = pd.DataFrame(tabla_ratios)
    st.dataframe(df_ratios, use_container_width=True, hide_index=True)
