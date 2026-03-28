#!/usr/bin/env python
"""检查 num3 用户的购买和评价情况"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.products.models import Product, PurchaseHistory, ProductEvaluation
from django.contrib.auth import get_user_model
User = get_user_model()

print("=" * 60)
print("检查 num3 用户的购买和评价情况")
print("=" * 60)

try:
    num3_user = User.objects.get(username='num3')
    print(f"\n用户 ID: {num3_user.id}")
    print(f"用户名：{num3_user.username}")
    print(f"昵称：{num3_user.nickname}")
    print(f"是否已验证：{num3_user.is_verified}")
    
    # 检查购买历史
    purchase_history = PurchaseHistory.objects.filter(buyer=num3_user).select_related('product', 'seller')
    print(f"\n购买记录数量：{purchase_history.count()}")
    
    if purchase_history.exists():
        print("\n所有购买的商品:")
        for record in purchase_history:
            product = record.product
            print(f"\n  商品 ID: {product.id}")
            print(f"  标题：{product.title}")
            print(f"  状态：{product.status}")
            print(f"  买家字段：{product.buyer.nickname if product.buyer else 'None'}")
            print(f"  卖家：{product.seller.nickname if product.seller else 'None'}")
            
            # 检查是否有评价
            evaluations = ProductEvaluation.objects.filter(product=product, buyer=num3_user)
            if evaluations.exists():
                print(f"  ✓ 已有 {evaluations.count()} 条评价")
                for eval_item in evaluations:
                    print(f"    - 收到货：{eval_item.received_item}, 描述一致：{eval_item.description_match}, 服务态度：{eval_item.service_attitude}")
            else:
                print(f"  ✗ 未评价")
                
            # 检查是否可以评价（status='sold' 且 buyer 匹配）
            can_evaluate = (product.status == 'sold' and product.buyer == num3_user)
            print(f"  是否可评价：{can_evaluate}")
    else:
        print("该用户没有任何购买记录")
    
except User.DoesNotExist:
    print("用户 num3 不存在")
