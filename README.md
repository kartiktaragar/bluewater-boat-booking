# Bluewater Boat Booking Frontend

React, Vite, and Tailwind CSS frontend for the Bluewater boat-booking application.

## Windows setup (PowerShell terminal in VS Code)

Open a terminal in this folder, copy the API environment example, then install and run:

```powershell
Copy-Item .env.example .env
npm install
npm run dev
```

The development server is available at `http://localhost:5173`. Set `VITE_API_URL` in `.env` if the FastAPI API is not at `http://localhost:8000/api`.

## Pages

- Home and searchable boat listings.
- Boat details, date availability, and booking checkout.
- Signup, login, customer profile, and booking history/cancellation.
- Role-protected admin dashboard for fleet creation and booking management.
- Optional Stripe Elements payment and admin refunds, available only when the backend is configured with Stripe test-mode keys and a verified webhook.

Create a production build with `npm run build`.
