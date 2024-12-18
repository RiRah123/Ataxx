# Ataxx Strategy Game  
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)  
[![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)  

## Project Summary  
Ataxx is a turn-based strategy game where two players compete to dominate a 7x7 grid board. Players can clone or jump their pieces to convert opponents’ pieces into their own. The player with the most pieces at the end of the game wins. This implementation introduces **Player vs Player** and **Player vs AI** modes, enhanced with animations, sound effects, and a custom **Level Editor**.

<p align="center">
  <img src="public/images/ataxx-main.png" height="350" width="700" alt="Ataxx Game">
</p>  

<br/>
<p align="center">
  <img src="public/images/ataxx-level-creator.png" height="350" width="350" alt="Level Creator">
  <img src="public/images/ataxx-ai.png" height="350" width="350" alt="AI Avatar Feedback">
</p>  

## Problem: What problem does this project address?  
Ataxx, despite its rich strategy gameplay, lacks modern features like customizable levels, smooth animations, and AI opponents. This project revitalizes the game with additional functionalities for a more engaging and interactive experience.

## Solution: How does this project solve the problem?  
This implementation includes:  
1. **Interactive Gameplay**: Supports Player vs Player and Player vs AI modes with seamless UI and Kivy-powered animations.  
2. **AI Opponent**: Features a SimpleNet-based AI strategy for competitive gameplay, complete with vocalized AI feedback.  
3. **Custom Level Creation**: A user-friendly **Level Editor** lets players design their own game boards, defining starting positions and obstacles.  
4. **Sound Effects**: Adds immersive sound for player moves, jumps, cloning, and game events.  
5. **Time-Limited Play**: Enables countdown timers to create high-stakes scenarios.

## Features  
- **Game Modes**: Player vs Player and Player vs AI.  
- **Custom Levels**: Create and save new levels using the **Level Editor**.  
- **AI Opponent**: Implements optimal AI moves and expressive feedback animations.  
- **Smooth Animations**: Movement, capturing, and cloning animations powered by Kivy’s `Animation` class.  
- **Sound Effects**: Distinct audio for key game actions and events.  
- **Timers**: Optional timed mode with a countdown per player.  

## Build Requirements  
To run the Ataxx Strategy Game, you need the following:

### Install Dependencies  
Install **Python**, **Kivy**/**NumPy** using pip and then run the app using python:  

```bash
pip install kivy numpy
python main.py
```
