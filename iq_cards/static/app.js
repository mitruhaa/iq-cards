const state = {
  cards: [],
  index: 0,
  revealed: false,
  correct: 0,
  incorrect: 0,
};

const elements = {
  deckStatus: document.querySelector("#deckStatus"),
  importButton: document.querySelector("#importButton"),
  appendButton: document.querySelector("#appendButton"),
  clearButton: document.querySelector("#clearButton"),
  emptyImportButton: document.querySelector("#emptyImportButton"),
  emptyAppendButton: document.querySelector("#emptyAppendButton"),
  emptyState: document.querySelector("#emptyState"),
  studyView: document.querySelector("#studyView"),
  summaryView: document.querySelector("#summaryView"),
  progressText: document.querySelector("#progressText"),
  scoreText: document.querySelector("#scoreText"),
  flashcard: document.querySelector("#flashcard"),
  questionText: document.querySelector("#questionText"),
  answerText: document.querySelector("#answerText"),
  imageGallery: document.querySelector("#imageGallery"),
  revealButton: document.querySelector("#revealButton"),
  correctButton: document.querySelector("#correctButton"),
  incorrectButton: document.querySelector("#incorrectButton"),
  summaryCorrect: document.querySelector("#summaryCorrect"),
  summaryTotal: document.querySelector("#summaryTotal"),
  summaryPercent: document.querySelector("#summaryPercent"),
  reviewButton: document.querySelector("#reviewButton"),
  toast: document.querySelector("#toast"),
};

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Request failed.");
  }
  return payload;
}

async function loadCards(resetSession = true) {
  try {
    const payload = await api("/api/cards");
    state.cards = payload.cards;
    if (resetSession) {
      resetProgress();
    }
    render();
  } catch (error) {
    showToast(error.message, true);
  }
}

function resetProgress() {
  state.index = 0;
  state.revealed = false;
  state.correct = 0;
  state.incorrect = 0;
}

function render() {
  const hasCards = state.cards.length > 0;
  elements.clearButton.hidden = !hasCards;
  elements.emptyState.hidden = hasCards;
  elements.studyView.hidden = !hasCards || state.index >= state.cards.length;
  elements.summaryView.hidden = !hasCards || state.index < state.cards.length;
  elements.deckStatus.textContent = hasCards
    ? `${state.cards.length} cards in deck`
    : "No cards in deck";

  if (!hasCards) {
    return;
  }
  if (state.index >= state.cards.length) {
    renderSummary();
    return;
  }
  renderCard();
}

function renderCard() {
  const card = state.cards[state.index];
  elements.progressText.textContent = `Card ${state.index + 1} of ${state.cards.length}`;
  elements.scoreText.textContent = `${state.correct} correct / ${state.incorrect} incorrect`;
  elements.questionText.textContent = card.question;
  elements.answerText.textContent = card.answer.text || "";
  elements.answerText.hidden = !card.answer.text;
  elements.imageGallery.replaceChildren(
    ...card.answer.images.map((image) => {
      const img = document.createElement("img");
      img.src = image.url;
      img.alt = image.filename.replace(/^[a-f0-9]{12}-/, "").replace(/[-_]/g, " ");
      return img;
    })
  );

  elements.flashcard.classList.toggle("is-flipped", state.revealed);
  elements.revealButton.hidden = state.revealed;
  elements.correctButton.hidden = !state.revealed;
  elements.incorrectButton.hidden = !state.revealed;
}

function renderSummary() {
  const total = state.cards.length;
  const percent = total === 0 ? 0 : Math.round((state.correct / total) * 100);
  elements.summaryCorrect.textContent = state.correct;
  elements.summaryTotal.textContent = total;
  elements.summaryPercent.textContent = `${percent}%`;
  elements.deckStatus.textContent = `${state.correct} of ${total} correct`;
}

async function importDeck(mode) {
  setBusy(true);
  showToast(
    mode === "replace"
      ? "Importing cards from import/cards.json..."
      : "Adding cards from import/cards.json..."
  );
  try {
    const result = await api("/api/import", {
      method: "POST",
      body: JSON.stringify({ mode }),
    });
    const verb = mode === "replace" ? "Imported" : "Added";
    showToast(`${verb} ${result.imported} cards.`);
    await loadCards(true);
    elements.deckStatus.textContent = `${verb} ${result.imported} cards · ${result.total} cards in deck`;
  } catch (error) {
    showToast(error.message, true);
  } finally {
    setBusy(false);
  }
}

async function clearDeck() {
  if (!window.confirm("Clear all cards?")) {
    return;
  }
  setBusy(true);
  try {
    await api("/api/clear", { method: "POST", body: "{}" });
    showToast("Cards cleared.");
    await loadCards(true);
  } catch (error) {
    showToast(error.message, true);
  } finally {
    setBusy(false);
  }
}

function revealAnswer() {
  state.revealed = true;
  renderCard();
}

function markAnswer(wasCorrect) {
  if (wasCorrect) {
    state.correct += 1;
  } else {
    state.incorrect += 1;
  }
  state.index += 1;
  state.revealed = false;
  elements.flashcard.classList.remove("is-flipped");
  render();
}

function reviewAgain() {
  resetProgress();
  render();
}

function setBusy(isBusy) {
  [
    elements.importButton,
    elements.appendButton,
    elements.clearButton,
    elements.emptyImportButton,
    elements.emptyAppendButton,
  ].forEach((button) => {
    button.disabled = isBusy;
  });
  setButtonLabel(elements.importButton, isBusy ? "Importing..." : "Import cards");
  setButtonLabel(elements.emptyImportButton, isBusy ? "Importing..." : "Import cards");
  setButtonLabel(elements.appendButton, isBusy ? "Adding..." : "Add cards");
  setButtonLabel(elements.emptyAppendButton, isBusy ? "Adding..." : "Add cards");
}

function setButtonLabel(button, label) {
  const labelElement = button.querySelector("span");
  if (labelElement) {
    labelElement.textContent = label;
  }
}

let toastTimer = null;

function showToast(message, isError = false) {
  window.clearTimeout(toastTimer);
  elements.toast.textContent = message;
  elements.toast.classList.toggle("is-error", isError);
  elements.toast.hidden = false;
  toastTimer = window.setTimeout(() => {
    elements.toast.hidden = true;
  }, 3600);
}

elements.importButton.addEventListener("click", () => importDeck("replace"));
elements.appendButton.addEventListener("click", () => importDeck("append"));
elements.emptyImportButton.addEventListener("click", () => importDeck("replace"));
elements.emptyAppendButton.addEventListener("click", () => importDeck("append"));
elements.clearButton.addEventListener("click", clearDeck);
elements.revealButton.addEventListener("click", revealAnswer);
elements.correctButton.addEventListener("click", () => markAnswer(true));
elements.incorrectButton.addEventListener("click", () => markAnswer(false));
elements.reviewButton.addEventListener("click", reviewAgain);

elements.flashcard.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    if (!state.revealed) {
      revealAnswer();
    }
  }
});

loadCards();
