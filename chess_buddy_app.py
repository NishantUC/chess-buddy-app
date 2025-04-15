# chess_buddy_app.py

import streamlit as st
import requests
import chess.pgn
import io
from collections import Counter

st.set_page_config(page_title="Chess Buddy", layout="centered")
st.title("♟️ Chess Buddy - Analyze Your Game with AI")

username = st.text_input("Enter your Chess.com username", "Nishi26")

if st.button("Analyze My Last 20 Games"):
    try:
        archive_url = f"https://api.chess.com/pub/player/{username.lower()}/games/archives"
        response = requests.get(archive_url)

        # 👇 Enhanced error reporting
        if response.status_code != 200:
            st.error(f"❌ Failed to fetch archives for '{username}'.")
            st.write(f"Status Code: {response.status_code}")
            st.write(f"Response Text: {response.text}")
            st.stop()

        archives = response.json().get("archives", [])
        if not archives:
            st.error(f"⚠️ No archived games found for {username}.")
            st.stop()

        # Try getting games from last available archive
        games = []
        for archive in reversed(archives):
            archive_data = requests.get(archive).json()
            if 'games' in archive_data:
                games.extend(archive_data['games'])
            if len(games) >= 20:
                break

        if not games:
            st.error("😢 No games found to analyze.")
            st.stop()

        games = games[:20]

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

        st.subheader("📚 Opening Performance")
        opening_counts = Counter(openings)
        for op, count in opening_counts.most_common(5):
            st.write(f"• {op}: played {count} times")

        st.subheader("🎯 Results Summary")
        wins = results.count("1-0") if username.lower() in games[0]['white']['username'].lower() else results.count("0-1")
        losses = results.count("0-1") if username.lower() in games[0]['white']['username'].lower() else results.count("1-0")
        draws = results.count("1/2-1/2")
        st.write(f"Wins: {wins}, Losses: {losses}, Draws: {draws}")

        st.subheader("🤖 AI Suggestions")
        st.write("- Try focusing on your best-performing openings.")
        st.write("- Review your losses and look for common blunders.")
        st.write("- Train endgames if you're losing in drawn or won positions.")

    except Exception as e:
        st.exception(f"Something went wrong: {e}")

st.markdown("---")
st.subheader("📝 Or Paste a PGN Manually")
pgn_input = st.text_area("Paste your PGN below and click Analyze")

if st.button("Analyze PGN"):
    try:
        cleaned_pgn = pgn_input.strip()
        if not cleaned_pgn:
            st.warning("⚠️ Please paste a full PGN game.")
            st.stop()

        game_io = io.StringIO(cleaned_pgn)
        pgn_game = chess.pgn.read_game(game_io)

        if pgn_game is None:
            st.error("❌ PGN could not be parsed. Make sure it includes moves and headers.")
            st.code(cleaned_pgn, language="pgn")
        else:
            white = pgn_game.headers.get("White", "?")
            black = pgn_game.headers.get("Black", "?")
            result = pgn_game.headers.get("Result", "?")
            opening = pgn_game.headers.get("Opening", "Unknown")

            st.success("✅ PGN Parsed Successfully!")
            st.write(f"**Players**: {white} vs {black}")
            st.write(f"**Result**: {result}")
            st.write(f"**Opening**: {opening}")

            board = pgn_game.board()
            moves = list(pgn_game.mainline_moves())
            move_preview = ' '.join([board.san(m) for m in moves[:10]])
            st.write(f"**First 10 Moves**: {move_preview}")

    except Exception as e:
        st.exception(f"Error parsing PGN: {e}")
