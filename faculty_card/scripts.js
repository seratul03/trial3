let facultyData = {};

document.addEventListener('DOMContentLoaded', () => {
  const profileContainer = document.getElementById('profileContainer');

  function renderProfileSingle(item) {
    if (!item) return;
    profileContainer.innerHTML = `
    <div class="profile-card">
      <div class="card-header">
        <a href="/faculty" class="back-link"><i class="fas fa-arrow-left"></i> Back to Faculty List</a>
      </div>

      <div class="profile-image-wrapper">
        <div class="image-border">
            <img id="profileImg" src="/${item.photo || ''}" alt="${item.name || ''}" class="profile-img">
        </div>
        <div class="online-indicator" title="Available for Research"></div>
      </div>

      <div class="profile-content">
        <div class="identity">
          <h2 class="name">${item.name || ''} <i class="fas fa-check-circle verified-icon" title="Verified Faculty"></i></h2>
          <p class="designation">${item.position || ''}</p>
          <p class="location"><i class="fas fa-university"></i> ${item.department || ''}</p>
        </div>

        <div class="stats-container">
          <div class="stat-box">
            <span class="stat-value">${(item.papers && item.papers.length) || '—'}</span>
            <span class="stat-label">Papers</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-box">
            <span class="stat-value">${item.citations || '—'}</span>
            <span class="stat-label">Citations</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-box">
            <span class="stat-value">${item.experience || '—'}</span>
            <span class="stat-label">Exp.</span>
          </div>
        </div>

        <div class="skills-container" id="skillsContainer">
        </div>

        <div class="action-buttons">
          <button class="btn btn-secondary" id="messageBtn" data-email="${item.email || ''}">
            <i class="fas fa-envelope"></i> Email
          </button>
        </div>
      </div>
    </div>
  `;

  // populate skills
  const skillsEl = document.getElementById('skillsContainer');
  const skills = item.research_area || [];
  if (skills.length === 0) {
    const span = document.createElement('span');
    span.className = 'skill-tag';
    span.textContent = 'This teacher does not have specified research areas.';
    skillsEl.appendChild(span);
  } else {
    skills.forEach(s => {
      const span = document.createElement('span');
      span.className = 'skill-tag';
      span.textContent = s;
      skillsEl.appendChild(span);
    });
  }
    }

    // Delegate mail button
    profileContainer.addEventListener('click', (e) => {
      const btn = e.target.closest('#messageBtn');
      if (!btn) return;
      const email = btn.getAttribute('data-email') || '';
      if (!email) {
        alert('Email address not available for this profile.');
        return;
      }
      window.location.href = `mailto:${email}`;
    });

    // Load faculty list then render requested single profile (no sidebar)
    fetch('/faculty-data')
      .then(r => r.json())
      .then(list => {
        // Build map
        const map = {};
        list.forEach((it, idx) => {
          const key = it.key || it.id || (it.name||'').toString().toLowerCase().replace(/\s+/g,'-') || `f${idx}`;
          map[key] = it;
        });

        // choose profile from URL
        const params = new URLSearchParams(window.location.search);
        let selectedKey = null;
        if (params.has('id')) selectedKey = params.get('id');
        if (!selectedKey && params.has('name')) selectedKey = decodeURIComponent(params.get('name'));
        if (selectedKey && map[selectedKey]) {
          renderProfileSingle(map[selectedKey]);
          return;
        }

        // fallback: first item
        if (list.length) renderProfileSingle(list[0]);
      })
      .catch(err => {
        console.error('Failed to load faculty data', err);
        if (profileContainer) profileContainer.textContent = 'Unable to load profile.';
      });
  
});