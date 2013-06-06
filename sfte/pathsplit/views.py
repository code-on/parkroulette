import json
from utils.views import render_to
from content.models import Path


@render_to('pathsplit-debug.html')
def debug(request):
    if 'id' in request.GET:
        path_id = int(request.GET['id'])
        route = Path.objects.get(path_id=path_id).path
        return {
            'route_json': json.dumps([i for i in route]),
            'route': route,
            'next_id': path_id + 1,
            'prev_id': path_id - 1,
        }
    return {}
