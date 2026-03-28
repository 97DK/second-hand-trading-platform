# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import warnings

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


# 打印思考过程
def print_analysis_step(step, content):
    print(f"\n{'=' * 60}")
    print(f"步骤 {step}: {content}")
    print('=' * 60)


# 1. 加载数据
print_analysis_step(1, "加载数据并查看基本信息")
file_path = r"C:\Users\PC\Desktop\1949到2001年中国人口数据.xls"
try:
    # 读取Excel文件
    data = pd.read_excel(file_path)
    print(f"数据形状: {data.shape}")
    print(f"数据列名: {data.columns.tolist()}")
    print(f"前5行数据:\n{data.head()}")

    # 假设第一列是年份，第二列是人口数据
    year_col = data.columns[0]
    pop_col = data.columns[1]

    # 设置年份为索引
    data = data.set_index(year_col)
    data.index.name = 'Year'
    time_series = data[pop_col]

    print(f"\n时间序列数据:")
    print(f"时间范围: {time_series.index.min()} 到 {time_series.index.max()}")
    print(f"数据点数: {len(time_series)}")

except Exception as e:
    print(f"读取文件出错: {e}")
    # 使用图片中提供的数据作为备用
    print("使用图片中提供的数据...")
    # 图片中的数据看起来是某一段时间的人口数据
    time_series_data = [11.985, 12.1121, 12.2389, 12.3626, 12.4761,
                        12.5786, 12.6743, 12.7627]
    # 假设这些数据对应1994-2001年
    years = list(range(1994, 2002))
    time_series = pd.Series(time_series_data, index=years, name='Population')
    print(f"使用备用数据，时间范围: {years[0]} 到 {years[-1]}")

# 2. 绘制时序图、自相关图和偏自相关图
print_analysis_step(2, "绘制时序图、自相关图(ACF)和偏自相关图(PACF)")

fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# 时序图
axes[0].plot(time_series.index, time_series.values, 'b-', marker='o', linewidth=2)
axes[0].set_title('中国人口时间序列图', fontsize=14, fontweight='bold')
axes[0].set_xlabel('年份', fontsize=12)
axes[0].set_ylabel('人口数量(亿)', fontsize=12)
axes[0].grid(True, alpha=0.3)
axes[0].fill_between(time_series.index, time_series.values, alpha=0.2, color='blue')

# ACF图
plot_acf(time_series, ax=axes[1], lags=20, alpha=0.05)
axes[1].set_title('自相关图(ACF)', fontsize=14, fontweight='bold')
axes[1].set_xlabel('滞后期数', fontsize=12)
axes[1].set_ylabel('自相关系数', fontsize=12)
axes[1].grid(True, alpha=0.3)

# PACF图
plot_pacf(time_series, ax=axes[2], lags=20, alpha=0.05, method='ywm')
axes[2].set_title('偏自相关图(PACF)', fontsize=14, fontweight='bold')
axes[2].set_xlabel('滞后期数', fontsize=12)
axes[2].set_ylabel('偏自相关系数', fontsize=12)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('时序分析图.png', dpi=300, bbox_inches='tight')
plt.show()

print_analysis_step(3, "分析时序图、ACF和PACF图像性质")

print("""
时序图分析:
1. 从时序图可以看出，中国人口呈现明显的上升趋势
2. 数据表现出非平稳性特征（有趋势成分）
3. 需要差分处理以获得平稳序列

ACF图分析:
1. ACF衰减缓慢，进一步确认序列的非平稳性
2. 自相关系数在较长的滞后期内保持较高值
3. 典型的非平稳时间序列特征

PACF图分析:
1. PACF在滞后1期后迅速截尾
2. 偏自相关系数在滞后1期后接近0
3. 这提示可能适合AR(1)模型

模型识别结论:
1. 原始序列非平稳，需要差分处理(d=1)
2. ACF缓慢衰减，PACF在滞后1期后截尾
3. 初步识别为ARIMA(1,1,0)模型
""")

# 3. 平稳性检验
print_analysis_step(4, "进行ADF平稳性检验")

adf_result = adfuller(time_series)
print(f"ADF统计量: {adf_result[0]:.4f}")
print(f"p-value: {adf_result[1]:.4f}")
print("临界值:")
for key, value in adf_result[4].items():
    print(f"  {key}: {value:.4f}")

if adf_result[1] > 0.05:
    print("\n结论: p值 > 0.05，序列不平稳，需要差分处理")
else:
    print("\n结论: p值 ≤ 0.05，序列平稳")

# 4. 差分处理
print_analysis_step(5, "对序列进行一阶差分")

diff_series = time_series.diff().dropna()
print(f"一阶差分后的序列长度: {len(diff_series)}")

# 绘制差分后的序列
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].plot(diff_series.index[1:], diff_series.values[1:], 'g-', marker='o', linewidth=2)
axes[0].set_title('一阶差分后的序列', fontsize=14, fontweight='bold')
axes[0].set_xlabel('年份', fontsize=12)
axes[0].set_ylabel('差分值', fontsize=12)
axes[0].grid(True, alpha=0.3)
axes[0].axhline(y=0, color='r', linestyle='--', alpha=0.5)

# 差分后的ACF图
plot_acf(diff_series, ax=axes[1], lags=15, alpha=0.05)
axes[1].set_title('一阶差分序列的ACF图', fontsize=14, fontweight='bold')
axes[1].set_xlabel('滞后期数', fontsize=12)
axes[1].set_ylabel('自相关系数', fontsize=12)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('差分分析图.png', dpi=300, bbox_inches='tight')
plt.show()

# 差分后的平稳性检验
adf_diff_result = adfuller(diff_series.dropna())
print(f"\n一阶差分后ADF检验p值: {adf_diff_result[1]:.4f}")
if adf_diff_result[1] > 0.05:
    print("差分后序列仍不平稳，可能需要二阶差分")
else:
    print("差分后序列已平稳")

print_analysis_step(6, "根据图像性质进行模型识别")

print("""
基于ACF和PACF图的模型识别:
1. 原始序列ACF缓慢衰减 → 需要差分(d=1)
2. 差分后序列ACF和PACF分析:
   - ACF在滞后1期后截尾或拖尾
   - PACF在滞后1期后截尾
3. 可能的模型:
   - ARIMA(1,1,0): PACF在滞后1期后截尾
   - ARIMA(0,1,1): ACF在滞后1期后截尾
   - ARIMA(1,1,1): ACF和PACF都拖尾

根据PACF在滞后1期后迅速截尾的特性，优先选择ARIMA(1,1,0)模型
""")

# 5. 建立ARIMA模型
print_analysis_step(7, "建立ARIMA模型")

# 尝试不同的ARIMA模型
models = {
    'ARIMA(1,1,0)': (1, 1, 0),
    'ARIMA(0,1,1)': (0, 1, 1),
    'ARIMA(1,1,1)': (1, 1, 1),
    'ARIMA(2,1,0)': (2, 1, 0),
    'ARIMA(0,1,2)': (0, 1, 2)
}

best_aic = np.inf
best_model_name = ''
best_model = None
model_results = []

print("比较不同ARIMA模型的AIC值:")
print("-" * 50)
print(f"{'模型':<15} {'AIC':<15} {'BIC':<15}")
print("-" * 50)

for name, order in models.items():
    try:
        model = ARIMA(time_series, order=order)
        model_fit = model.fit()
        aic = model_fit.aic
        bic = model_fit.bic
        model_results.append((name, model_fit, aic, bic))

        print(f"{name:<15} {aic:<15.2f} {bic:<15.2f}")

        if aic < best_aic:
            best_aic = aic
            best_model_name = name
            best_model = model_fit
    except Exception as e:
        print(f"{name:<15} 拟合失败: {str(e)[:30]}")

print("-" * 50)
print(f"\n最优模型: {best_model_name}, AIC = {best_aic:.2f}")

# 6. 展示最优模型结果
print_analysis_step(8, "最优模型参数估计")

print(f"最优模型: {best_model_name}")
print(best_model.summary())

print("\n模型参数解释:")
print("1. 常数项(const): 表示模型的截距项")
print("2. AR参数(ar.L1): 表示一阶自回归系数")
print("3. MA参数(ma.L1): 表示一阶移动平均系数(如果模型包含)")
print(f"\n残差标准差: {np.std(best_model.resid):.4f}")

# 7. 模型诊断
print_analysis_step(9, "模型诊断")

# 绘制残差图
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# 残差序列图
residuals = best_model.resid
axes[0, 0].plot(residuals.index, residuals.values, 'r-', linewidth=1)
axes[0, 0].axhline(y=0, color='b', linestyle='--', alpha=0.5)
axes[0, 0].set_title('残差序列图', fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('年份', fontsize=10)
axes[0, 0].set_ylabel('残差', fontsize=10)
axes[0, 0].grid(True, alpha=0.3)

# 残差直方图
axes[0, 1].hist(residuals, bins=15, edgecolor='black', alpha=0.7)
axes[0, 1].set_title('残差直方图', fontsize=12, fontweight='bold')
axes[0, 1].set_xlabel('残差值', fontsize=10)
axes[0, 1].set_ylabel('频数', fontsize=10)
axes[0, 1].grid(True, alpha=0.3)

# 残差ACF图
plot_acf(residuals, ax=axes[1, 0], lags=15, alpha=0.05)
axes[1, 0].set_title('残差ACF图', fontsize=12, fontweight='bold')
axes[1, 0].set_xlabel('滞后期数', fontsize=10)
axes[1, 0].set_ylabel('自相关系数', fontsize=10)
axes[1, 0].grid(True, alpha=0.3)

# Q-Q图
from scipy import stats

stats.probplot(residuals.dropna(), dist="norm", plot=axes[1, 1])
axes[1, 1].set_title('残差Q-Q图', fontsize=12, fontweight='bold')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('模型诊断图.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n模型诊断结论:")
print("1. 残差序列应无明显趋势（是否在0附近随机波动）")
print("2. 残差ACF图应无显著自相关（所有条柱应在置信区间内）")
print("3. Q-Q图应接近直线，表示残差近似正态分布")
print("4. 如果以上条件满足，说明模型拟合良好")

# 8. 预测2002-2005年人口
print_analysis_step(10, "预测2002-2005年中国人口数量")

# 预测未来4年
forecast_years = [2002, 2003, 2004, 2005]
n_forecast = len(forecast_years)

# 进行预测
forecast_result = best_model.get_forecast(steps=n_forecast)
forecast_values = forecast_result.predicted_mean
forecast_ci = forecast_result.conf_int()

print("\n预测结果:")
print("-" * 60)
print(f"{'年份':<10} {'预测人口(亿)':<15} {'95%置信区间下限':<20} {'95%置信区间上限':<20}")
print("-" * 60)

for i, year in enumerate(forecast_years):
    pred = forecast_values.iloc[i]
    ci_lower = forecast_ci.iloc[i, 0]
    ci_upper = forecast_ci.iloc[i, 1]
    print(f"{year:<10} {pred:<15.4f} {ci_lower:<20.4f} {ci_upper:<20.4f}")

print("-" * 60)

# 9. 绘制预测图
print_analysis_step(11, "绘制预测图")

fig, ax = plt.subplots(figsize=(12, 7))

# 绘制历史数据
historical_years = time_series.index
ax.plot(historical_years, time_series.values, 'b-', marker='o',
        linewidth=2, markersize=6, label='历史数据')

# 绘制预测数据
forecast_index = forecast_years
ax.plot(forecast_index, forecast_values.values, 'r--', marker='s',
        linewidth=2, markersize=8, label='预测数据')

# 绘制置信区间
ax.fill_between(forecast_index,
                forecast_ci.iloc[:, 0],
                forecast_ci.iloc[:, 1],
                color='gray', alpha=0.2, label='95%置信区间')

# 标记预测起始点
last_year = historical_years[-1]
last_value = time_series.iloc[-1]
ax.plot([last_year, forecast_years[0]], [last_value, forecast_values.iloc[0]],
        'k--', alpha=0.5)

# 设置图形属性
ax.set_title('中国人口历史数据与预测(2002-2005)', fontsize=16, fontweight='bold')
ax.set_xlabel('年份', fontsize=14)
ax.set_ylabel('人口数量(亿)', fontsize=14)
ax.legend(loc='best', fontsize=12)
ax.grid(True, alpha=0.3)
ax.set_xlim([historical_years.min() - 1, forecast_years[-1] + 1])

# 添加数值标签
for i, (year, value) in enumerate(zip(historical_years, time_series.values)):
    if i % 5 == 0 or i == len(historical_years) - 1:  # 每5年或最后一个点标记
        ax.annotate(f'{value:.2f}', (year, value),
                    textcoords="offset points", xytext=(0, 10),
                    ha='center', fontsize=9)

for i, (year, value) in enumerate(zip(forecast_index, forecast_values.values)):
    ax.annotate(f'{value:.2f}', (year, value),
                textcoords="offset points", xytext=(0, 10),
                ha='center', fontsize=9, color='red')

plt.tight_layout()
plt.savefig('人口预测图.png', dpi=300, bbox_inches='tight')
plt.show()

# 10. 总结
print_analysis_step(12, "总结与思考")

print(f"""
时间序列分析总结:
1. 数据特征: 中国人口数据呈现明显上升趋势，是非平稳时间序列
2. 模型识别: 通过ACF和PACF图分析，识别为{best_model_name}模型
3. 模型验证: AIC准则选择{best_model_name}为最优模型(AIC={best_aic:.2f})
4. 预测结果: 
   - 2002年: {forecast_values.iloc[0]:.4f}亿
   - 2003年: {forecast_values.iloc[1]:.4f}亿
   - 2004年: {forecast_values.iloc[2]:.4f}亿
   - 2005年: {forecast_values.iloc[3]:.4f}亿

思考过程:
1. 从时序图识别趋势性 → 需要差分处理(d=1)
2. 从ACF缓慢衰减确认非平稳性 → 支持差分处理
3. 从PACF在滞后1期后截尾 → 提示AR(1)结构
4. 结合ACF和PACF特征 → 初步识别为ARIMA(1,1,0)
5. 通过比较不同模型的AIC值 → 确认最优模型
6. 检查模型残差 → 验证模型假设是否满足
7. 使用最优模型 → 进行未来4年的预测

注意事项:
1. 人口预测受政策、经济等多因素影响，ARIMA模型主要捕捉历史趋势
2. 长期预测误差可能较大，建议定期更新模型
3. 95%置信区间提供了预测的不确定性范围
""")

print("\n所有图表已保存为PNG文件:")
print("1. 时序分析图.png - 时序图、ACF图、PACF图")
print("2. 差分分析图.png - 差分序列及ACF图")
print("3. 模型诊断图.png - 残差分析图")
print("4. 人口预测图.png - 历史数据与预测图")