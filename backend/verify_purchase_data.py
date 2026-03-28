#!/usr/bin/env python
"""验证现有购买数据一致性"""

import os
import sys
import django

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.products.models import Product, PurchaseHistory
from django.contrib.auth import get_user_model
User = get_user_model()

def verify_existing_data():
    """验证现有数据的一致性"""
    print("=== 验证现有购买数据一致性 ===")
    
    # 检查现有的购买历史记录
    purchase_histories = PurchaseHistory.objects.all()[:10]  # 只检查前10条
    
    print(f"找到 {PurchaseHistory.objects.count()} 条购买记录")
    
    if not purchase_histories:
        print("没有购买记录可供验证")
        return
    
    for i, history in enumerate(purchase_histories, 1):
        print(f"\n--- 记录 {i} ---")
        print(f"商品: {history.product.title}")
        print(f"买家: {history.buyer.nickname}")
        print(f"卖家: {history.seller.nickname}")
        print(f"购买数量: {history.quantity}")
        print(f"单价: ¥{history.unit_price}")
        print(f"总价: ¥{history.total_price}")
        print(f"购买时间: {history.purchased_at}")
        
        # 验证商品状态
        product = history.product
        print(f"商品状态: {product.status}")
        print(f"商品库存: {product.inventory}")
        
        # 检查是否存在重复购买
        duplicate_count = PurchaseHistory.objects.filter(
            product=history.product,
            buyer=history.buyer
        ).count()
        
        if duplicate_count > 1:
            print(f"⚠️  警告: 发现 {duplicate_count} 条重复购买记录")
        else:
            print("✅ 无重复购买记录")

def check_bought_products_view():
    """检查"我买到的"页面数据"""
    print("\n=== 检查'我买到的'页面数据 ===")
    
    # 获取一些有购买记录的用户
    buyers = User.objects.filter(purchases__isnull=False).distinct()[:3]
    
    for buyer in buyers:
        print(f"\n用户: {buyer.nickname}")
        bought_products = Product.objects.filter(buyer=buyer, status='sold')
        print(f"买到的商品数量: {bought_products.count()}")
        
        for product in bought_products:
            # 获取购买历史
            purchase_history = PurchaseHistory.objects.filter(
                product=product,
                buyer=buyer
            ).first()
            
            if purchase_history:
                print(f"  - {product.title}: 购买数量={purchase_history.quantity}")
            else:
                print(f"  - {product.title}: 无购买记录")

if __name__ == '__main__':
    verify_existing_data()
    check_bought_products_view()