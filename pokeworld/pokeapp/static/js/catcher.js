const playArea = document.getElementById('play-area');
const scoreEl = document.getElementById('score');
const timeEl = document.getElementById('time');

let score = 0;
let timeLeft = 30;
let gameInterval;

function spawnPokemon() {
    const img = document.createElement('img');
    img.src = imageList[Math.floor(Math.random() * imageList.length)];
    img.classList.add('pokemon');

    const maxLeft = playArea.clientWidth - 70;
    const maxTop = playArea.clientHeight - 70;

    img.style.left = Math.floor(Math.random() * maxLeft) + 'px';
    img.style.top = Math.floor(Math.random() * maxTop) + 'px';

    img.addEventListener('click', () => {
        score++;
        scoreEl.innerText = score;
        img.remove();
    });

    playArea.appendChild(img);

    setTimeout(() => img.remove(), 1000); // remove after 1s
}

function startGame() {
    gameInterval = setInterval(() => {
        if (timeLeft <= 0) {
            clearInterval(gameInterval);
            alert(`Time's up! You caught ${score} Pokémon.`);
        } else {
            spawnPokemon();
            timeLeft--;
            timeEl.innerText = timeLeft;
        }
    }, 1000);
}

window.onload = startGame;
