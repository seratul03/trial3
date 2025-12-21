const cards = Array.from(document.querySelectorAll(".card"));
const searchInput = document.getElementById("searchInput");

let debounceTimer = null;

// Highlight helper
function highlight(text, term) {
  if (!term) return text;
  const regex = new RegExp(`(${term})`, "gi");
  return text.replace(regex, "<mark>$1</mark>");
}

// Search with debounce
searchInput.addEventListener("input", () => {
  clearTimeout(debounceTimer);

  debounceTimer = setTimeout(() => {
    const value = searchInput.value.trim().toLowerCase();

    cards.forEach((card) => {
      const title = card.dataset.title;
      const intro = card.dataset.intro;
      const titleEl = card.querySelector(".text-title");
      const introEl = card.querySelector(".card-intro");

      // Reset text
      titleEl.innerHTML = card.dataset.originalTitle;
      introEl.innerHTML = card.dataset.originalIntro;

      if (!value) {
        card.classList.remove("hidden");
        return;
      }

      const isMatch = title.includes(value) || intro.includes(value);

      if (isMatch) {
        card.classList.remove("hidden");
        titleEl.innerHTML = highlight(card.dataset.originalTitle, value);
        introEl.innerHTML = highlight(card.dataset.originalIntro, value);
      } else {
        card.classList.add("hidden");
      }
    });
  }, 180);
});