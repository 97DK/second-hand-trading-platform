# backend/apps/products/models.py
from django.db import models
from django.conf import settings


class Product(models.Model):
    STATUS_CHOICES = (
        ('on_sale', '出售中'),
        ('sold', '已售出'),
        ('removed', '已下架'),
    )
    CATEGORY_CHOICES = (
        ('book', '教材图书'),
        ('digital', '数码产品'),
        ('life', '生活用品'),
        ('other', '其他'),
    )
    
    CONDITION_CHOICES = (
        ('new', '全新'),
        ('nine', '九成新'),
        ('eight', '八成新'),
        ('seven', '七成新'),
        ('below_six', '六成新及以下'),
    )

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sold_products')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='bought_products')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new', verbose_name='新旧程度')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='on_sale')
    dormitory_building = models.CharField(max_length=50)
    inventory = models.PositiveIntegerField(default=1, verbose_name='库存数量')
    # Main image for list display
    images = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# 购买历史模型
class PurchaseHistory(models.Model):
    """记录商品购买历史"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_history')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sales')
    quantity = models.PositiveIntegerField(verbose_name='购买数量')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总价')
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name='购买时间')
    
    class Meta:
        ordering = ['-purchased_at']
        verbose_name = '购买历史'
        verbose_name_plural = '购买历史'
        # 移除唯一约束，允许同一买家对同一商品多次购买
        # unique_together = ('product', 'buyer')
    
    def __str__(self):
        return f"{self.buyer.nickname} 购买了 {self.quantity} 件 {self.product.title}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)


class WishItem(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '被拒绝'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_fulfilled = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reject_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


# 聊天消息模型
class ChatMessage(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_messages')
    wish = models.ForeignKey(WishItem, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class ProductEvaluation(models.Model):
    """商品评价模型"""
    EVALUATION_CHOICES = (
        ('yes', '是'),
        ('no', '否'),
    )
    
    APPEAL_STATUS = (
        ('pending', '待申诉'),
        ('submitted', '已申诉'),
        ('resolved', '已处理'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='evaluations')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_evaluations')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_evaluations')
    
    # 三个评价维度
    received_item = models.CharField(max_length=3, choices=EVALUATION_CHOICES, verbose_name='是否收到货')
    description_match = models.CharField(max_length=3, choices=EVALUATION_CHOICES, verbose_name='是否与商品描述一致')
    service_attitude = models.CharField(max_length=3, choices=EVALUATION_CHOICES, verbose_name='商家服务态度')
    
    # 评价证据照片
    evidence_photos = models.JSONField(default=list, blank=True, verbose_name='评价证据照片')
    
    # 申诉相关字段
    appeal_status = models.CharField(max_length=10, choices=APPEAL_STATUS, default='pending', verbose_name='申诉状态')
    appeal_content = models.TextField(blank=True, verbose_name='申诉内容')
    appeal_evidence_photos = models.JSONField(default=list, blank=True, verbose_name='申诉证据照片')
    appeal_response = models.TextField(blank=True, verbose_name='申诉回复')
    appeal_deadline = models.DateTimeField(null=True, blank=True, verbose_name='申诉截止时间')
    
    # 评价时间
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('product', 'buyer')  # 每个买家对同一商品只能评价一次
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.buyer.nickname} 对 {self.product.title} 的评价"
    
    def calculate_deduction_points(self):
        """计算应该扣除的信用分数"""
        deduction = 0
        if self.received_item == 'no':
            deduction += 10
        if self.description_match == 'no':
            deduction += 5
        if self.service_attitude == 'no':
            deduction += 2
        return deduction
    
    def get_deduction_reasons(self):
        """获取扣分原因列表"""
        reasons = []
        if self.received_item == 'no':
            reasons.append('not_received')
        if self.description_match == 'no':
            reasons.append('description_mismatch')
        if self.service_attitude == 'no':
            reasons.append('poor_service')
        return reasons