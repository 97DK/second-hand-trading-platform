#!/usr/bin/env python
"""直接调用 API 检查 num3 用户的已购买商品"""

import os
import sys
import django
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# 登录 num3 用户
session = requests.Session()

# 获取 CSRF token
csrf_response = session.get('http://localhost:8080/api/users/csrf/')
print(f"CSRF 响应状态码：{csrf_response.status_code}")

# 登录
login_data = {
    'username': 'num3',
    'password': 'TFBOYS2023',
    'user_type': 'student'
}
login_response = session.post(
    'http://localhost:8080/api/users/login/',
    json=login_data,
    headers={'X-CSRFToken': csrf_response.cookies.get('csrftoken')}
)
print(f"\n登录响应：{login_response.status_code}")
print(f"登录响应数据：{login_response.json()}")

# 获取已购买商品
bought_response = session.get(
    'http://localhost:8080/api/products/bought-products/',
    headers={'X-CSRFToken': csrf_response.cookies.get('csrftoken')}
)
print(f"\n已购买商品响应：{bought_response.status_code}")
bought_products = bought_response.json()
print(f"已购买商品数量：{len(bought_products)}")

if bought_products:
    print("\n已购买商品列表:")
    for product in bought_products[:10]:
        print(f"  - 商品 ID: {product['id']}, 标题：{product['title']}, 状态：{product['status']}")
        
        # 检查评价状态
        eval_response = session.get(
            f'http://localhost:8080/api/products/{product["id"]}/evaluate/',
            headers={'X-CSRFToken': csrf_response.cookies.get('csrftoken')}
        )
        evaluations = eval_response.json()
        if evaluations:
            print(f"    ✓ 已有 {len(evaluations)} 条评价")
        else:
            print(f"    ✗ 未评价")
