import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data, save_entry
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from games import MiniSudoku

# Configuration
DATA_FILE = 'data.csv'
st.set_page_config(page_title="Happiness Dashboard", page_icon="😊", layout="wide")

# ... (rest of CSS and main function remains same) ...


# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        color: white;
        background-color: #4CAF50;
        border-radius: 5px;
    }
    .stMetric {
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Go to", ["Activity: Log Happiness", "Dashboard: Analytics"])
    
    st.sidebar.markdown("---")
    st.sidebar.info("Use this app to track and analyze happiness levels.")

    if app_mode == "Activity: Log Happiness":
        render_activity_page()
    elif app_mode == "Dashboard: Analytics":
        render_dashboard_page()

def render_activity_page():
    st.title("😊 Log Your Happiness")
    st.markdown("Taking a moment to reflect on your well-being.")
    
    # Game Section
    st.markdown("### 🎮 Boost Your Focus")
    with st.expander("Play Mini-Sudoku (Optional)", expanded=False):
        game = MiniSudoku()
        is_complete, score, attempts = game.render_game()
        
        # Logic: If attempted but not complete, score is 0. If complete, score is calculated.
        # If not attempted, score is None.
        if is_complete:
            st.session_state['latest_game_score'] = score
        elif attempts > 0:
             st.session_state['latest_game_score'] = 0
        else:
             # Keep previous state if existing, else None
             if 'latest_game_score' not in st.session_state:
                 st.session_state['latest_game_score'] = None
    
    with st.form("happiness_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name (Optional)", placeholder="Anonymous")
            happiness_score = st.slider("How happy do you feel? (1-10)", 1, 10, 5)
            energy_score = st.slider("How energetic do you feel? (1-10)", 1, 10, 5, help="Physical vitality")
            sleep_score = st.slider("How well did you sleep? (1-10)", 1, 10, 5, help="Restfulness of last night")
            
        with col2:
            stress_score = st.slider("How stressed are you? (1-10)", 1, 10, 5, help="Mental pressure (1=Low, 10=High)")
            social_score = st.slider("How socially connected do you feel? (1-10)", 1, 10, 5, help="Sense of belonging")
            factors = st.multiselect(
                "What is influencing your mood?",
                ["Work", "Family", "Health", "Weather", "Social Life", "Hobbies", "Sleep", "Food", "Other"]
            )
            gratitude = st.text_input("One thing you are grateful for today:", placeholder="I am grateful for...")
            notes = st.text_area("Any other thoughts?", placeholder="Share more details...")
            
        # Display game score if available
        game_score = st.session_state.get('latest_game_score', None)
        if game_score is not None:
            if game_score > 0:
                st.info(f"✨ Including Game Focus Score: {game_score}/10")
            elif game_score == 0:
                st.warning(f"⚠️ Including Game Focus Score: 0/10 (Incorrect Solution)")
            
        submitted = st.form_submit_button("Submit Entry")
        
        if submitted:
            # Prepare data
            entry = {
                'Name': name if name else "Anonymous",
                'Happiness Score': happiness_score,
                'Energy Level': energy_score,
                'Stress Level': stress_score,
                'Sleep Quality': sleep_score,
                'Social Connection': social_score,
                'Game Score': game_score if game_score is not None else None, # Explicitly handle None
                'Factors': ", ".join(factors),
                'Gratitude': gratitude,
                'Notes': notes
            }
            
            # Save data
            save_entry(DATA_FILE, entry)
            st.cache_data.clear()
            
            # Reset Game State
            if 'sudoku_attempts' in st.session_state:
                del st.session_state['sudoku_attempts']
            if 'latest_game_score' in st.session_state:
                del st.session_state['latest_game_score']
            if 'sudoku_board' in st.session_state: # Reset board for new game
                del st.session_state['sudoku_board']
                
            st.success("Thank you! Your activity has been recorded.")
            st.balloons()

def render_dashboard_page():
    st.title("📊 Happiness Dashboard")
    
    # Load data
    df, source, error = load_data(DATA_FILE)
    
    # Connection Status
    with st.sidebar.expander("Connection Status", expanded=True):
        if source == "Google Sheets":
            st.success(f"🟢 Connected to {source}")
        else:
            st.warning(f"🟠 Using {source}")
            st.error(f"Error: {error}")
    
    if df.empty:
        st.warning("No data available yet. Go to the 'Activity' tab to log some entries!")
        return

    # KPI Metrics
    st.subheader("Well-being Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    avg_happiness = df['Happiness Score'].mean()
    
    # helper for safe mean
    def safe_mean(col):
        return df[col].mean() if col in df.columns else 0

    with col1:
        st.metric("Avg Happiness", f"{avg_happiness:.1f}/10")
    with col2:
        st.metric("Avg Energy", f"{safe_mean('Energy Level'):.1f}/10")
    with col3:
        st.metric("Avg Stress", f"{safe_mean('Stress Level'):.1f}/10")
    with col4:
        st.metric("Avg Sleep", f"{safe_mean('Sleep Quality'):.1f}/10")
    with col5:
        st.metric("Total Responses", len(df))

    st.markdown("---")

    # Visualizations
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Distributions")
        # Multi-metric histogram
        metrics_to_plot = ['Happiness Score', 'Energy Level', 'Stress Level']
        available_metrics = [m for m in metrics_to_plot if m in df.columns]
        
        if available_metrics:
            df_melted = df.melt(value_vars=available_metrics, var_name="Metric", value_name="Score")
            fig_hist = px.histogram(df_melted, x="Score", color="Metric", barmode='overlay',
                                    title="Distribution of Key Metrics", nbins=10)
            fig_hist.update_layout(bargap=0.1)
            st.plotly_chart(fig_hist, width="stretch")
        
    with col_chart2:
        st.subheader("Top Influencing Factors")
        # Process factors (comma-separated strings)
        all_factors = []
        if 'Factors' in df.columns:
            for item in df['Factors'].dropna():
                if item:
                    all_factors.extend([f.strip() for f in item.split(',')])
        
        if all_factors:
            factors_df = pd.DataFrame(all_factors, columns=['Factor'])
            factor_counts = factors_df['Factor'].value_counts().reset_index()
            factor_counts.columns = ['Factor', 'Count']
            
            fig_bar = px.bar(factor_counts, x='Factor', y='Count', 
                             title="Frequency of Factors",
                             color='Count', color_continuous_scale='Greens')
            st.plotly_chart(fig_bar, width="stretch")
        else:
            st.info("No factors recorded yet.")

    # Timeline layout
    st.subheader("Trends Over Time")
    if 'Timestamp' in df.columns and not df['Timestamp'].isnull().all():
        df_sorted = df.sort_values('Timestamp')
        plot_cols = [c for c in ['Happiness Score', 'Energy Level', 'Stress Level'] if c in df.columns]
        
        if plot_cols:
            fig_line = px.line(df_sorted, x='Timestamp', y=plot_cols, 
                               title="Well-being Metrics Over Time", markers=True)
            st.plotly_chart(fig_line, width="stretch")
    
    # Gratitude Log
    st.subheader("🙏 Gratitude Wall")
    if 'Gratitude' in df.columns:
        gratitude_entries = df[df['Gratitude'].notnull() & (df['Gratitude'] != "")].tail(5)
        for index, row in gratitude_entries.iterrows():
            st.info(f"**{row.get('Name', 'Anonymous')}**: {row['Gratitude']}")
    
    # Recent Notes
    st.subheader("Recent Thoughts")
    if 'Notes' in df.columns:
        recent_notes = df[df['Notes'].notnull() & (df['Notes'] != "")].tail(5)
        for index, row in recent_notes.iterrows():
            st.markdown(f"**{row.get('Name', 'Anonymous')}**: _{row['Notes']}_")

    # Word Cloud & Cognitive Insights
    st.subheader("☁️ Mood & Mind")
    col_cloud, col_game = st.columns(2)
    
    with col_cloud:
        st.markdown("##### 💭 Word Cloud")
        text_data = ""
        # Add factors
        if 'Factors' in df.columns:
            factors_list = df['Factors'].dropna().tolist()
            text_data += " ".join([f.replace(',', ' ') for f in factors_list]) + " "
        
        # Add notes
        if 'Notes' in df.columns:
            notes_list = df['Notes'].dropna().tolist()
            text_data += " ".join(notes_list)
        
        if text_data.strip():
            # Generate word cloud
            wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='Greens').generate(text_data)
            
            # Display using matplotlib
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.info("Not enough text data for Word Cloud yet.")

    with col_game:
        st.markdown("##### 🧠 Cognitive Insights")
        if 'Game Score' in df.columns and df['Game Score'].notnull().any():
            valid_scores = df[df['Game Score'].notnull()] # Include 0s, exclude NaNs
            if not valid_scores.empty:
                avg_focus = valid_scores['Game Score'].mean()
                
                # Gauge-like metric
                st.metric("Avg Focus Score", f"{avg_focus:.1f}/10", delta="Based on Mini-Sudoku")
                
                # Interpretation
                if avg_focus >= 8:
                    st.success("🌟 **High Mental Clarity**: The team is sharp and focused!")
                elif avg_focus >= 5:
                    st.info("⚖️ **Moderate Focus**: Balanced mental energy.")
                else:
                    st.warning("💤 **Low Focus**: Signs of potential mental fatigue.")
                
                # Scatter Plot (Happiness vs Focus)
                if 'Happiness Score' in valid_scores.columns:
                    fig_scatter = px.scatter(valid_scores, x='Happiness Score', y='Game Score',
                                           title="Happiness vs. Focus Correlation",
                                           labels={'Happiness Score': 'Happiness', 'Game Score': 'Focus'},
                                           trendline="ols" if len(valid_scores) > 2 else None)
                    st.plotly_chart(fig_scatter, width="stretch")
            else:
                st.info("No game data recorded yet. Play Mini-Sudoku in the Activity tab!")
        else:
            st.info("No game data recorded yet. Play Mini-Sudoku in the Activity tab!")

if __name__ == "__main__":
    main()
