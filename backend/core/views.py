from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def home(request):
    """
    首页视图 - 返回API信息
    """
    data = {
        'message': '欢迎使用校园二手交易平台API',
        'version': '1.0.0',
        'available_endpoints': {
            'admin': '/admin/',
            'users_api': '/api/users/',
            'products_api': '/api/products/',
        },
        'description': '这是一个基于Django REST Framework构建的校园二手交易平台后端API'
    }
    return JsonResponse(data, status=200)

@csrf_exempt 
def health_check(request):
    """
    健康检查端点
    """
    return JsonResponse({'status': 'healthy', 'message': 'Server is running'}, status=200)