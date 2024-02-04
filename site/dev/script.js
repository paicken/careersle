const website = 'https://careersle.piersaicken.com'
let careerData;
let guesses = 0;
let correctPlayer;
let dateParam = new URLSearchParams(window.location.search).get('date');
let currentDate = dateParam || new Date().toISOString().split('T')[0];

document.addEventListener('DOMContentLoaded', function() {
    fetchData();
    document.getElementById('submitBtn').addEventListener('click', submitGuess);
    document.getElementById('skipBtn').addEventListener('click', skipGuess);
    $('#playerSelect').on('change', function() {
        var selectedValue = $(this).val();
        if (selectedValue === "") {
            $('#submitBtn').prop('disabled', true);
        } else {
            $('#submitBtn').prop('disabled', false);
        }
    });
});

function fetchData() {
    fetch(`${website}/api/${currentDate}.json`)
        .then(response => response.json())
        .then(data => {
            careerData = data;
            populateClubs(data.clubs);
            populateYears();
            populateApps();
            populatePosition();
            populateNationality();
            correctPlayer = data.name;
        });
        fetch('https://careersle.piersaicken.com/api/players.json')
            .then(response => response.json())
            .then(data => {
                $('#playerSelect').select2({
                    data: data.players.map(player => ({ id: player, text: player })),
                    placeholder: "Select a player",
                    allowClear: true,
                    minimumInputLength: 3
                });
            });
            $('#playerSelect').val(null).trigger('change');
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
        updateTableWithCorrectGuess();
        displayModal(true);
    } else {
        guesses++;
        updateTableWithIncorrectGuess(selectedPlayer);
        if (guesses === 5) { // Assuming 4 steps: years, apps/goals, position, nationality
            displayModal(false);
        }
    }
}

function populateYears() {
    let tableBody = document.getElementById('careerTable').getElementsByTagName('tbody')[0];
    let rows = tableBody.rows;
    for (let i = 0; i < rows.length; i++) {
        rows[i].cells[0].innerHTML = `<span class="invisible-element">${careerData.years[i]}</span>`; // Years
    }
}
function populateApps() {
    let tableBody = document.getElementById('careerTable').getElementsByTagName('tbody')[0];
    let rows = tableBody.rows;
    for (let i = 0; i < rows.length; i++) {
        rows[i].cells[2].innerHTML = `<pre class="careersle-code black-text invisible-element">${careerData.appearances_and_goals[i]}</pre>`; // Apps (Goals)
    }
}

function populatePosition() {
    document.getElementById('position').innerText = careerData.position;
}

function populateNationality() {
    document.getElementById('nationality').innerText = careerData.nationality;
}

function skipGuess() {
    $('#playerSelect').val(null).trigger('change');
    submitGuess();
}

function updateTableWithIncorrectGuess(selectedPlayer) {
    let tableBody = document.getElementById('careerTable').getElementsByTagName('tbody')[0];
    let rows = tableBody.rows;
    let selectElement = document.getElementById("playerSelect");
    if (selectedPlayer != "") {
        toast_text = "Sorry, try again"
    }
    else {
        toast_text = "Revealing more details"
    }

    switch (guesses) {
        case 1:
            for (let i = 0; i < rows.length; i++) {
                fadeInElement(rows[i].cells[0].getElementsByClassName('invisible-element')[0])
            }
            $('#playerSelect').val(null).trigger('change');
            showToast(toast_text)
            break;
        case 2:
            for (let i = 0; i < rows.length; i++) {
                fadeInElement(rows[i].cells[2].getElementsByClassName('invisible-element')[0])
            }
            $('#playerSelect').val(null).trigger('change');
            showToast(toast_text)
            break;
        case 3:
            fadeInElement(document.getElementById('position'));
            $('#playerSelect').val(null).trigger('change');
            showToast(toast_text)
            break;
        case 4:
            fadeInElement(document.getElementById('nationality'));
            $('#playerSelect').val(null).trigger('change');
            showToast(toast_text)
            break;
    }
}

function updateTableWithCorrectGuess() {
    let tableBody = document.getElementById('careerTable').getElementsByTagName('tbody')[0];
    let rows = tableBody.rows;
    let selectElement = document.getElementById("playerSelect");

    switch (guesses) {
        case 0:
            allPres = document.getElementsByTagName('pre');
            for (let i = 0; i < allPres.length; i++) {
                markElementGreen(allPres[i]);
            }
            for (let i = 0; i < rows.length; i++) {
                markElementGreen(rows[i].cells[0])
                fadeInElement(rows[i].cells[0].getElementsByClassName('invisible-element')[0])
                fadeInElement(rows[i].cells[2].getElementsByClassName('invisible-element')[0])
            }
            markElementGreen(document.getElementById('position'))
            fadeInElement(document.getElementById('position'));
            markElementGreen(document.getElementById('nationality'))
            fadeInElement(document.getElementById('nationality'));
            $('#playerSelect').val(null).trigger('change');
            break;
        case 1:
            allPres = document.getElementsByTagName('pre');
            for (let i = 0; i < allPres.length; i++) {
                markElementGreen(allPres[i]);
            }
            for (let i = 0; i < rows.length; i++) {
                fadeInElement(rows[i].cells[2].getElementsByClassName('invisible-element')[0])
            }
            markElementGreen(document.getElementById('position'))
            fadeInElement(document.getElementById('position'));
            markElementGreen(document.getElementById('nationality'))
            fadeInElement(document.getElementById('nationality'));
            $('#playerSelect').val(null).trigger('change');
            break;
        case 2:
            markElementGreen(document.getElementById('position'))
            fadeInElement(document.getElementById('position'));
            markElementGreen(document.getElementById('nationality'))
            fadeInElement(document.getElementById('nationality'));
            $('#playerSelect').val(null).trigger('change');
            break;
        case 3:
            markElementGreen(document.getElementById('nationality'))
            fadeInElement(document.getElementById('nationality'));
            $('#playerSelect').val(null).trigger('change');
            break;
    }
}

function displayModal(isCorrect) {
    let modal = document.getElementById('modal');
    modal.innerHTML = "";
    let modalContent = document.createElement('div');
    modalContent.classList.add('modal-content');
    let message, emojiSequence;

    if (isCorrect) {
        message = `Congratulations, you have correctly identified today's player, <b>${correctPlayer}</b>!`;
        emojiSequence = '🟥'.repeat(guesses) + '✅'; // Red for incorrect, green for correct
    } else {
        message = `Hard luck, today's player was <b>${correctPlayer}</b>`;
        emojiSequence = '🟥'.repeat(guesses); // All red for incorrect guesses
    }
    console.log(`guesses: ${guesses}`)

    let chars = ["🏟️", "🗓️", "🎯", "🏃", "🌍"];
    let strtoshare = "";

    for (let i = 0; i < 5; i++) {
        if (i < guesses) {
            strtoshare += "🟥";
        } else if (i == guesses) {
            strtoshare += "✅";
        }
    }

    if (dateParam) {
        dateAppend = `/?date=${currentDate}`
    }
    else {
        dateAppend = ""
    }
    let shareText = `Careersle ${currentDate}:\n${emojiSequence}\n${website}${dateAppend}`;
    
    modalContent.innerHTML = `<p>${message}<br><pre class="careersle-pre">${shareText}</pre></p>`;

    let shareButton = document.createElement('button');
    shareButton.innerText = 'Share';
    shareButton.addEventListener('click', () => {
        navigator.clipboard.writeText(shareText).then(() => {
            showToast("Copied to clipboard");
        });
    });

    let closeButton = document.createElement('button');
    closeButton.innerText = 'Close';
    closeButton.classList.add('modalCloseBtn');
    closeButton.style.margin = '10px';
    closeButton.addEventListener('click', () => {
        modal.style.display ='none';
        modal.innerHTML = '';
    });

    modalContent.appendChild(shareButton);
    modalContent.appendChild(closeButton);
    modal.appendChild(modalContent);
    modal.style.display = 'block';
}

function showHowToPlay() {
    let modal = document.getElementById('modal');
    modal.innerHTML = "";
    let modalContent = document.createElement('div');
    modalContent.classList.add('modal-content');
    howToPlayText = '<h4>How to play Careersle</h4>' +
    '<p>Careersle is a Wordle-inspired game where the aim is to guess the football player based on their career</p>' +
    '<p>Try to identify the player from the clubs they\'ve played for and select' + 
    ' your guess from the player list provided.</p>' +
    '<p>Every incorrect guess reveals more information about the player - when they played for those clubs,' +
    ' how many appearances they made and how many goals they scored (a \'*\' indicates there may be missing data for that period), their general position, then their nationality.</p>' +
    '<p>If you either correctly identify the player or guess incorrectly 5 times, a box will pop up with the ' +
    'answer, your result, and the ability to share the game</p>' +
    '<p>Feedback is welcome, especially on how I can improve the game - ' +
    'just use the link at the bottom of the screen, and I hope you enjoy!</p>'
    
    modalContent.innerHTML = `${howToPlayText}`;

    let closeButton = document.createElement('button');
    closeButton.innerText = 'Close';
    closeButton.classList.add('modalCloseBtn');
    closeButton.addEventListener('click', () => {
        modal.style.display ='none';
        modal.innerHTML = '';
    });

    modalContent.appendChild(closeButton);
    modal.appendChild(modalContent);
    modal.style.display = 'block';
}

function showToast(message) {
    let toast = document.createElement('div');
    toast.innerText = message;
    toast.classList.add('toast-message');
    document.body.appendChild(toast);

    // Trigger reflow to apply initial opacity
    void toast.offsetWidth;

    // Fade in the toast message
    toast.style.opacity = '1';

    // Remove the toast message after a few seconds
    setTimeout(() => {
        toast.style.opacity = '0'; // Fade out
        setTimeout(() => {
            toast.remove(); // Remove after fading out
        },300);
    }, 1000);
}


// Add event listener to close the modal when clicked outside
window.onclick = function(event) {
    let modal = document.getElementById('modal');
    if (event.target == modal) {
        modal.style.display = "none";
        modal.innerHTML = ''; // Clear modal content
    }
}

function fadeInElement(element) {
    element.classList.add('fade-in');
    setTimeout(() => {
        element.style.opacity = 1;
    }, 50); // Adjust timeout as needed
}

function markElementGreen(element) {
    element.classList.remove('black-text');
    element.classList.add('green-text');
}