"""
全局请求/响应日志中间件
用于调试所有接口的详细信息
"""

import json
import logging
from django.http import HttpRequest, HttpResponse

# 配置日志
logger = logging.getLogger('debug_logger')
logger.setLevel(logging.DEBUG)

class DebugLoggingMiddleware:
    """
    全局调试日志中间件
    记录所有请求的详细信息（数据、文件、headers等）
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # 记录请求开始
        self.log_request_start(request)
        
        # 处理请求
        response = self.get_response(request)
        
        # 记录响应结束
        self.log_response_end(request, response)
        
        return response
    
    def log_request_start(self, request):
        """记录请求开始的详细信息"""
        try:
            # 基本信息
            method = request.method
            path = request.path
            content_type = request.content_type or 'unknown'
            
            # 请求数据（根据content_type处理）
            if content_type and 'application/json' in content_type:
                try:
                    request_data = json.loads(request.body.decode('utf-8'))
                except:
                    request_data = str(request.body)
            elif content_type and 'multipart/form-data' in content_type:
                # multipart/form-data需要特殊处理
                request_data = {
                    'POST': dict(request.POST),
                    'FILES': list(request.FILES.keys()) if hasattr(request, 'FILES') else []
                }
            else:
                request_data = dict(request.GET) if request.method == 'GET' else dict(request.POST)
            
            # headers
            headers = {k: v for k, v in request.META.items() if k.startswith('HTTP_') or k in ['CONTENT_TYPE', 'CONTENT_LENGTH']}
            
            # 日志输出
            logger.debug(f"=== REQUEST START ===")
            logger.debug(f"Method: {method}")
            logger.debug(f"Path: {path}")
            logger.debug(f"Content-Type: {content_type}")
            logger.debug(f"Headers: {headers}")
            logger.debug(f"Request Data: {request_data}")
            logger.debug(f"Files: {list(request.FILES.keys()) if hasattr(request, 'FILES') else []}")
            logger.debug(f"User: {getattr(request, 'user', 'Anonymous')}")
            logger.debug(f"=== REQUEST END ===")
            
        except Exception as e:
            logger.error(f"日志记录错误: {str(e)}")
    
    def log_response_end(self, request, response):
        """记录响应结束的详细信息"""
        try:
            # 响应状态码和内容
            status_code = response.status_code
            content_type = response.get('Content-Type', 'unknown')
            
            # 响应内容（如果是JSON）
            if content_type and 'application/json' in content_type:
                try:
                    response_content = json.loads(response.content.decode('utf-8'))
                except:
                    response_content = str(response.content)
            else:
                response_content = str(response.content)[:200] + ('...' if len(str(response.content)) > 200 else '')
            
            logger.debug(f"=== RESPONSE END ===")
            logger.debug(f"Status Code: {status_code}")
            logger.debug(f"Content-Type: {content_type}")
            logger.debug(f"Response Content: {response_content}")
            logger.debug(f"=== RESPONSE END ===")
            
        except Exception as e:
            logger.error(f"响应日志记录错误: {str(e)}")