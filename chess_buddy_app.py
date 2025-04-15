# chess_buddy_app.py

import streamlit as st
import requests
import chess.pgn
import io
from collections import Counter

st.title("♟️ Chess Buddy - AI Insights from Your Games")

# Input: Chess.com username
username = st.text_input("Enter your Chess.com username", "Nishi26")

if st.button("Analyze My Last 20 Games"):
    try:
        # Fetch last games archive
        archives = requests.get(f"https://api.chess.com/pub/player/{username}/games/archives").json()
        latest_url = archives['archives'][-1]

        # Fetch games from the latest month
        games = requests.get(latest_url).json()['games']
        games = games[:20]  # Get only the last 20 games

        openings = []
        results = []

        for game in games:
            pgn = game.get('pgn', '')
            if not pgn:
                continue
            game_io = io.StringIO(pgn)
            pgn_game = chess.pgn.read_game(game_io)

            opening = pgn_game.headers.get("Opening", "Unknown")
            result = pgn_game.headers.get("Result", "*")

            openings.append(opening)
            results.append(result)

        # Summary statistics
        st.subheader("📚 Opening Performance")
        opening_counts = Counter(openings)
        for op, count in opening_counts.most_common(5):
            st.write(f"{op}: played {count} times")

        st.subheader("🎯 Results Summary")
        wins = results.count("1-0") if username.lower() in games[0]['white']['username'].lower() else results.count("0-1")
        losses = results.count("0-1") if username.lower() in games[0]['white']['username'].lower() else results.count("1-0")
        draws = results.count("1/2-1/2")
        st.write(f"Wins: {wins}, Losses: {losses}, Draws: {draws}")

        # Optional AI suggestions (placeholder for now)
        st.subheader("🤖 AI Suggestions")
        st.write("- Try focusing on your top-performing opening to build confidence.")
        st.write("- You may want to analyze your losses to spot tactical blunders.")
        st.write("- Consider training endgames if many losses happen in the final phase.")

    except Exception as e:
        st.error(f"Something went wrong: {e}")

st.markdown("---")
st.subheader("📝 Or Paste a PGN Manually")
pgn_input = st.text_area("Paste PGN here")

if st.button("Analyze PGN"):
    try:
        game_io = io.StringIO(pgn_input)
        pgn_game = chess.pgn.read_game(game_io)
        opening = pgn_game.headers.get("Opening", "Unknown")
        result = pgn_game.headers.get("Result", "*")

        st.write(f"Opening: {opening}")
        st.write(f"Result: {result}")
    except Exception as e:
        st.error(f"Could not parse PGN: {e}")
