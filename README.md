# SmartChess
Senior Capstone Smart Chessboard Project.
This project is a physical chess board that detects when pieces are picked up and shows the user all possible moves for any given piece in the current state of the board.
It utilizes 64 hall-effect sensors that are multiplexed into the Raspberry Pi with 8 multiplexors, so there are 8 hall-effect sensors per multiplexor, 3 GPIO pins are used as slect lines, and each multiplexor has its output connected to a GPIO pin.

This repo contains code utilized on Raspberry Pi for Senior Capstone. This code serves many purposes, including:
1) initializing and tracking the state of the board
3) Cycle through all 8 combinations from 3 select lines to record the current outputs of all 64 signals
4) Compare current values to previous values to detect when a player picks up the piece
5) Translating serial binary data from the 64 sensors into a usable format
6) Determining the possible moves for a given piece given the state of the board
7) Handling essential game logic
8) Mapping 8x8 grid of possible moves to serial LED positions for display
9) Detecting when an opposing piece has been captured

Further descriptions of the methodology, system design, hardware, and software can be found in the SmartChessboardReport.pdf
