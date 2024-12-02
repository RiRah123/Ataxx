- **Full name:** Rian Rahman
- **Email:** rian.rahman@gatech.edu
- **GT SSO account name:** rrahman35

---

## Any Build Requirements Outside of Kivy

You need to install numpy for this application because I needed it for the AI model that I used in the Player vs Computer mode.

```bash
pip install numpy
```

## Extra Credit Features

I implemented the following extra credit features:

### AI Avatar with Vocalized Feedback

- Added a Player vs Computer mode which you can access through the settings menu.
- The AI opponent uses a trained **SimpleNet** model to select moves that maximize the positive difference in total pieces between the two teams.
- AI moves are accompanied by vocalized feedback for enhanced interactivity.

### Level Creation Tool

- Developed a level creation tool that allows users to design custom game boards.
- Features include:
  - Clicking on cells to cycle between Player 1, Player 2, and Player 3 pieces.
  - Assigning a title name to the level.
  - Saving the custom level configuration to the local system for future use.

---

## Bugs

### Cloned Circle Artifact

- When performing an adjacent move to clone a piece, followed by a jump, a smaller version of the cloned circle may remain on the canvas.
- This artifact is purely visual and does not affect game functionality, as the small circle is not recognized as a valid game piece.
