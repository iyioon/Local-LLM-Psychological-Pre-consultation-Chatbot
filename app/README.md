# Psychological Pre-Consultation Chatbot Interface

This front-end provides a user-friendly interface for the local psychological pre-consultation chatbot. It combines a lightweight Flask backend with a HTML/CSS frontend.

## Framework Choice Justification

- **Flask**: A minimal web framework that integrates cleanly with the existing Python moderation pipeline. Flask keeps the stack lightweight, works well with local deployments, and requires only a few readable routes to expose the chat engine.
- **HTML/CSS/JS**: Avoids heavy front-end dependencies while giving full control over accessibility and responsive layout. The interface runs in any modern browser.

## Additional Dependencies

Install the following library in addition to the project’s base requirements:

```bash
pip install Flask
```

## Installation Instructions

1. Create and activate a virtual environment if you have not already.
2. Install baseline dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install the Flask dependency for the UI:
   ```bash
   pip install Flask
   ```

## Running Instructions

Run the Flask application inside the `app` directory:

```bash
flask run
```

Open `http://localhost:5000` in your browser.

## UI Design Decisions

### Safety-First Principles

- A disclaimer panel is displayed in the conversation canvas before any messages appear. It is used to prime users on limits before they interact.
- Moderation results are shown as labeled message chips: `Safety Alert` for blocked content, `Safety Redirect` for policy-guided fallback, and `System Notice` for technical disruptions. Colors follow safety heuristics—green for active/ready, amber for pending, red for escalation—so risks are instantly recognizable.
- The connection-status chip pulses during the LLM health check and switches to red if the backend is unreachable. This ensures transparency about availability.

### Accessibility Requirements

- Semantic elements (`header`, `main`, `section`) and `aria-live` regions ensure predictable navigation for screen readers, while visually hidden labels keep controls accessible without adding visual clutter.
- The interface provides a built-in light/dark theme toggle and honours system `prefers-color-scheme`, supporting users with light sensitivity or low-vision needs. Typography and spacing follow WCAG 2.2 AA contrast ratios and minimum touch-target guidance.
- All interactive elements are fully keyboard operable, reflecting inclusive design principles such as WCAG’s operable and perceivable guidelines.

### User Trust and Comfort

- The assistant avatar is represented by a friendly illustrated portrait, establishing a sense of personal presence while clearly signaling that the AI is a supportive listener rather than an anonymous, faceless bot.
- Glassmorphic surfaces, subtle gradients, and warm typography are used to reduce cognitive load while preserving professionalism.
- A privacy note beneath the title clearly states that sessions are local and cleared on reload, reinforcing the “transparency” principle in trustworthy AI frameworks. Meanwhile, the animated status chip reassures users that the system remains responsive and actively monitored.
- The composer adopts familiar chat conventions—multi-line input, send icon, and responsive hover states—offering modern reliability without introducing distracting decorative elements.

### Clear Communication of System Boundaries

- The disclaimer outlines what the assistant can and cannot do.
- Moderation tags, reflected back into the transcript, indicate when the AI blocked or redirected content. This makes boundary enforcement transparent.
- After a message is sent, the input box is temporarily disabled and a message bubble appears indicating that the assistant is formulating a response. This prevents users from sending multiple messages at once and helps manage expectations about response times.
