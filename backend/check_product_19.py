#!/usr/bin/env python
"""检查商品 19 的详细信息"""

import os
import sys
import django

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.products.models import Product
from django.contrib.auth import get_user_model
User = get_user_model()

print("=" * 60)
print("检查商品 19 的详细信息")
print("=" * 60)

try:
    product_19 = Product.objects.get(id=19)
    print(f"\n商品 ID: {product_19.id}")
    print(f"商品标题：{product_19.title}")
    print(f"商品状态：{product_19.status}")
    print(f"卖家：{product_19.seller.nickname if product_19.seller else 'None'}")
    print(f"买家：{product_19.buyer.nickname if product_19.buyer else 'None'}")
    print(f"库存：{product_19.inventory}")
    print(f"价格：{product_19.price}")
    
    # 检查是否有评价
    evaluations = product_19.evaluations.all()
    print(f"\n评价数量：{evaluations.count()}")
    
    # 检查学生用户（sssass）是否是买家
    try:
        student_user = User.objects.get(username='sssass')
        print(f"\n学生用户 ID: {student_user.id}")
        print(f"学生用户是否是买家：{product_19.buyer == student_user}")
        
        # 检查该用户的购买历史
        from apps.products.models import PurchaseHistory
        purchase_history = PurchaseHistory.objects.filter(
            product=product_19,
            buyer=student_user
        )
        print(f"该用户是否有购买记录：{purchase_history.exists()}")
        if purchase_history.exists():
            for record in purchase_history:
                print(f"  - 购买时间：{record.purchased_at}, 数量：{record.quantity}")
        
    except User.DoesNotExist:
        print("学生用户 sssass 不存在")
    
except Product.DoesNotExist:
    print("商品 19 不存在")

print("\n" + "=" * 60)
print("检查所有状态为 sold 且有买家的商品")
print("=" * 60)

sold_products = Product.objects.filter(status='sold', buyer__isnull=False)[:5]
for p in sold_products:
    print(f"商品 ID: {p.id}, 标题：{p.title}, 买家：{p.buyer.nickname if p.buyer else 'None'}")
