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
            document.getElementById('quiz').innerHTML = '<p>Quiz zakończony przedwcześnie!</p>';
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
            document.getElementById('results').innerHTML += `
                <p>${result.polish} - Twoja odpowiedź: ${result.your_answer} - ${
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