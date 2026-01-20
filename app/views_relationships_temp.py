
@require_admin
def admin_relationships_list(request):
    """List all Remedy Relationships from DB"""
    from .models import RemedyRelationship
    
    # Fetch all records
    relationships = RemedyRelationship.objects.all().order_by('remedy')
    
    # Convert to list of dicts for consistency with template logic if needed, 
    # but object list is fine. We just need to group them.
    
    by_letter = {}
    for r in relationships:
        letter = r.remedy[0].upper() if r.remedy else 'A'
        if letter not in by_letter:
            by_letter[letter] = []
        by_letter[letter].append(r)
        
    context = {
        'authenticated': True,
        'source': 'relationships',
        'source_title': "Relationship Table",
        'relationships': relationships,
        'by_letter': dict(sorted(by_letter.items())),
        'total_count': relationships.count(),
    }
    return render(request, 'app/admin_relationships.html', context)

@require_admin
def admin_relationship_save(request):
    """Save edited relationship data via AJAX"""
    from django.http import JsonResponse
    from .models import RemedyRelationship
    
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=400)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'delete':
            pid = data.get('id')
            RemedyRelationship.objects.filter(id=pid).delete()
            return JsonResponse({'status': 'ok'})
            
        elif action == 'save':
            pid = data.get('id')
            
            defaults = {
                'remedy': data.get('remedy'),
                'complements': data.get('complements'),
                'follows': data.get('follows'),
                'antidotes': data.get('antidotes'),
                'inimical': data.get('inimical'),
                'duration': data.get('duration'),
            }
            
            if pid:
                # Update
                RemedyRelationship.objects.update_or_create(id=pid, defaults=defaults)
            else:
                # Create
                RemedyRelationship.objects.create(**defaults)
                
            return JsonResponse({'status': 'ok'})
            
        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
