# Financial Auditor Frontend

React + TypeScript + Tailwind CSS dashboard for the local FastAPI financial document auditor.

## Run Locally

Start the backend first:

```powershell
uvicorn financial_auditor.api.main:app --reload
```

Then start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## API Integration

The Vite development server proxies frontend calls from `/api` to `http://127.0.0.1:8000`.

To use a different API base URL:

```powershell
$env:VITE_API_BASE_URL="http://127.0.0.1:8000"
npm run dev
```

## Features

- Document upload for invoices, receipts, and expense reports
- FastAPI multipart integration with loading and error states
- Document metadata panel
- Audit confidence and routing summary
- Extracted field cards with verifier confidence
- Line item table
- Validation findings and severity table
- Structured JSON viewer

