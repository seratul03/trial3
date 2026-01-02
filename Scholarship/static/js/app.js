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

// ============================================================================
// SCHOLARSHIP HIGHLIGHTING FROM URL PARAMETER
// ============================================================================

// Check if there's a 'highlight' parameter in the URL
function checkAndHighlightScholarship() {
  const urlParams = new URLSearchParams(window.location.search);
  const highlightSlug = urlParams.get('highlight');
  
  if (highlightSlug) {
    // Find the card with matching slug
    const targetCard = cards.find(card => {
      const cardLink = card.getAttribute('onclick');
      return cardLink && cardLink.includes(`id=${highlightSlug}`);
    });
    
    if (targetCard) {
      // Add highlight animation styles
      targetCard.style.animation = 'highlightPulse 2s ease-in-out';
      targetCard.style.border = '3px solid #2563eb';
      targetCard.style.boxShadow = '0 0 20px rgba(37, 99, 235, 0.4)';
      
      // Scroll to the card after a small delay to ensure page is loaded
      setTimeout(() => {
        targetCard.scrollIntoView({
          behavior: 'smooth',
          block: 'center'
        });
      }, 300);
      
      // Remove highlight after 5 seconds
      setTimeout(() => {
        targetCard.style.animation = '';
        targetCard.style.border = '';
        targetCard.style.boxShadow = '';
      }, 5000);
    }
  }
}

// Add CSS for highlight animation
const style = document.createElement('style');
style.textContent = `
  @keyframes highlightPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
  }
  
  .card.hidden {
    display: none;
  }
`;
document.head.appendChild(style);

// Run highlighting when page loads
window.addEventListener('DOMContentLoaded', checkAndHighlightScholarship);