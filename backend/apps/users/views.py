# backend/apps/users/views.py
from rest_framework import status
from apps.products.models import Product
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from .models import User, PasswordResetRequest, CreditDeductionRecord
from .serializers import UserSerializer, RegisterSerializer, PasswordResetRequestSerializer, CreditDeductionRecordSerializer, UserInfoUpdateSerializer
from django.contrib.auth import logout
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# 新增获取CSRF token的视图
@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        csrf_token = get_token(request)
        return Response({'csrfToken': csrf_token})


class LoginView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user_type = request.data.get('user_type', 'student')

        # 验证用户名是否为空
        if not username or not username.strip():
            return Response({
                'success': False,
                'message': '请输入用户名'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证密码是否为空
        if not password or not password.strip():
            return Response({
                'success': False,
                'message': '请输入密码'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 首先根据用户类型查找用户
        try:
            user = User.objects.get(username=username, user_type=user_type)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': '用户不存在'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证密码
        if not user.check_password(password):
            return Response({
                'success': False,
                'message': '密码错误'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 对于学生用户，检查是否已经通过审核
        if user.user_type == 'student' and not user.is_verified:
            return Response({
                'success': False,
                'message': '您的账号尚未通过审核，请耐心等待'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 登录用户
        login(request, user)

        return Response({
            'success': True,
            'user': UserSerializer(user).data,
            'message': '登录成功'
        })


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': '注册成功，请等待管理员审核'
            })

        # 处理验证错误，提供具体的错误信息
        errors = serializer.errors
        error_messages = []

        # 收集所有字段的错误信息
        for field, field_errors in errors.items():
            for error in field_errors:
                error_messages.append(str(error))

        return Response({
            'success': False,
            'message': '；'.join(error_messages) if error_messages else '注册失败'
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        # 使用序列化器处理文件上传和数据验证
        try:
            # 使用序列化器进行验证
            serializer = PasswordResetRequestSerializer(data=request.data)
            
            if not serializer.is_valid():
                # 格式化错误信息
                error_messages = []
                for field, errors in serializer.errors.items():
                    if isinstance(errors, list):
                        error_messages.extend([f"{field}: {error}" for error in errors])
                    else:
                        error_messages.append(f"{field}: {errors}")
                
                return Response({
                    'success': False,
                    'message': '; '.join(error_messages)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证通过，创建密码重置请求
            reset_request = serializer.save()
            
            return Response({
                'success': True,
                'message': '密码重置申请已提交，请等待管理员审核'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'提交失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 检查是否需要保持认证状态（用于测试）
        keep_auth = request.data.get('keep_auth', False)
        
        if not keep_auth:
            # 正常登出流程
            logout(request)
        
        return Response({
            'success': True,
            'message': '已成功退出登录'
        })


# 用户充值视图
class RechargeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 只有学生用户才能充值
        if request.user.user_type != 'student':
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)

        amount = request.data.get('amount')
        
        # 检查金额是否有效
        try:
            amount = Decimal(str(amount))
            if amount < Decimal('0.01') or amount > Decimal('9999'):
                return Response({'error': '充值金额必须在0.01-9999之间'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': '无效的金额'}, status=status.HTTP_400_BAD_REQUEST)

        # 增加余额
        request.user.balance += amount
        request.user.save()

        # 返回更新后的用户信息
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# 用户提现视图
class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 只有学生用户才能提现
        if request.user.user_type != 'student':
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)

        amount = request.data.get('amount')
        
        # 检查金额是否有效
        try:
            amount = Decimal(str(amount))
            if amount < Decimal('0.01') or amount > request.user.balance:
                return Response({'error': '提现金额无效'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': '无效的金额'}, status=status.HTTP_400_BAD_REQUEST)

        # 减少余额
        request.user.balance -= amount
        request.user.save()

        # 返回更新后的用户信息
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# 用户信息更新视图
class UserInfoUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        """更新用户头像和昵称"""
        user = request.user
        
        # 使用序列化器进行验证
        serializer = UserInfoUpdateSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新用户信息
        try:
            # 手动处理文件上传
            if 'avatar' in request.FILES:
                user.avatar = request.FILES['avatar']
            
            if 'nickname' in request.data:
                user.nickname = request.data['nickname'].strip()
            
            user.save()
            
            # 返回更新后的用户信息
            response_serializer = UserSerializer(user)
            return Response({
                'success': True,
                'message': '用户信息更新成功',
                'user': response_serializer.data
            })
        except Exception as e:
            return Response({
                'error': f'更新失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 管理员视图 - 用户管理
class AdminUserManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 只有管理员才能访问
        if request.user.user_type != 'admin':
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)

        # 获取查询参数 type，而不是 tab
        user_type = request.GET.get('type', 'pending')

        if user_type == 'pending':
            # 待审核用户：学生类型且未验证
            users = User.objects.filter(user_type='student', is_verified=False)
        elif user_type == 'verified':
            # 已审核用户：已验证的用户
            users = User.objects.filter(is_verified=True)
        else:
            # 所有用户
            users = User.objects.all()

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, user_id=None, action=None):
        # 只有管理员才能访问
        if request.user.user_type != 'admin':
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)

        # 如果提供了user_id和action，直接处理对应操作
        if user_id and action:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

            if action == 'approve':
                user.is_verified = True
                user.save()
                return Response({'success': True, 'message': '用户已通过审核'})
            elif action == 'reject':
                user.delete()
                return Response({'success': True, 'message': '用户已被拒绝'})
            else:
                return Response({'error': '无效的操作'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 否则按原来的方式处理（从request.data获取action）
        elif user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

            action = request.data.get('action')

            if action == 'approve':
                user.is_verified = True
                user.save()
                return Response({'success': True, 'message': '用户已通过审核'})
            elif action == 'reject':
                user.delete()
                return Response({'success': True, 'message': '用户已被拒绝'})
            else:
                return Response({'error': '无效的操作'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': '缺少用户ID'}, status=status.HTTP_400_BAD_REQUEST)


# 管理员视图 - 数据统计面板
class AnalyticsDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 只有管理员才能访问
        if request.user.user_type != 'admin':
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)

        # 统计数据
        total_users = User.objects.count()
        verified_users = User.objects.filter(is_verified=True).count()
        total_products = Product.objects.count()
        on_sale_products = Product.objects.filter(status='on_sale').count()

        # 近7天新增用户数
        week_ago = timezone.now() - timedelta(days=7)
        new_users_last_week = User.objects.filter(date_joined__gte=week_ago).count()

        data = {
            'total_users': total_users,
            'verified_users': verified_users,
            'total_products': total_products,
            'on_sale_products': on_sale_products,
            'new_users_last_week': new_users_last_week,
        }

        return Response(data)


# 信用分相关API

class CreditScoreView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取当前用户的信用分"""
        user = request.user
        return Response({
            'credit_score': user.credit_score,
            'message': '您的信用极佳，请继续保持！' if user.credit_score == 100 else '您的信用分有待提升'
        })
    
    def patch(self, request):
        """更新用户信用分（仅管理员可用）"""
        if request.user.user_type != 'admin':
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        new_score = request.data.get('credit_score')
        
        try:
            target_user = User.objects.get(id=user_id)
            target_user.credit_score = new_score
            target_user.save()
            return Response({
                'success': True,
                'message': '信用分更新成功',
                'credit_score': target_user.credit_score
            })
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)


class CreditDeductionListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取当前用户的信用分扣分记录"""
        deductions = CreditDeductionRecord.objects.filter(user=request.user).order_by('-created_at')
        serializer = CreditDeductionRecordSerializer(deductions, many=True)
        return Response(serializer.data)


class CreditAppealView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, deduction_id):
        """提交信用分申诉"""
        try:
            deduction = CreditDeductionRecord.objects.get(id=deduction_id, user=request.user)
        except CreditDeductionRecord.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        appeal_content = request.data.get('appeal_content', '')
        if not appeal_content:
            return Response({'error': '申诉内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        deduction.appeal_status = 'submitted'
        deduction.appeal_content = appeal_content
        deduction.save()
        
        serializer = CreditDeductionRecordSerializer(deduction)
        return Response({
            'success': True,
            'message': '申诉提交成功',
            'data': serializer.data
        })


# 管理员视图 - 用户统计
class UserStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 只有管理员才能访问
        if request.user.user_type != 'admin':
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)

        # 总用户数
        total_users = User.objects.count()
        
        # 学生用户总数
        student_users = User.objects.filter(user_type='student').count()
        
        # 已验证学生用户
        verified_students = User.objects.filter(user_type='student', is_verified=True).count()
        
        # 待验证学生用户
        pending_students = User.objects.filter(user_type='student', is_verified=False).count()
        
        # 管理员用户
        admin_users = User.objects.filter(user_type='admin').count()

        data = {
            'total_users': total_users,
            'student_users': student_users,
            'verified_students': verified_students,
            'pending_students': pending_students,
            'admin_users': admin_users
        }

        return Response(data)