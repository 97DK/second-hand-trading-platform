<!-- frontend/src/views/PublishProduct.vue -->
<template>
  <div class="publish-product">
    <el-card>
      <template #header>
        <h2 class="publish-product-title">发布商品</h2>
      </template>

      <el-form
        :model="productForm"
        :rules="rules"
        ref="productFormRef"
        label-width="100px"
      >
        <!-- 上传图片 -->
        <el-form-item label="商品图片" prop="images" class="image-upload-item">
          <el-upload
            v-model:file-list="fileList"
            action="#"
            list-type="picture-card"
            :auto-upload="false"
            :limit="1"
            :on-exceed="handleExceed"
            :on-preview="handlePictureCardPreview"
            :on-remove="handleRemove"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <p class="upload-tip">最多可上传1张图片，建议尺寸750x750像素以上，大小不超过5M</p>
        </el-form-item>

        <!-- 标题 -->
        <el-form-item label="商品标题" prop="title">
          <el-input
            v-model="productForm.title"
            placeholder="请输入商品标题，建议20字以内"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <!-- 描述 -->
        <el-form-item label="商品描述" prop="description">
          <el-input
            v-model="productForm.description"
            type="textarea"
            :rows="4"
            placeholder="详细描述商品的品牌、规格、新旧程度、是否有瑕疵等信息"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <!-- 分类 -->
        <el-form-item label="商品分类" prop="category">
          <el-select v-model="productForm.category" placeholder="请选择分类">
            <el-option label="教材图书" value="book" />
            <el-option label="数码产品" value="digital" />
            <el-option label="生活用品" value="life" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <!-- 价格 -->
        <el-form-item label="价　　格" prop="price">
          <el-input
            v-model.number="productForm.price"
            placeholder="请输入价格"
            type="number"
            min="0"
            max="999999"
            step="0.01"
          >
            <template #prepend>¥</template>
          </el-input>
        </el-form-item>

        <!-- 库存 -->
        <el-form-item label="库　　存" prop="inventory">
          <el-input-number
            v-model="productForm.inventory"
            :min="1"
            :max="999"
            controls-position="right"
            placeholder="请输入库存数量"
          />
          <span class="inventory-tip">件</span>
        </el-form-item>

        <!-- 成色 -->
        <el-form-item label="新旧程度" prop="condition">
          <el-select v-model="productForm.condition" placeholder="请选择新旧程度">
            <el-option label="全新" value="new" />
            <el-option label="九成新" value="nine" />
            <el-option label="八成新" value="eight" />
            <el-option label="七成新" value="seven" />
            <el-option label="六成新及以下" value="below_six" />
          </el-select>
        </el-form-item>

        <!-- 地理位置 -->
        <el-form-item label="交易地点" prop="dormitory_building">
          <el-input
            v-model="productForm.dormitory_building"
            placeholder="请输入大致交易地点（宿舍楼/教学楼等）"
          />
        </el-form-item>

        <!-- 提交按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            @click="submitProduct"
            :loading="loading"
            size="large"
          >
            发布商品
          </el-button>
          <el-button @click="resetForm" size="large">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图片预览对话框 -->
    <el-dialog v-model="dialogVisible">
      <img w-full :src="dialogImageUrl" alt="预览图片" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()

// 表单引用
const productFormRef = ref()

// 响应式数据
const loading = ref(false)
const dialogImageUrl = ref('')
const dialogVisible = ref(false)
const fileList = ref([])

// 商品表单数据
const productForm = reactive({
  title: '',
  description: '',
  category: '',
  price: null,
  inventory: 1,
  condition: '',
  dormitory_building: ''
})

// 验证规则
const rules = {
  title: [
    { required: true, message: '请输入商品标题', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入商品描述', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择商品分类', trigger: 'change' }
  ],
  price: [
    { required: true, message: '请输入价格', trigger: 'blur' },
    { type: 'number', min: 0, message: '价格必须大于等于0', trigger: 'blur' }
  ],
  inventory: [
    { required: true, message: '请输入库存数量', trigger: 'blur' },
    { type: 'number', min: 1, message: '库存数量必须大于等于1', trigger: 'blur' }
  ],
  condition: [
    { required: true, message: '请选择新旧程度', trigger: 'change' },
    { validator: (rule, value, callback) => {
        if (!value || value === '') {
          callback(new Error('请选择新旧程度'))
        } else {
          callback()
        }
      }, trigger: 'change' }
  ],
  dormitory_building: [
    { required: true, message: '请输入交易地点', trigger: 'blur' }
  ]
}

// 处理图片预览
const handlePictureCardPreview = (uploadFile) => {
  dialogImageUrl.value = uploadFile.url
  dialogVisible.value = true
}

// 处理图片移除
const handleRemove = (uploadFile, uploadFiles) => {
  fileList.value = uploadFiles
}

// 处理超出限制
const handleExceed = () => {
  ElMessage.warning('最多只能上传9张图片')
}

// 重置表单
const resetForm = () => {
  productFormRef.value.resetFields()
  fileList.value = []
}

// 提交商品
const submitProduct = async () => {
  try {
    await productFormRef.value.validate()
    loading.value = true

    // 准备表单数据
    const formData = new FormData()
    formData.append('title', productForm.title)
    formData.append('description', productForm.description)
    formData.append('category', productForm.category)
    formData.append('condition', productForm.condition)
    formData.append('price', productForm.price)
    formData.append('inventory', productForm.inventory)
    formData.append('dormitory_building', productForm.dormitory_building)

    // 添加图片
    if (fileList.value.length > 0) {
      fileList.value.forEach(file => {
        formData.append('images', file.raw)
      })
    }

    // 提交到后端
    const response = await axios.post('/api/products/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.id) {
      ElMessage.success('商品发布成功，等待管理员审核')
      router.push('/dashboard')
    } else {
      throw new Error('发布失败')
    }
  } catch (error) {
    ElMessage.error('商品发布失败，请检查填写内容')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.publish-product {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.publish-product-title {
  color: #737BBE;
  text-align: center;
  margin: 0;
}

.upload-tip {
  font-size: 12px;
  color: #999;
  margin-top: 10px;
}

.inventory-tip {
  margin-left: 10px;
  color: #999;
  font-size: 14px;
}

.el-select,
.el-input {
  width: 100%;
}

:deep(.el-card__header) {
  padding: 5px 15px;
  font-size: 14px;
}

:deep(.el-form-item) {
  font-size: 14px;
  margin-bottom: 18px;
}

:deep(.el-form-item__label) {
  font-size: 14px;
}

:deep(.el-input__inner),
:deep(.el-textarea__inner) {
  font-size: 14px;
}

.image-upload-item :deep(.el-upload--picture-card) {
  width: 250px;
  height: 120px;
  line-height: 120px;
  border-radius: 6px;
  border: 2px dashed #737BBE;
  background-color: rgba(115, 123, 190, 0.1);
}

.image-upload-item :deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 250px;
  height: 120px;
  border-radius: 6px;
}

.image-upload-item :deep(.el-upload--picture-card .el-icon) {
  font-size: 28px;
  color: #737BBE;
  margin-top: -10px;
}

.image-upload-item :deep(.el-upload--picture-card:hover) {
  border-color: #6269a9;
  background-color: rgba(115, 123, 190, 0.15);
}

:deep(.el-form-item__label) {
  color: #737BBE;
}

:deep(.el-form-item__label::before) {
  color: #737BBE;
}

/* 修改发布商品按钮在不同状态下的颜色 */
:deep(.el-button--primary) {
  background-color: #737BBE;
  border-color: #737BBE;
}

:deep(.el-button--primary:hover) {
  background-color: #6269a9;
  border-color: #6269a9;
}

:deep(.el-button--primary:focus) {
  background-color: #737BBE;
  border-color: #737BBE;
}
</style>
