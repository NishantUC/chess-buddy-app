import streamlit as st
import chess.pgn
import io

st.set_page_config(page_title="Chess Buddy - PGN Analyzer", layout="centered")
st.title("♟️ Chess Buddy – PGN Game Analyzer")

# === Instructions and UI ===
with st.expander("📖 How to Get Your PGN"):
    st.markdown("""
    PGN (Portable Game Notation) is the format for recording chess games.

    **To get your PGN:**
    - From [Chess.com](https://www.chess.com/games/archive):
      - Open a game → Click the ⚙️ icon → Select **Download → Copy PGN**
    - From [Lichess](https://lichess.org/@/Nishi26/all):
      - Click on a game → Menu → Download PGN

    Paste it below or upload a `.pgn` file.
    """)

st.markdown("---")

# === PGN Upload Section ===
st.subheader("📝 Paste PGN or Upload File")

# Option 1: Paste PGN manually
pgn_input = st.text_area("Paste your PGN here", height=200)

# Option 2: Upload a PGN file
uploaded_file = st.file_uploader("Or upload a .pgn file", type=["pgn"])

# === PGN Analyzer Button ===
if st.button("Analyze PGN"):
    try:
        # Read PGN from input or uploaded file
        if uploaded_file is not None:
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            pgn_game = chess.pgn.read_game(stringio)
        elif pgn_input.strip():
            game_io = io.StringIO(pgn_input.strip())
            pgn_game = chess.pgn.read_game(game_io)
        else:
            st.warning("⚠️ Please either paste a PGN or upload a .pgn file.")
            st.stop()

        if pgn_game is None:
            st.error("❌ Failed to parse PGN. Make sure it includes full move list.")
            st.stop()

        # === Extract Info from PGN ===
        white = pgn_game.headers.get("White", "?")
        black = pgn_game.headers.get("Black", "?")
        result = pgn_game.headers.get("Result", "?")
        opening = pgn_game.headers.get("Opening", "Unknown")

        st.success("✅ PGN Parsed Successfully!")
        st.markdown(f"**Players:** {white} vs {black}")
        st.markdown(f"**Result:** {result}")
        st.markdown(f"**Opening:** {opening}")

        # Show first few moves
        board = pgn_game.board()
        moves = list(pgn_game.mainline_moves())
        move_preview = ' '.join([board.san(m) for m in moves[:10]])
        st.markdown(f"**First 10 Moves:** {move_preview}")

    except Exception as e:
        st.exception(f"Unexpected error during PGN analysis: {e}")
