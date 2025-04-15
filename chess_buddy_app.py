import streamlit as st
import chess.pgn
import io

st.set_page_config(page_title="Chess Buddy - PGN Analyzer", layout="centered")
st.title("♟️ Chess Buddy – PGN Game Analyzer")

# === ECO Opening Map ===
ECO_OPENINGS = {
    "e4 d5": ("B01", "Scandinavian Defense"),
    "e4 c5": ("B20", "Sicilian Defense"),
    "e4 e5 Nf3 Nc6 Bb5": ("C65", "Ruy Lopez"),
    "d4 d5 c4": ("D06", "Queen's Gambit"),
    "d4 Nf6 c4 g6": ("E60", "King's Indian Defense"),
    "e4 e5 Nf3 Nc6 Bc4 Bc5": ("C50", "Italian Game"),
    "e4 e5 Nf3 Nc6 d4": ("C21", "Center Game"),
    "e4 e5 Nf3 Nc6 f4": ("C30", "King's Gambit"),
    "d4 d5 Nf3 Nf6": ("D02", "Queen's Pawn Game"),
}

def detect_eco_opening(san_moves):
    move_seq = ' '.join(san_moves)
    for pattern, (eco, name) in ECO_OPENINGS.items():
        if move_seq.startswith(pattern):
            return eco, name
    return None, None

# === Simple Tactical Check ===
def detect_tactical_events(game):
    board = game.board()
    events = []
    move_number = 1
    turn = "White"
    prev_piece_map = board.piece_map()

    for move in game.mainline_moves():
        san = board.san(move)
        board.push(move)
        piece_map = board.piece_map()

        # Check for hanging pieces (own pieces attacked and undefended)
        for square, piece in piece_map.items():
            attackers = board.attackers(not piece.color, square)
            defenders = board.attackers(piece.color, square)
            if attackers and not defenders:
                events.append(f"❌ Move {move_number} ({turn}): {piece.symbol()} on {chess.square_name(square)} is hanging.")

        # Check for missed capture (opponent had piece hanging last move)
        for square, piece in prev_piece_map.items():
            if square not in piece_map:
                # piece was captured or moved
                continue
            attackers = board.attackers(not piece.color, square)
            if attackers and not board.is_attacked_by(piece.color, square):
                events.append(f"⚠️ Missed capture: {piece.symbol()} on {chess.square_name(square)} was hanging on last move.")

        prev_piece_map = board.piece_map()
        move_number += 0.5
        turn = "Black" if turn == "White" else "White"

    return events

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
pgn_input = st.text_area("Paste your PGN here", height=200)
uploaded_file = st.file_uploader("Or upload a .pgn file", type=["pgn"])

if st.button("Analyze PGN"):
    try:
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

        white = pgn_game.headers.get("White", "?")
        black = pgn_game.headers.get("Black", "?")
        result = pgn_game.headers.get("Result", "?")
        opening_from_header = pgn_game.headers.get("Opening", None)

        st.success("✅ PGN Parsed Successfully!")
        st.markdown(f"**Players:** {white} vs {black}")
        st.markdown(f"**Result:** {result}")

        board = pgn_game.board()
        moves = list(pgn_game.mainline_moves())
        san_moves = []
        preview_moves = []

        for i, move in enumerate(moves[:10]):
            try:
                san_move = board.san(move)
                san_moves.append(san_move)
                preview_moves.append(san_move)
                board.push(move)
            except Exception:
                preview_moves.append(f"[Invalid move {i+1}]")
                break

        eco_code, opening_name = detect_eco_opening(san_moves[:6])
        if opening_from_header:
            st.markdown(f"**Opening:** {opening_from_header}")
        elif eco_code:
            st.markdown(f"**Opening:** {opening_name} ({eco_code})")
        else:
            st.markdown("**Opening:** Unknown")

        st.markdown(f"**First 10 Moves:** {' '.join(preview_moves)}")

        # === New: Tactical Event Detector ===
        st.markdown("---")
        st.subheader("🚨 Tactical Blunders & Misses")
        events = detect_tactical_events(pgn_game)
        if events:
            for e in events:
                st.write(e)
        else:
            st.info("No obvious tactical blunders or missed opportunities found.")

    except Exception as e:
        st.exception(f"Unexpected error during PGN analysis: {e}")

# === Comparison Block ===
st.markdown("---")
with st.expander("🤔 How is Chess Buddy different from Chess.com engine analysis?"):
    st.markdown("""
| Feature                         | Chess.com Engine Analysis              | Chess Buddy 🚀 |
|----------------------------------|----------------------------------------|----------------|
| **Goal**                        | Tell you the best move                 | Help you improve over time |
| **Focus**                       | One game at a time                     | Patterns across many games |
| **Feedback Style**              | “Blunder! Play this.”                  | “You often miss forks in this opening.” |
| **Opening Advice**              | Basic labels (Sicilian, etc.)          | Win rates, ECO codes, & training suggestions |
| **Personalization**             | Minimal                                | Tracks your style & weaknesses |
| **Data Source**                 | Games only from your Chess.com account | Any PGN file (Chess.com, Lichess, OTB, etc.) |
| **Training Suggestions**        | None                                   | Recommends tactics, videos, or courses |
| **Explainability**             | Engine evals (“+1.5”)                  | Plain English insights |
| **Extensibility**              | Locked to Chess.com                    | Modular & open for features like coach chat |

💡 **In short:**  
*Chess.com tells you what happened.  
Chess Buddy helps you fix it for next time.* 🎯
    """, unsafe_allow_html=True)
