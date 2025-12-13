// Fetch notices, render them, and apply filtering (search, month, year, sorting, category)
// Category dropdown is now inside the filter panel

let ALL_NOTICES = [];

document.addEventListener("DOMContentLoaded", async () => {
  const filterBtn = document.getElementById("filterBtn");
  const panel = document.getElementById("filterPanel");
  const clearBtn = document.getElementById("clearFilters");
  const applyBtn = document.getElementById("applyFilters");

  const searchInput = document.getElementById("search");
  const monthInput = document.getElementById("dateMonth");
  const yearInput = document.getElementById("dateYear");
  const categorySelect = document.getElementById("categorySelect");

  // 1) Load PDFs from Flask API
  try {
    ALL_NOTICES = await fetch("/api/notices").then((res) => res.json());
  } catch (e) {
    console.error("Failed to fetch notices:", e);
    ALL_NOTICES = [];
  }

  // 2) Populate category select based on data
  populateCategorySelect(ALL_NOTICES, categorySelect);

  // 3) Render initially (no demo data)
  renderNotices(ALL_NOTICES);

  /*--------------------------
      FILTER PANEL BEHAVIOR
  ---------------------------*/

  filterBtn.addEventListener("click", () => {
    panel.classList.toggle("hidden");
  });

  clearBtn.addEventListener("click", () => {
    monthInput.value = "";
    yearInput.value = "";
    searchInput.value = "";
    categorySelect.value = "";
    renderNotices(ALL_NOTICES);
    panel.classList.add("hidden");
  });

  applyBtn.addEventListener("click", () => {
    applyFilters();
    panel.classList.add("hidden");
  });

  // Search while typing
  searchInput.addEventListener("input", applyFilters);

  // Category change
  categorySelect.addEventListener("change", applyFilters);

  // Quick Filters (sort options)
  document.querySelectorAll(".quick").forEach((btn) => {
    btn.addEventListener("click", () => {
      const type = btn.dataset.filter;
      applyFilters(type);
      panel.classList.add("hidden");
    });
  });
});

/*--------------------------
      POPULATE CATEGORY SELECT
---------------------------*/
function populateCategorySelect(notices, selectEl) {
  const cats = new Set();
  notices.forEach((n) => {
    if (n.category) cats.add(n.category);
  });
  // clear existing options except first
  while (selectEl.options.length > 1) selectEl.remove(1);
  Array.from(cats)
    .sort()
    .forEach((cat) => {
      const opt = document.createElement("option");
      opt.value = cat;
      opt.textContent = cat;
      selectEl.appendChild(opt);
    });
}

/*--------------------------
      APPLY FILTERS
---------------------------*/
function applyFilters(sortType = null) {
  let filtered = [...ALL_NOTICES];

  const search = document.getElementById("search").value.toLowerCase();
  const monthVal = document.getElementById("dateMonth").value; // YYYY-MM
  const yearVal = document.getElementById("dateYear").value; // YYYY
  const categoryVal = document.getElementById("categorySelect").value;

  // Category filter
  if (categoryVal) {
    filtered = filtered.filter(
      (n) => (n.category || "").toLowerCase() === categoryVal.toLowerCase()
    );
  }

  // Search filter
  if (search.trim() !== "") {
    filtered = filtered.filter(
      (n) =>
        (n.title || "").toLowerCase().includes(search) ||
        (n.category || "").toLowerCase().includes(search)
    );
  }

  // Month filter
  if (monthVal) {
    const [y, m] = monthVal.split("-");
    filtered = filtered.filter(
      (n) =>
        (n.date || "").slice(0, 4) === y && (n.date || "").slice(5, 7) === m
    );
  }

  // Year filter
  if (yearVal) {
    filtered = filtered.filter((n) => (n.date || "").slice(0, 4) === yearVal);
  }

  /*--------------------------
         SORTING
  ---------------------------*/

  if (sortType === "new" || sortType === "new-old") {
    filtered.sort((a, b) => new Date(b.date) - new Date(a.date));
  } else if (sortType === "old-new") {
    filtered.sort((a, b) => new Date(a.date) - new Date(b.date));
  } else if (sortType === "7days") {
    const now = new Date();
    filtered = filtered.filter((n) => {
      const d = new Date(n.date);
      return (now - d) / (1000 * 60 * 60 * 24) <= 7;
    });
  } else {
    // default: newest first
    filtered.sort((a, b) => new Date(b.date) - new Date(a.date));
  }

  renderNotices(filtered);
}

/*--------------------------
      RENDER NOTICE CARDS
---------------------------*/
function renderNotices(list) {
  const container = document.getElementById("noticesList");
  container.innerHTML = "";

  if (!list || list.length === 0) {
    container.innerHTML = `
      <div style="text-align:center;opacity:0.6;padding:20px;font-size:18px;">
        No notices found
      </div>
    `;
    return;
  }

  list.forEach((n) => {
    const div = document.createElement("div");
    div.className = "notice-card";

    // Create body preview for announcements
    let bodyPreview = "";
    if (n.type === "announcement" && n.body) {
      const preview = n.body.substring(0, 120);
      bodyPreview = `<p style="color:#555;font-size:14px;margin-top:8px;line-height:1.5;">${escapeHtml(
        preview
      )}${n.body.length > 120 ? "..." : ""}</p>`;
    }

    // Create document button
    let docButton = "";
    if (n.type === "pdf") {
      docButton = `
        <button class="doc-btn" onclick="event.stopPropagation(); window.open('/pdfs/' + encodeURIComponent('${n.filename}'), '_blank')">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5v2z"/>
            <path d="M4.603 14.087a.81.81 0 0 1-.438-.42c-.195-.388-.13-.776.08-1.102.198-.307.526-.568.897-.787a7.68 7.68 0 0 1 1.482-.645 19.697 19.697 0 0 0 1.062-2.227 7.269 7.269 0 0 1-.43-1.295c-.086-.4-.119-.796-.046-1.136.075-.354.274-.672.65-.823.192-.077.4-.12.602-.077a.7.7 0 0 1 .477.365c.088.164.12.356.127.538.007.188-.012.396-.047.614-.084.51-.27 1.134-.52 1.794a10.954 10.954 0 0 0 .98 1.686 5.753 5.753 0 0 1 1.334.05c.364.066.734.195.96.465.12.144.193.32.2.518.007.192-.047.382-.138.563a1.04 1.04 0 0 1-.354.416.856.856 0 0 1-.51.138c-.331-.014-.654-.196-.933-.417a5.712 5.712 0 0 1-.911-.95 11.651 11.651 0 0 0-1.997.406 11.307 11.307 0 0 1-1.02 1.51c-.292.35-.609.656-.927.787a.793.793 0 0 1-.58.029zm1.379-1.901c-.166.076-.32.156-.459.238-.328.194-.541.383-.647.547-.094.145-.096.25-.04.361.01.022.02.036.026.044a.266.266 0 0 0 .035-.012c.137-.056.355-.235.635-.572a8.18 8.18 0 0 0 .45-.606zm1.64-1.33a12.71 12.71 0 0 1 1.01-.193 11.744 11.744 0 0 1-.51-.858 20.801 20.801 0 0 1-.5 1.05zm2.446.45c.15.163.296.3.435.41.24.19.407.253.498.256a.107.107 0 0 0 .07-.015.307.307 0 0 0 .094-.125.436.436 0 0 0 .059-.2.095.095 0 0 0-.026-.063c-.052-.062-.2-.152-.518-.209a3.876 3.876 0 0 0-.612-.053zM8.078 7.8a6.7 6.7 0 0 0 .2-.828c.031-.188.043-.343.038-.465a.613.613 0 0 0-.032-.198.517.517 0 0 0-.145.04c-.087.035-.158.106-.196.283-.04.192-.03.469.046.822.024.111.054.227.09.346z"/>
          </svg>
          Open PDF
        </button>
      `;
    } else if (
      n.type === "announcement" &&
      n.attachments &&
      n.attachments.length > 0
    ) {
      docButton = `
        <button class="doc-btn" onclick="event.stopPropagation(); showAnnouncementModal(${list.indexOf(
          n
        )})">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M6.002 5.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/>
            <path d="M1.5 2A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-13zm13 1a.5.5 0 0 1 .5.5v6l-3.775-1.947a.5.5 0 0 0-.577.093l-3.71 3.71-2.66-1.772a.5.5 0 0 0-.63.062L1.002 12v.54A.505.505 0 0 1 1 12.5v-9a.5.5 0 0 1 .5-.5h13z"/>
          </svg>
          View Attachments (${n.attachments.length})
        </button>
      `;
    }

    div.innerHTML = `
      <h3>${escapeHtml(n.title)}</h3>
      <p style="margin-top:6px;font-weight:600;color:#2b556f">${escapeHtml(
        n.category
      )}</p>
      <p style="opacity:0.7;margin-top:8px">${formatDate(n.date)}</p>
      ${bodyPreview}
      ${docButton}
    `;

    // Click handler for the card (only if not a PDF)
    if (n.type === "announcement") {
      div.addEventListener("click", () => {
        showAnnouncementModal(list.indexOf(n));
      });
    } else {
      div.addEventListener("click", () => {
        window.open("/pdfs/" + encodeURIComponent(n.filename), "_blank");
      });
    }

    container.appendChild(div);
  });

  // Store current list for modal access
  window.CURRENT_NOTICES = list;
}

/*--------------------------
      DATE FORMATTER & HELPERS
---------------------------*/
function formatDate(d) {
  if (!d) return "";
  const dt = new Date(d + "T00:00");
  return dt.toLocaleDateString();
}

function escapeHtml(text) {
  if (!text) return "";
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

/*--------------------------
      ANNOUNCEMENT MODAL
---------------------------*/
function showAnnouncementModal(index) {
  const announcement = window.CURRENT_NOTICES[index];
  if (!announcement) return;

  const modal = document.createElement("div");
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    padding: 20px;
  `;

  const content = document.createElement("div");
  content.style.cssText = `
    background: white;
    border-radius: 12px;
    max-width: 600px;
    max-height: 80vh;
    overflow-y: auto;
    padding: 24px;
    position: relative;
  `;

  let attachmentsHtml = "";
  if (announcement.attachments && announcement.attachments.length > 0) {
    attachmentsHtml = `
      <div style="margin-top:16px;padding-top:16px;border-top:1px solid #e0e0e0;">
        <h4 style="font-size:14px;font-weight:600;margin-bottom:8px;">Attachments:</h4>
        ${announcement.attachments
          .map(
            (att) => `
          <a href="${
            att.url
          }" target="_blank" style="display:block;padding:8px;background:#f7f9fc;border-radius:6px;margin-bottom:6px;text-decoration:none;color:#1976d2;font-size:13px;">
            📎 ${escapeHtml(att.name)}
          </a>
        `
          )
          .join("")}
      </div>
    `;
  }

  content.innerHTML = `
    <button onclick="this.closest('[data-modal]').remove()" style="
      position: absolute;
      top: 16px;
      right: 16px;
      background: transparent;
      border: none;
      font-size: 24px;
      cursor: pointer;
      color: #717171;
      width: 32px;
      height: 32px;
    ">×</button>
    <div style="margin-bottom:12px;">
      <span style="display:inline-block;padding:4px 10px;background:#e3f2fd;color:#1976d2;border-radius:4px;font-size:12px;font-weight:500;">Announcement</span>
      <span style="color:#717171;font-size:13px;margin-left:12px;">${formatDate(
        announcement.date
      )}</span>
    </div>
    <h2 style="font-size:20px;font-weight:700;color:#333;margin-bottom:16px;">${escapeHtml(
      announcement.title
    )}</h2>
    <div style="color:#555;font-size:14px;line-height:1.6;white-space:pre-wrap;">${escapeHtml(
      announcement.body || ""
    )}</div>
    ${attachmentsHtml}
  `;

  modal.setAttribute("data-modal", "true");
  modal.appendChild(content);
  document.body.appendChild(modal);

  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.remove();
  });
}
