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
      const response = await fetch('http://127.0.0.1:5001/detect-language', {
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