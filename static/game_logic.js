

function pollForChanges() {
    fetch('/poll-for-updates/')
      .then(response => response.json())
      .then(data => {
        if (data.updated) {
          updateGameBoard(data.gameState);
          pollForChanges();
        }
      });
  }
  
  pollForChanges();
  