const website = 'https://piersaicken.com'
let careerData;
let guesses = 0;
let correctPlayer;
let dateParam = new URLSearchParams(window.location.search).get('date');
let currentDate = dateParam || new Date().toISOString().split('T')[0];

document.addEventListener('DOMContentLoaded', function() {
    fetchData();
    document.getElementById('submitBtn').addEventListener('click', submitGuess);
    // $('.js-example-basic-single').select2();
});

function fetchData() {
    // let dateParam = new URLSearchParams(window.location.search).get('date');
    // let currentDate = dateParam || new Date().toISOString().split('T')[0];

    fetch(`${website}/${currentDate}.json`)
        .then(response => response.json())
        .then(data => {
            careerData = data;
            populateClubs(data.clubs);
            correctPlayer = data.name;
        });

    fetch(`${website}/players.json`)
        .then(response => response.json())
        .then(data => populatePlayerSelect(data.players));
}

function populateClubs(clubs) {
    let tableBody = document.getElementById('careerTable').getElementsByTagName('tbody')[0];
    tableBody.innerHTML = ''; // Clear existing rows
    clubs.forEach(club => {
        let row = tableBody.insertRow();
        row.insertCell().innerText = ''; // Years
        row.insertCell().innerText = club; // Clubs
        row.insertCell().innerText = ''; // Apps (Goals)
    });
}

function populatePlayerSelect(players) {
    let select = document.getElementById('playerSelect');
    select.innerHTML = ''; // Clear existing options
    players.forEach(player => {
        let option = document.createElement('option');
        option.value = player;
        option.text = player;
        select.appendChild(option);
    });
}

function submitGuess() {
    let selectedPlayer = document.getElementById('playerSelect').value;
    console.log(selectedPlayer);
    if (selectedPlayer === correctPlayer) {
        displayModal(true);
    } else {
        guesses++;
        updateTableWithIncorrectGuess();
        if (guesses === 5) { // Assuming 4 steps: years, apps/goals, position, nationality
            displayModal(false);
        }
    }
}

function updateTableWithIncorrectGuess() {
    let tableBody = document.getElementById('careerTable').getElementsByTagName('tbody')[0];
    let rows = tableBody.rows;

    switch (guesses) {
        case 1:
            for (let i = 0; i < rows.length; i++) {
                rows[i].cells[0].innerText = careerData.years[i]; // Years
            }
            break;
        case 2:
            for (let i = 0; i < rows.length; i++) {
                rows[i].cells[2].innerText = careerData.appearances_and_goals[i]; // Apps (Goals)
            }
            break;
        case 3:
            document.getElementById('position').innerText = careerData.position;
            break;
        case 4:
            document.getElementById('nationality').innerText = careerData.nationality;
            break;
    }
}

function displayModal(isCorrect) {
    let modal = document.getElementById('modal');
    let modalContent = document.createElement('div');
    modalContent.classList.add('modal-content');
    let message, emojiSequence;

    if (isCorrect) {
        message = `Congratulations, you have correctly identified today's player, ${correctPlayer}!`;
        emojiSequence = '🟥'.repeat(guesses) + '✅'; // Red for incorrect, green for correct
    } else {
        message = `Hard luck, today's player was ${correctPlayer}`;
        emojiSequence = '🟥'.repeat(guesses); // All red for incorrect guesses
    }
    console.log(`guesses: ${guesses}`)

    let chars = ["🏟️", "🗓️", "🎯", "🏃", "🌍"];
    let strtoshare = "";

    for (let i = 0; i < 5; i++) {
        if (i < guesses) {
            strtoshare += chars[i] + ": 🟥\n";
        } else if (i == guesses) {
            strtoshare += chars[i] + ": ✅\n";
            // break;
        } else {
            strtoshare += chars[i] + ": -\n";
        }
    }

    modalContent.innerHTML = `<p>${message}</p>`;

    // let shareText = `Careersle ${new Date().toISOString().split('T')[0]}: ${emojiSequence} http://careersle.example.com/?date=${new Date().toISOString().split('T')[0]}`;
    let shareText = `Careersle ${currentDate}:\n${strtoshare}${website}/?date=${currentDate}`;
    
    let shareButton = document.createElement('button');
    shareButton.innerText = 'Share';
    shareButton.addEventListener('click', () => navigator.clipboard.writeText(shareText));

    modalContent.appendChild(shareButton);
    modal.appendChild(modalContent);
    modal.style.display = 'block';
}


// Add event listener to close the modal when clicked outside
window.onclick = function(event) {
    let modal = document.getElementById('modal');
    if (event.target == modal) {
        modal.style.display = "none";
        modal.innerHTML = ''; // Clear modal content
    }
}
