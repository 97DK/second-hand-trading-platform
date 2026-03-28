from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', '管理员'),
        ('student', '学生'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True, error_messages={'unique': '该学号已注册'})
    student_card_photo = models.ImageField(upload_to='student_cards/', null=False, blank=False, verbose_name='学生证照片')
    is_verified = models.BooleanField(default=False)
    nickname = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # 添加余额字段
    credit_score = models.IntegerField(default=100)  # 信用分，默认100分

    def save(self, *args, **kwargs):
        """
        重写保存方法，自动处理逻辑：
        1. 超级用户自动设置为管理员类型
        2. 学生自动生成昵称
        """
        # 如果是超级用户，自动设置为管理员类型
        if self.is_superuser:
            self.user_type = 'admin'
            self.is_verified = True  # 管理员默认已验证

        # 如果没设置昵称但有学号，自动生成默认昵称
        if not self.nickname and self.student_id:
            self.nickname = f"用户{self.student_id[-4:]}"  # 这里修复：添加了冒号

        # 调用父类的保存方法
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id} ({self.nickname})"


class PasswordResetRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    )
    student_id = models.CharField(max_length=20)
    student_name = models.CharField(max_length=50)
    student_card_photo = models.ImageField(upload_to='password_reset_cards/')
    new_password = models.CharField(max_length=128)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)


class CreditDeductionRecord(models.Model):
    """信用分扣分记录"""
    DEDUCTION_REASONS = (
        ('not_received', '未收到货物'),
        ('description_mismatch', '商品与描述不符'),
        ('poor_service', '服务态度差'),
    )
    
    APPEAL_STATUS = (
        ('pending', '待申诉'),
        ('submitted', '已申诉'),
        ('resolved', '已处理'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_deductions')
    deduction_points = models.IntegerField()  # 扣分数
    reason = models.CharField(max_length=20, choices=DEDUCTION_REASONS)
    description = models.TextField(blank=True)  # 详细说明
    appeal_status = models.CharField(max_length=10, choices=APPEAL_STATUS, default='pending')
    appeal_content = models.TextField(blank=True)  # 申诉内容
    appeal_response = models.TextField(blank=True)  # 申诉回复
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.nickname} - {self.get_reason_display()} (-{self.deduction_points}分)"