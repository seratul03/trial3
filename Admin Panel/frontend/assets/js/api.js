/*
 * api.js — Fixed ApiClient
 * - Robust request handling (JSON, text, blobs)
 * - No top-level instantiation (avoids "Cannot access 'ApiClient' before initialization")
 * - Lazy global singleton: window.api and getApi() create instance on first access
 * - Works when included as a classic script. Also exposes module.exports when available.
 */

const API_BASE_URL = ""; // keep empty so frontend served from same origin as backend

class ApiClient {
  constructor() {
    this.token =
      typeof localStorage !== "undefined" && localStorage.getItem
        ? localStorage.getItem("auth_token")
        : null;
  }

  setToken(token) {
    this.token = token;
    try {
      localStorage.setItem("auth_token", token);
    } catch (e) {
      // ignore (e.g. not running in browser)
    }
  }

  clearToken() {
    this.token = null;
    try {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("user");
    } catch (e) {
      // ignore
    }
  }

  getDefaultHeaders({ isJSON = true } = {}) {
    const headers = {
      Accept: "application/json",
    };

    if (isJSON) headers["Content-Type"] = "application/json";
    if (this.token) headers["Authorization"] = `Bearer ${this.token}`;
    return headers;
  }

  _isFormData(body) {
    try {
      return typeof FormData !== "undefined" && body instanceof FormData;
    } catch (e) {
      return false;
    }
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const opts = { ...options };
    opts.method = (opts.method || "GET").toUpperCase();

    if (
      opts.body &&
      !this._isFormData(opts.body) &&
      typeof opts.body !== "string"
    ) {
      try {
        opts.body = JSON.stringify(opts.body);
      } catch (e) {
        console.warn("Failed to stringify request body:", e);
      }
    }

    if ((opts.method === "GET" || opts.method === "HEAD") && opts.body) {
      delete opts.body;
    }

    let headers = opts.headers ?? null;
    if (!headers) {
      const isJSON = !this._isFormData(opts.body);
      headers = this.getDefaultHeaders({ isJSON });
    } else {
      if (this.token && !headers["Authorization"]) {
        headers["Authorization"] = `Bearer ${this.token}`;
      }
      if (this._isFormData(opts.body) && headers["Content-Type"]) {
        delete headers["Content-Type"];
      }
      if (!headers["Accept"]) headers["Accept"] = "application/json";
    }

    const config = {
      ...opts,
      headers,
      cache: opts.cache ?? "no-cache",
    };

    const maxRetries = 3;
    let lastError = null;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.debug(
          `[ApiClient] ${config.method} ${url} (attempt ${attempt})`,
          {
            headers: config.headers,
            hasBody: !!config.body,
            body: config.body
              ? typeof config.body === "string"
                ? config.body.substring(0, 200)
                : "FormData"
              : null,
          }
        );

        let response;
        try {
          response = await fetch(url, config);
        } catch (fetchError) {
          throw new Error(
            `Fetch failed: ${fetchError.message}. Check if servers are running and CORS is configured.`
          );
        }

        if (response.status === 401) {
          this.clearToken();
          try {
            if (typeof window !== "undefined")
              window.location.href = "/index.html";
          } catch (e) {}
          return { success: false, status: 401, error: "Unauthorized" };
        }

        if (response.status === 204 || response.status === 205) {
          return null;
        }

        const contentType = (
          response.headers.get("content-type") || ""
        ).toLowerCase();

        if (contentType.includes("application/json")) {
          const data = await response.json();

          if (!response.ok) {
            const errObj = {
              success: false,
              status: response.status,
              error:
                data?.error ||
                data?.message ||
                data?.detail ||
                "Request failed",
              message:
                data?.error ||
                data?.message ||
                data?.detail ||
                "Request failed",
              raw: data,
            };

            console.error(`[ApiClient] HTTP ${response.status} error:`, {
              url,
              method: config.method,
              error: errObj,
              fullResponse: data,
            });

            if (response.status >= 500 && attempt < maxRetries) {
              await new Promise((r) => setTimeout(r, 1000 * attempt));
              continue;
            }

            return errObj;
          }

          return data;
        }

        if (
          contentType.includes("application/pdf") ||
          contentType.includes("application/octet-stream") ||
          contentType.includes("image/") ||
          contentType.includes("application/zip")
        ) {
          const blob = await response.blob();
          if (!response.ok) {
            lastError = new Error(
              `Server returned ${response.status} for binary response`
            );
            if (response.status >= 500 && attempt < maxRetries) {
              await new Promise((r) => setTimeout(r, 1000 * attempt));
              continue;
            }
            return {
              success: false,
              status: response.status,
              error: "File download failed",
              raw: blob,
            };
          }
          return blob;
        }

        if (contentType.includes("text/") || contentType === "") {
          const text = await response.text();
          if (!response.ok) {
            const snippet = text?.slice(0, 200);
            lastError = new Error(`HTTP ${response.status}: ${snippet}`);
            if (response.status >= 500 && attempt < maxRetries) {
              await new Promise((r) => setTimeout(r, 1000 * attempt));
              continue;
            }
            return {
              success: false,
              status: response.status,
              error: text || "Request failed",
            };
          }
          return text;
        }

        try {
          const data = await response.json();
          if (!response.ok) {
            if (response.status >= 500 && attempt < maxRetries) {
              lastError = new Error(`Server error ${response.status}`);
              await new Promise((r) => setTimeout(r, 1000 * attempt));
              continue;
            }
            return {
              success: false,
              status: response.status,
              error: data?.message || data,
            };
          }
          return data;
        } catch (parseErr) {
          const text = await response.text();
          if (!response.ok) {
            lastError = parseErr;
            if (response.status >= 500 && attempt < maxRetries) {
              await new Promise((r) => setTimeout(r, 1000 * attempt));
              continue;
            }
            return {
              success: false,
              status: response.status,
              error: text || "Request failed",
            };
          }
          return text;
        }
      } catch (err) {
        lastError = err;
        console.error(
          `[ApiClient] Network error (Attempt ${attempt}/${maxRetries}):`,
          { url, method: config.method, error: err, message: err.message }
        );

        if (attempt < maxRetries) {
          console.warn(`[ApiClient] Retrying after network error...`);
          await new Promise((resolve) => setTimeout(resolve, 1000 * attempt));
          continue;
        }

        return {
          success: false,
          error: `Network error: ${
            err.message || "Failed to connect to server"
          }\n\nPlease check the backend server is running and accessible.`,
          message: err.message || "Network error",
        };
      }
    }

    return {
      success: false,
      error: `Unknown error after ${maxRetries} attempts.`,
    };
  }

  // --- Auth endpoints ---
  async login(email, password) {
    return this.request("/api/auth/login", {
      method: "POST",
      body: { email, password },
    });
  }

  async logout() {
    const result = await this.request("/api/auth/logout", { method: "POST" });
    this.clearToken();
    return result;
  }

  async getCurrentUser() {
    return this.request("/api/auth/me");
  }
  async createUser(userData) {
    return this.request("/api/auth/users", { method: "POST", body: userData });
  }
  async listUsers() {
    return this.request("/api/auth/users");
  }

  // --- KB endpoints ---
  async getFAQs(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/api/kb/faqs?${query}`);
  }
  async createFAQ(faqData) {
    return this.request("/api/kb/faqs", { method: "POST", body: faqData });
  }
  async updateFAQ(id, faqData) {
    return this.request(`/api/kb/faqs/${id}`, { method: "PUT", body: faqData });
  }
  async deleteFAQ(id) {
    return this.request(`/api/kb/faqs/${id}`, { method: "DELETE" });
  }

  async uploadPDF(formData) {
    const headers = {};
    if (this.token) headers["Authorization"] = `Bearer ${this.token}`;
    return this.request("/api/kb/pdfs", {
      method: "POST",
      headers,
      body: formData,
    });
  }

  async getPDFs(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/api/kb/pdfs?${query}`);
  }
  async getPDF(id) {
    return this.request(`/api/kb/pdfs/${id}`);
  }

  async getTags() {
    return this.request("/api/kb/tags");
  }
  async createTag(name) {
    return this.request("/api/kb/tags", { method: "POST", body: { name } });
  }
  async deleteTag(id) {
    return this.request(`/api/kb/tags/${id}`, { method: "DELETE" });
  }
  async searchKB(query) {
    return this.request(`/api/kb/search?q=${encodeURIComponent(query)}`);
  }

  // --- Subject endpoints ---
  async getSubjects(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/api/subjects?${query}`);
  }
  async getSubject(id) {
    return this.request(`/api/subjects/${id}`);
  }
  async createSubject(subjectData) {
    return this.request("/api/subjects", { method: "POST", body: subjectData });
  }
  async updateSubject(id, subjectData) {
    return this.request(`/api/subjects/${id}`, {
      method: "PUT",
      body: subjectData,
    });
  }
  async deleteSubject(id) {
    return this.request(`/api/subjects/${id}`, { method: "DELETE" });
  }

  // --- Query endpoints ---
  async getQueries(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/api/queries?${query}`);
  }
  async getQuery(id) {
    return this.request(`/api/queries/${id}`);
  }
  async replyToQuery(id, replyData) {
    return this.request(`/api/queries/${id}/reply`, {
      method: "POST",
      body: replyData,
    });
  }
  async updateQueryStatus(id, status, assignedTeacherId = null) {
    return this.request(`/api/queries/${id}`, {
      method: "PATCH",
      body: { status, assigned_teacher_id: assignedTeacherId },
    });
  }
  async getQueryStats() {
    return this.request("/api/queries/stats/summary");
  }
  async getQueryLogs(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/api/analytics/logs?${query}`);
  }
  async exportQueryLogs(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/api/analytics/export-logs?${query}`);
  }
  async reviewFeedback(id) {
    return this.request(`/api/feedback/${id}`, {
      method: "PATCH",
      body: { reviewed_bool: true },
    });
  }

  // --- Announcement endpoints ---
  async getAnnouncements(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/api/announcements?${query}`);
  }
  async getActiveAnnouncements() {
    return this.request("/api/announcements/active");
  }
  async createAnnouncement(announcementData) {
    return this.request("/api/announcements", {
      method: "POST",
      body: announcementData,
    });
  }
  async updateAnnouncement(id, announcementData) {
    return this.request(`/api/announcements/${id}`, {
      method: "PUT",
      body: announcementData,
    });
  }
  async deleteAnnouncement(id) {
    return this.request(`/api/announcements/${id}`, { method: "DELETE" });
  }
  async publishAnnouncement(id) {
    return this.request(`/api/announcements/${id}/publish`, { method: "POST" });
  }

  // --- Analytics ---
  async getDashboardStats() {
    return this.request("/api/analytics/dashboard");
  }
  async getTopSubjects(limit = 10) {
    return this.request(`/api/analytics/top-subjects?limit=${limit}`);
  }
  async getConfusingQuestions(limit = 10) {
    return this.request(`/api/analytics/confusing-questions?limit=${limit}`);
  }
  async getSubjectsNeedingData() {
    return this.request("/api/analytics/subjects-needing-data");
  }
  async getImprovementTrend(period = "week") {
    return this.request(`/api/analytics/improvement-trend?period=${period}`);
  }
  async getLogs(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/api/analytics/logs?${query}`);
  }
  async exportLogs(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/api/analytics/export-logs?${query}`);
  }

  // --- Feedback ---
  async getFeedback(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/api/feedback?${query}`);
  }
  async updateFeedback(id, reviewed) {
    return this.request(`/api/feedback/${id}`, {
      method: "PATCH",
      body: { reviewed_bool: reviewed },
    });
  }
  async fixKBFromFeedback(feedbackId, faqId, correctedAnswer) {
    return this.request(`/api/feedback/${feedbackId}/fix-kb?faq_id=${faqId}`, {
      method: "POST",
      body: { corrected_answer: correctedAnswer },
    });
  }

  // --- Bot config ---
  async getBotConfig() {
    return this.request("/api/bot-config");
  }
  async updateBotConfig(configData) {
    return this.request("/api/bot-config", { method: "PUT", body: configData });
  }
}

// --- Lazy singleton & globals ---
(function () {
  let _apiInstance = null;

  function createInstance() {
    if (!_apiInstance) _apiInstance = new ApiClient();
    return _apiInstance;
  }

  // Expose a global getApi() helper (useful for modules or other scripts)
  try {
    if (typeof globalThis !== "undefined") {
      globalThis.getApi = function () {
        return createInstance();
      };
    }
  } catch (e) {
    // ignore
  }

  // Provide window.api as a lazy getter so other scripts can use `api` or `window.api`
  if (typeof window !== "undefined") {
    Object.defineProperty(window, "api", {
      configurable: true,
      enumerable: true,
      get() {
        return createInstance();
      },
      set(v) {
        _apiInstance = v;
      },
    });
  }

  // CommonJS export support (for Node tests or bundlers that use CommonJS)
  try {
    if (typeof module !== "undefined" && module.exports) {
      module.exports = { ApiClient, getApi: globalThis.getApi };
    }
  } catch (e) {
    // ignore
  }
})();

// end of file
