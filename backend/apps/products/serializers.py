# backend/apps/products/serializers.py
from rest_framework import serializers
from .models import Product, ProductImage, WishItem, ChatMessage, ProductEvaluation, PurchaseHistory


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    seller_nickname = serializers.CharField(source='seller.nickname', read_only=True)
    seller_avatar = serializers.ImageField(source='seller.avatar', read_only=True)
    seller_credit_score = serializers.IntegerField(source='seller.credit_score', read_only=True)
    buyer_nickname = serializers.CharField(source='buyer.nickname', read_only=True)
    additional_images = ProductImageSerializer(many=True, read_only=True)
    
    # 为condition和inventory字段添加严格的验证
    condition = serializers.ChoiceField(
        choices=Product.CONDITION_CHOICES,
        error_messages={
            'required': '请选择新旧程度',
            'invalid_choice': '请选择有效的商品成色',
            'blank': '请选择新旧程度'
        }
    )
    
    inventory = serializers.IntegerField(
        min_value=1,
        error_messages={
            'required': '请输入库存数量',
            'min_value': '库存数量必须大于0',
            'invalid': '请输入有效的库存数量',
            'null': '库存数量不能为空'
        }
    )

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category', 'condition', 'status',
                  'dormitory_building', 'inventory', 'images', 'created_at', 'seller',
                  'buyer', 'seller_nickname', 'buyer_nickname', 'seller_avatar', 
                  'seller_credit_score', 'additional_images']
        read_only_fields = ['seller', 'created_at']
        
    def validate_condition(self, value):
        """验证新旧程度字段"""
        if not value or value.strip() == '':
            raise serializers.ValidationError('请选择新旧程度')
        return value
        
    def validate_inventory(self, value):
        """验证库存字段"""
        if value is None or value == '':
            raise serializers.ValidationError('请输入库存数量')
        if int(value) < 1:
            raise serializers.ValidationError('库存数量必须大于0')
        return int(value)


class PurchaseHistorySerializer(serializers.ModelSerializer):
    """购买历史序列化器"""
    buyer_nickname = serializers.CharField(source='buyer.nickname', read_only=True)
    seller_nickname = serializers.CharField(source='seller.nickname', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)
    purchased_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = PurchaseHistory
        fields = [
            'id', 'product', 'buyer', 'seller', 'quantity', 'unit_price', 
            'total_price', 'purchased_at', 'buyer_nickname', 'seller_nickname', 
            'product_title'
        ]


class BoughtProductSerializer(serializers.ModelSerializer):
    """我购买的商品序列化器（包含购买数量）"""
    seller_nickname = serializers.CharField(source='seller.nickname', read_only=True)
    seller_avatar = serializers.ImageField(source='seller.avatar', read_only=True)
    seller_credit_score = serializers.IntegerField(source='seller.credit_score', read_only=True)
    purchase_quantity = serializers.SerializerMethodField()
    purchased_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category', 'status',
                  'dormitory_building', 'inventory', 'images', 'created_at', 'seller',
                  'seller_nickname', 'seller_avatar', 'seller_credit_score', 
                  'purchase_quantity', 'purchased_at']
    
    def get_purchase_quantity(self, obj):
        """获取购买数量 - 基于唯一的购买历史记录"""
        try:
            purchase_history = obj.purchase_history.filter(buyer=self.context['request'].user).first()
            return purchase_history.quantity if purchase_history else 1
        except Exception as e:
            print(f"获取购买数量出错: {e}")
            return 1
    
    def get_purchased_at(self, obj):
        """获取购买时间"""
        try:
            purchase_history = obj.purchase_history.filter(buyer=self.context['request'].user).first()
            if purchase_history:
                return purchase_history.purchased_at.strftime('%Y-%m-%d %H:%M:%S')
            return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')


class SoldProductSerializer(serializers.ModelSerializer):
    """我卖出的商品序列化器（包含销售数量）"""
    buyer_nickname = serializers.CharField(source='buyer.nickname', read_only=True)
    buyer_avatar = serializers.ImageField(source='buyer.avatar', read_only=True)
    sale_quantity = serializers.SerializerMethodField()
    sold_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category', 'status',
                  'dormitory_building', 'inventory', 'images', 'created_at', 'buyer',
                  'buyer_nickname', 'buyer_avatar', 'sale_quantity', 'sold_at']
    
    def get_sale_quantity(self, obj):
        """获取销售数量 - 基于唯一的销售历史记录"""
        try:
            purchase_history = obj.purchase_history.filter(seller=self.context['request'].user).first()
            return purchase_history.quantity if purchase_history else 1
        except Exception as e:
            print(f"获取销售数量出错: {e}")
            return 1
    
    def get_sold_at(self, obj):
        """获取销售时间"""
        try:
            purchase_history = obj.purchase_history.filter(seller=self.context['request'].user).first()
            if purchase_history:
                return purchase_history.purchased_at.strftime('%Y-%m-%d %H:%M:%S')
            return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')


class WishItemSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)

    class Meta:
        model = WishItem
        fields = ['id', 'title', 'description', 'max_price', 'is_fulfilled',
                  'status', 'reject_reason', 'created_at', 'user',
                  'user_nickname', 'user_avatar']
        read_only_fields = ['user', 'created_at']


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_nickname = serializers.CharField(source='sender.nickname', read_only=True)
    receiver_nickname = serializers.CharField(source='receiver.nickname', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)
    wish_title = serializers.CharField(source='wish.title', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'receiver', 'product', 'wish', 'content', 
                  'is_read', 'created_at', 'sender_nickname', 'receiver_nickname',
                  'product_title', 'wish_title']
        read_only_fields = ['sender', 'created_at']


class ProductEvaluationSerializer(serializers.ModelSerializer):
    buyer_nickname = serializers.CharField(source='buyer.nickname', read_only=True)
    seller_nickname = serializers.CharField(source='seller.nickname', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)
    appeal_status_display = serializers.CharField(source='get_appeal_status_display', read_only=True)
    
    class Meta:
        model = ProductEvaluation
        fields = [
            'id', 'product', 'buyer', 'seller', 'received_item',
            'description_match', 'service_attitude', 'evidence_photos',
            'appeal_status', 'appeal_status_display', 'appeal_content',
            'appeal_evidence_photos', 'appeal_response', 'appeal_deadline', 
            'created_at', 'buyer_nickname', 'seller_nickname', 'product_title'
        ]
        read_only_fields = ['buyer', 'seller', 'created_at', 'appeal_status', 'appeal_deadline']