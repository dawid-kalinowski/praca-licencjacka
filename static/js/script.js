let words = [];
let currentIndex = 0;
let quizActive = false;

async function startQuiz() {
  const response = await fetch('/get_words');
  words = await response.json();
  currentIndex = 0;
  quizActive = true;
  document.getElementById('results').innerHTML = '';
  document.getElementById('end-btn').style.display = 'inline';
  showNextWord();
}

function endQuiz() {
  quizActive = false;
  document.getElementById('quiz').innerHTML = '<p>Quiz zakończony!</p>';
  document.getElementById('end-btn').style.display = 'none';
}

async function checkAnswer() {
  if (!quizActive) return;

  const userAnswer = document.getElementById('answer').value;
  const currentWord = words[currentIndex];

  const response = await fetch('/check_word', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({answer: userAnswer, word: currentWord})
  });

  const result = await response.json();
  const resultClass = result.correct ? 'correct' : 'incorrect';
  document.getElementById('results').innerHTML += `
    <p class="${resultClass}">${result.polish} - Twoja odpowiedź: ${result.your_answer} - ${
    result.correct ? '✔️ Poprawnie' : `❌ Niepoprawnie, poprawna odpowiedź: ${result.correct_answer}`
  }</p>`;

  currentIndex++;
  if (currentIndex < words.length) {
    showNextWord();
  } else {
    endQuiz();
  }
}

function showNextWord() {
  if (!quizActive) return;

  document.getElementById('quiz').innerHTML = `
    <p>${words[currentIndex].polish}</p>
    <input type="text" id="answer" placeholder="Tłumaczenie...">
    <button onclick="checkAnswer()">Sprawdź</button>
  `;
}

async function detectLanguage() {
  const text = document.getElementById("textInput").value;
  const resultElement = document.getElementById("result");
  const errorElement = document.getElementById("error");

  resultElement.textContent = '';
  errorElement.textContent = '';

  if (!text.trim()) {
    errorElement.textContent = "Wprowadź tekst.";
    return;
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/detect-language', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    const data = await response.json();
    if (response.ok) {
      resultElement.textContent = `Wykryty język: ${data.language}`;
    } else {
      errorElement.textContent = data.error || "Wystąpił błąd.";
    }
  } catch (err) {
    errorElement.textContent = "Wystąpił błąd podczas połączenia z serwerem.";
  }
}

function showResult(element, message) {
  const card = document.querySelector(element);
  card.classList.add('show');
  if(element === '#result') {
      document.querySelector('.result-text').textContent = message;
  } else {
      document.querySelector('.error-text').textContent = message;
  }
}

function resetResults() {
  document.querySelectorAll('.result-card').forEach(card => {
      card.classList.remove('show');
  });
}