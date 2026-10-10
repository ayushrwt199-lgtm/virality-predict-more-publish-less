# Virality 2.0 Launcher Script
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  VIRALITY 2.0 — Predict More. Publish Less.             " -ForegroundColor Green
Write-Host "  Gemini 2.5 Flash -> MiroFish Swarm -> Tiger Data        " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$backendPath = "c:\Users\ayush\OneDrive\Desktop\Virality\backend"
$frontendPath = "c:\Users\ayush\OneDrive\Desktop\Virality\frontend"

Write-Host "`n[1/2] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; .\.venv\Scripts\python.exe run.py"

Start-Sleep -Seconds 2

Write-Host "[2/2] Starting React/Vite Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev"

Write-Host "`nAll services launched successfully!" -ForegroundColor Green
Write-Host "Demo Credentials: demo@virality.ai / innohacks2026" -ForegroundColor Yellow
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
