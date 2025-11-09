# Script PowerShell pour tester l'API sans interrompre le serveur
Write-Host "🧪 Test de l'API Auto-Responder" -ForegroundColor Cyan
Write-Host "=" * 50

try {
    # Test de l'endpoint /api/status
    Write-Host "`n1️⃣  Test de /api/status..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/status" -Method Get
    Write-Host "✅ Serveur opérationnel!" -ForegroundColor Green
    Write-Host "Status: $($response.status)"
    Write-Host "Message: $($response.message)"
    Write-Host "Timestamp: $($response.timestamp)"
    
    # Test de l'endpoint /api/receive (avec données de test)
    Write-Host "`n2️⃣  Test de /api/receive..." -ForegroundColor Yellow
    $headers = @{
        "Authorization" = "Bearer your_secret_key_for_webhook_authentication"
        "Content-Type" = "application/json"
    }
    
    $testData = @{
        response_id = "test_$(Get-Date -Format 'yyyyMMddHHmmss')"
        email = "test@example.com"
        phone = "+33612345678"
        name = "Test User"
        timestamp = (Get-Date).ToString("o")
    } | ConvertTo-Json
    
    $webhookResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/receive" -Method Post -Headers $headers -Body $testData
    Write-Host "✅ Webhook fonctionne!" -ForegroundColor Green
    Write-Host "Message: $($webhookResponse.message)"
    Write-Host "Response ID: $($webhookResponse.response_id)"
    
} catch {
    Write-Host "❌ Erreur: $_" -ForegroundColor Red
    Write-Host "`nAssurez-vous que le serveur est en cours d'exécution:" -ForegroundColor Yellow
    Write-Host "  cd C:\Users\bobim\Autoresponder"
    Write-Host "  .venv\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000"
}

Write-Host "`n" + "=" * 50
Write-Host "✅ Tests terminés!" -ForegroundColor Cyan
