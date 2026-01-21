from django.http import JsonResponse
from django.conf import settings
import json
import os
from app.models import RemedyRelationship, RemedyDuration
from app.views import is_admin_authenticated

def trigger_import(request):
    # Use the same JWT auth as admin panel
    if not is_admin_authenticated(request):
        return JsonResponse({"error": "Unauthorized. Please login to admin panel first."}, status=403)

    results = {
        "status": "started",
        "relationships_added": 0,
        "durations_added": 0,
        "errors": []
    }
    
    try:
        # Use the new remedies_table.json file
        possible_paths = [
            os.path.join(settings.BASE_DIR, 'remedies_table.json'),
            'remedies_table.json'
        ]
        
        json_path = None
        for p in possible_paths:
            if os.path.exists(p):
                json_path = p
                break
                
        if not json_path:
            return JsonResponse({"error": "JSON file not found on server"}, status=404)
            
        with open(json_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # The new format has a "relationships" key
        data = raw_data.get('relationships', [])
            
        count_rel = 0
        count_dur = 0
        
        for item in data:
            remedy_name = item.get('remedy')
            if not remedy_name:
                continue

            # Map new field names to model fields
            # complementary -> complements (join array to string)
            # follows_well -> follows (join array to string)
            # inimicals -> inimical (join array to string)
            # antidotes -> antidotes (join array to string)
            
            complements = ', '.join(item.get('complementary', []))
            follows = ', '.join(item.get('follows_well', []))
            inimical = ', '.join(item.get('inimicals', []))
            antidotes = ', '.join(item.get('antidotes', []))
            duration_val = item.get('duration', '')

            # 1. Update/Create Relationship
            try:
                obj, created = RemedyRelationship.objects.update_or_create(
                    remedy=remedy_name,
                    defaults={
                        'complements': complements,
                        'follows': follows,
                        'antidotes': antidotes,
                        'inimical': inimical,
                    }
                )
                if created: count_rel += 1
            except Exception as e:
                results["errors"].append(f"Rel Error {remedy_name}: {str(e)}")

            # 2. Update/Create Duration
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

