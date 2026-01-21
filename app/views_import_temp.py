from django.http import JsonResponse
from django.conf import settings
import json
import os
from app.models import RemedyRelationship, RemedyDuration

def trigger_import(request):
    # Basic security: Check for superuser or a secret header/param could be added here
    # For now, relying on obscurity and user action
    
    if not request.user.is_superuser:
        return JsonResponse({"error": "Unauthorized. Please login as superuser."}, status=403)

    results = {
        "status": "started",
        "relationships_added": 0,
        "durations_added": 0,
        "errors": []
    }
    
    try:
        # Try multiple possible paths
        possible_paths = [
            os.path.join(settings.BASE_DIR, 'app', 'medicines', 'remedy_relationships.json'),
            'app/medicines/remedy_relationships.json'
        ]
        
        json_path = None
        for p in possible_paths:
            if os.path.exists(p):
                json_path = p
                break
                
        if not json_path:
            return JsonResponse({"error": "JSON file not found on server"}, status=404)
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        count_rel = 0
        count_dur = 0
        
        for item in data:
            remedy_name = item.get('remedy')
            if not remedy_name:
                continue

            # 1. Update/Create Relationship
            try:
                obj, created = RemedyRelationship.objects.update_or_create(
                    remedy=remedy_name,
                    defaults={
                        'complements': item.get('complements', ''),
                        'follows': item.get('follows', ''),
                        'antidotes': item.get('antidotes', ''),
                        'inimical': item.get('inimical', ''),
                    }
                )
                if created: count_rel += 1
            except Exception as e:
                results["errors"].append(f"Rel Error {remedy_name}: {str(e)}")

            # 2. Update/Create Duration
            duration_val = item.get('duration', '')
            if duration_val:
                try:
                    obj, created = RemedyDuration.objects.update_or_create(
                        remedy=remedy_name,
                        defaults={
                            'duration': duration_val
                        }
                    )
                    if created: count_dur += 1
                except Exception as e:
                    results["errors"].append(f"Dur Error {remedy_name}: {str(e)}")
                    
        results["status"] = "completed"
        results["relationships_added"] = count_rel
        results["durations_added"] = count_dur
        results["total_relationships"] = RemedyRelationship.objects.count()
        results["total_durations"] = RemedyDuration.objects.count()
        
    except Exception as e:
        results["status"] = "failed"
        results["critical_error"] = str(e)

    return JsonResponse(results)
