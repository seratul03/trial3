

// ========== SCRIPT BLOCK ==========

// Academics Modal Functions
          function openAcademicsModal() {
            const modal = document.getElementById("academicsModal");
            modal.style.display = "flex";
            modal.classList.remove("closing");
            modal.classList.add("opening");
            document.getElementById("academicsMainCards").style.display =
              "block";
            document.getElementById("academicsSectionContent").innerHTML = "";
          }
          function closeAcademicsModal() {
            const modal = document.getElementById("academicsModal");
            modal.classList.remove("opening");
            modal.classList.add("closing");
            setTimeout(() => {
              modal.style.display = "none";
              modal.classList.remove("closing");
            }, 300);
          }
          async function showAcademicsSection(section) {
            const contentDiv = document.getElementById(
              "academicsSectionContent"
            );

            if (section === "subjects") {
              // Hide the main cards when entering subjects section
              document.getElementById("academicsMainCards").style.display =
                "none";

              contentDiv.innerHTML =
                '<div class="loading">Loading semesters...</div>';
              try {
                const response = await fetch("/semesters");
                const semesters = await response.json();

                let html =
                  '<div style="margin-top:16px;"><h3 style="font-size:16px;margin-bottom:12px;color:#333;">Select a Semester</h3><div style="display:grid;gap:12px;">';
                semesters.forEach((sem) => {
                  html += `
              <button onclick="loadSemesterSubjects(${sem.id})" style="
                padding:14px 18px;
                background:linear-gradient(135deg, #f7f9fc 0%, #e8eef5 100%);
                border:1px solid #d0d7de;
                border-radius:10px;
                cursor:pointer;
                text-align:left;
                transition:all 0.2s ease;
                font-size:14px;
              " onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)';" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none';">
                <div style="font-weight:600;color:#1976d2;">${sem.name}</div>
                <div style="color:#717171;font-size:13px;margin-top:4px;">${sem.subject_count} subjects</div>
              </button>`;
                });
                html += "</div></div>";
                contentDiv.innerHTML = html;
              } catch (error) {
                contentDiv.innerHTML =
                  '<div style="color:#c62828;">Error loading semesters</div>';
              }
            } else {
              let content = "";
              switch (section) {
                case "syllabus":
                  // Hide the main cards when entering syllabus section
                  document.getElementById("academicsMainCards").style.display = "none";
                  contentDiv.innerHTML = '<div id="syllabus-modal-loader" class="loading">Loading syllabus...</div>';
                  // Dynamically load syllabus CSS if not already loaded
                  if (!document.getElementById('syllabus-css-modal')) {
                    var link = document.createElement('link');
                    link.rel = 'stylesheet';
                    link.href = '/static/syllabus.css';
                    link.id = 'syllabus-css-modal';
                    document.head.appendChild(link);
                  }
                  // Dynamically load syllabus.js and inject syllabus section
                  fetch('/syllabus/syllabus.html').then(r => r.text()).then(html => {
                    // Extract the syllabus-container div
                    var temp = document.createElement('div');
                    temp.innerHTML = html;
                    var sc = temp.querySelector('.syllabus-container');
                    if (sc) {
                      contentDiv.innerHTML = '';
                      contentDiv.appendChild(sc);
                      // Load syllabus.js if not already loaded
                      if (!document.getElementById('syllabus-js-modal')) {
                        var script = document.createElement('script');
                        script.src = '/static/syllabus.js';
                        script.id = 'syllabus-js-modal';
                        document.body.appendChild(script);
                      } else {
                        // If already loaded, re-run the script
                        if (typeof window.syllabusInit === 'function') window.syllabusInit();
                      }
                    } else {
                      contentDiv.innerHTML = '<div style="color:#c62828;">Failed to load syllabus content.</div>';
                    }
                  }).catch(() => {
                    contentDiv.innerHTML = '<div style="color:#c62828;">Failed to load syllabus content.</div>';
                  });
                  return;
                // Scholarship now opens in new tab - no case needed
                case "exam":
                  openExamModal();
                  return;
                case "notice":
                  // Hide the main cards when entering notice section
                  document.getElementById("academicsMainCards").style.display =
                    "none";
                  loadNoticeSection();
                  return;
                case "grading":
                  content =
                    "<b>Grading & Other Details:</b><br>Information about grading, marks, and other academic details. (Content coming soon)";
                  break;
              }
              if (content) contentDiv.innerHTML = content;
            }
          }

          async function loadSemesterSubjects(semId) {
            const contentDiv = document.getElementById(
              "academicsSectionContent"
            );
            contentDiv.innerHTML =
              '<div class="loading">Loading subjects...</div>';

            try {
              const response = await fetch(`/semester/${semId}/subjects`);
              const data = await response.json();

              // Store semester data for later use
              window.currentSemesterData = data;
              window.currentSemesterId = semId;

              let html = `
          <div style="margin-top:16px;">
            <h3 style="font-size:20px;font-weight:700;color:#1976d2;margin-bottom:16px;">${data.semester}</h3>
            <div style="display:flex;flex-direction:column;gap:14px;max-height:500px;overflow-y:auto;padding-right:8px;scrollbar-width:none;-ms-overflow-style:none;">
            <style>#academicsSectionContent div::-webkit-scrollbar{display:none;}</style>`;

              data.subjects.forEach((subject, index) => {
                html += `
            <button onclick="viewSubjectDetails(${index})" style="
              background:#fff;
              border:1px solid #e0e0e0;
              border-radius:10px;
              padding:16px 18px;
              cursor:pointer;
              display:flex;
              justify-content:space-between;
              align-items:center;
              gap:12px;
              transition:all 0.2s ease;
              text-align:left;
              width:100%;
            " onmouseover="this.style.transform='translateX(4px)';this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)';this.style.borderColor='#1976d2';" onmouseout="this.style.transform='translateX(0)';this.style.boxShadow='none';this.style.borderColor='#e0e0e0';">
              <div style="flex:1;min-width:0;">
                <div style="font-weight:600;color:#333;font-size:16px;line-height:1.4;word-wrap:break-word;word-break:break-word;">
                  ${
                    subject.course_name
                  } <span style="color:#717171;font-weight:500;">(${
                  subject.course_code
                })</span>
                </div>
                <div style="color:#717171;font-size:13px;margin-top:4px;">${
                  subject.modules.length
                } modules • ${
                  subject.recommended_books?.length || 0
                } books</div>
              </div>
              <svg style="width:24px;height:24px;min-width:24px;color:#1976d2;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </button>`;
              });

              html +=
                "</div><style>#academicsSectionContent > div > div::-webkit-scrollbar{display:none;}</style></div>";
              contentDiv.innerHTML = html;
            } catch (error) {
              contentDiv.innerHTML =
                '<div style="color:#c62828;">Error loading subjects</div>';
            }
          }

          async function viewSubjectDetails(subjectIndex) {
            const contentDiv = document.getElementById(
              "academicsSectionContent"
            );
            const data = window.currentSemesterData;
            const subject = data.subjects[subjectIndex];

            // Fetch detailed subject data including summary
            let subjectDetails = subject;
            try {
              const response = await fetch(
                `/course-explanation/${subject.course_code}`
              );
              if (response.ok) {
                subjectDetails = await response.json();
              }
            } catch (error) {
              console.log("Using basic subject data");
            }

            let html = `
        <div style="margin-top:16px;">
          <button onclick="loadSemesterSubjects(${window.currentSemesterId})" style="
            background:none;
            border:none;
            color:#1976d2;
            cursor:pointer;
            padding:8px 0;
            font-size:14px;
            display:flex;
            align-items:center;
            gap:6px;
            margin-bottom:12px;
          " onmouseover="this.style.textDecoration='underline';" onmouseout="this.style.textDecoration='none';">
            ← Back to ${data.semester}
          </button>
          
          <div style="background:linear-gradient(135deg, #1976d2 0%, #1565c0 100%);border-radius:12px;padding:20px;margin-bottom:20px;color:#fff;">
            <h3 style="font-size:22px;font-weight:700;margin:0 0 8px 0;">${subject.course_name}</h3>
            <div style="font-size:14px;opacity:0.9;">Course Code: ${subject.course_code}</div>
          </div>
          
          <div style="margin-bottom:20px;display:flex;gap:12px;justify-content:flex-end;">
            <button onclick="showCourseOutcomes('${subject.course_code}')" style="
              background:#fff;color:#1976d2;border:2px solid #1976d2;padding:10px 20px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:500;
              transition:all 0.2s;
            " onmouseover="this.style.background='#1976d2';this.style.color='#fff';" onmouseout="this.style.background='#fff';this.style.color='#1976d2';">
              🎯 Course Outcomes
            </button>
            <button onclick="showPrerequisites('${subject.course_code}')" style="
              background:#fff;color:#1976d2;border:2px solid #1976d2;padding:10px 20px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:500;
              transition:all 0.2s;
            " onmouseover="this.style.background='#1976d2';this.style.color='#fff';" onmouseout="this.style.background='#fff';this.style.color='#1976d2';">
              📋 Prerequisites
            </button>
          </div>
          
          <div>
            <div style="margin-bottom:24px;">
              <h4 style="font-size:18px;font-weight:600;color:#1976d2;margin-bottom:14px;display:flex;align-items:center;gap:8px;">
                <span>📚</span> Modules
              </h4>
              <div style="display:flex;flex-direction:column;gap:10px;">`;

            (subjectDetails.modules || subject.modules).forEach((module) => {
              html += `
                <div style="
                  padding:14px 16px;
                  background:#fff;
                  border:1px solid #e3f2fd;
                  border-left:4px solid #1976d2;
                  border-radius:8px;
                  font-size:14px;
                  line-height:1.6;
                  box-shadow:0 2px 4px rgba(0,0,0,0.05);
                  transition:all 0.2s ease;
                " onmouseover="this.style.transform='translateX(4px)';this.style.boxShadow='0 4px 8px rgba(0,0,0,0.1)';" onmouseout="this.style.transform='translateX(0)';this.style.boxShadow='0 2px 4px rgba(0,0,0,0.05)';">
                  <div style="display:flex;align-items:start;gap:10px;">
                    <span style="font-weight:700;color:#1976d2;font-size:15px;min-width:85px;">Module ${module.module_number}:</span>
                    <span style="color:#333;flex:1;">${module.title}</span>
                  </div>
                </div>`;
            });

            html += `
              </div>
            </div>`;

            // Add 5-sentence summary
            if (subjectDetails.summary) {
              html += `
            <div style="background:#f0f7ff;border:1px solid #d0e8f7;border-radius:10px;padding:18px;margin-bottom:24px;">
              <h4 style="font-size:16px;font-weight:600;color:#1976d2;margin:0 0 12px 0;display:flex;align-items:center;gap:8px;">
                <span>💡</span> About this Subject
              </h4>
              <p style="margin:0;color:#333;font-size:14px;line-height:1.8;text-align:justify;">
                ${subjectDetails.summary}
              </p>
            </div>`;
            }

            // Add recommended books at the bottom
            if (
              subjectDetails.recommended_books &&
              subjectDetails.recommended_books.length > 0
            ) {
              html += `
            <div style="margin-bottom:16px;">
              <h4 style="font-size:18px;font-weight:600;color:#1976d2;margin-bottom:14px;display:flex;align-items:center;gap:8px;">
                <span>📖</span> Recommended Books
              </h4>
              <div style="background:#fff;border:1px solid #e0e0e0;border-radius:10px;padding:18px;">
                <ul style="margin:0;padding-left:20px;list-style:none;">`;

              subjectDetails.recommended_books.forEach((book, idx) => {
                html += `
                  <li style="
                    color:#333;
                    font-size:14px;
                    margin-bottom:12px;
                    line-height:1.6;
                    padding-left:8px;
                    position:relative;
                  " onmouseover="this.style.color='#1976d2';" onmouseout="this.style.color='#333';">
                    <span style="position:absolute;left:-20px;color:#1976d2;font-weight:600;">${
                      idx + 1
                    }.</span>
                    ${book}
                  </li>`;
              });

              html += `
                </ul>
              </div>
            </div>`;
            }

            html += `
          </div>
        </div>`;

            contentDiv.innerHTML = html;
          }

          function getSubjectDescription(courseCode) {
            const descriptions = {
              HSMCM101:
                "This course focuses on developing effective communication skills essential for professional and academic success. Students will learn the fundamentals of functional grammar, expand their vocabulary, master pronunciation techniques, and understand communication theory. The course emphasizes practical application through comprehension exercises, enabling students to express ideas clearly and confidently. By the end of this course, students will be equipped with the linguistic tools necessary for effective written and oral communication in diverse contexts.",

              BSCM101:
                "This course provides a comprehensive introduction to semiconductor physics, exploring the quantum mechanical principles that govern electronic materials. Students will delve into the behavior of semiconductors, understand optical transitions, and learn various measurement techniques. The curriculum bridges theoretical concepts with practical applications in modern electronic devices. Through this course, students gain insights into the fundamental properties of semiconductors that form the backbone of contemporary technology and optoelectronics.",

              BSCM102:
                "This comprehensive mathematics course covers essential topics in calculus and linear algebra crucial for engineering and scientific applications. Students will explore single and multivariable calculus, sequences and series, matrix operations, and vector spaces. The course develops analytical thinking and problem-solving skills through rigorous mathematical methods. These fundamental concepts serve as building blocks for advanced engineering courses and provide the mathematical foundation necessary for modeling real-world phenomena in various scientific disciplines.",

              ESCM101:
                "This foundational course introduces students to the principles of electrical and electronics engineering, covering both theoretical and practical aspects. The curriculum encompasses DC and AC circuit analysis, transformers, electrical machines, and semiconductor devices including diodes and transistors. Students will develop a strong understanding of electrical systems and electronic components essential for modern technology. The course prepares students for advanced topics in electronics and provides hands-on experience with fundamental electrical concepts.",

              BSCM191:
                "This laboratory course provides hands-on experience with semiconductor physics experiments and measurements. Students will perform practical experiments on pn junction diodes, Zener diodes, optical fibers, and various semiconductor properties. The lab sessions reinforce theoretical concepts through direct observation and measurement of physical phenomena. This practical exposure helps students develop experimental skills, data analysis capabilities, and a deeper understanding of semiconductor behavior in real-world applications.",

              ESCM191:
                "This practical laboratory course offers comprehensive hands-on training in basic electrical and electronics engineering. Students will conduct experiments on diode characteristics, rectifiers, transistors, electrical measurements, network theorems, and transformers. The lab provides essential experience in using measuring instruments, circuit analysis, and understanding the operation of electrical machines. Through these practical sessions, students bridge the gap between theoretical knowledge and real-world engineering applications.",

              ESCM192:
                "This course introduces students to engineering graphics and computer-aided design principles essential for technical documentation and visualization. Students will learn manual drafting techniques including geometrical constructions, projections, isometric views, and sectional drawings. The course also covers AutoCAD software for digital drafting and design. These skills are fundamental for engineers to communicate design ideas effectively and create accurate technical drawings for manufacturing and construction purposes.",

              "AUM-1":
                "This multidisciplinary course explores the critical relationship between human activities and the environment, covering ecosystems, natural resources, pollution, and sustainability. Students will examine environmental challenges, understand ecological principles, and analyze the impact of human population growth on natural systems. The course emphasizes the importance of environmental conservation and sustainable practices. Students will develop awareness of environmental issues and learn strategies for responsible resource management and environmental protection.",

              default:
                "This course provides comprehensive coverage of essential concepts and practical applications in the subject area. Students will engage with theoretical foundations while developing practical skills through hands-on exercises and real-world problem solving. The curriculum is designed to build a strong foundation for advanced studies and professional practice. Through lectures, assignments, and projects, students will gain deep understanding and develop critical thinking abilities necessary for success in their chosen field of study.",
            };

            return descriptions[courseCode] || descriptions["default"];
          }

          function getModuleExplanation(courseCode, moduleNumber) {
            // Short explanations for modules (can be expanded later)
            const map = {
              HSMCM101: {
                1: "Functional Grammar: This module focuses on understanding sentence structures, verb forms, tenses, and common grammar patterns used in academic and professional writing. Activities include sentence correction, transformation exercises, and grammar in context.",
                2: "Vocabulary: Builds lexical resources for academic reading and speaking. Covers collocations, phrasal verbs, word formation, and context usage to improve precision and fluency.",
                3: "Pronunciation: Covers articulation, stress, intonation, and rhythm to improve spoken clarity. Includes practice with minimal pairs and connected speech.",
                4: "Communication Theory: Introduces models of communication, barriers, and effective strategies for interpersonal and group communication.",
                5: "Comprehension: Develops reading strategies, skimming, scanning, and critical reading to extract meaning and infer intent from texts.",
              },
              BSCM101: {
                1: "Introduction to Quantum Mechanics: Basics of wave-particle duality, Schrödinger equation, and simple quantum systems.",
                2: "Electronic Materials: Study of crystalline solids, energy bands, and charge carriers.",
                3: "Semiconductors: Intrinsic and extrinsic semiconductors, carrier concentration and transport.",
                4: "Optical Transitions: Interaction of light with semiconductors, absorption and emission processes.",
                5: "Measurements: Techniques for measuring electrical and optical properties of materials.",
              },
              BSCM102: {
                1: "Single Variable Calculus: Limits, differentiation, and applications to curve sketching and optimization.",
                2: "Sequences and Series: Convergence tests, power series and Taylor expansions.",
                3: "Multivariable Calculus: Partial derivatives, multiple integrals, and vector calculus basics.",
                4: "Matrices: Matrix operations, determinants, and solving linear systems.",
                5: "Vector Spaces: Basis, dimension, linear transformations and their applications.",
              },
              ESCM101: {
                1: "DC Circuit: Fundamentals of resistive circuits, Ohm’s law, and Kirchhoff’s laws.",
                2: "AC Circuits: Sinusoidal steady state analysis, phasors and impedance.",
                3: "Transformers: Operating principles, equivalent circuits and testing.",
                4: "Electrical Machines: Basics of motors and generators and their characteristics.",
                5: "Physics of Semiconductors: Semiconductor basics relevant to electronic devices.",
                6: "p-n Junction and Diodes: Structure, I-V characteristics and applications.",
                7: "Bipolar Junction Transistor: Operation, configurations and basic amplifier action.",
              },
              default: {
                1: "Module overview: This module introduces the core concepts and objectives. Refer to the course for detailed syllabus and readings.",
              },
            };

            const courseMap = map[courseCode] || map["default"];
            return (
              courseMap[moduleNumber] ||
              courseMap[1] ||
              "Explanation not available."
            );
          }

          async function showModuleExplain(subjectIndex, moduleIndex) {
            const data = window.currentSemesterData;
            if (!data || !data.subjects || !data.subjects[subjectIndex]) return;
            const subject = data.subjects[subjectIndex];
            const module = subject.modules[moduleIndex];

            // Show loading modal first
            showLoadingModal(subject, module, subjectIndex);

            try {
              const response = await fetch(
                `/module-explanation/${subject.course_code}/${module.module_number}`
              );
              const explanationData = await response.json();
              const explanation =
                explanationData.detailed_content ||
                explanationData.summary ||
                "Module explanation not available.";
              updateExplanationModal(
                subject,
                module,
                explanation,
                explanationData,
                subjectIndex
              );
            } catch (error) {
              console.error("Error:", error);
              updateExplanationModal(
                subject,
                module,
                "Error loading explanation.",
                {},
                subjectIndex
              );
            }
          }

          function showLoadingModal(subject, module, subjectIndex) {
            const existing = document.getElementById("moduleExplainModal");
            if (existing) existing.remove();
            const modalHtml = `
        <div id="moduleExplainModal" style="position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.5);z-index:10000;backdrop-filter:blur(4px);"> 
          <div style="background:#fff;border-radius:16px;max-width:800px;width:92%;max-height:85vh;overflow:auto;padding:24px;box-shadow:0 12px 40px rgba(0,0,0,0.5);position:relative;scrollbar-width:none;-ms-overflow-style:none;">
            <style>#moduleExplainModal > div::-webkit-scrollbar{display:none;}</style>
            <button aria-label="Close" onclick="closeModuleExplain()" style="position:absolute;right:16px;top:16px;border:none;background:#f4f4f4;border-radius:50%;width:40px;height:40px;cursor:pointer;font-size:22px;transition:all 0.2s;display:flex;align-items:center;justify-content:center;" onmouseover="this.style.background='#e0e0e0';this.style.transform='rotate(90deg)';" onmouseout="this.style.background='#f4f4f4';this.style.transform='rotate(0deg)';">×</button>
            <div style="margin-bottom:20px;padding-bottom:16px;border-bottom:2px solid #e3f2fd;">
              <div style="color:#717171;font-size:13px;margin-bottom:4px;">${subject.course_code}</div>
              <h3 style="margin:0 0 8px 0;color:#1976d2;font-size:24px;line-height:1.3;">${subject.course_name}</h3>
              <div style="display:flex;align-items:center;gap:10px;">
                <span style="background:#1976d2;color:#fff;padding:4px 12px;border-radius:16px;font-size:13px;font-weight:600;">Module ${module.module_number}</span>
                <span style="color:#444;font-weight:500;font-size:15px;">${module.title}</span>
              </div>
            </div>
            <div id="moduleExplanationContent" style="line-height:1.8;color:#333;font-size:14px;">
              <div style="display:flex;align-items:center;justify-content:center;padding:40px;color:#717171;">
                <div style="text-align:center;">
                  <div style="width:50px;height:50px;border:3px solid #1976d2;border-top-color:transparent;border-radius:50%;margin:0 auto 16px;animation:spin 1s linear infinite;"></div>
                  <div>Loading...</div>
                </div>
              </div>
            </div>
            <div style="margin-top:24px;display:flex;gap:12px;justify-content:flex-end;padding-top:16px;border-top:1px solid #e0e0e0;">
              <button onclick="closeModuleExplain()" style="padding:10px 20px;border-radius:8px;border:1px solid #d0e8f7;background:#e3f2fd;color:#1976d2;cursor:pointer;font-size:14px;font-weight:500;">Close</button>
            </div>
            <style>@keyframes spin{to{transform:rotate(360deg);}}</style>
          </div>
        </div>`;
            document.body.insertAdjacentHTML("beforeend", modalHtml);
          }

          function updateExplanationModal(
            subject,
            module,
            explanation,
            explanationData,
            subjectIndex
          ) {
            const contentDiv = document.getElementById(
              "moduleExplanationContent"
            );
            if (!contentDiv) return;

            // Helper function to format text into paragraphs
            function formatParagraphs(text) {
              if (!text) return "";
              return text
                .split("\n\n")
                .filter((p) => p.trim())
                .map(
                  (p) =>
                    `<p style="margin:0 0 16px 0;text-align:justify;">${p.trim()}</p>`
                )
                .join("");
            }

            let html = "";
            if (explanationData.summary && explanationData.summary.trim()) {
              html += `<div style="background:#e3f2fd;border-left:4px solid #1976d2;padding:14px 16px;border-radius:8px;margin-bottom:20px;"><div style="font-weight:600;color:#1976d2;margin-bottom:6px;font-size:13px;">SUMMARY</div><div style="color:#333;font-size:14px;line-height:1.7;">${formatParagraphs(
                explanationData.summary
              )}</div></div>`;
            }
            html += `<div style="background:#fff;padding:4px 0;"><div style="font-weight:600;color:#1976d2;margin-bottom:12px;font-size:15px;">Detailed Explanation</div><div style="line-height:1.8;color:#333;">${formatParagraphs(
              explanation
            )}</div></div>`;
            if (
              explanationData.raw_text &&
              explanationData.raw_text !== explanation &&
              explanationData.raw_text.trim()
            ) {
              html += `<div style="margin-top:24px;padding-top:20px;border-top:1px solid #e0e0e0;"><div style="font-weight:600;color:#1976d2;margin-bottom:12px;font-size:15px;">Syllabus Details</div><div style="background:#f8f9fa;padding:14px;border-radius:8px;font-size:13px;line-height:1.7;color:#555;">${formatParagraphs(
                explanationData.raw_text
              )}</div></div>`;
            }
            contentDiv.innerHTML = html;
          }

          function closeModuleExplain() {
            const m = document.getElementById("moduleExplainModal");
            if (m) m.remove();
          }

          async function showCourseExplanation(courseCode) {
            // Remove existing modal if present
            const existing = document.getElementById("courseExplainModal");
            if (existing) existing.remove();

            // Create loading modal
            const loadingHtml = `
        <div id="courseExplainModal" style="position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.5);z-index:10000;backdrop-filter:blur(4px);">
          <div style="background:#fff;border-radius:16px;max-width:900px;width:95%;max-height:90vh;overflow:auto;padding:32px;box-shadow:0 12px 40px rgba(0,0,0,0.5);position:relative;scrollbar-width:none;-ms-overflow-style:none;">
            <style>#courseExplainModal > div::-webkit-scrollbar{display:none;}</style>
            <button aria-label="Close" onclick="closeCourseExplain()" style="position:absolute;right:16px;top:16px;border:none;background:#f4f4f4;border-radius:50%;width:40px;height:40px;cursor:pointer;font-size:24px;transition:all 0.2s;display:flex;align-items:center;justify-content:center;font-weight:300;" onmouseover="this.style.background='#e0e0e0';this.style.transform='rotate(90deg)';" onmouseout="this.style.background='#f4f4f4';this.style.transform='rotate(0deg)';">×</button>
            <div style="display:flex;align-items:center;justify-content:center;padding:60px;color:#717171;">
              <div style="text-align:center;">
                <div style="width:60px;height:60px;border:4px solid #1976d2;border-top-color:transparent;border-radius:50%;margin:0 auto 20px;animation:spin 1s linear infinite;"></div>
                <div style="font-size:16px;">Loading explanation...</div>
              </div>
            </div>
          </div>
        </div>`;

            document.body.insertAdjacentHTML("beforeend", loadingHtml);

            try {
              const response = await fetch(`/course-explanation/${courseCode}`);
              if (!response.ok) throw new Error("Failed to fetch explanation");

              const explanationData = await response.json();
              updateCourseExplanationModal(courseCode, explanationData);
            } catch (error) {
              console.error("Error:", error);
              const modal = document.getElementById("courseExplainModal");
              if (modal) {
                modal.innerHTML = `
            <div style="position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.5);z-index:10000;">
              <div style="background:#fff;border-radius:16px;max-width:500px;width:90%;padding:40px;text-align:center;">
                <div style="font-size:48px;margin-bottom:16px;">⚠️</div>
                <h3 style="color:#c62828;font-size:18px;margin-bottom:10px;">Unable to Load Explanation</h3>
                <p style="color:#666;margin-bottom:20px;">Sorry, we couldn't load the detailed explanation at this moment.</p>
                <button onclick="closeCourseExplain()" style="padding:10px 24px;background:#1976d2;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:14px;">Close</button>
              </div>
            </div>`;
              }
            }
          }

          function updateCourseExplanationModal(courseCode, explanationData) {
            const modal = document.getElementById("courseExplainModal");
            if (!modal) return;

            const explanation =
              explanationData.explanation || "Explanation not available.";
            const courseName = explanationData.course_name || courseCode;

            function formatText(text) {
              if (!text) return "";
              // Split into paragraphs and format
              return text
                .split("\n")
                .filter((line) => line.trim())
                .map((line, idx) => {
                  const trimmed = line.trim();
                  // Check if it's a heading (starts with **, ###, etc.)
                  if (trimmed.startsWith("**")) {
                    const cleanText = trimmed.replace(/\*\*/g, "");
                    return `<div style="font-weight:700;color:#1976d2;margin:16px 0 8px 0;font-size:15px;">${cleanText}</div>`;
                  }
                  if (trimmed.startsWith("###")) {
                    const cleanText = trimmed.replace(/#+\s*/g, "");
                    return `<div style="font-weight:600;color:#1976d2;margin:12px 0 6px 0;font-size:14px;">${cleanText}</div>`;
                  }
                  // Check if it's a bullet point
                  if (trimmed.startsWith("*") || trimmed.startsWith("-")) {
                    const text = trimmed.replace(/^[\*\-]\s*/, "");
                    return `<div style="margin-left:20px;margin-bottom:8px;line-height:1.6;"><span style="color:#1976d2;margin-right:8px;">•</span><span>${text}</span></div>`;
                  }
                  // Regular paragraph
                  if (trimmed.length > 0) {
                    return `<p style="margin:0 0 12px 0;line-height:1.8;text-align:justify;color:#333;">${trimmed}</p>`;
                  }
                  return "";
                })
                .join("");
            }

            const contentHtml = `
        <div style="position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.5);z-index:10000;backdrop-filter:blur(4px);">
          <div style="background:#fff;border-radius:16px;max-width:900px;width:95%;max-height:90vh;overflow:auto;padding:32px;box-shadow:0 12px 40px rgba(0,0,0,0.5);position:relative;scrollbar-width:none;-ms-overflow-style:none;">
            <style>#courseExplainModal > div::-webkit-scrollbar{display:none;}</style>
            <button aria-label="Close" onclick="closeCourseExplain()" style="position:absolute;right:16px;top:16px;border:none;background:#f4f4f4;border-radius:50%;width:40px;height:40px;cursor:pointer;font-size:24px;transition:all 0.2s;display:flex;align-items:center;justify-content:center;font-weight:300;" onmouseover="this.style.background='#e0e0e0';this.style.transform='rotate(90deg)';" onmouseout="this.style.background='#f4f4f4';this.style.transform='rotate(0deg)';">×</button>
            
            <div style="margin-bottom:24px;padding-bottom:20px;border-bottom:2px solid #e3f2fd;">
              <div style="color:#717171;font-size:13px;margin-bottom:6px;font-weight:500;text-transform:uppercase;letter-spacing:0.5px;">Course Explanation</div>
              <h2 style="margin:0 0 8px 0;color:#1976d2;font-size:28px;line-height:1.3;font-weight:700;">${courseName}</h2>
              <div style="display:flex;align-items:center;gap:8px;">
                <span style="background:#e3f2fd;color:#1976d2;padding:6px 14px;border-radius:20px;font-size:13px;font-weight:600;">${courseCode}</span>
                <span style="color:#888;font-size:13px;">📚 AI-Generated Explanation</span>
              </div>
            </div>
            
            <div style="line-height:1.8;color:#333;font-size:15px;">
              ${formatText(explanation)}
            </div>
            
            <div style="margin-top:32px;padding-top:20px;border-top:1px solid #e0e0e0;display:flex;gap:12px;justify-content:flex-end;">
              <button onclick="closeCourseExplain()" style="
                padding:12px 24px;border-radius:8px;border:1px solid #d0d0d0;background:#f5f5f5;color:#333;cursor:pointer;font-size:14px;font-weight:500;transition:all 0.2s;
              " onmouseover="this.style.background='#e0e0e0';" onmouseout="this.style.background='#f5f5f5';">Close</button>
              <button style="
                padding:12px 24px;border-radius:8px;border:none;background:#1976d2;color:#fff;cursor:pointer;font-size:14px;font-weight:500;transition:all 0.2s;
                box-shadow:0 4px 12px rgba(25,118,210,0.2);
              " onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 16px rgba(25,118,210,0.3)';" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 12px rgba(25,118,210,0.2)';">Copy Explanation</button>
            </div>
          </div>
        </div>`;

            modal.outerHTML = contentHtml;
          }

          function closeCourseExplain() {
            const m = document.getElementById("courseExplainModal");
            if (m) m.remove();
          }

          async function showCourseOutcomes(courseCode) {
            // Remove existing modal if present
            const existing = document.getElementById("courseOutcomesModal");
            if (existing) existing.remove();

            try {
              const response = await fetch(`/course-explanation/${courseCode}`);
              if (!response.ok) throw new Error("Failed to fetch");

              const data = await response.json();
              const outcomes = data.course_outcomes || [];

              const modalHtml = `
          <div id="courseOutcomesModal" style="position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.5);z-index:10000;backdrop-filter:blur(4px);">
            <div style="background:#fff;border-radius:16px;max-width:700px;width:90%;max-height:85vh;overflow:auto;padding:32px;box-shadow:0 12px 40px rgba(0,0,0,0.5);position:relative;scrollbar-width:none;-ms-overflow-style:none;">
              <style>#courseOutcomesModal > div::-webkit-scrollbar{display:none;}</style>
              <button aria-label="Close" onclick="closeCourseOutcomesModal()" style="position:absolute;right:16px;top:16px;border:none;background:#f4f4f4;border-radius:50%;width:40px;height:40px;cursor:pointer;font-size:24px;transition:all 0.2s;display:flex;align-items:center;justify-content:center;font-weight:300;" onmouseover="this.style.background='#e0e0e0';this.style.transform='rotate(90deg)';" onmouseout="this.style.background='#f4f4f4';this.style.transform='rotate(0deg)';">×</button>
              
              <div style="margin-bottom:24px;">
                <h2 style="margin:0 0 8px 0;color:#1976d2;font-size:24px;line-height:1.3;font-weight:700;display:flex;align-items:center;gap:10px;">
                  <span>🎯</span> Course Outcomes
                </h2>
                <div style="color:#717171;font-size:14px;">${
                  data.course_name
                } (${courseCode})</div>
              </div>
              
              <div style="line-height:1.8;color:#333;font-size:15px;">
                ${
                  outcomes.length > 0
                    ? `
                  <ul style="margin:0;padding-left:24px;list-style:none;">
                    ${outcomes
                      .map(
                        (outcome, idx) => `
                      <li style="margin-bottom:16px;position:relative;padding-left:8px;">
                        <span style="position:absolute;left:-24px;color:#1976d2;font-weight:700;">${
                          idx + 1
                        }.</span>
                        ${outcome}
                      </li>
                    `
                      )
                      .join("")}
                  </ul>
                `
                    : `
                  <div style="background:#f8f9fa;border:1px solid #e0e0e0;border-radius:10px;padding:20px;text-align:center;color:#717171;">
                    <p style="margin:0;font-size:16px;">📝</p>
                    <p style="margin:8px 0 0 0;">Course outcomes will be added soon</p>
                  </div>
                `
                }
              </div>
              
              <div style="margin-top:24px;padding-top:20px;border-top:1px solid #e0e0e0;display:flex;justify-content:flex-end;">
                <button onclick="closeCourseOutcomesModal()" style="padding:12px 24px;border-radius:8px;border:1px solid #d0d0d0;background:#f5f5f5;color:#333;cursor:pointer;font-size:14px;font-weight:500;transition:all 0.2s;" onmouseover="this.style.background='#e0e0e0';" onmouseout="this.style.background='#f5f5f5';">Close</button>
              </div>
            </div>
          </div>`;

              document.body.insertAdjacentHTML("beforeend", modalHtml);
            } catch (error) {
              console.error("Error loading course outcomes:", error);
            }
          }

          function closeCourseOutcomesModal() {
            const m = document.getElementById("courseOutcomesModal");
            if (m) m.remove();
          }

          async function showPrerequisites(courseCode) {
            // Remove existing modal if present
            const existing = document.getElementById("prerequisitesModal");
            if (existing) existing.remove();

            try {
              const response = await fetch(`/course-explanation/${courseCode}`);
              if (!response.ok) throw new Error("Failed to fetch");

              const data = await response.json();
              const prerequisites = data.prerequisites || [];

              const modalHtml = `
          <div id="prerequisitesModal" style="position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.5);z-index:10000;backdrop-filter:blur(4px);">
            <div style="background:#fff;border-radius:16px;max-width:700px;width:90%;max-height:85vh;overflow:auto;padding:32px;box-shadow:0 12px 40px rgba(0,0,0,0.5);position:relative;scrollbar-width:none;-ms-overflow-style:none;">
              <style>#prerequisitesModal > div::-webkit-scrollbar{display:none;}</style>
              <button aria-label="Close" onclick="closePrerequisitesModal()" style="position:absolute;right:16px;top:16px;border:none;background:#f4f4f4;border-radius:50%;width:40px;height:40px;cursor:pointer;font-size:24px;transition:all 0.2s;display:flex;align-items:center;justify-content:center;font-weight:300;" onmouseover="this.style.background='#e0e0e0';this.style.transform='rotate(90deg)';" onmouseout="this.style.background='#f4f4f4';this.style.transform='rotate(0deg)';">×</button>
              
              <div style="margin-bottom:24px;">
                <h2 style="margin:0 0 8px 0;color:#1976d2;font-size:24px;line-height:1.3;font-weight:700;display:flex;align-items:center;gap:10px;">
                  <span>📋</span> Prerequisites
                </h2>
                <div style="color:#717171;font-size:14px;">${
                  data.course_name
                } (${courseCode})</div>
              </div>
              
              <div style="line-height:1.8;color:#333;font-size:15px;">
                ${
                  prerequisites.length > 0
                    ? `
                  <ul style="margin:0;padding-left:24px;list-style:none;">
                    ${prerequisites
                      .map(
                        (prereq, idx) => `
                      <li style="margin-bottom:16px;position:relative;padding-left:8px;">
                        <span style="position:absolute;left:-24px;color:#1976d2;font-weight:700;">${
                          idx + 1
                        }.</span>
                        ${prereq}
                      </li>
                    `
                      )
                      .join("")}
                  </ul>
                `
                    : `
                  <div style="background:#f8f9fa;border:1px solid #e0e0e0;border-radius:10px;padding:20px;text-align:center;color:#717171;">
                    <p style="margin:0;font-size:16px;">📚</p>
                    <p style="margin:8px 0 0 0;">Prerequisites will be added soon</p>
                  </div>
                `
                }
              </div>
              
              <div style="margin-top:24px;padding-top:20px;border-top:1px solid #e0e0e0;display:flex;justify-content:flex-end;">
                <button onclick="closePrerequisitesModal()" style="padding:12px 24px;border-radius:8px;border:1px solid #d0d0d0;background:#f5f5f5;color:#333;cursor:pointer;font-size:14px;font-weight:500;transition:all 0.2s;" onmouseover="this.style.background='#e0e0e0';" onmouseout="this.style.background='#f5f5f5';">Close</button>
              </div>
            </div>
          </div>`;

              document.body.insertAdjacentHTML("beforeend", modalHtml);
            } catch (error) {
              console.error("Error loading prerequisites:", error);
            }
          }

          function closePrerequisitesModal() {
            const m = document.getElementById("prerequisitesModal");
            if (m) m.remove();
          }

          // Close modal on overlay click
          window.addEventListener("click", function (e) {
            const modal = document.getElementById("academicsModal");
            if (e.target === modal) {
              closeAcademicsModal();
            }
          });
          // Close modal with Escape key
          window.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
              const modal = document.getElementById("academicsModal");
              if (modal.style.display === "flex") {
                closeAcademicsModal();
              }
            }
          });

// ========== SCRIPT BLOCK ==========

// Show the next upcoming holiday inline on the welcome screen (no modal)
      document.addEventListener("DOMContentLoaded", function () {
        const el = document.getElementById("welcomeUpcomingHoliday");
        const cardContainer = document.getElementById(
          "welcomeUpcomingHolidayCard"
        );
        if (!el || !cardContainer) return;

        // Configurable timeout (milliseconds) to auto-hide the card after showing
        const WELCOME_HOLIDAY_TIMEOUT_MS = 8000;

        // Keep a reference to the hide timer so we can clear it if user interacts
        let hideTimer = null;

        // Helper: hide the card (with a short transition)
        function hideWelcomeHolidayCard() {
          if (!cardContainer) return;
          const cardEl = cardContainer.querySelector(".welcome-holiday-card");
          if (cardEl) {
            cardEl.classList.add("hidden");
            // wait for transition then remove content and hide container
            setTimeout(() => {
              cardContainer.innerHTML = "";
              cardContainer.style.display = "none";
            }, 300);
          } else {
            cardContainer.innerHTML = "";
            cardContainer.style.display = "none";
          }
          if (hideTimer) {
            clearTimeout(hideTimer);
            hideTimer = null;
          }
        }

        // Make parent clickable
        const parent = el.closest(".feature-item");
        if (parent) parent.style.cursor = "pointer";

        parent.addEventListener("click", async () => {
          // Clear any previous hide timer and reset
          if (hideTimer) {
            clearTimeout(hideTimer);
            hideTimer = null;
          }

          cardContainer.style.display = "block";
          cardContainer.innerHTML =
            '<div class="loading">Loading upcoming holiday…</div>';

          try {
            const res = await fetch("/holiday-data", { cache: "no-store" });
            if (!res.ok) throw new Error("Failed to fetch holiday data");
            const data = await res.json();

            // local flexible date parser (handles 'D Month YYYY' and ISO)
            function parseDateFlexible(dateStr) {
              if (!dateStr) return null;
              if (dateStr.includes(" to ")) {
                const start = dateStr.split(" to ")[0].trim();
                return parseDateFlexible(start);
              }
              const dm = dateStr.match(/^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$/);
              if (dm) {
                const day = parseInt(dm[1], 10);
                const monthName = dm[2];
                const year = parseInt(dm[3], 10);
                const months = {
                  January: 0,
                  February: 1,
                  March: 2,
                  April: 3,
                  May: 4,
                  June: 5,
                  July: 6,
                  August: 7,
                  September: 8,
                  October: 9,
                  November: 10,
                  December: 11,
                };
                const m =
                  months[monthName] ??
                  months[
                    monthName.charAt(0).toUpperCase() +
                      monthName.slice(1).toLowerCase()
                  ];
                if (m !== undefined) {
                  const d = new Date(year, m, day);
                  d.setHours(0, 0, 0, 0);
                  return d;
                }
              }
              const iso = dateStr.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
              if (iso) {
                const d = new Date(
                  parseInt(iso[1], 10),
                  parseInt(iso[2], 10) - 1,
                  parseInt(iso[3], 10)
                );
                d.setHours(0, 0, 0, 0);
                return d;
              }
              return null;
            }

            const today = new Date();
            today.setHours(0, 0, 0, 0);

            const mapped = (Array.isArray(data) ? data : [])
              .map((h) => ({ ...h, dateObj: parseDateFlexible(h.date) }))
              .filter((h) => h.dateObj && h.dateObj >= today)
              .sort((a, b) => a.dateObj - b.dateObj);

            if (!mapped || mapped.length === 0) {
              cardContainer.innerHTML =
                '<div style="color:#717171;padding:12px;border-radius:8px;background:#fff8f0;border:1px solid #ffe0b2">No upcoming holidays</div>';
              // auto-hide after a short delay
              hideTimer = setTimeout(hideWelcomeHolidayCard, 3000);
              return;
            }

            const next = mapped[0];
            cardContainer.innerHTML = `
            <div class="welcome-holiday-card" role="button" aria-label="Upcoming holiday: ${next.event}">
              <div class="welcome-holiday-icon">📅</div>
              <div class="welcome-holiday-body">
                <div class="welcome-holiday-title">${next.event}</div>
                <div class="welcome-holiday-date">${next.date}</div>
              </div>
              <button class="welcome-holiday-close" aria-label="Dismiss upcoming holiday">×</button>
            </div>
          `;

            // Add a brief highlight animation to draw attention
            const cardEl = cardContainer.querySelector(".welcome-holiday-card");
            const closeBtn = cardContainer.querySelector(
              ".welcome-holiday-close"
            );
            if (cardEl) {
              // trigger highlight class
              cardEl.classList.add("highlight");
              // remove highlight after animation duration so it doesn't persist
              setTimeout(() => cardEl.classList.remove("highlight"), 2200);

              // clear any existing hidden state
              cardEl.classList.remove("hidden");

              // clicking the card should open the full Holiday modal (optional)
              cardEl.addEventListener("click", (ev) => {
                // avoid clicks on the close button bubbling here
                if (
                  ev.target &&
                  ev.target.classList &&
                  ev.target.classList.contains("welcome-holiday-close")
                )
                  return;
                openHolidayModal();
              });
            }

            // Dismiss (close) button
            if (closeBtn) {
              closeBtn.addEventListener("click", (ev) => {
                ev.stopPropagation();
                hideWelcomeHolidayCard();
              });
            }

            // Auto-hide after configured timeout
            hideTimer = setTimeout(() => {
              hideWelcomeHolidayCard();
            }, WELCOME_HOLIDAY_TIMEOUT_MS);
          } catch (err) {
            console.error("Error loading upcoming holiday:", err);
            cardContainer.innerHTML =
              '<div style="color:#c62828;padding:12px">Failed to load upcoming holiday</div>';
            hideTimer = setTimeout(hideWelcomeHolidayCard, 3000);
          }
        });
      });

// ========== SCRIPT BLOCK ==========

// ========== EXISTING CHATBOT FUNCTIONALITY ==========

      // Theme toggle functionality
      function toggleTheme() {
        const body = document.body;
        const isDark = body.classList.toggle("dark-theme");
        localStorage.setItem("theme", isDark ? "dark" : "light");
      }

      // Load saved theme
      document.addEventListener("DOMContentLoaded", function () {
        const savedTheme = localStorage.getItem("theme");
        if (savedTheme === "dark") {
          document.body.classList.add("dark-theme");
        }
      });

      // Chat functionality
      function openChat() {
        document.getElementById("chatContainer").style.display = "flex";
        document.getElementById("chatFloatBtn").style.display = "none";
      }

      function closeChat() {
        document.getElementById("chatContainer").style.display = "none";
        document.getElementById("chatFloatBtn").style.display = "flex";
      }

      function startChatting() {
        document.getElementById("welcomeScreen").style.display = "none";
        document.getElementById("chatInterface").style.display = "flex";
      }

      function handleKeyPress(event) {
        if (event.key === "Enter") {
          sendMessage();
        }
      }

      function sendMessage() {
        const userInput = document.getElementById("userInput").value.trim();
        if (!userInput) return;

        // Add user message to chat
        addMessage(userInput, "user");
        document.getElementById("userInput").value = "";

        // Show typing indicator
        showTypingIndicator();

        // Call the chat API (include credentials so session cookie is sent)
        fetch("/chat", {
          method: "POST",
          credentials: 'same-origin',
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ query: userInput }),
        })
          .then((response) => response.json())
          .then((data) => {
            hideTypingIndicator();
            
            // Debug logging
            console.log("Chat response data:", data);
            console.log("Has scholarship link:", data.has_scholarship_link);
            console.log("Needs disambiguation:", data.needs_disambiguation);
            
            if (data.response) {
              // Check if disambiguation is needed
              if (data.needs_disambiguation && data.options) {
                console.log("Showing disambiguation options");
                addDisambiguationMessage(data.response, data.options);
              }
              // Check if this is a scholarship response with link
              else if (data.has_scholarship_link && data.scholarship_slug) {
                console.log("Calling addMessageWithScholarshipLink");
                addMessageWithScholarshipLink(data.response, data.scholarship_slug, data.scholarship_name);
              } else {
                console.log("Calling regular addMessage");
                addMessage(data.response, "bot");
              }
            } else if (data.error) {
              addMessage("Sorry, I encountered an error: " + data.error, "bot");
            } else {
              addMessage("Sorry, I could not process your request.", "bot");
            }
          })
          .catch((error) => {
            hideTypingIndicator();
            console.error("Error:", error);
            addMessage(
              "Sorry, I encountered a connection error. Please try again.",
              "bot"
            );
          });
      }

      function addMessage(message, sender) {
        const chatlog = document.getElementById("chatlog");
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${sender}`;

        const time = new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        });

        if (sender === "bot") {
          messageDiv.innerHTML = `
          <div class="message-avatar">
            <img src="/logo/Brainware_University.jpg" alt="Bot">
          </div>
          <div class="message-bubble">
            <div class="message-content">${message}</div>
            <div class="message-time">${time}</div>
            <div class="feedback-container" data-message-id="${Date.now()}-${Math.random().toString(36).slice(2,6)}">
              <button class="feedback-btn like-btn" title="Like">
                <img src="/sidebar/Like%20svg.svg" alt="Like">
              </button>
              <button class="feedback-btn dislike-btn" title="Dislike">
                <img src="/sidebar/Dislike%20svg.svg" alt="Dislike">
              </button>
            </div>
          </div>
        `;
        } else {
          messageDiv.innerHTML = `
          <div class="message-bubble">
            <div class="message-content">${message}</div>
            <div class="message-time">${time}</div>
          </div>
        `;
        }

        chatlog.appendChild(messageDiv);
        chatlog.scrollTop = chatlog.scrollHeight;

        // Attach feedback handlers (Like / Dislike)
        const fb = messageDiv.querySelector('.feedback-container');
        if (fb) {
          const mid = fb.dataset.messageId;
          const likeBtn = fb.querySelector('.like-btn');
          const dislikeBtn = fb.querySelector('.dislike-btn');

          // restore previous selection from localStorage (no counts shown)
          try {
            const prev = localStorage.getItem('feedback_' + mid);
            if (prev === 'like') {
              likeBtn.classList.add('active');
            } else if (prev === 'dislike') {
              dislikeBtn.classList.add('active');
            }
          } catch (e) {}

          likeBtn.addEventListener('click', () => {
            const isActive = likeBtn.classList.toggle('active');
            if (isActive) {
              dislikeBtn.classList.remove('active');
              try { localStorage.setItem('feedback_' + mid, 'like'); } catch (e) {}
            } else {
              try { localStorage.removeItem('feedback_' + mid); } catch (e) {}
            }
            likeBtn.classList.add('clicked');
            setTimeout(() => likeBtn.classList.remove('clicked'), 220);
          });

          dislikeBtn.addEventListener('click', () => {
            const isActive = dislikeBtn.classList.toggle('active');
            if (isActive) {
              likeBtn.classList.remove('active');
              try { localStorage.setItem('feedback_' + mid, 'dislike'); } catch (e) {}
            } else {
              try { localStorage.removeItem('feedback_' + mid); } catch (e) {}
            }
            dislikeBtn.classList.add('clicked');
            setTimeout(() => dislikeBtn.classList.remove('clicked'), 220);
          });
        }
      }

      function addMessageWithScholarshipLink(message, scholarshipSlug, scholarshipName) {
        const chatlog = document.getElementById("chatlog");
        const messageDiv = document.createElement("div");
        messageDiv.className = "message bot";

        const time = new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit"
        });

        // Extract intro text (everything before "Please go through")
        const parts = message.split("Please go through our scholarship portal for more details.");
        let introText = parts[0].trim();
        
        // Remove excessive whitespace and format properly
        introText = introText.replace(/\s+/g, ' ').trim();
        
        // Create scholarship link URL with highlight parameter
        const scholarshipUrl = `/scholarship?highlight=${scholarshipSlug}`;

        messageDiv.innerHTML = `
          <div class="message-avatar">
            <img src="/logo/Brainware_University.jpg" alt="Bot">
          </div>
          <div class="message-bubble">
            <div class="message-content">
              <h4 style="margin: 0 0 3px 0; color: #1976d2; font-size: 15px; font-weight: 600;">
                ${scholarshipName}
              </h4>
              <p style="margin: 0 0 3px 0; line-height: 1.5; color: #333;">${introText}</p>
              <p style="margin: 0 0 3px 0; font-size: 14px; color: #666;">Please go through our scholarship portal for more details.</p>
              <a href="${scholarshipUrl}" 
                 style="display: inline-flex; align-items: center; gap: 4px; 
                        color: #1976d2; text-decoration: none; font-weight: 500; 
                        font-size: 14px; padding: 3px 6px; background: #f0f7ff; 
                        border: 1px solid #d0e8f7; border-radius: 4px; transition: all 0.2s;"
                 onmouseover="this.style.background='#e3f2fd'; this.style.borderColor='#1976d2';"
                 onmouseout="this.style.background='#f0f7ff'; this.style.borderColor='#d0e8f7';"
                 target="_blank">
                View Details →
              </a>
            </div>
            <div class="message-time">${time}</div>
            <div class="feedback-container" data-message-id="${Date.now()}-${Math.random().toString(36).slice(2,6)}">
              <button class="feedback-btn like-btn" title="Like">
                <img src="/sidebar/Like%20svg.svg" alt="Like">
              </button>
              <button class="feedback-btn dislike-btn" title="Dislike">
                <img src="/sidebar/Dislike%20svg.svg" alt="Dislike">
              </button>
            </div>
          </div>
        `;

        chatlog.appendChild(messageDiv);
        chatlog.scrollTop = chatlog.scrollHeight;

        // Attach feedback handlers
        const fb = messageDiv.querySelector('.feedback-container');
        if (fb) {
          const mid = fb.dataset.messageId;
          const likeBtn = fb.querySelector('.like-btn');
          const dislikeBtn = fb.querySelector('.dislike-btn');

          try {
            const prev = localStorage.getItem('feedback_' + mid);
            if (prev === 'like') {
              likeBtn.classList.add('active');
            } else if (prev === 'dislike') {
              dislikeBtn.classList.add('active');
            }
          } catch (e) {}

          likeBtn.addEventListener('click', () => {
            const isActive = likeBtn.classList.toggle('active');
            if (isActive) {
              dislikeBtn.classList.remove('active');
              try { localStorage.setItem('feedback_' + mid, 'like'); } catch (e) {}
            } else {
              try { localStorage.removeItem('feedback_' + mid); } catch (e) {}
            }
            likeBtn.classList.add('clicked');
            setTimeout(() => likeBtn.classList.remove('clicked'), 220);
          });

          dislikeBtn.addEventListener('click', () => {
            const isActive = dislikeBtn.classList.toggle('active');
            if (isActive) {
              likeBtn.classList.remove('active');
              try { localStorage.setItem('feedback_' + mid, 'dislike'); } catch (e) {}
            } else {
              try { localStorage.removeItem('feedback_' + mid); } catch (e) {}
            }
            dislikeBtn.classList.add('clicked');
            setTimeout(() => dislikeBtn.classList.remove('clicked'), 220);
          });
        }
      }

      function addDisambiguationMessage(message, options) {
        const chatlog = document.getElementById("chatlog");
        const messageDiv = document.createElement("div");
        messageDiv.className = "message bot";

        const time = new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        });

        // Build options HTML with modern styling
        let optionsHTML = options.map((opt, index) => `
          <button 
            class="scholarship-option-btn" 
            data-slug="${opt.slug}"
            data-name="${opt.name}"
            onclick="selectScholarship('${opt.slug}', '${opt.name.replace(/'/g, "\\'")}')"
            style="display: flex; align-items: center; width: 100%; text-align: left; 
                   padding: 10px 12px; margin-bottom: 3px; 
                   background: ${index % 2 === 0 ? '#ffffff' : '#f8fafc'}; 
                   border: 1px solid #e2e8f0; border-radius: 6px;
                   cursor: pointer; font-size: 14px; font-weight: 500; 
                   color: #334155; transition: all 0.2s ease;
                   gap: 10px;"
            onmouseover="this.style.background='#e0f2fe'; this.style.color='#0369a1'; this.style.paddingLeft='16px';"
            onmouseout="this.style.background='${index % 2 === 0 ? '#ffffff' : '#f8fafc'}'; this.style.color='#334155'; this.style.paddingLeft='12px';">
            <span style="display: inline-flex; align-items: center; justify-content: center; 
                         width: 22px; height: 22px; background: linear-gradient(135deg, #3b82f6, #1d4ed8); 
                         color: white; border-radius: 50%; font-size: 12px; font-weight: 600;
                         flex-shrink: 0;">${opt.number}</span>
            <span style="flex: 1;">${opt.name}</span>
            <span style="color: #94a3b8; font-size: 16px;">›</span>
          </button>
        `).join('');

        messageDiv.innerHTML = `
          <div class="message-avatar">
            <img src="/logo/Brainware_University.jpg" alt="Bot">
          </div>
          <div class="message-bubble">
            <div class="message-content">
              ${message}
              <div style="margin-top: 10px;">
                ${optionsHTML}
              </div>
            </div>
            <div class="message-time">${time}</div>
          </div>
        `;

        chatlog.appendChild(messageDiv);
        chatlog.scrollTop = chatlog.scrollHeight;
      }

      function selectScholarship(slug, name) {
        console.log("Selected scholarship:", slug, name);
        
        // Add user's selection to chat
        addMessage(name, "user");
        
        // Show typing indicator
        showTypingIndicator();
        
        // Fetch scholarship details by slug
        fetch("/scholarship-by-slug", {
          method: "POST",
          credentials: 'same-origin',
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ slug: slug }),
        })
          .then((response) => response.json())
          .then((data) => {
            hideTypingIndicator();
            if (data.has_scholarship_link && data.scholarship_slug) {
              addMessageWithScholarshipLink(data.response, data.scholarship_slug, data.scholarship_name);
            } else if (data.error) {
              addMessage("Sorry, I couldn't find that scholarship.", "bot");
            }
          })
          .catch((error) => {
            hideTypingIndicator();
            console.error("Error:", error);
            addMessage("Sorry, I encountered an error. Please try again.", "bot");
          });
      }

      function showTypingIndicator() {
        document.getElementById("typingContainer").style.display = "block";
        const chatlog = document.getElementById("chatlog");
        chatlog.scrollTop = chatlog.scrollHeight;
      }

      function hideTypingIndicator() {
        document.getElementById("typingContainer").style.display = "none";
      }

      function processMessage(message) {
        const lowerMessage = message.toLowerCase();

        if (lowerMessage.includes("hello") || lowerMessage.includes("hi")) {
          return "Hello! I'm BWU UniBot. How can I help you today?";
        } else if (lowerMessage.includes("academic")) {
          return "I can help you with academic information. What specific academic details do you need?";
        } else if (lowerMessage.includes("faculty")) {
          return "I can provide information about our faculty members. Would you like to search for a specific faculty member?";
        } else if (lowerMessage.includes("exam")) {
          return "I can help you with exam schedules and information. What exam details do you need?";
        } else if (lowerMessage.includes("holiday")) {
          return "I can show you upcoming holidays and help you check holiday dates. Would you like to see the holiday calendar?";
        } else {
          return "I'm here to help! You can ask me about Academic info, Faculty details, Exam schedules, or Holiday information. Use the quick action buttons above for easy access.";
        }
      }

      function selectCategory(category) {
        // Remove active state from all buttons
        document.querySelectorAll(".quick-action-btn").forEach((btn) => {
          btn.classList.remove("active");
        });

        // Determine clicked button
        const clickedBtn = document.querySelector(
          `[data-category="${category}"]`
        );

        // Only keep `.active` for categories that should remain highlighted
        // (e.g., Academic and Faculty). Exams and Holiday will not get any
        // persistent or transient styling — they immediately open the modal
        // and return to normal state, matching Academics/Faculty behavior.
        if (clickedBtn) {
          if (category === "Academic" || category === "Faculty") {
            clickedBtn.classList.add("active");
          }
        }

        // Handle category selection
        switch (category) {
          case "Academic":
            addMessage(
              "I can help you with academic information. What specific academic details do you need?",
              "bot"
            );
            break;
          case "Faculty":
            openFacultyModal();
            break;
          case "Examination":
            openExamModal();
            break;
          case "Holiday":
            openHolidayModal();
            break;
        }
      }

      // Faculty Modal Functions
      function openFacultyModal() {
        document.getElementById("facultyModal").style.display = "flex";
        loadFacultyData();
      }

      function closeFacultyModal() {
        document.getElementById("facultyModal").style.display = "none";
      }

      function loadFacultyData() {
        const resultsContainer = document.getElementById("facultyResults");
        resultsContainer.innerHTML =
          '<div class="faculty-loading">Loading faculty data...</div>';

        fetch("/faculty-data")
          .then((response) => response.json())
          .then((data) => {
            displayFacultyResults(data);
          })
          .catch((error) => {
            resultsContainer.innerHTML =
              '<div class="faculty-error">Error loading faculty data</div>';
          });
      }

      function displayFacultyResults(faculty) {
        const resultsContainer = document.getElementById("facultyResults");

        if (!faculty || faculty.length === 0) {
          resultsContainer.innerHTML =
            '<div class="faculty-no-results">No faculty members found</div>';
          return;
        }

        const html = faculty
          .map(
            (member) => `
        <div class="faculty-card">
          <div class="faculty-info">
            <h3 class="faculty-name">${member.name}</h3>
            <p class="faculty-position">${member.position}</p>
            <p class="faculty-department">${member.department}</p>
            ${
              member.email ? `<p class="faculty-email">${member.email}</p>` : ""
            }
            ${
              member.research
                ? `<p class="faculty-research">Research: ${member.research}</p>`
                : ""
            }
          </div>
        </div>
      `
          )
          .join("");

        resultsContainer.innerHTML = html;
      }

      function searchFaculty() {
        const searchTerm = document
          .getElementById("facultySearchInput")
          .value.toLowerCase();

        fetch("/faculty-data")
          .then((response) => response.json())
          .then((data) => {
            const filtered = data.filter(
              (member) =>
                member.name.toLowerCase().includes(searchTerm) ||
                member.position.toLowerCase().includes(searchTerm) ||
                member.department.toLowerCase().includes(searchTerm) ||
                (member.research &&
                  member.research.toLowerCase().includes(searchTerm))
            );
            displayFacultyResults(filtered);
          });
      }

      // Announcements Modal Functions
      function openAnnouncementsModal() {
        document.getElementById("announcementsModal").style.display = "flex";
        loadAnnouncements();
      }

      function closeAnnouncementsModal() {
        document.getElementById("announcementsModal").style.display = "none";
      }

      function loadAnnouncements() {
        const container = document.getElementById("announcementsContainer");
        container.innerHTML =
          '<div class="loading">Loading announcements…</div>';

        fetch("/api/announcements/active")
          .then((response) => response.json())
          .then((result) => {
            if (result.success && result.data && result.data.length > 0) {
              displayAnnouncements(result.data);
            } else {
              container.innerHTML = `
              <div style="text-align:center;padding:40px 20px;color:#717171;">
                <div style="font-size:48px;margin-bottom:16px;">📢</div>
                <h3 style="font-size:18px;color:#333;margin-bottom:8px;">No Announcements Yet</h3>
                <p style="margin:0;font-size:14px;">Check back later for updates from the administration.</p>
              </div>`;
            }
          })
          .catch((error) => {
            console.error("Error loading announcements:", error);
            container.innerHTML = `
            <div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:16px;color:#856404;">
              <strong>⚠️ Unable to load announcements</strong>
              <p style="margin:8px 0 0 0;font-size:14px;">Please try again later or contact support if the issue persists.</p>
            </div>`;
          });
      }

      function displayAnnouncements(announcements) {
        const container = document.getElementById("announcementsContainer");

        const html = announcements
          .map((announcement) => {
            const publishedDate = new Date(announcement.published_at);
            const formattedDate = publishedDate.toLocaleDateString("en-US", {
              year: "numeric",
              month: "short",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            });

            const now = new Date();
            const diffTime = Math.abs(now - publishedDate);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            const isNew = diffDays <= 3;

            return `
          <div class="result-card" style="background:#fff;border:1px solid #e0e0e0;padding:18px;border-radius:10px;margin-bottom:14px;border-left:4px solid #1976d2;">
            <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:10px;">
              <h3 style="margin:0;font-size:17px;font-weight:600;color:#1976d2;display:flex;align-items:center;gap:8px;">
                ${announcement.title}
                ${
                  isNew
                    ? '<span style="background:#ff385c;color:#fff;font-size:10px;padding:2px 8px;border-radius:12px;font-weight:600;">NEW</span>'
                    : ""
                }
              </h3>
              <span style="font-size:12px;color:#717171;white-space:nowrap;margin-left:12px;">${formattedDate}</span>
            </div>
            <div style="color:#333;font-size:14px;line-height:1.7;margin-bottom:10px;">
              ${announcement.body.replace(/\n/g, "<br>")}
            </div>
            ${
              announcement.attachments && announcement.attachments.length > 0
                ? `
              <div style="margin-top:12px;padding-top:12px;border-top:1px solid #f0f0f0;">
                <div style="font-size:12px;color:#717171;margin-bottom:6px;font-weight:600;">📎 Attachments:</div>
                ${announcement.attachments
                  .map(
                    (att) => `
                  <a href="${att}" target="_blank" style="display:inline-block;color:#1976d2;text-decoration:none;font-size:13px;margin-right:12px;margin-bottom:4px;" onmouseover="this.style.textDecoration='underline'" onmouseout="this.style.textDecoration='none'">
                    📄 ${att.split("/").pop()}
                  </a>
                `
                  )
                  .join("")}
              </div>
            `
                : ""
            }
          </div>
        `;
          })
          .join("");

        container.innerHTML = html;
      }

      // Exam Modal Functions
      let examData = null;
      let selectedExamSemester = null;

      async function loadExamData() {
        if (examData) return examData;
        try {
          const response = await fetch("/exam-data");
          if (!response.ok) throw new Error("Failed to load exam data");
          examData = await response.json();
          return examData;
        } catch (error) {
          console.error("Error loading exam data:", error);
          return null;
        }
      }

      async function openExamModal() {
        const modal = document.getElementById("examModal");
        modal.style.display = "flex";

        // Load exam data
        await loadExamData();

        // Reset selection
        const cards = document.querySelectorAll(".exam-select-card");
        cards.forEach((c) => c.setAttribute("aria-pressed", "false"));
        document.getElementById("examEventsContainer").style.display = "none";
      }

      function closeExamModal() {
        document.getElementById("examModal").style.display = "none";
      }

      async function selectSemester(semester) {
        selectedExamSemester = semester;

        // Update card selection
        const cards = document.querySelectorAll(".exam-select-card");
        cards.forEach((card) => {
          if (card.dataset.semester === semester) {
            card.setAttribute("aria-pressed", "true");
            card.style.borderColor = "#1976d2";
            card.style.background = "#f0f7ff";
          } else {
            card.setAttribute("aria-pressed", "false");
            card.style.borderColor = "";
            card.style.background = "";
          }
        });

        // Load and display events
        await displayExamEvents(semester);
      }

      async function displayExamEvents(semester) {
        const container = document.getElementById("examEventsContainer");
        const eventsList = document.getElementById("examEventsList");

        container.style.display = "block";
        eventsList.innerHTML =
          '<div class="loading">Loading exam schedule...</div>';

        const data = await loadExamData();
        if (!data || !data.academic_calendar_2025_26) {
          eventsList.innerHTML =
            '<p style="text-align:center;color:#c62828;">Failed to load exam data</p>';
          return;
        }

        const semesterKey =
          semester === "odd" ? "odd_semester" : "even_semester";
        const events = data.academic_calendar_2025_26[semesterKey];

        if (!events || events.length === 0) {
          eventsList.innerHTML =
            '<p style="text-align:center;color:#717171;">No events found</p>';
          return;
        }

        // Parse and categorize events
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const categorizedEvents = {
          "Class Tests": [],
          Examinations: [],
          "Form Fill-up": [],
          "Other Events": [],
        };

        events.forEach((event) => {
          const eventLower = event.event.toLowerCase();
          if (eventLower.includes("class test")) {
            categorizedEvents["Class Tests"].push(event);
          } else if (
            eventLower.includes("examination") ||
            eventLower.includes("exam")
          ) {
            categorizedEvents["Examinations"].push(event);
          } else if (eventLower.includes("form fill-up")) {
            categorizedEvents["Form Fill-up"].push(event);
          } else {
            categorizedEvents["Other Events"].push(event);
          }
        });

        let html = "";

        // Display categorized events
        const eventTypeIcon = {
          'Class Tests': '📝',
          'Examinations': '📚',
          'Form Fill-up': '🗂️',
          'Other Events': '📅'
        };
        const eventTypeColor = {
          'Class Tests': '#ffe082',
          'Examinations': '#b3e5fc',
          'Form Fill-up': '#c8e6c9',
          'Other Events': '#f3e5f5'
        };
        const eventTypeBorder = {
          'Class Tests': '#ffb300',
          'Examinations': '#0288d1',
          'Form Fill-up': '#388e3c',
          'Other Events': '#8e24aa'
        };
        Object.keys(categorizedEvents).forEach((category) => {
          if (categorizedEvents[category].length > 0) {
            html += `<div style="margin-bottom:28px;">
                    <h4 style="font-size:15px;font-weight:800;color:${eventTypeBorder[category]};text-transform:uppercase;letter-spacing:0.5px;margin-bottom:14px;display:flex;align-items:center;gap:8px;"><span style='font-size:20px;'>${eventTypeIcon[category]}</span> ${category}</h4>`;

            categorizedEvents[category].forEach((event, idx) => {
              html += `
              <div style="
                background:${eventTypeColor[category]};
                border:1.5px solid ${eventTypeBorder[category]};
                border-left:5px solid ${eventTypeBorder[category]};
                border-radius:10px;
                padding:18px 18px 14px 18px;
                margin-bottom:10px;
                transition:all 0.2s;
                box-shadow:0 2px 8px rgba(25,118,210,0.06);
                position:relative;
              " onmouseover="this.style.transform='translateX(4px)';this.style.boxShadow='0 4px 16px rgba(25,118,210,0.10)';" onmouseout="this.style.transform='translateX(0)';this.style.boxShadow='0 2px 8px rgba(25,118,210,0.06)';">
                <div style="display:flex;align-items:start;gap:14px;">
                  <div style="font-size:26px;line-height:1;">${eventTypeIcon[category]}</div>
                  <div style="flex:1;">
                    <div style="font-weight:700;color:#22223b;font-size:16px;margin-bottom:7px;letter-spacing:0.1px;">${escapeHtml(event.event)}</div>
                    <div style="display:flex;align-items:center;gap:8px;color:#374151;font-size:14px;">
                      <span style='font-size:16px;'>🗓️</span>
                      <span>${escapeHtml(event.date)}</span>
                    </div>
                  </div>
                </div>
                ${idx < categorizedEvents[category].length-1 ? '<hr style="border:none;border-top:1px dashed #bdbdbd;margin:14px 0 0 0;">' : ''}
              </div>`;
            });

            html += `</div>`;
          }
        });

        eventsList.innerHTML = html;
      }

      function showToast(message) {
        const toast = document.getElementById("examToast");
        if (!toast) return;
        toast.textContent = message;
        toast.style.display = "block";

        setTimeout(() => {
          toast.style.display = "none";
        }, 3000);
      }

      // ========== HOLIDAY FUNCTIONALITY ==========

      // Holiday-specific global state
      let holidayData = [];
      let calendarCurrentMonth = new Date().getMonth();
      let calendarCurrentYear = new Date().getFullYear();
      let selectedStartDate = null;
      let selectedEndDate = null;
      let selectedSingleDate = null; // Track selected date in single mode
      let autoRefreshTimer = null;

      // Utility functions for holiday system
      function parseDateFlexible(dateStr) {
        if (!dateStr) return null;
        if (dateStr.includes(" to ")) {
          const start = dateStr.split(" to ")[0].trim();
          return parseDateFlexible(start);
        }

        // "D Month YYYY" (e.g., 6 July 2025)
        const dm = dateStr.match(/^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$/);
        if (dm) {
          const day = parseInt(dm[1], 10);
          const monthName = dm[2];
          const year = parseInt(dm[3], 10);
          const months = {
            January: 0,
            February: 1,
            March: 2,
            April: 3,
            May: 4,
            June: 5,
            July: 6,
            August: 7,
            September: 8,
            October: 9,
            November: 10,
            December: 11,
          };
          const m =
            months[monthName] ??
            months[
              monthName.charAt(0).toUpperCase() +
                monthName.slice(1).toLowerCase()
            ];
          if (m !== undefined) {
            const d = new Date(year, m, day);
            d.setHours(0, 0, 0, 0);
            return d;
          }
        }

        // ISO YYYY-MM-DD
        const iso = dateStr.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
        if (iso) {
          const d = new Date(
            parseInt(iso[1], 10),
            parseInt(iso[2], 10) - 1,
            parseInt(iso[3], 10)
          );
          d.setHours(0, 0, 0, 0);
          return d;
        }

        return null;
      }

      function escapeHtml(text) {
        if (!text) return "";
        return String(text).replace(
          /[&<>"']/g,
          (s) =>
            ({
              "&": "&amp;",
              "<": "&lt;",
              ">": "&gt;",
              '"': "&quot;",
              "'": "&#039;",
            }[s])
        );
      }

      function formatDisplayDate(d) {
        if (!d) return "";
        const months = [
          "Jan",
          "Feb",
          "Mar",
          "Apr",
          "May",
          "Jun",
          "Jul",
          "Aug",
          "Sep",
          "Oct",
          "Nov",
          "Dec",
        ];
        return d.getDate() + " " + months[d.getMonth()] + " " + d.getFullYear();
      }

      function daysBetween(a, b) {
        const one = 24 * 60 * 60 * 1000;
        return Math.round((b - a) / one);
      }

      // Load holiday data from backend
      async function fetchHolidayData() {
        try {
          const res = await fetch("/holiday-data", { cache: "no-store" });
          if (!res.ok) throw new Error("HTTP " + res.status);
          const data = await res.json();
          if (!Array.isArray(data))
            throw new Error("Unexpected data shape from /holiday-data");
          return data;
        } catch (err) {
          console.error("Failed to fetch holiday-data:", err);
          return null;
        }
      }

      // Holiday modal functions
      function openHolidayModal() {
        const modal = document.getElementById("holidayModal");
        modal.style.display = "flex";
        displayUpcomingHolidays();
      }

      async function displayUpcomingHolidays() {
        const container = document.getElementById("upcomingHolidaysContainer");
        container.innerHTML = '<div class="loading">Loading holidays…</div>';

        const data = await fetchHolidayData();
        if (!data) {
          container.innerHTML =
            '<div style="color:#c62828;text-align:center;">Error loading holidays</div>';
          return;
        }

        holidayData = data;
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        console.log("=== HOLIDAY DEBUG ===");
        console.log("Today:", today.toISOString(), today);
        console.log("Holiday data count:", data.length);

        const mapped = data
          .map((h) => {
            const d = parseDateFlexible(h.date);
            console.log(`Parse "${h.date}" => ${d ? d.toISOString() : "null"}`);
            return { ...h, dateObj: d };
          })
          .filter((h) => {
            const keep = h.dateObj && h.dateObj >= today;
            console.log(
              `Filter "${h.date}": ${h.dateObj} >= ${today}? ${keep}`
            );
            return keep;
          })
          .sort((a, b) => a.dateObj - b.dateObj)
          .slice(0, 5);

        console.log("Mapped upcoming holidays:", mapped);

        if (mapped.length === 0) {
          container.innerHTML =
            '<p style="text-align:center;color:#717171;">No upcoming holidays</p>';
          return;
        }

        container.innerHTML = mapped
          .map((h) => {
            const daysUntil = daysBetween(today, h.dateObj);
            const daysText =
              daysUntil === 0
                ? "Today"
                : daysUntil === 1
                ? "Tomorrow"
                : `in ${daysUntil} days`;
            return `<div class="holiday-card">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <strong>${escapeHtml(h.event)}</strong>
                    <span style="color:#717171">${daysText}</span>
                  </div>
                  <div style="color:#717171;margin-top:6px">${escapeHtml(
                    h.date
                  )}</div>
                </div>`;
          })
          .join("");

        renderSingleDateCalendar();
        renderDateRangeCalendar();
      }

      // Calendar rendering functions
      function generateCalendarHTML(
        mode,
        currentMonth = calendarCurrentMonth,
        currentYear = calendarCurrentYear
      ) {
        const firstDay = new Date(currentYear, currentMonth, 1);
        const lastDay = new Date(currentYear, currentMonth + 1, 0);
        const prevLast = new Date(currentYear, currentMonth, 0);
        const firstIndex = firstDay.getDay();
        const lastDate = lastDay.getDate();
        const prevLastDate = prevLast.getDate();
        const months = [
          "January",
          "February",
          "March",
          "April",
          "May",
          "June",
          "July",
          "August",
          "September",
          "October",
          "November",
          "December",
        ];

        let html = `<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
                    <button class="calendar-nav-btn" onclick="changeCalendarMonth(-1,'${mode}')">‹</button>
                    <div style="font-weight:600">${months[currentMonth]} ${currentYear}</div>
                    <button class="calendar-nav-btn" onclick="changeCalendarMonth(1,'${mode}')">›</button>
                  </div>
                  <div class="calendar-grid">
                    <div class="calendar-day-header">Su</div><div class="calendar-day-header">Mo</div><div class="calendar-day-header">Tu</div>
                    <div class="calendar-day-header">We</div><div class="calendar-day-header">Th</div><div class="calendar-day-header">Fr</div><div class="calendar-day-header">Sa</div>`;

        // Previous month days
        for (let i = firstIndex; i > 0; i--) {
          html += `<div class="calendar-day other-month">${
            prevLastDate - i + 1
          }</div>`;
        }

        // Current month days
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        for (let d = 1; d <= lastDate; d++) {
          const dt = new Date(currentYear, currentMonth, d);
          dt.setHours(0, 0, 0, 0);
          const classes = ["calendar-day"];

          if (dt.getTime() === today.getTime()) classes.push("today");

          // Check if it's a holiday
          let isHoliday = false;
          for (const h of holidayData || []) {
            const hd = parseDateFlexible(h.date);
            if (!hd) continue;
            if (h.date.includes(" to ")) {
              const parts = h.date.split(" to ");
              const start = parseDateFlexible(parts[0].trim());
              const end = parseDateFlexible(parts[1].trim());
              if (start && end && dt >= start && dt <= end) {
                isHoliday = true;
                break;
              }
            } else {
              if (hd.getTime() === dt.getTime()) {
                isHoliday = true;
                break;
              }
            }
          }
          if (isHoliday) classes.push("holiday");

          // Single date selection state
          if (mode === "single") {
            if (
              selectedSingleDate &&
              dt.getTime() === selectedSingleDate.getTime()
            ) {
              classes.push("selected-single");
            }
          }

          // Range selection state
          if (mode === "range") {
            if (
              selectedStartDate &&
              dt.getTime() === selectedStartDate.getTime()
            )
              classes.push("range-start");
            else if (
              selectedEndDate &&
              dt.getTime() === selectedEndDate.getTime()
            )
              classes.push("range-end");
            else if (
              selectedStartDate &&
              selectedEndDate &&
              dt > selectedStartDate &&
              dt < selectedEndDate
            )
              classes.push("in-range");
          }

          const onclick =
            mode === "single"
              ? `selectSingleCalendarDate(${currentYear},${currentMonth},${d})`
              : `selectRangeCalendarDate(${currentYear},${currentMonth},${d})`;
          html += `<div class="${classes.join(
            " "
          )}" onclick="${onclick}" role="button" tabindex="0">${d}</div>`;
        }

        // Next month padding
        const used = firstIndex + lastDate;
        for (let i = 1; i <= 42 - used; i++) {
          html += `<div class="calendar-day other-month">${i}</div>`;
        }
        html += `</div>`;
        return html;
      }

      function renderSingleDateCalendar() {
        const cont = document.getElementById("singleDateCalendar");
        if (!cont) return;
        try {
          // Add smooth fade transition
          cont.style.opacity = "0.7";
          setTimeout(() => {
            cont.innerHTML = generateCalendarHTML("single");
            cont.style.opacity = "1";
          }, 100);
        } catch (e) {
          cont.innerHTML =
            '<div class="loading" style="color:#c62828">Error loading calendar</div>';
        }
      }

      function renderDateRangeCalendar() {
        const cont = document.getElementById("dateRangeCalendar");
        if (!cont) return;
        try {
          // Add smooth fade transition
          cont.style.opacity = "0.7";
          setTimeout(() => {
            cont.innerHTML = generateCalendarHTML("range");
            cont.style.opacity = "1";
          }, 100);
        } catch (e) {
          cont.innerHTML =
            '<div class="loading" style="color:#c62828">Error loading calendar</div>';
        }
      }

      function changeCalendarMonth(delta, mode) {
        if (mode === "single" || mode === "range") {
          calendarCurrentMonth += delta;
          if (calendarCurrentMonth > 11) {
            calendarCurrentMonth = 0;
            calendarCurrentYear++;
          }
          if (calendarCurrentMonth < 0) {
            calendarCurrentMonth = 11;
            calendarCurrentYear--;
          }
          if (mode === "single") renderSingleDateCalendar();
          else renderDateRangeCalendar();
        }
      }

      // Date selection functions
      function selectSingleCalendarDate(y, m, d) {
        const sel = new Date(y, m, d);
        sel.setHours(0, 0, 0, 0);

        // Store the selected date for highlighting
        selectedSingleDate = sel;

        const found = (holidayData || []).find((h) => {
          if (!h.date) return false;
          if (h.date.includes(" to ")) {
            const parts = h.date.split(" to ");
            const s = parseDateFlexible(parts[0].trim());
            const e = parseDateFlexible(parts[1].trim());
            return s && e && sel >= s && sel <= e;
          } else {
            const hd = parseDateFlexible(h.date);
            return hd && hd.getTime() === sel.getTime();
          }
        });

        const resultContainer = document.getElementById("singleDateResult");
        if (found) {
          resultContainer.innerHTML = `<div class="result-card success">
          <div style="font-weight:700;color:#00A86B;font-size:18px">✓</div>
          <div>
            <div style="font-weight:600">${escapeHtml(found.event)}</div>
            <div style="color:#717171">${escapeHtml(found.date)} — ${escapeHtml(
            found.day || ""
          )}</div>
          </div>
        </div>`;
        } else {
          const future = (holidayData || [])
            .map((h) => ({ ...h, dateObj: parseDateFlexible(h.date) }))
            .filter((h) => h.dateObj && h.dateObj > sel)
            .sort((a, b) => a.dateObj - b.dateObj)[0];
          const nextText = future
            ? `<div style="margin-top:8px;color:#717171">Next holiday: ${escapeHtml(
                future.event
              )} (${formatDisplayDate(future.dateObj)})</div>`
            : "";
          resultContainer.innerHTML = `<div class="result-card warning">
          <div style="font-weight:700;color:#FFA500;font-size:18px">✗</div>
          <div>
            <div style="font-weight:600">Not a Holiday</div>
            <div style="color:#717171">${formatDisplayDate(
              sel
            )} is not a holiday</div>
            ${nextText}
          </div>
        </div>`;
        }
        renderSingleDateCalendar();
      }

      function selectRangeCalendarDate(y, m, d) {
        const clicked = new Date(y, m, d);
        clicked.setHours(0, 0, 0, 0);

        if (!selectedStartDate || (selectedStartDate && selectedEndDate)) {
          selectedStartDate = clicked;
          selectedEndDate = null;
          document.getElementById("startDateDisplay").textContent =
            formatDisplayDate(clicked);
          document.getElementById("endDateDisplay").textContent =
            "Not selected";
          document.getElementById("checkRangeBtn").disabled = true;
          document.getElementById("dateRangeResult").innerHTML = "";
          renderDateRangeCalendar();
        } else if (clicked > selectedStartDate) {
          selectedEndDate = clicked;
          document.getElementById("endDateDisplay").textContent =
            formatDisplayDate(clicked);
          document.getElementById("checkRangeBtn").disabled = false;

          // Animate the range selection with a smooth expanding effect
          animateRangeSelection(selectedStartDate, selectedEndDate);
        } else {
          selectedStartDate = clicked;
          selectedEndDate = null;
          document.getElementById("startDateDisplay").textContent =
            formatDisplayDate(clicked);
          document.getElementById("endDateDisplay").textContent =
            "Not selected";
          document.getElementById("checkRangeBtn").disabled = true;
          document.getElementById("dateRangeResult").innerHTML = "";
          renderDateRangeCalendar();
        }
      }

      // Animate range selection with smooth expanding effect
      function animateRangeSelection(startDate, endDate) {
        // First render without animation
        renderDateRangeCalendar();

        // Get all calendar days in range
        const calendarDays = document.querySelectorAll(
          "#dateRangeCalendar .calendar-day.in-range"
        );

        // Remove animation classes first
        calendarDays.forEach((day) => {
          day.style.animation = "none";
        });

        // Force reflow
        void document.offsetHeight;

        // Add animated range expansion with staggered delay
        calendarDays.forEach((day, index) => {
          setTimeout(() => {
            day.style.animation = `rangeExpand 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards`;
          }, index * 40); // 40ms delay between each day
        });
      }

      // Initialize holiday functionality when DOM is loaded
      document.addEventListener("DOMContentLoaded", function () {
        // Tab switching
        document
          .getElementById("singleDateTab")
          ?.addEventListener("click", function () {
            document.getElementById("singleDateTab").classList.add("active");
            document.getElementById("dateRangeTab").classList.remove("active");
            document.getElementById("singleDateCheckForm").style.display =
              "block";
            document.getElementById("dateRangeCheckForm").style.display =
              "none";

            // Clear range selection when switching to single mode
            selectedStartDate = null;
            selectedEndDate = null;
            document.getElementById("startDateDisplay").textContent =
              "Not selected";
            document.getElementById("endDateDisplay").textContent =
              "Not selected";
            document.getElementById("checkRangeBtn").disabled = true;
            document.getElementById("dateRangeResult").innerHTML = "";

            renderSingleDateCalendar();
          });

        document
          .getElementById("dateRangeTab")
          ?.addEventListener("click", function () {
            document.getElementById("dateRangeTab").classList.add("active");
            document.getElementById("singleDateTab").classList.remove("active");
            document.getElementById("dateRangeCheckForm").style.display =
              "block";
            document.getElementById("singleDateCheckForm").style.display =
              "none";

            // Clear single date selection when switching to range mode
            selectedSingleDate = null;
            document.getElementById("singleDateResult").innerHTML = "";

            renderDateRangeCalendar();
          });

        // Range check button
        document
          .getElementById("checkRangeBtn")
          ?.addEventListener("click", function () {
            if (!selectedStartDate || !selectedEndDate) return;

            const found = (holidayData || [])
              .filter((h) => {
                if (!h.date) return false;
                if (h.date.includes(" to ")) {
                  const parts = h.date.split(" to ");
                  const s = parseDateFlexible(parts[0].trim());
                  const e = parseDateFlexible(parts[1].trim());
                  return (
                    s && e && !(e < selectedStartDate || s > selectedEndDate)
                  );
                } else {
                  const hd = parseDateFlexible(h.date);
                  return hd && hd >= selectedStartDate && hd <= selectedEndDate;
                }
              })
              .sort((a, b) => {
                const aDate = parseDateFlexible(a.date);
                const bDate = parseDateFlexible(b.date);
                return aDate - bDate;
              });

            const out = document.getElementById("dateRangeResult");
            if (found.length === 0) {
              out.innerHTML = `<div class="result-card warning">
            <div style="font-weight:700;color:#FFA500">✗</div>
            <div>
              <div style="font-weight:600">No Holidays Found</div>
              <div style="color:#717171">There are no holidays in the selected date range</div>
            </div>
          </div>`;
            } else {
              out.innerHTML =
                `<div style="font-weight:600;color:#00A86B">Found ${
                  found.length
                } holiday${found.length > 1 ? "s" : ""}</div>` +
                found
                  .map(
                    (h) => `<div class="result-card success">
              <div style="font-weight:700;color:#00A86B">✓</div>
              <div>
                <div style="font-weight:600">${escapeHtml(h.event)}</div>
                <div style="color:#717171">${escapeHtml(h.date)}</div>
              </div>
            </div>`
                  )
                  .join("");
            }
          });

        // PDF download
        document
          .getElementById("downloadPdfBtn")
          ?.addEventListener("click", function () {
            window.open("/holiday/holiday.pdf", "_blank");
          });

        // Modal close
        document
          .getElementById("closeModalBtn")
          ?.addEventListener("click", function () {
            document.getElementById("holidayModal").style.display = "none";
            if (autoRefreshTimer) clearInterval(autoRefreshTimer);
          });

        // Close modal on overlay click
        window.addEventListener("click", function (e) {
          const modal = document.getElementById("holidayModal");
          if (e.target === modal) {
            modal.style.display = "none";
            if (autoRefreshTimer) clearInterval(autoRefreshTimer);
          }
        });

        // Close modal with Escape key
        window.addEventListener("keydown", function (e) {
          if (e.key === "Escape") {
            const modal = document.getElementById("holidayModal");
            if (modal.style.display === "flex") {
              modal.style.display = "none";
              if (autoRefreshTimer) clearInterval(autoRefreshTimer);
            }
          }
        });

        // Initialize holiday data
        fetchHolidayData()
          .then((data) => {
            if (Array.isArray(data)) holidayData = data;
          })
          .catch((e) => console.warn(e));
      });

      // Notice Section Functions
      let allNotices = [];
      let filteredNotices = [];

      async function loadNoticeSection() {
        const contentDiv = document.getElementById("academicsSectionContent");

        contentDiv.innerHTML = `
          <div class="notice-container">
            <div class="notice-header">
              <div class="notice-search-bar">
                <input type="text" id="noticeSearch" placeholder="Search notices..." onkeyup="filterNotices()">
                <svg class="notice-search-icon" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
              </div>
              <button class="notice-filter-btn" onclick="toggleNoticeFilters()">
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>
                </svg>
                Filters
              </button>
            </div>

            <div class="notice-filter-panel" id="noticeFilterPanel">
              <div class="notice-filter-row">
                <div class="notice-filter-group">
                  <label>Category</label>
                  <select id="categoryFilter" onchange="filterNotices()">
                    <option value="">All Categories</option>
                    <option value="Announcement">Announcement</option>
                    <option value="Academic">Academic</option>
                    <option value="Examination">Examination</option>
                    <option value="Event">Event</option>
                    <option value="Holiday">Holiday</option>
                    <option value="Important">Important</option>
                    <option value="General">General</option>
                  </select>
                </div>
                <div class="notice-filter-group">
                  <label>Date Mode</label>
                  <select id="dateMode" onchange="changeDateMode()">
                    <option value="all">All Dates</option>
                    <option value="specific">Specific Date</option>
                    <option value="month">Month</option>
                    <option value="year">Year</option>
                  </select>
                </div>
                <div class="notice-filter-group" id="dateFilterGroup" style="display:none;">
                  <label id="dateFilterLabel">Date</label>
                  <input type="date" id="dateFilter" onchange="filterNotices()">
                </div>
                <div class="notice-filter-group" id="monthFilterGroup" style="display:none;">
                  <label>Month</label>
                  <input type="month" id="monthFilter" onchange="filterNotices()">
                </div>
                <div class="notice-filter-group" id="yearFilterGroup" style="display:none;">
                  <label>Year</label>
                  <input type="number" id="yearFilter" min="2020" max="2030" placeholder="YYYY" onchange="filterNotices()">
                </div>
              </div>
              <div class="notice-quick-filters">
                <button class="notice-quick-filter active" onclick="applyQuickFilter('newest', event)">Newest First</button>
                <button class="notice-quick-filter" onclick="applyQuickFilter('oldest', event)">Oldest First</button>
                <button class="notice-quick-filter" onclick="applyQuickFilter('7days', event)">Last 7 Days</button>
              </div>
            </div>

            <div class="notice-list" id="noticeList">
              <div class="loading">Loading notices...</div>
            </div>
          </div>
        `;

        // Load notices from API
        await fetchNotices();
      }

      async function fetchNotices() {
        try {
          const response = await fetch("/api/notices");
          const data = await response.json();
          allNotices = data;
          filteredNotices = [...allNotices];
          applyQuickFilter("newest");
        } catch (error) {
          console.error("Error fetching notices:", error);
          document.getElementById("noticeList").innerHTML =
            '<div class="no-notices">Failed to load notices. Please try again later.</div>';
        }
      }

      function toggleNoticeFilters() {
        const panel = document.getElementById("noticeFilterPanel");
        panel.classList.toggle("active");
      }

      function changeDateMode() {
        const mode = document.getElementById("dateMode").value;
        document.getElementById("dateFilterGroup").style.display =
          mode === "specific" ? "block" : "none";
        document.getElementById("monthFilterGroup").style.display =
          mode === "month" ? "block" : "none";
        document.getElementById("yearFilterGroup").style.display =
          mode === "year" ? "block" : "none";
        filterNotices();
      }

      function filterNotices() {
        const searchTerm = document
          .getElementById("noticeSearch")
          .value.toLowerCase();
        const category = document.getElementById("categoryFilter").value;
        const dateMode = document.getElementById("dateMode").value;

        filteredNotices = allNotices.filter((notice) => {
          // Search filter
          if (searchTerm && !notice.title.toLowerCase().includes(searchTerm)) {
            return false;
          }

          // Category filter
          if (category && notice.category !== category) {
            return false;
          }

          // Date filter
          if (dateMode === "specific") {
            const filterDate = document.getElementById("dateFilter").value;
            if (filterDate && notice.date !== filterDate) {
              return false;
            }
          } else if (dateMode === "month") {
            const filterMonth = document.getElementById("monthFilter").value;
            if (filterMonth && !notice.date.startsWith(filterMonth)) {
              return false;
            }
          } else if (dateMode === "year") {
            const filterYear = document.getElementById("yearFilter").value;
            if (filterYear && !notice.date.startsWith(filterYear)) {
              return false;
            }
          }

          return true;
        });

        renderNotices();
      }

      function applyQuickFilter(filter, event) {
        // Update button states
        document.querySelectorAll(".notice-quick-filter").forEach((btn) => {
          btn.classList.remove("active");
        });

        // Only update button state if called from a click event
        if (event && event.target) {
          event.target.classList.add("active");
        } else {
          // Set default active button when called programmatically
          const buttons = document.querySelectorAll(".notice-quick-filter");
          if (filter === "newest" && buttons[0]) {
            buttons[0].classList.add("active");
          } else if (filter === "oldest" && buttons[1]) {
            buttons[1].classList.add("active");
          } else if (filter === "7days" && buttons[2]) {
            buttons[2].classList.add("active");
          }
        }

        if (filter === "newest") {
          filteredNotices.sort((a, b) => new Date(b.date) - new Date(a.date));
        } else if (filter === "oldest") {
          filteredNotices.sort((a, b) => new Date(a.date) - new Date(b.date));
        } else if (filter === "7days") {
          const sevenDaysAgo = new Date();
          sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
          filteredNotices = allNotices.filter(
            (notice) => new Date(notice.date) >= sevenDaysAgo
          );
          filteredNotices.sort((a, b) => new Date(b.date) - new Date(a.date));
        }

        renderNotices();
      }

      function renderNotices() {
        const listDiv = document.getElementById("noticeList");

        if (filteredNotices.length === 0) {
          listDiv.innerHTML =
            '<div class="no-notices">No notices found matching your filters.</div>';
          return;
        }

        let html = "";
        filteredNotices.forEach((notice, index) => {
          const formattedDate = new Date(notice.date).toLocaleDateString(
            "en-US",
            {
              year: "numeric",
              month: "short",
              day: "numeric",
            }
          );

          // Show body preview for announcements
          const bodyPreview =
            notice.type === "announcement" && notice.body
              ? `<p style="color:#717171;font-size:13px;margin:8px 0 0 0;line-height:1.4;">${notice.body.substring(
                  0,
                  120
                )}${notice.body.length > 120 ? "..." : ""}</p>`
              : "";

          // Create document button for PDFs and announcements with attachments
          let documentButton = "";
          if (notice.type === "pdf") {
            documentButton = `
              <button onclick="event.stopPropagation(); openNoticePdf('${notice.filename}')" style="
                margin-top: 12px;
                padding: 8px 16px;
                background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                transition: all 0.2s ease;
              " onmouseover="this.style.transform='translateY(-1px)';this.style.boxShadow='0 4px 8px rgba(25,118,210,0.3)'" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none'">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5v2z"/>
                  <path d="M4.603 14.087a.81.81 0 0 1-.438-.42c-.195-.388-.13-.776.08-1.102.198-.307.526-.568.897-.787a7.68 7.68 0 0 1 1.482-.645 19.697 19.697 0 0 0 1.062-2.227 7.269 7.269 0 0 1-.43-1.295c-.086-.4-.119-.796-.046-1.136.075-.354.274-.672.65-.823.192-.077.4-.12.602-.077a.7.7 0 0 1 .477.365c.088.164.12.356.127.538.007.188-.012.396-.047.614-.084.51-.27 1.134-.52 1.794a10.954 10.954 0 0 0 .98 1.686 5.753 5.753 0 0 1 1.334.05c.364.066.734.195.96.465.12.144.193.32.2.518.007.192-.047.382-.138.563a1.04 1.04 0 0 1-.354.416.856.856 0 0 1-.51.138c-.331-.014-.654-.196-.933-.417a5.712 5.712 0 0 1-.911-.95 11.651 11.651 0 0 0-1.997.406 11.307 11.307 0 0 1-1.02 1.51c-.292.35-.609.656-.927.787a.793.793 0 0 1-.58.029zm1.379-1.901c-.166.076-.32.156-.459.238-.328.194-.541.383-.647.547-.094.145-.096.25-.04.361.01.022.02.036.026.044a.266.266 0 0 0 .035-.012c.137-.056.355-.235.635-.572a8.18 8.18 0 0 0 .45-.606zm1.64-1.33a12.71 12.71 0 0 1 1.01-.193 11.744 11.744 0 0 1-.51-.858 20.801 20.801 0 0 1-.5 1.05zm2.446.45c.15.163.296.3.435.41.24.19.407.253.498.256a.107.107 0 0 0 .07-.015.307.307 0 0 0 .094-.125.436.436 0 0 0 .059-.2.095.095 0 0 0-.026-.063c-.052-.062-.2-.152-.518-.209a3.876 3.876 0 0 0-.612-.053zM8.078 7.8a6.7 6.7 0 0 0 .2-.828c.031-.188.043-.343.038-.465a.613.613 0 0 0-.032-.198.517.517 0 0 0-.145.04c-.087.035-.158.106-.196.283-.04.192-.03.469.046.822.024.111.054.227.09.346z"/>
                </svg>
                Open PDF
              </button>
            `;
          } else if (
            notice.type === "announcement" &&
            notice.attachments &&
            notice.attachments.length > 0
          ) {
            documentButton = `
              <button onclick="event.stopPropagation(); openNoticeByIndex(${index})" style="
                margin-top: 12px;
                padding: 8px 16px;
                background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                transition: all 0.2s ease;
              " onmouseover="this.style.transform='translateY(-1px)';this.style.boxShadow='0 4px 8px rgba(25,118,210,0.3)'" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none'">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M6.002 5.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/>
                  <path d="M1.5 2A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-13zm13 1a.5.5 0 0 1 .5.5v6l-3.775-1.947a.5.5 0 0 0-.577.093l-3.71 3.71-2.66-1.772a.5.5 0 0 0-.63.062L1.002 12v.54A.505.505 0 0 1 1 12.5v-9a.5.5 0 0 1 .5-.5h13z"/>
                </svg>
                View Attachments (${notice.attachments.length})
              </button>
            `;
          }

          html += `
            <div class="notice-card" onclick="${
              notice.type === "announcement"
                ? `openNoticeByIndex(${index})`
                : `openNoticePdf('${notice.filename}')`
            }" style="cursor: pointer;">
              <div class="notice-card-header">
                <span class="notice-category">${notice.category}</span>
                <span class="notice-date">${formattedDate}</span>
              </div>
              <h4 class="notice-title">${notice.title}</h4>
              ${bodyPreview}
              ${documentButton}
            </div>
          `;
        });

        listDiv.innerHTML = html;
      }

      function openNoticeByIndex(index) {
        const notice = filteredNotices[index];
        if (notice) {
          showAnnouncementDetail(notice);
        }
      }

      function openNoticePdf(filename) {
        window.open(`/pdfs/${filename}`, "_blank");
      }

      function showAnnouncementDetail(announcement) {
        // Create modal for announcement detail
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

        const formattedDate = new Date(announcement.date).toLocaleDateString(
          "en-US",
          {
            year: "numeric",
            month: "long",
            day: "numeric",
          }
        );

        let attachmentsHtml = "";
        if (announcement.attachments && announcement.attachments.length > 0) {
          attachmentsHtml = `
            <div style="margin-top:16px;padding-top:16px;border-top:1px solid #e0e0e0;">
              <h4 style="font-size:14px;font-weight:600;margin-bottom:8px;">Attachments:</h4>
              ${announcement.attachments
                .map(
                  (att) => `
                <a href="${att.url}" target="_blank" style="display:block;padding:8px;background:#f7f9fc;border-radius:6px;margin-bottom:6px;text-decoration:none;color:#1976d2;font-size:13px;">
                  📎 ${att.name}
                </a>
              `
                )
                .join("")}
            </div>
          `;
        }

        content.innerHTML = `
          <button onclick="this.closest('[role=dialog]').remove()" style="
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
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
          " onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='transparent'">×</button>
          <div style="margin-bottom:12px;">
            <span style="display:inline-block;padding:4px 10px;background:#e3f2fd;color:#1976d2;border-radius:4px;font-size:12px;font-weight:500;">Announcement</span>
            <span style="color:#717171;font-size:13px;margin-left:12px;">${formattedDate}</span>
          </div>
          <h2 style="font-size:20px;font-weight:700;color:#333;margin-bottom:16px;line-height:1.4;">${announcement.title}</h2>
          <div style="color:#555;font-size:14px;line-height:1.6;white-space:pre-wrap;">${announcement.body}</div>
          ${attachmentsHtml}
        `;

        modal.setAttribute("role", "dialog");
        modal.appendChild(content);
        document.body.appendChild(modal);

        // Close on background click
        modal.addEventListener("click", (e) => {
          if (e.target === modal) modal.remove();
        });

        // Close on Escape key
        const handleEscape = (e) => {
          if (e.key === "Escape") {
            modal.remove();
            document.removeEventListener("keydown", handleEscape);
          }
        };
        document.addEventListener("keydown", handleEscape);
      }
