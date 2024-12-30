import streamlit as st
import asyncio
import websockets
import json

# URL of the backend WebSocket server
BACKEND_URL = "wss://game-hyfq.onrender.com/ws"

# State management
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "passcode" not in st.session_state:
    st.session_state.passcode = ""
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = {}

# WebSocket communication
async def send_message(action, data=None):
    async with websockets.connect(BACKEND_URL) as websocket:
        message = {"action": action}
        if data:
            message.update(data)
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
        return json.loads(response)

def connect_to_game():
    st.session_state.player_name = st.text_input("Enter your name:", key="name_input")
    st.session_state.passcode = st.text_input("Enter passcode (create or join):", key="passcode_input")
    if st.button("Create Game"):
        asyncio.run(send_message("create_game", {"passcode": st.session_state.passcode}))
        st.success(f"Game created with passcode: {st.session_state.passcode}")
        st.session_state.game_started = True
    elif st.button("Join Game"):
        result = asyncio.run(send_message("join_game", {
            "player_name": st.session_state.player_name,
            "passcode": st.session_state.passcode
        }))
        if result.get("status") == "success":
            st.success("Joined game successfully!")
            st.session_state.game_started = True
        else:
            st.error("Invalid passcode or error joining game.")

def play_game():
    st.title(f"Welcome, {st.session_state.player_name}!")
    st.subheader("Game has started!")
    word_display = st.empty()
    input_box = st.text_input("Guess the word:", key="guess_input")
    if st.button("Submit Guess"):
        result = asyncio.run(send_message("guess_word", {
            "player_name": st.session_state.player_name,
            "guess": input_box
        }))
        if result.get("correct"):
            st.success("Correct guess!")
        else:
            st.error("Wrong guess!")
    leaderboard_btn = st.button("View Leaderboard")
    if leaderboard_btn:
        leaderboard = asyncio.run(send_message("leaderboard"))
        st.session_state.leaderboard = leaderboard
    if st.session_state.leaderboard:
        st.write("Leaderboard:")
        for player, score in st.session_state.leaderboard.items():
            st.write(f"{player}: {score} points")

# Main UI
st.title("Guess the Word Game")
if not st.session_state.game_started:
    connect_to_game()
else:
    play_game()
