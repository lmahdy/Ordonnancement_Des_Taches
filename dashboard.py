"""
Streamlit Dashboard - Compare GA, SA, ACO, TABU scheduling results.

Usage:
    cd NEWPROJECT
    streamlit run dashboard.py
"""

import json
from pathlib import Path

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = Path(__file__).parent / "results"

ALGO_COLORS = {'GA': '#2ecc71', 'SA': '#3498db', 'ACO': '#e74c3c', 'TABU': '#9b59b6'}


def load_comparison():
    """Load the comparison.json produced by run_all.py."""
    path = RESULTS_DIR / "comparison.json"
    if not path.exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    st.set_page_config(
        page_title="Scheduling Algorithms Comparison",
        layout="wide",
    )

    st.title("Ordonnancement des Taches - Comparaison des Algorithmes")
    st.markdown("**Genetic Algorithm (GA)** vs **Simulated Annealing (SA)** "
                "vs **Ant Colony Optimization (ACO)** vs **Tabu Search (TABU)** "
                "on **1000 tasks**")

    results = load_comparison()
    if results is None:
        st.error("No results found! Run `python run_all.py` first to generate results.")
        return

    # ==================== SUMMARY TABLE ====================
    st.header("Tableau Recapitulatif")

    table_data = []
    for r in results:
        table_data.append({
            'Algorithme': r['algorithm'],
            'Makespan (min)': r['makespan'],
            'Makespan (heures)': r['makespan_hours'],
            'Temps d\'execution (s)': r['runtime_seconds'],
            'Nombre d\'operations': r['num_operations'],
        })

    st.table(table_data)

    best = results[0]  # Already sorted by makespan
    st.success(
        f"**Meilleur algorithme: {best['algorithm']}** avec un makespan de "
        f"**{best['makespan']} minutes** ({best['makespan_hours']} heures)"
    )

    # ==================== BAR CHARTS ====================
    st.header("Comparaison Graphique")

    col1, col2 = st.columns(2)

    algos = [r['algorithm'] for r in results]
    makespans = [r['makespan'] for r in results]
    runtimes = [r['runtime_seconds'] for r in results]
    colors = [ALGO_COLORS.get(a, '#999') for a in algos]

    with col1:
        st.subheader("Makespan (minutes)")
        fig, ax = plt.subplots(figsize=(7, 5))
        bars = ax.bar(algos, makespans, color=colors, edgecolor='black', linewidth=1.2)
        ax.set_ylabel('Makespan (minutes)', fontsize=12)
        ax.set_title('Comparaison du Makespan', fontweight='bold', fontsize=14)
        for bar, val in zip(bars, makespans):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(makespans) * 0.01,
                    f'{val}', ha='center', fontweight='bold', fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        fig.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("Temps d'execution (secondes)")
        fig, ax = plt.subplots(figsize=(7, 5))
        bars = ax.bar(algos, runtimes, color=colors, edgecolor='black', linewidth=1.2)
        ax.set_ylabel('Temps (secondes)', fontsize=12)
        ax.set_title('Comparaison du Temps d\'Execution', fontweight='bold', fontsize=14)
        for bar, val in zip(bars, runtimes):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(runtimes) * 0.01,
                    f'{val:.1f}s', ha='center', fontweight='bold', fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        fig.tight_layout()
        st.pyplot(fig)

    # ==================== MAKESPAN IN HOURS (PIE-STYLE COMPARISON) ====================
    st.header("Performance Relative")
    col3, col4 = st.columns(2)

    with col3:
        # Horizontal bar chart showing hours
        hours = [r['makespan_hours'] for r in results]
        fig, ax = plt.subplots(figsize=(8, 4))
        y_pos = range(len(algos))
        bars = ax.barh(y_pos, hours, color=colors, edgecolor='black', height=0.5)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(algos, fontsize=12)
        ax.set_xlabel('Makespan (heures)', fontsize=12)
        ax.set_title('Makespan en Heures', fontweight='bold', fontsize=14)
        for bar, val in zip(bars, hours):
            ax.text(bar.get_width() + max(hours) * 0.01, bar.get_y() + bar.get_height() / 2,
                    f'{val:.2f}h', va='center', fontweight='bold', fontsize=11)
        ax.grid(axis='x', alpha=0.3)
        fig.tight_layout()
        st.pyplot(fig)

    with col4:
        # Improvement percentages relative to worst
        worst_ms = max(makespans)
        st.subheader("Amelioration vs le pire")
        for r in results:
            improvement = ((worst_ms - r['makespan']) / worst_ms) * 100
            st.metric(
                label=r['algorithm'],
                value=f"{r['makespan']} min",
                delta=f"{improvement:+.1f}%" if improvement > 0 else "Reference",
            )

    # ==================== CONVERGENCE CURVES ====================
    st.header("Courbes de Convergence")

    fig, ax = plt.subplots(figsize=(12, 5))
    for r in results:
        conv = r.get('convergence', [])
        if conv:
            color = ALGO_COLORS.get(r['algorithm'], '#999')
            ax.plot(conv, label=f"{r['algorithm']} (final={conv[-1]})",
                    color=color, linewidth=2)
    ax.set_xlabel('Iteration / Generation', fontsize=12)
    ax.set_ylabel('Meilleur Makespan', fontsize=12)
    ax.set_title('Convergence de Chaque Algorithme', fontweight='bold', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)

    # ==================== GANTT CHARTS ====================
    st.header("Diagrammes de Gantt")

    for name in ['ga', 'sa', 'aco', 'tabu']:
        img_path = RESULTS_DIR / f"{name}_gantt.png"
        if img_path.exists():
            st.subheader(f"{name.upper()} - Diagramme de Gantt")
            st.image(str(img_path), use_container_width=True)
        else:
            st.warning(f"Gantt chart not found for {name.upper()}")

    # ==================== ALGORITHM PARAMETERS ====================
    st.header("Parametres Utilises")
    for r in results:
        with st.expander(f"{r['algorithm']} - Parametres"):
            st.json(r.get('params', {}))

    # ==================== FOOTER ====================
    st.markdown("---")
    st.markdown("*Projet d'Ordonnancement des Taches - Comparaison GA vs SA vs ACO vs TABU*")


if __name__ == '__main__':
    main()
