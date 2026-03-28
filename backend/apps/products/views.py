# backend/apps/products/views.py
from rest_framework import generics, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Product, ProductImage, WishItem, ChatMessage, ProductEvaluation, PurchaseHistory
from .serializers import ProductSerializer, WishItemSerializer, ChatMessageSerializer, ProductEvaluationSerializer, BoughtProductSerializer, SoldProductSerializer, PurchaseHistorySerializer
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework import status
from decimal import Decimal
from django.db.models import Q, Max, Count
from django.utils import timezone
from datetime import timedelta


# 自定义过滤器
class ProductFilter(FilterSet):
    search = CharFilter(field_name='title', lookup_expr='icontains')
    
    class Meta:
        model = Product
        fields = ['category', 'search']


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(status='on_sale')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user, status='pending')


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# 商品购买视图
class PurchaseProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        try:
            # 获取商品
            product = Product.objects.get(id=product_id, status='on_sale')
            
            # 检查买家是否为卖家本人
            if product.seller == request.user:
                return Response(
                    {'error': '不能购买自己发布的商品'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 获取购买数量
            quantity_str = request.data.get('quantity', '1')
            
            # 严格验证数量输入
            try:
                # 先转换为浮点数再转为整数，处理各种输入格式
                quantity_float = float(str(quantity_str).strip())
                quantity = int(quantity_float)
                
                # 验证转换后是否等于原值（防止科学计数法等问题）
                if str(quantity) != str(int(quantity_float)):
                    raise ValueError('数量格式不正确')
                    
            except (ValueError, TypeError) as e:
                return Response(
                    {'error': f'购买数量必须是有效的正整数: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 验证数量范围 - 加强验证，明确禁止0和负数
            if quantity <= 0:
                return Response(
                    {'error': '购买数量必须大于0'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 检查库存是否足够
            if quantity > product.inventory:
                return Response(
                    {'error': f'库存不足，当前库存仅剩{product.inventory}件'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 再次验证库存（双重检查）
            product.refresh_from_db()
            if quantity > product.inventory:
                return Response(
                    {'error': f'库存不足，当前库存仅剩{product.inventory}件'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 计算总价格
            total_price = product.price * quantity
            
            # 检查余额是否足够
            if request.user.balance < total_price:
                return Response(
                    {'error': '余额不足，请充值后再购买'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 使用数据库事务确保数据一致性
            from django.db import transaction
            with transaction.atomic():
                # 重新获取最新的商品信息
                product = Product.objects.select_for_update().get(id=product_id, status='on_sale')
                
                # 最终验证库存
                if quantity > product.inventory:
                    raise ValueError(f'库存不足，当前库存仅剩{product.inventory}件')
                
                # 执行交易
                # 1. 扣除买家余额
                request.user.balance -= total_price
                request.user.save()
                
                # 2. 增加卖家余额
                product.seller.balance += total_price
                product.seller.save()
                
                # 3. 扣减库存
                product.inventory -= quantity
                
                # 4. 如果库存为0，自动下架商品
                if product.inventory == 0:
                    product.status = 'removed'
                
                # 5. 更新买家信息（重要：每次购买都要记录）
                # 修改逻辑：只要有购买行为就记录买家信息
                if not product.buyer:
                    product.buyer = request.user
                
                # 如果是完全售罄，则标记为已售出
                if product.inventory == 0:
                    product.status = 'sold'
                
                product.save()
                
                # 6. 创建购买历史记录
                from .models import PurchaseHistory
                PurchaseHistory.objects.create(
                    product=product,
                    buyer=request.user,
                    seller=product.seller,
                    quantity=quantity,
                    unit_price=product.price,
                    total_price=total_price
                )
            
            # 发送系统消息给卖家
            ChatMessage.objects.create(
                sender=request.user,
                receiver=product.seller,
                product=product,
                content="我已购买，请准备交货事宜~"
            )
            
            # 返回成功信息
            return Response({
                'success': True,
                'message': '购买成功',
                'product': ProductSerializer(product).data
            })
            
        except Product.DoesNotExist:
            return Response(
                {'error': '商品不存在或不可购买'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # 打印详细错误信息以便调试
            print(f"Purchase error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'购买失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MyProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        status = self.request.query_params.get('status', None)
        queryset = Product.objects.filter(seller=self.request.user)

        if status:
            queryset = queryset.filter(status=status)

        return queryset


class BoughtProductsView(APIView):
    """用户购买的商品视图 - 基于PurchaseHistory实现"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 获取用户的购买历史
        purchase_history = PurchaseHistory.objects.filter(
            buyer=request.user
        ).select_related('product', 'seller').order_by('-purchased_at')
        
        # 构造返回数据
        bought_products = []
        for history in purchase_history:
            product_data = {
                'id': history.product.id,
                'title': history.product.title,
                'description': history.product.description,
                'price': history.product.price,
                'category': history.product.category,
                'status': history.product.status,
                'dormitory_building': history.product.dormitory_building,
                'inventory': history.product.inventory,
                'images': history.product.images.url if history.product.images else None,
                'created_at': history.product.created_at,
                'seller_nickname': history.seller.nickname,
                'seller_avatar': history.seller.avatar.url if history.seller.avatar else None,
                'seller_credit_score': history.seller.credit_score,
                'purchase_quantity': history.quantity,
                'purchased_at': history.purchased_at.strftime('%Y-%m-%d %H:%M:%S'),
                'unit_price': history.unit_price,
                'total_price': history.total_price
            }
            bought_products.append(product_data)
        
        return Response(bought_products)


class SoldProductsView(generics.ListAPIView):
    """用户卖出的商品视图"""
    serializer_class = SoldProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user, status='sold').order_by('-created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


# 心愿相关视图
class WishItemListView(generics.ListCreateAPIView):
    serializer_class = WishItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # 只返回已审核通过的心愿
        return WishItem.objects.filter(status='approved').order_by('-created_at')

    def perform_create(self, serializer):
        # 创建时默认为待审核状态
        serializer.save(user=self.request.user, status='pending')


class UserWishItemsView(generics.ListAPIView):
    serializer_class = WishItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 返回当前用户的所有心愿
        return WishItem.objects.filter(user=self.request.user)


class AdminWishManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 检查是否为管理员
        if request.user.user_type != 'admin':
            return Response({'error': 'Permission denied'}, status=403)

        # 根据查询参数返回不同类型的数据
        filter_type = request.query_params.get('type', 'pending')

        if filter_type == 'pending':
            # 待审核心愿
            wishes = WishItem.objects.filter(status='pending')
        elif filter_type == 'approved':
            # 已审核心愿
            wishes = WishItem.objects.filter(status='approved')
        elif filter_type == 'rejected':
            # 被拒绝心愿
            wishes = WishItem.objects.filter(status='rejected')
        else:
            wishes = WishItem.objects.all()

        serializer = WishItemSerializer(wishes, many=True)
        return Response(serializer.data)

    def post(self, request):
        # 检查是否为管理员
        if request.user.user_type != 'admin':
            return Response({'error': 'Permission denied'}, status=403)

        wish_id = request.data.get('wish_id')
        action = request.data.get('action')

        try:
            wish = WishItem.objects.get(id=wish_id)

            if action == 'approve':
                wish.status = 'approved'
                wish.save()
                return Response({'success': True, 'message': '心愿已通过审核'})
            elif action == 'reject':
                wish.status = 'rejected'
                wish.reject_reason = request.data.get('reason', '')
                wish.save()
                return Response({'success': True, 'message': '心愿已被拒绝'})
        except WishItem.DoesNotExist:
            return Response({'error': '心愿不存在'}, status=404)


class AdminProductManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 检查是否为管理员
        if request.user.user_type != 'admin':
            return Response({'error': 'Permission denied'}, status=403)

        # 根据查询参数返回不同类型的数据
        filter_type = request.query_params.get('type', 'pending')

        if filter_type == 'pending':
            # 待审核商品
            products = Product.objects.filter(status='pending')
        elif filter_type == 'approved':
            # 已审核商品
            products = Product.objects.exclude(status='pending')
        elif filter_type == 'rejected':
            # 被拒绝商品
            products = Product.objects.filter(status='rejected')
        else:
            products = Product.objects.all()

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        # 检查是否为管理员
        if request.user.user_type != 'admin':
            return Response({'error': 'Permission denied'}, status=403)

        product_id = request.data.get('product_id')
        action = request.data.get('action')

        try:
            product = Product.objects.get(id=product_id)

            if action == 'approve':
                product.status = 'on_sale'
                product.save()
                return Response({'success': True, 'message': '商品已上架'})
            elif action == 'reject':
                product.status = 'rejected'
                product.reject_reason = request.data.get('reason', '')
                product.save()
                return Response({'success': True, 'message': '商品已被拒绝'})
            elif action == 'remove':
                product.status = 'removed'
                product.save()
                return Response({'success': True, 'message': '商品已下架'})
        except Product.DoesNotExist:
            return Response({'error': '商品不存在'}, status=404)


# 聊天相关视图
class ChatMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """发送消息"""
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            # 设置发送者为当前用户
            serializer.save(sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        """获取聊天记录"""
        # 获取与当前用户相关的所有聊天记录（发送的和接收的）
        messages = ChatMessage.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)
        ).order_by('-created_at')
        
        # 序列化数据
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)


class ChatConversationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        """获取与特定用户的聊天记录"""
        # 获取与特定用户的聊天记录
        messages = ChatMessage.objects.filter(
            (Q(sender=request.user) & Q(receiver_id=user_id)) |
            (Q(sender_id=user_id) & Q(receiver=request.user))
        ).order_by('created_at')
        
        # 标记为已读
        messages.filter(receiver=request.user, is_read=False).update(is_read=True)
        
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)


class UnreadMessagesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取未读消息数量"""
        unread_count = ChatMessage.objects.filter(
            receiver=request.user, 
            is_read=False
        ).count()
        
        return Response({'unread_count': unread_count})


class ContactSellerView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, product_id):
        """联系卖家"""
        try:
            product = Product.objects.get(id=product_id)
            content = request.data.get('content', '我想了解这个商品')
            
            # 创建聊天消息
            message = ChatMessage.objects.create(
                sender=request.user,
                receiver=product.seller,
                product=product,
                content=content
            )
            
            serializer = ChatMessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({'error': '商品不存在'}, status=status.HTTP_404_NOT_FOUND)


class ContactWishUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, wish_id):
        """联系心愿发布者"""
        try:
            wish = WishItem.objects.get(id=wish_id)
            content = request.data.get('content', '我有你想要的商品')
            
            # 创建聊天消息
            message = ChatMessage.objects.create(
                sender=request.user,
                receiver=wish.user,
                wish=wish,
                content=content
            )
            
            serializer = ChatMessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except WishItem.DoesNotExist:
            return Response({'error': '心愿不存在'}, status=status.HTTP_404_NOT_FOUND)


# 申诉相关API
@method_decorator(csrf_exempt, name='dispatch')
class AppealEvaluationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, evaluation_id):
        """提交申诉"""
        try:
            evaluation = ProductEvaluation.objects.get(id=evaluation_id, seller=request.user)
        except ProductEvaluation.DoesNotExist:
            return Response({'error': '评价不存在或您无权限操作'}, status=status.HTTP_404_NOT_FOUND)
        
        # 检查是否还在申诉期限内
        if evaluation.appeal_deadline and timezone.now() > evaluation.appeal_deadline:
            return Response({'error': '申诉期限已过'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查申诉状态
        if evaluation.appeal_status != 'pending':
            return Response({'error': '该评价已处理或已在申诉中'}, status=status.HTTP_400_BAD_REQUEST)
        
        appeal_content = request.data.get('appeal_content', '').strip()
        appeal_evidence_photos = request.data.get('appeal_evidence_photos', [])
        
        if not appeal_content:
            return Response({'error': '请输入申诉内容'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新申诉状态
        evaluation.appeal_status = 'submitted'
        evaluation.appeal_content = appeal_content
        # 如果有申诉证据照片，则保存
        if appeal_evidence_photos:
            evaluation.appeal_evidence_photos = appeal_evidence_photos
        evaluation.save()
        
        # 发送通知给买家
        ChatMessage.objects.create(
            sender=request.user,
            receiver=evaluation.buyer,
            product=evaluation.product,
            content=f"卖家对您的评价提出了申诉，请等待管理员处理。"
        )
        
        serializer = ProductEvaluationSerializer(evaluation)
        return Response({
            'success': True,
            'message': '申诉提交成功，等待管理员处理',
            'data': serializer.data
        })
    
    def get(self, request, evaluation_id):
        """获取申诉详情"""
        try:
            evaluation = ProductEvaluation.objects.get(id=evaluation_id, seller=request.user)
            serializer = ProductEvaluationSerializer(evaluation)
            return Response(serializer.data)
        except ProductEvaluation.DoesNotExist:
            return Response({'error': '评价不存在或您无权限查看'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name='dispatch')
class AdminAppealManagementView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取待处理的申诉"""
        if request.user.user_type != 'admin':
            return Response({'error': 'Permission denied'}, status=403)
        
        # 获取所有已提交申诉的评价
        appeals = ProductEvaluation.objects.filter(appeal_status='submitted')
        serializer = ProductEvaluationSerializer(appeals, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """处理申诉"""
        if request.user.user_type != 'admin':
            return Response({'error': 'Permission denied'}, status=403)
        
        evaluation_id = request.data.get('evaluation_id')
        action = request.data.get('action')  # 'approve' 或 'reject'
        response_content = request.data.get('response_content', '')
        
        try:
            evaluation = ProductEvaluation.objects.get(id=evaluation_id)
        except ProductEvaluation.DoesNotExist:
            return Response({'error': '评价不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        if evaluation.appeal_status != 'submitted':
            return Response({'error': '该评价不在申诉状态'}, status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'approve':
            # 申诉成功，不扣除信用分
            evaluation.appeal_status = 'resolved'
            evaluation.appeal_response = f'申诉通过：{response_content}'
            evaluation.save()
            
            # 通知双方
            ChatMessage.objects.create(
                sender=request.user,
                receiver=evaluation.seller,
                product=evaluation.product,
                content=f"您的申诉已通过，不会扣除信用分。"
            )
            ChatMessage.objects.create(
                sender=request.user,
                receiver=evaluation.buyer,
                product=evaluation.product,
                content=f"您对商品的评价存在争议，申诉已通过。"
            )
            
            return Response({'success': True, 'message': '申诉处理完成，维持原评价'})
            
        elif action == 'reject':
            # 申诉失败，扣除信用分
            deduction_points = evaluation.calculate_deduction_points()
            if deduction_points > 0:
                # 扣除卖家信用分
                evaluation.seller.credit_score -= deduction_points
                evaluation.seller.save()
                
                # 创建信用分扣分记录
                from apps.users.models import CreditDeductionRecord
                reasons = evaluation.get_deduction_reasons()
                for reason in reasons:
                    CreditDeductionRecord.objects.create(
                        user=evaluation.seller,
                        deduction_points=10 if reason == 'not_received' else (5 if reason == 'description_mismatch' else 2),
                        reason=reason,
                        description=f'商品评价扣分（申诉失败）：{evaluation.product.title}'
                    )
                
                # 扣除买家恶意评价分（1分）
                evaluation.buyer.credit_score -= 1
                evaluation.buyer.save()
                
                # 创建恶意评价扣分记录
                CreditDeductionRecord.objects.create(
                    user=evaluation.buyer,
                    deduction_points=1,
                    reason='malicious_review',
                    description=f'恶意评价扣分：{evaluation.product.title}'
                )
            
            evaluation.appeal_status = 'resolved'
            evaluation.appeal_response = f'申诉驳回：{response_content}'
            evaluation.save()
            
            # 通知双方
            ChatMessage.objects.create(
                sender=request.user,
                receiver=evaluation.seller,
                product=evaluation.product,
                content=f"您的申诉被驳回，信用分已被扣除。"
            )
            ChatMessage.objects.create(
                sender=request.user,
                receiver=evaluation.buyer,
                product=evaluation.product,
                content=f"卖家的申诉被驳回，评价有效。"
            )
            
            return Response({
                'success': True, 
                'message': f'申诉处理完成，扣除信用分{deduction_points}分',
                'deduction_points': deduction_points
            })
        
        return Response({'error': '无效的操作'}, status=status.HTTP_400_BAD_REQUEST)


# 获取卖家负面评价列表
class SellerNegativeEvaluationsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取当前卖家收到的所有负面评价"""
        # 获取当前用户作为卖家收到的所有评价
        evaluations = ProductEvaluation.objects.filter(
            seller=request.user
        ).select_related('product', 'buyer').order_by('-created_at')
        
        # 筛选出负面评价（有任何一项为'no'的评价）
        negative_evaluations = []
        for evaluation in evaluations:
            if (evaluation.received_item == 'no' or 
                evaluation.description_match == 'no' or 
                evaluation.service_attitude == 'no'):
                negative_evaluations.append(evaluation)
        
        serializer = ProductEvaluationSerializer(negative_evaluations, many=True)
        return Response(serializer.data)


# 商品评价相关API
class ProductEvaluationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, product_id):
        """提交商品评价"""
        try:
            product = Product.objects.get(id=product_id, buyer=request.user, status='sold')
        except Product.DoesNotExist:
            return Response({'error': '商品不存在或您不是购买者'}, status=status.HTTP_404_NOT_FOUND)
        
        # 检查是否已评价
        if hasattr(product, 'evaluations') and product.evaluations.filter(buyer=request.user).exists():
            return Response({'error': '您已对该商品进行过评价'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取评价数据
        received_item = request.data.get('received_item')
        description_match = request.data.get('description_match')
        service_attitude = request.data.get('service_attitude')
        evidence_photos = request.data.get('evidence_photos', [])
        
        # 验证评价数据
        if not all([received_item, description_match, service_attitude]):
            return Response({'error': '请完成所有评价项'}, status=status.HTTP_400_BAD_REQUEST)
        
        if received_item not in ['yes', 'no'] or description_match not in ['yes', 'no'] or service_attitude not in ['yes', 'no']:
            return Response({'error': '评价选项无效'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否需要上传证据照片
        negative_evaluation = (received_item == 'no' or description_match == 'no' or service_attitude == 'no')
        if negative_evaluation and (not evidence_photos or len(evidence_photos) == 0):
            return Response({
                'error': '当选择"否"时，必须上传至少一张证据照片'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建评价
        from datetime import timedelta
        appeal_deadline = timezone.now() + timedelta(hours=24)
        
        evaluation = ProductEvaluation.objects.create(
            product=product,
            buyer=request.user,
            seller=product.seller,
            received_item=received_item,
            description_match=description_match,
            service_attitude=service_attitude,
            evidence_photos=evidence_photos,
            appeal_deadline=appeal_deadline
        )
        
        # 计算信用分扣除点数（但不立即扣除）
        deduction_points = evaluation.calculate_deduction_points()
        
        # 发送通知给卖家
        ChatMessage.objects.create(
            sender=request.user,
            receiver=product.seller,
            product=product,
            content=f"您收到了一条新的商品评价，请在24小时内申诉，否则系统将自动处理。"
        )
        
        serializer = ProductEvaluationSerializer(evaluation)
        return Response({
            'success': True,
            'message': '评价提交成功',
            'data': serializer.data,
            'deduction_points': deduction_points
        })
    
    def get(self, request, product_id):
        """获取商品评价"""
        try:
            product = Product.objects.get(id=product_id)
            evaluations = product.evaluations.all()
            serializer = ProductEvaluationSerializer(evaluations, many=True)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': '商品不存在'}, status=status.HTTP_404_NOT_FOUND)