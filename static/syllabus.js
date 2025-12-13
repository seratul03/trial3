// syllabus.js: Handles tab switching and micro lecture plan toggling

// Load syllabus data from JSON file (AJAX)
async function loadSyllabus() {
    const response = await fetch('/syllabus/syllabus.json');
    return await response.json();
}

function createTab(semester, idx) {
    const tab = document.createElement('div');
    tab.className = 'tab' + (idx === 0 ? ' active' : '');
    tab.textContent = `Semester ${semester}`;
    tab.dataset.semester = idx;
    tab.onclick = () => selectTab(idx);
    return tab;
}

function selectTab(idx) {
    document.querySelectorAll('.tab').forEach((tab, i) => {
        tab.classList.toggle('active', i === idx);
    });
    document.querySelectorAll('.semester-section').forEach((sec, i) => {
        sec.classList.toggle('active', i === idx);
    });
    // After switching, re-apply any active search filter for the new semester
    const searchInput = document.getElementById('syllabus-search-input');
    if (searchInput) {
        filterSubjects(searchInput.value || '');
    }
    // hide global search results on manual tab change
    const results = document.querySelector('.syllabus-search-results');
    if (results) results.style.display = 'none';
}

function createSubject(course) {
    const li = document.createElement('li');
    // Minimal subject item: only title shown in list.
    li.className = 'subject' + ((course.course_type === 'PE' || course.course_type === 'OE' || course.course_type === 'OEC') ? ' elective' : '');
    const title = document.createElement('div');
    title.className = 'subject-title';
    title.textContent = `${course.course_code}: ${course.course_name}`;
    li.appendChild(title);
    // Add searchable attributes
    li.dataset.code = (course.course_code || '').toLowerCase();
    li.dataset.name = (course.course_name || '').toLowerCase();
    // If elective, show a small badge
    if (course.course_type === 'PE' || course.course_type === 'OE' || course.course_type === 'OEC') {
        const badge = document.createElement('span');
        badge.className = 'subject-badge';
        badge.textContent = 'Elective';
        li.appendChild(badge);
    }
    // Details are intentionally omitted here and presented inside the Micro Lecture Plan
    return li;
}

function createMicroLecturePlan(courses, semIdx) {
    const btn = document.createElement('button');
    btn.className = 'micro-lecture-toggle';
    btn.textContent = 'Show Micro Lecture Plan';
    const plan = document.createElement('div');
    plan.className = 'micro-lecture-plan';
    const table = document.createElement('table');
    table.className = 'micro-lecture-table';
    table.dataset.sem = semIdx;
    // Header
    const thead = document.createElement('thead');
    thead.innerHTML = `<tr><th>Code</th><th>Course</th><th>Type</th><th>Credits</th><th>Marks</th><th>Hours (L-T-P)</th><th>Options</th></tr>`;
    table.appendChild(thead);
    const tbody = document.createElement('tbody');
    // Rows
    courses.forEach((course, index) => {
        const optsText = course.options ? course.options.join('; ') : '-';
        const marks = course.marks ?? '-';
        const credits = course.credits ?? 0;
        const hours = `L${course.hours.L},T${course.hours.T ?? 0},P${course.hours.P ?? 0}`;
        const tr = document.createElement('tr');
        tr.className = 'course-row';
        tr.dataset.code = (course.course_code || '').toLowerCase();
        tr.dataset.name = (course.course_name || '').toLowerCase();
        tr.innerHTML = `<td>${course.course_code}</td><td>${course.course_name}</td><td>${course.course_type}</td><td>${credits}</td><td>${marks}</td><td>${hours}</td><td>${optsText}</td>`;
        tbody.appendChild(tr);
        // If elective and has options, add a sub-row per option for clarity
        if (course.options && Array.isArray(course.options) && course.options.length > 0) {
            course.options.forEach(opt => {
                const sub = document.createElement('tr');
                sub.className = 'elective-sub';
                sub.innerHTML = `<td></td><td colspan="6">Elective option: <strong>${opt}</strong></td>`;
                tbody.appendChild(sub);
            });
        }
    });
    table.appendChild(tbody);
    // Wrap table for horizontal scrolling
    const wrap = document.createElement('div');
    wrap.className = 'micro-lecture-wrap';
    wrap.appendChild(table);
    plan.appendChild(wrap);
    btn.onclick = () => {
        plan.classList.toggle('active');
        btn.textContent = plan.classList.contains('active') ? 'Hide Micro Lecture Plan' : 'Show Micro Lecture Plan';
    };
    return [btn, plan];
}

function createSemesterSection(semester, idx) {
    const section = document.createElement('div');
    section.className = 'semester-section' + (idx === 0 ? ' active' : '');
    const h2 = document.createElement('h2');
    h2.textContent = `Semester ${semester.semester}`;
    section.appendChild(h2);
    const ul = document.createElement('ul');
    ul.className = 'subject-list';
    semester.courses.forEach(course => {
        ul.appendChild(createSubject(course));
    });
    section.appendChild(ul);
    // Micro Lecture Plan
    const [btn, plan] = createMicroLecturePlan(semester.courses, idx);
    section.appendChild(btn);
    section.appendChild(plan);
    return section;
}

// Allow re-initialization for dynamic modal injection
window.syllabusInit = async function syllabusInit() {
    const tabs = document.getElementById('semester-tabs');
    const content = document.getElementById('semester-content');
    if (!tabs || !content) return;
    tabs.innerHTML = '';
    content.innerHTML = '';
    const data = await loadSyllabus();
    // Insert search UI above tabs
    let searchBar = document.querySelector('.syllabus-search');
    if (!searchBar) {
        searchBar = document.createElement('div');
        searchBar.className = 'syllabus-search';
        const input = document.createElement('input');
        input.type = 'search';
        input.placeholder = 'Search courses by code or name...';
        input.id = 'syllabus-search-input';
        const clearBtn = document.createElement('button');
        clearBtn.className = 'clear-btn';
        clearBtn.textContent = 'Clear';
        clearBtn.onclick = () => {
            input.value = '';
            filterSubjects('');
            input.focus();
        };
        searchBar.appendChild(input);
        searchBar.appendChild(clearBtn);
        // If semester-tabs exists in DOM, insert search before it
        const container = tabs.parentElement || document.body;
        container.insertBefore(searchBar, tabs);
    }
        // Make data available globally for cross-semester search
        window.syllabusData = data;

        // Create / attach search results container
        let searchResults = document.querySelector('.syllabus-search-results');
        if (!searchResults) {
            searchResults = document.createElement('div');
            searchResults.className = 'syllabus-search-results';
            searchResults.style.display = 'none';
            // insert after searchBar
            searchBar.parentNode.insertBefore(searchResults, tabs);
        }

        // Debounced search handler (global across semesters)
        const searchInput = document.getElementById('syllabus-search-input');
        let debounceTimer = null;
        searchInput.oninput = (e) => {
            clearTimeout(debounceTimer);
            const q = e.target.value;
            debounceTimer = setTimeout(() => performSearch(q), 180);
    };
        // Keyboard navigation for results: up/down/enter/esc
        searchInput.addEventListener('keydown', (ev) => {
            const resultsContainer = document.querySelector('.syllabus-search-results');
            if (!resultsContainer || resultsContainer.style.display === 'none') return;
            const items = Array.from(resultsContainer.querySelectorAll('.result-item'));
            if (!items.length) return;
            let focused = resultsContainer.querySelector('.result-item.focused');
            let idx = focused ? items.indexOf(focused) : -1;
            if (ev.key === 'ArrowDown') {
                ev.preventDefault();
                idx = Math.min(items.length - 1, idx + 1);
                items.forEach(it => it.classList.remove('focused'));
                items[idx].classList.add('focused');
                items[idx].scrollIntoView({ block: 'nearest' });
                try { items[idx].focus(); } catch (e) {}
            } else if (ev.key === 'ArrowUp') {
                ev.preventDefault();
                idx = Math.max(0, idx - 1);
                items.forEach(it => it.classList.remove('focused'));
                items[idx].classList.add('focused');
                items[idx].scrollIntoView({ block: 'nearest' });
                try { items[idx].focus(); } catch (e) {}
            } else if (ev.key === 'Enter') {
                ev.preventDefault();
                if (idx >= 0 && items[idx]) items[idx].click();
            } else if (ev.key === 'Escape') {
                resultsContainer.style.display = 'none';
                searchInput.blur();
            }
        });
    data.semesters.forEach((sem, idx) => {
        tabs.appendChild(createTab(sem.semester, idx));
        content.appendChild(createSemesterSection(sem, idx));
    });
    // Reset any active filters
    filterSubjects('');
};

// Perform search across all semesters and show results; also filter active semester
function performSearch(q) {
    const query = (q || '').trim().toLowerCase();
    // Filter current active semester for quick local results
    filterSubjects(query);

    const resultsContainer = document.querySelector('.syllabus-search-results');
    resultsContainer.innerHTML = '';
    if (!query) {
        resultsContainer.style.display = 'none';
        return;
    }

    const results = [];
    if (!window.syllabusData || !window.syllabusData.semesters) {
        resultsContainer.style.display = 'none';
        return;
    }

    window.syllabusData.semesters.forEach((sem, semIdx) => {
        sem.courses.forEach(course => {
            const code = (course.course_code || '').toLowerCase();
            const name = (course.course_name || '').toLowerCase();
            if (code.includes(query) || name.includes(query)) {
                results.push({ semIdx, semLabel: sem.semester, code: course.course_code, name: course.course_name });
            }
        });
    });

    if (results.length === 0) {
        const no = document.createElement('div');
        no.className = 'result-item';
        no.textContent = 'No matches';
        resultsContainer.appendChild(no);
        resultsContainer.style.display = 'block';
        return;
    }

    // Render results (limit to 50)
    results.slice(0, 50).forEach(r => {
        const item = document.createElement('div');
        item.className = 'result-item';
        item.tabIndex = 0;
        const left = document.createElement('div');
        left.style.display = 'flex'; left.style.alignItems = 'center';
        const sem = document.createElement('div');
        sem.className = 'result-sem';
        sem.textContent = `Sem ${r.semLabel}`;
        const title = document.createElement('div');
        title.className = 'result-title';
        title.textContent = `${r.code}: ${r.name}`;
        left.appendChild(sem);
        left.appendChild(title);
        item.appendChild(left);
        item.onclick = () => {
            // Open the semester and highlight the subject
            selectTab(r.semIdx);
            // ensure search results hidden
            resultsContainer.style.display = 'none';
            // after DOM update, find the subject element and highlight
            setTimeout(() => {
                const sec = document.querySelectorAll('.semester-section')[r.semIdx];
                if (!sec) return;
                const subjects = sec.querySelectorAll('.subject');
                let target = null;
                for (let s of subjects) {
                    if ((s.dataset.code || '').includes((r.code || '').toLowerCase())) { target = s; break; }
                    if ((s.dataset.name || '').includes((r.name || '').toLowerCase())) { target = s; break; }
                }
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    highlightSubject(target);
                    // Open the micro-lecture plan for this semester if not already open
                    const planBtn = sec.querySelector('.micro-lecture-toggle');
                    const planDiv = sec.querySelector('.micro-lecture-plan');
                    if (planBtn && planDiv && !planDiv.classList.contains('active')) {
                        planBtn.click();
                    }
                }
            }, 120);
        };
        // support Enter/Space on focused item
        item.addEventListener('keydown', (ev) => {
            if (ev.key === 'Enter' || ev.key === ' ') {
                ev.preventDefault();
                item.click();
            }
        });
        resultsContainer.appendChild(item);
    });
    resultsContainer.style.display = 'block';
}

function highlightSubject(el) {
    if (!el) return;
    el.classList.add('highlight');
    setTimeout(() => el.classList.remove('highlight'), 2200);
}

// Filter subjects by query (current semester only)
function filterSubjects(q) {
    const query = (q || '').trim().toLowerCase();
    const activeSection = document.querySelector('.semester-section.active');
    if (!activeSection) return;
    const items = activeSection.querySelectorAll('.subject');
    if (!query) {
        items.forEach(it => it.style.display = 'flex');
        // also reset micro-plan table rows
        const table = activeSection.querySelector('.micro-lecture-table');
        if (table) {
            Array.from(table.querySelectorAll('tbody tr')).forEach(r => r.style.display = 'table-row');
        }
        return;
    }
    items.forEach(it => {
        const code = it.dataset.code || '';
        const name = it.dataset.name || '';
        const match = code.includes(query) || name.includes(query);
        it.style.display = match ? 'flex' : 'none';
    });
    // Also filter micro lecture plan rows for active semester
    const activeIdx = Array.from(document.querySelectorAll('.semester-section')).indexOf(activeSection);
    const table = document.querySelector(`.micro-lecture-table[data-sem="${activeIdx}"]`);
    if (table) {
        Array.from(table.querySelectorAll('tbody tr.course-row')).forEach(r => {
            const rc = (r.dataset.code || '').toLowerCase();
            const rn = (r.dataset.name || '').toLowerCase();
            const keep = rc.includes(query) || rn.includes(query);
            r.style.display = keep ? 'table-row' : 'none';
            // hide subsequent elective-sub rows when parent hidden
            let next = r.nextElementSibling;
            while (next && next.classList.contains('elective-sub')) {
                next.style.display = keep ? 'table-row' : 'none';
                next = next.nextElementSibling;
            }
        });
    }
}

// Auto-run if on standalone page
if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', () => {
        if (document.getElementById('semester-tabs') && document.getElementById('semester-content')) {
            window.syllabusInit();
        }
    });
} else {
    if (document.getElementById('semester-tabs') && document.getElementById('semester-content')) {
        window.syllabusInit();
    }
}
