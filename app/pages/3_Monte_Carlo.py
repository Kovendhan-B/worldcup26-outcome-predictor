import sys
from pathlib import Path

import streamlit as st

# ----------------------------------
# Project Imports
# ----------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.monte_carlo import run_monte_carlo_simulations
from src.flags import COUNTRY_CODES, FLAG_CDN

# ----------------------------------
# Page Config
# ----------------------------------

st.set_page_config(
    page_title="Monte Carlo Simulator - FIFA World Cup 2026",
    page_icon="🎲",
    layout="wide"
)

# ----------------------------------
# Title
# ----------------------------------

st.title("🎲 Monte Carlo Simulator")

st.markdown(
    """
    Run full tournament simulations N times using probability-weighted random sampling
    to determine the true likelihood of each team's success in the FIFA World Cup 2026.
    """
)

# ----------------------------------
# Sidebar Controls
# ----------------------------------

st.sidebar.header("Simulation Settings")

num_sims = st.sidebar.slider(
    "Number of Simulations",
    min_value=100,
    max_value=10000,
    value=1000,
    step=100,
    help="Higher numbers take longer but provide more stable probabilities."
)

run_button = st.sidebar.button("⚡ Run Simulations")

# ----------------------------------
# Main Content
# ----------------------------------

if run_button:
    
    progress_bar = st.progress(0, text="Starting simulations...")
    
    def update_progress(current, total):
        pct = current / total
        # Cap at 1.0
        pct = min(pct, 1.0)
        progress_bar.progress(pct, text=f"Simulating tournament {current}/{total}...")
        
    fixtures_path = "data/fixtures/worldcup2026_fixtures.csv"
    
    # Run the simulations
    df = run_monte_carlo_simulations(
        fixtures_path=fixtures_path,
        num_simulations=num_sims,
        progress_callback=update_progress
    )
    
    progress_bar.progress(1.0, text="Simulation complete!")
    st.success(f"Successfully ran {num_sims} tournament simulations!")
    
    # ----------------------------------
    # Results visualization
    # ----------------------------------
    
    st.header("🏆 Top 10 Championship Contenders")
    
    top_10 = df.head(10).copy()
    
    # Bar chart using Streamlit native charts
    st.bar_chart(
        data=top_10,
        x="Team",
        y="Champion %",
        color="#4CAF50"
    )
    
    st.header("📊 Full Tournament Probabilities")
    
    df_display = df.copy()
    
    # Create a column for Flag URLs instead of raw HTML
    df_display.insert(0, "Flag", df_display["Team"].apply(
        lambda t: f"{FLAG_CDN}/{COUNTRY_CODES.get(t)}.png" if t in COUNTRY_CODES else None
    ))
    
    # Format columns
    format_dict = {
        col: "{:.1f}%" for col in df_display.columns if "%" in col
    }
    
    st.dataframe(
        df_display.style.format(format_dict),
        column_config={
            "Flag": st.column_config.ImageColumn(
                "Flag", help="Country Flag"
            )
        },
        use_container_width=True,
        hide_index=True,
        height=800
    )
    
    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Results (CSV)",
        data=csv,
        file_name='monte_carlo_results.csv',
        mime='text/csv',
    )
else:
    st.info("👈 Set your parameters and click **Run Simulations** in the sidebar to begin.")
