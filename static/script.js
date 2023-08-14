document.querySelector('form').addEventListener('submit', rollDice);

function rollDice(event) {
    event.preventDefault(); // Prevent form submission
    
    const diceElement = document.getElementById('dice');
    const resultElement = document.getElementById('resultMessage');
    const chosenNumber = parseInt(document.querySelector('[name="chosen_number"]').value);
    const betAmount = parseInt(document.querySelector('[name="bet_amount"]').value);
    
    if (betAmount <= 0) {
        showResultMessage('Bet amount must be positive.', 'error');
        return;
    }
    
    diceElement.classList.add('rolling');
    document.querySelector('[type="submit"]').disabled = true;
    
    setTimeout(() => {
        diceElement.classList.remove('rolling');
        const rolledNumber = Math.floor(Math.random() * 6) + 1;
        
        const resultMessage = rolledNumber === chosenNumber ? 'You won!' : 'You lost!';
        const resultClass = rolledNumber === chosenNumber ? 'won' : 'lost';
        showResultMessage(resultMessage, resultClass);
        
        document.querySelector('[type="submit"]').disabled = false;
    }, 2000);
}

function showResultMessage(message, resultClass) {
    const resultElement = document.getElementById('resultMessage');
    resultElement.textContent = message;
    resultElement.className = `game-result ${resultClass}`;
}
