# backend/apps/users/serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, PasswordResetRequest, CreditDeductionRecord


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar', 'student_id', 'is_verified', 'user_type', 'student_card_photo', 'balance', 'credit_score']
        read_only_fields = ['student_id', 'is_verified', 'user_type']


class UserInfoUpdateSerializer(serializers.ModelSerializer):
    """用户信息更新序列化器"""
    class Meta:
        model = User
        fields = ['nickname', 'avatar']
    
    def validate_nickname(self, value):
        """验证昵称"""
        if value is not None:
            if len(value.strip()) == 0:
                raise serializers.ValidationError("昵称不能为空")
            if len(value) > 50:
                raise serializers.ValidationError("昵称长度不能超过50个字符")
        return value
    
    def validate_avatar(self, value):
        """验证头像"""
        if value is not None:
            # 验证文件类型
            if not value.content_type.startswith('image/'):
                raise serializers.ValidationError("请上传有效的图片文件")
            
            # 验证文件大小（5MB）
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("头像文件大小不能超过5MB")
        return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True, error_messages={'required': '请确认密码'})
    student_card_photo = serializers.ImageField(required=True, error_messages={'required': '请上传学生证照片'})

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'student_id', 'student_card_photo']

    def validate_username(self, value):
        """验证用户名是否唯一"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("该用户名已被使用")
        return value
    
    def validate(self, attrs):
        """整体验证"""
        # 调用父类验证
        attrs = super().validate(attrs)
        
        # 验证密码和确认密码是否一致
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("两次输入的密码不一致")
        
        # 验证密码长度
        if len(attrs.get('password', '')) < 8:
            raise serializers.ValidationError("密码长度不能少于8位")
        
        # 删除confirm_password，因为它不需要保存到数据库
        attrs.pop('confirm_password', None)
        
        return attrs

    def validate_student_id(self, value):
        """验证学号是否唯一"""
        if User.objects.filter(student_id=value).exists():
            raise serializers.ValidationError("该学号已注册")
        return value
    
    def validate_student_card_photo(self, value):
        """验证学生证照片"""
        if not value or not hasattr(value, 'content_type'):
            raise serializers.ValidationError("请上传学生证照片")
        
        # 验证文件类型
        if not value.content_type.startswith('image/'):
            raise serializers.ValidationError("请上传有效的图片文件")
        
        # 验证文件大小（7MB）
        if value.size > 7 * 1024 * 1024:
            raise serializers.ValidationError("学生证照片大小不能超过7MB")
        
        return value

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class PasswordResetRequestSerializer(serializers.ModelSerializer):
    student_card_photo = serializers.ImageField(required=True, error_messages={'required': '请上传学生证照片'})
    
    class Meta:
        model = PasswordResetRequest
        fields = ['student_id', 'student_name', 'student_card_photo', 'new_password']

    def validate_student_id(self, value):
        """验证学号"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("学号不能为空")
        if len(value) > 20:
            raise serializers.ValidationError("学号长度不能超过20位")
        return value.strip()
    
    def validate_student_name(self, value):
        """验证姓名"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("姓名不能为空")
        if len(value) > 50:
            raise serializers.ValidationError("姓名长度不能超过50位")
        return value.strip()
    
    def validate_new_password(self, value):
        """验证新密码"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("新密码不能为空")
        if len(value) < 8:
            raise serializers.ValidationError("密码长度不能少于8位")
        return value.strip()
    
    def validate_student_card_photo(self, value):
        """验证学生证照片"""
        if not value:
            raise serializers.ValidationError("请上传学生证照片")
        if not hasattr(value, 'content_type'):
            raise serializers.ValidationError("请上传学生证照片")
        
        # 验证文件类型
        if not value.content_type.startswith('image/'):
            raise serializers.ValidationError("请上传有效的图片文件")
        
        # 验证文件大小（7MB）
        if value.size > 7 * 1024 * 1024:
            raise serializers.ValidationError("学生证照片大小不能超过7MB")
        
        return value
    
    def validate(self, attrs):
        """整体验证"""
        # 调用父类验证
        attrs = super().validate(attrs)
        return attrs

    def create(self, validated_data):
        validated_data['new_password'] = make_password(validated_data['new_password'])
        return super().create(validated_data)


class CreditDeductionRecordSerializer(serializers.ModelSerializer):
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    appeal_status_display = serializers.CharField(source='get_appeal_status_display', read_only=True)
    
    class Meta:
        model = CreditDeductionRecord
        fields = [
            'id', 'user', 'deduction_points', 'reason', 'reason_display',
            'description', 'appeal_status', 'appeal_status_display',
            'appeal_content', 'appeal_response', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']