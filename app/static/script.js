(function () {
  function escapeHtml(text) {
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function renderInlineMarkdown(text) {
    let html = escapeHtml(text);
    html = html.replace(
      /\[([^\]]+)\]\((https?:[^\s)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener">$1</a>'
    );
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/__(.+?)__/g, "<strong>$1</strong>");
    html = html.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, "<em>$1</em>");
    html = html.replace(/_(.+?)_/g, "<em>$1</em>");
    html = html.replace(/`(.+?)`/g, "<code>$1</code>");
    return html;
  }

  function renderMarkdown(text) {
    const lines = (text || "").split(/\r?\n/);
    const blocks = [];
    let listItems = [];
    let paragraphLines = [];

    const flushParagraph = () => {
      if (paragraphLines.length) {
        const combined = paragraphLines.join(" ").trim();
        if (combined) {
          blocks.push(`<p>${renderInlineMarkdown(combined)}</p>`);
        }
        paragraphLines = [];
      }
    };

    const flushList = () => {
      if (listItems.length) {
        const items = listItems
          .map((item) => `<li>${renderInlineMarkdown(item)}</li>`)
          .join("");
        blocks.push(`<ul>${items}</ul>`);
        listItems = [];
      }
    };

    lines.forEach((line) => {
      const trimmed = line.trim();

      const listMatch = trimmed.match(/^[-*]\s+(.*)$/);
      if (listMatch) {
        flushParagraph();
        listItems.push(listMatch[1]);
        return;
      }

      if (trimmed === "---") {
        flushParagraph();
        flushList();
        blocks.push("<hr>");
        return;
      }

      if (trimmed === "") {
        flushParagraph();
        flushList();
        blocks.push("<br>");
        return;
      }

      flushList();
      paragraphLines.push(trimmed);
    });

    flushParagraph();
    flushList();

    return blocks.join("");
  }

  document.addEventListener("DOMContentLoaded", () => {
    const messagesEl = document.getElementById("messages");
    const formEl = document.getElementById("message-form");
    const inputEl = document.getElementById("message-input");
    const sendButton = document.getElementById("send-button");
    const connectionStatus = document.getElementById("connection-status");
    const themeToggle = document.getElementById("theme-toggle");
    const themeToggleInput = document.getElementById("theme-toggle-checkbox");
    let overlayEl = document.getElementById("disclaimer-overlay");
    let overlayContent = overlayEl
      ? overlayEl.querySelector(".disclaimer")
      : null;

    let conversation = [];
    const THEME_STORAGE_KEY = "chat-theme";
    const prefersDark = window.matchMedia
      ? window.matchMedia("(prefers-color-scheme: dark)")
      : null;
    let userSetTheme = false;

    function getStoredTheme() {
      try {
        return localStorage.getItem(THEME_STORAGE_KEY);
      } catch (error) {
        console.warn(
          "Unable to access localStorage for theme preference.",
          error
        );
        return null;
      }
    }

    function storeTheme(theme) {
      try {
        localStorage.setItem(THEME_STORAGE_KEY, theme);
      } catch (error) {
        console.warn("Unable to persist theme preference.", error);
      }
    }

    function applyTheme(theme) {
      const normalized = theme === "dark" ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", normalized);
      if (!themeToggleInput) {
        return;
      }
      const isDark = normalized === "dark";
      themeToggleInput.checked = !isDark;
      themeToggleInput.setAttribute(
        "aria-label",
        isDark ? "Switch to light theme" : "Switch to dark theme"
      );
      if (themeToggle) {
        themeToggle.setAttribute("data-theme", normalized);
      }
    }

    function initializeTheme() {
      const stored = getStoredTheme();
      if (stored === "light" || stored === "dark") {
        userSetTheme = true;
        applyTheme(stored);
        return;
      }
      const systemPrefersDark = prefersDark ? prefersDark.matches : false;
      applyTheme(systemPrefersDark ? "dark" : "light");
    }

    function scrollToBottom() {
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function setConnectionStatus(message, { state } = {}) {
      if (!connectionStatus) return;
      const text = connectionStatus.querySelector(".status-text");
      if (text) {
        text.textContent = message;
      }
      connectionStatus.classList.remove("error", "pending");
      if (state === "error") {
        connectionStatus.classList.add("error");
      } else if (state === "pending") {
        connectionStatus.classList.add("pending");
      }
    }

    function hideDisclaimerOverlay() {
      if (overlayEl) {
        overlayEl.remove();
        overlayEl = null;
        overlayContent = null;
      }
    }

    function renderDisclaimerContent(text) {
      if (!overlayContent) return;
      overlayContent.innerHTML = "";

      const lines = text.split("\n");
      let listEl = null;

      const closeList = () => {
        listEl = null;
      };

      lines.forEach((line, index) => {
        const trimmed = line.trim();

        if (!trimmed) {
          closeList();
          return;
        }

        if (trimmed.startsWith("- ")) {
          if (!listEl) {
            listEl = document.createElement("ul");
            overlayContent.appendChild(listEl);
          }
          const li = document.createElement("li");
          li.textContent = trimmed.slice(2).trim();
          listEl.appendChild(li);
          return;
        }

        closeList();

        const isHeading = trimmed.endsWith(":");
        if (isHeading) {
          const headingText = trimmed.replace(/:\s*$/, "");
          const tag = overlayContent.childElementCount === 0 ? "h2" : "h3";
          const heading = document.createElement(tag);
          heading.textContent = headingText;
          overlayContent.appendChild(heading);
          return;
        }

        const para = document.createElement("p");
        para.textContent = trimmed;
        overlayContent.appendChild(para);
      });

      closeList();
    }

    function renderMessage(msg) {
      hideDisclaimerOverlay();
      const wrapper = document.createElement("article");
      wrapper.classList.add("message", msg.role);
      if (msg.typing) {
        wrapper.classList.add("typing");
      }
      if (
        msg.role === "assistant" &&
        msg.safetyAction &&
        msg.safetyAction !== "allow"
      ) {
        wrapper.classList.add(msg.safetyAction);
      }

      const avatar = document.createElement("div");
      avatar.className = "avatar";
      if (msg.role === "assistant") {
        const img = document.createElement("img");
        img.className = "avatar-img";
        img.alt = "AI assistant avatar";
        img.src = "https://img.freepik.com/free-vector/young-man-with-glasses-avatar_1308-175763.jpg";
        avatar.appendChild(img);
      } else {
        avatar.textContent = "You";
      }
      wrapper.appendChild(avatar);

      const bubble = document.createElement("div");
      bubble.className = "bubble";

      if (msg.role === "assistant" && !msg.typing) {
        const meta = document.createElement("div");
        meta.className = "meta";
        const badge = document.createElement("span");
        badge.className = "badge";

        if (msg.safetyAction === "block") {
          badge.textContent = "Safety Alert";
        } else if (msg.safetyAction === "fallback") {
          badge.textContent =
            msg.policyTags && msg.policyTags.length
              ? "Safety Redirect"
              : "System Notice";
        } else {
          badge.textContent = "Assistant";
          badge.classList.add("neutral");
        }
        meta.appendChild(badge);

        if (msg.policyTags && msg.policyTags.length) {
          const tags = document.createElement("span");
          tags.textContent = `Policy tags: ${msg.policyTags.join(", ")}`;
          meta.appendChild(tags);
        }

        bubble.appendChild(meta);
      }

      if (msg.typing) {
        const indicator = document.createElement("div");
        indicator.className = "typing-indicator";

        for (let i = 0; i < 3; i += 1) {
          const dot = document.createElement("span");
          dot.className = "dot";
          dot.style.animationDelay = `${i * 0.15}s`;
          indicator.appendChild(dot);
        }

        const srOnly = document.createElement("span");
        srOnly.className = "sr-only";
        srOnly.textContent = "Assistant is typing";

        bubble.appendChild(indicator);
        bubble.appendChild(srOnly);
      } else {
        const content = document.createElement("div");
        content.className = "message-body";
        if (msg.role === "assistant") {
          content.innerHTML = renderMarkdown(msg.text || "");
        } else {
          content.textContent = msg.text;
          content.style.whiteSpace = "pre-wrap";
        }
        bubble.appendChild(content);
      }
      wrapper.appendChild(bubble);

      messagesEl.appendChild(wrapper);
      scrollToBottom();
      return wrapper;
    }

    function renderConversation() {
      messagesEl.innerHTML = "";
      conversation.forEach(renderMessage);
    }

    initializeTheme();

    if (prefersDark) {
      const handlePreferenceChange = (event) => {
        if (userSetTheme) {
          return;
        }
        applyTheme(event.matches ? "dark" : "light");
      };

      if (typeof prefersDark.addEventListener === "function") {
        prefersDark.addEventListener("change", handlePreferenceChange);
      } else if (typeof prefersDark.addListener === "function") {
        prefersDark.addListener(handlePreferenceChange);
      }
    }

    if (themeToggleInput) {
      themeToggleInput.addEventListener("change", () => {
        const nextTheme = themeToggleInput.checked ? "light" : "dark";
        userSetTheme = true;
        applyTheme(nextTheme);
        storeTheme(nextTheme);
      });
    }

    function addTypingIndicator() {
      const typingEntry = {
        role: "assistant",
        typing: true,
      };
      conversation.push(typingEntry);
      typingEntry.element = renderMessage(typingEntry);
      return typingEntry;
    }

    function removeTypingIndicator(entry) {
      if (!entry) {
        return;
      }
      const index = conversation.indexOf(entry);
      if (index !== -1) {
        conversation.splice(index, 1);
      }
      if (entry.element && entry.element.parentNode) {
        entry.element.parentNode.removeChild(entry.element);
      }
    }

    async function bootstrapSession() {
      try {
        setConnectionStatus("Checking model connection", { state: "pending" });
        const response = await fetch("/api/session");
        if (!response.ok) {
          throw new Error("Failed to connect to the language model.");
        }
        const data = await response.json();
        setConnectionStatus("Online");
        if (overlayContent && data.disclaimer) {
          renderDisclaimerContent(data.disclaimer);
        }
      } catch (error) {
        console.error(error);
        setConnectionStatus("Offline", { state: "error" });
      }
    }

    async function sendMessage(message) {
      sendButton.disabled = true;
      inputEl.disabled = true;

      const userEntry = {
        role: "user",
        text: message,
        safetyAction: null,
        policyTags: [],
      };
      conversation.push(userEntry);
      renderMessage(userEntry);

      const typingEntry = addTypingIndicator();

      try {
        const response = await fetch("/api/message", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            errorData.error || "The server was unable to respond."
          );
        }

        const data = await response.json();
        const safetyAction =
          data.safety_action === "safe_fallback"
            ? "fallback"
            : data.safety_action;
        removeTypingIndicator(typingEntry);
        const assistantEntry = {
          role: "assistant",
          text: data.response,
          safetyAction,
          policyTags: Array.isArray(data.policy_tags) ? data.policy_tags : [],
        };
        conversation.push(assistantEntry);
        renderMessage(assistantEntry);
      } catch (error) {
        console.error(error);
        removeTypingIndicator(typingEntry);
        const errorEntry = {
          role: "assistant",
          text: "I encountered a technical issue and could not respond. Please try again or restart the conversation.",
          safetyAction: "fallback",
          policyTags: [],
        };
        conversation.push(errorEntry);
        renderMessage(errorEntry);
      } finally {
        sendButton.disabled = false;
        inputEl.disabled = false;
        inputEl.value = "";
        inputEl.focus();
      }
    }

    formEl.addEventListener("submit", (event) => {
      event.preventDefault();
      const message = inputEl.value.trim();
      if (!message) {
        return;
      }
      sendMessage(message);
    });

    bootstrapSession().then(() => {});
  });
})();
