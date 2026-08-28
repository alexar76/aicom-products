# Acceptance Scenarios

## Onboarding

1. A new user visits the Relay landing page and clicks the primary CTA "Start a free handoff".
2. The browser navigates to the signup page (`/signup`). The user enters their email, a password of at least 10 characters, and a workspace name, then submits the form.
3. The backend creates the operator account and workspace, sets a session cookie, and redirects to the operator inbox (`/inbox`). The inbox displays a welcome message and a prompt to create the first handoff.
4. The user clicks "New Handoff" (`/handoffs/new`), pastes an AI-generated draft (≥20 characters), fills in the client name, project name, and source AI tool, and submits.
5. The handoff appears in the inbox under the "Pending" tab. The user opens the handoff detail, runs the skeptic verification pass (marking all four checklist items as pass), and clicks "Approve & Publish".
6. The handoff status changes to "approved". The user can now view the branded public share page at `/share/{token}` or copy the embed snippet from the detail view.

**Edge case – invalid input:** If the user submits the signup form with a password shorter than 10 characters, the API returns a 422 error and the form displays an inline validation message. The account is not created.

**Recovery – session expiry:** If the user's session expires while they are on the inbox, the next API request returns 401. The SPA redirects to the login page. After logging in again, the user returns to the inbox and all previously created handoffs are still visible.
