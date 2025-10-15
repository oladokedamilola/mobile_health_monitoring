from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
import json

@csrf_exempt
def upload_sync_data(request):
    """Receives offline readings and saves to DB (simplified example)."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(f"📥 Received {len(data)} offline records")
            # TODO: Save to HealthRecord model via MonitoringService
            return JsonResponse({"status": "success", "count": len(data)})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"message": "Invalid method"}, status=405)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import SyncLog, OfflineRecord

@login_required
def sync_view(request):
    logs = SyncLog.objects.filter(user=request.user).order_by("-created_at")[:20]
    offline_data = OfflineRecord.objects.filter(user=request.user, synced=False)
    return render(request, "sync/sync.html", {
        "logs": logs,
        "offline_data": offline_data,
    })
