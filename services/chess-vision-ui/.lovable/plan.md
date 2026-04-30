
# Chess Game Viewer

## Overview
A dark-themed chess game viewer that accepts PGN, FEN, or chess.com/lichess links and displays the game on an interactive board.

## Pages & Layout
- **Single-page app** with a centered layout: input area on top, board + controls below
- **Dark mode** throughout using dark background with muted accents

## Input Section
- Text input area that auto-detects format (PGN, FEN, or URL)
- "Load Game" button to parse and display
- For chess.com/lichess links: fetch the PGN via their public APIs
- Example games / paste hints for guidance

## Chess Board
- **Modern dark style**: dark gray and charcoal square colors with subtle contrast
- Responsive board that scales to viewport
- Piece rendering using Unicode chess symbols or an SVG piece set
- Highlighted last move squares
- Board flip button to toggle perspective

## Move Navigation (Full Interactive Controls)
- **Arrow buttons**: first, previous, next, last move
- **Keyboard shortcuts**: left/right arrows for prev/next, home/end for first/last
- **Auto-play**: play/pause button with adjustable speed
- **Clickable move list**: sidebar/panel showing algebraic notation; clicking a move jumps to that position
- Current move highlighted in the move list

## Basic Evaluation Bar
- Vertical bar alongside the board showing position evaluation
- White/black gradient indicating advantage
- Evaluation computed using simple material count (piece values)
- Updates as user navigates through moves

## Libraries
- **chess.js** for PGN/FEN parsing, move validation, and game logic
- Built-in PGN parser from chess.js for move extraction

## Technical Notes
- Parse chess.com URLs → use their public game export API endpoint
- Parse lichess URLs → use lichess game export API endpoint
- All processing client-side with chess.js
