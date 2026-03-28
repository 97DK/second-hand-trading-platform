#!/usr/bin/env python
"""测试购买数量数据一致性"""

import os
import sys
import django
from django.test import TestCase

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.products.models import Product, PurchaseHistory
from django.contrib.auth import get_user_model
User = get_user_model()

def test_purchase_consistency():
    """测试购买数量一致性"""
    print("=== 测试购买数量数据一致性 ===")
    
    # 创建测试用户
    buyer, created = User.objects.get_or_create(
        username='test_buyer',
        defaults={'nickname': '测试买家', 'balance': 1000}
    )
    
    seller, created = User.objects.get_or_create(
        username='test_seller',
        defaults={'nickname': '测试卖家', 'balance': 1000}
    )
    
    # 创建测试商品
    product, created = Product.objects.get_or_create(
        title='测试商品',
        defaults={
            'description': '测试商品描述',
            'price': 100,
            'category': 'other',
            'status': 'on_sale',
            'dormitory_building': '测试楼栋',
            'inventory': 10,
            'seller': seller
        }
    )
    
    print(f"商品信息: {product.title}, 库存: {product.inventory}")
    
    # 测试购买逻辑
    try:
        # 第一次购买
        quantity1 = 3
        total_price1 = product.price * quantity1
        
        # 模拟购买过程
        buyer.balance -= total_price1
        seller.balance += total_price1
        product.inventory -= quantity1
        product.buyer = buyer
        product.status = 'sold'
        product.save()
        
        # 创建购买历史
        purchase1 = PurchaseHistory.objects.create(
            product=product,
            buyer=buyer,
            seller=seller,
            quantity=quantity1,
            unit_price=product.price,
            total_price=total_price1
        )
        
        print(f"第一次购买: {quantity1}件")
        
        # 尝试第二次购买同一商品（应该失败）
        try:
            quantity2 = 2
            PurchaseHistory.objects.create(
                product=product,
                buyer=buyer,
                seller=seller,
                quantity=quantity2,
                unit_price=product.price,
                total_price=product.price * quantity2
            )
            print("❌ 错误：应该不允许同一买家重复购买同一商品")
        except Exception as e:
            print(f"✅ 正确：数据库约束阻止了重复购买 - {str(e)}")
        
        # 验证购买数量（获取最新的记录）
        purchase_history = PurchaseHistory.objects.filter(
            product=product, 
            buyer=buyer
        ).order_by('-purchased_at').first()
        
        if purchase_history and purchase_history.quantity == quantity1:
            print(f"✅ 购买数量一致：记录={purchase_history.quantity}, 实际={quantity1}")
        else:
            print(f"❌ 购买数量不一致：记录={purchase_history.quantity if purchase_history else 'None'}, 实际={quantity1}")
            
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

if __name__ == '__main__':
    test_purchase_consistency()