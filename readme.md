- **Full name:** Rian Rahman
- **Email:** rian.rahman@gatech.edu
- **GT SSO account name:** rrahman35

---

## Any Build Requirements Outside of Kivy

You need to install numpy for this application because I needed it for the AI model that I used in the Player vs Computer mode.

```bash
pip install numpy
```

## Bugs

### With Moving Cloning and Then Jumping

- There is a visual bug in my program that I couldn't fix where performing an adjacent move to clone a piece and then following it by a jum, a smaller version of the original cloned circle remains on the canvas. I could not figure on why this drawn on the canvas because for normal jumps (where who do not jump from cloned circle it works properly).
- Although this smaller cloned circle appears, it is only a visual that does not affect of the game functionality. The small circle is not recognized as a valid game piece and tranversable move during the game.

## Extra Credit Features

I implemented the following extra credit features:

### AI Avatar with Vocalized Feedback

- Added a Player vs Computer mode which you can access through the settings menu.
- I used a **SimpleNet** model help select moves that maximize the positive difference in total pieces between the two teams.
  -I added vocalized feedback where the Computer responds with happy or sad voice message.

### Level Creation Tool

- Developed a level creation tool that accessible with a button on the front page where users can create their own levels
- This feature involves:
  - Clicking on cells to cycle between Player 1, Player 2, and Untraversable Cells.
  - Assigning a title name to the level.
  - Saving the custom level configuration onto the levels.txt

---
