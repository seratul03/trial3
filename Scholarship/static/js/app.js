const cards = Array.from(document.querySelectorAll(".card"));
const searchInput = document.getElementById("searchInput");
const overlay = document.getElementById("overlay");

let activeCard = null;
let debounceTimer = null;

// Store original order
cards.forEach((card, index) => {
  card.dataset.originalOrder = index;
});

// Expand / close
function openCard(card) {
  if (activeCard) closeCard();
  activeCard = card;
  card.classList.add("expanded");
  overlay.classList.add("active");
  document.body.style.overflow = "hidden";
}

function closeCard() {
  if (!activeCard) return;
  activeCard.classList.remove("expanded");
  overlay.classList.remove("active");
  document.body.style.overflow = "";
  activeCard = null;
}

// Events
cards.forEach((card) => {
  const btn = card.querySelector(".card-button");
  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    openCard(card);
  });
});

overlay.addEventListener("click", closeCard);
document.addEventListener("keydown", (e) => e.key === "Escape" && closeCard());

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
        card.style.order = card.dataset.originalOrder;
        return;
      }

      const isMatch = title.includes(value) || intro.includes(value);

      if (isMatch) {
        card.classList.remove("hidden");
        card.style.order = 0;

        titleEl.innerHTML = highlight(card.dataset.originalTitle, value);
        introEl.innerHTML = highlight(card.dataset.originalIntro, value);
      } else {
        card.classList.add("hidden");
        card.style.order = 1;
      }
    });
  }, 180);
});
