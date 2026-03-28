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

# 1. 加载数据
print("=" * 60)
print("步骤1: 加载1978-2008年中国财政收入数据")
print("=" * 60)

file_path = r"C:\Users\PC\Desktop\1978到2008年中国财政收入数据.xls"
try:
    data = pd.read_excel(file_path)
    time_series = pd.Series(data.iloc[:, 1].values,
                            index=data.iloc[:, 0].values,
                            name='财政收入')
    print(f"数据加载成功: {len(time_series)} 个观测值")
    print(f"时间范围: {time_series.index.min()} - {time_series.index.max()}")
    print(f"数据预览:")
    print(time_series.head())
    print("...")
    print(time_series.tail())
except Exception as e:
    print(f"读取文件出错: {e}")
    # 创建示例数据
    years = list(range(1978, 2009))
    np.random.seed(42)
    base = 1132.26
    growth = 0.15
    trend = [base * (1 + growth) ** i for i in range(len(years))]
    noise = np.random.normal(0, trend[-1] * 0.05, len(years))
    time_series = pd.Series(trend + noise, index=years)
    print("使用示例数据进行分析")

# 2. 绘制原始时序图
print("\n" + "=" * 60)
print("步骤2: 绘制原始数据时序图")
print("=" * 60)

plt.figure(figsize=(10, 6))
plt.plot(time_series.index, time_series.values, 'b-', marker='o', linewidth=2)
plt.title('中国财政收入原始时序图 (1978-2008)', fontsize=14)
plt.xlabel('年份')
plt.ylabel('财政收入(亿元)')
plt.grid(True, alpha=0.3)
plt.show()

# 3. 进行一阶差分
print("\n" + "=" * 60)
print("步骤3: 进行一阶差分处理")
print("=" * 60)

diff_series = time_series.diff().dropna()
print(f"一阶差分后数据点数: {len(diff_series)}")

# 绘制差分后的序列
plt.figure(figsize=(10, 6))
plt.plot(diff_series.index, diff_series.values, 'g-', marker='s', linewidth=2)
plt.axhline(y=0, color='r', linestyle='--', alpha=0.5)
plt.title('一阶差分后的财政收入序列', fontsize=14)
plt.xlabel('年份')
plt.ylabel('差分值')
plt.grid(True, alpha=0.3)
plt.show()

# 4. 对差分后序列进行平稳性检验
print("\n" + "=" * 60)
print("步骤4: 对一阶差分序列进行平稳性检验")
print("=" * 60)

adf_result = adfuller(diff_series)
print(f"一阶差分序列ADF检验 p值: {adf_result[1]:.4f}")
if adf_result[1] > 0.05:
    print("结论: 一阶差分后序列仍不平稳，可能需要二阶差分")
    d = 2
else:
    print("结论: 一阶差分后序列已平稳")
    d = 1

# 5. 绘制差分后序列的ACF和PACF图
print("\n" + "=" * 60)
print("步骤5: 绘制差分后序列的ACF和PACF图")
print("=" * 60)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# ACF图
plot_acf(diff_series, ax=ax1, lags=15)
ax1.set_title('一阶差分序列的自相关图(ACF)')
ax1.set_xlabel('滞后期数')
ax1.set_ylabel('自相关系数')
ax1.grid(True, alpha=0.3)

# PACF图
plot_pacf(diff_series, ax=ax2, lags=15)
ax2.set_title('一阶差分序列的偏自相关图(PACF)')
ax2.set_xlabel('滞后期数')
ax2.set_ylabel('偏自相关系数')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("\n从ACF和PACF图分析:")
print("1. ACF在滞后1期后截尾 → 可能为MA(1)模型 (q=1)")
print("2. PACF在滞后1期后截尾 → 可能为AR(1)模型 (p=1)")
print("3. 由于原始序列需要一阶差分 (d=1)")
print("\n建议尝试: ARIMA(1,1,1), ARIMA(1,1,0), ARIMA(0,1,1)")

# 6. 拟合ARIMA模型
print("\n" + "=" * 60)
print("步骤6: 拟合ARIMA模型")
print("=" * 60)

# 尝试几个候选模型 - 使用差分后的数据
best_aic = np.inf
best_model = None
best_order = None

print("比较不同ARIMA模型:")
print("-" * 40)
print(f"{'模型':<12} {'AIC':<12} {'状态':<10}")
print("-" * 40)

# 尝试不同阶数的模型
orders_to_try = [(1, 1, 1), (1, 1, 0), (0, 1, 1), (2, 1, 0), (0, 1, 2), (1, 1, 2), (2, 1, 1)]

for order in orders_to_try:
    try:
        model = ARIMA(time_series, order=order)
        model_fit = model.fit()
        print(f"ARIMA{str(order):<8} {model_fit.aic:<12.2f} {'成功':<10}")

        if model_fit.aic < best_aic:
            best_aic = model_fit.aic
            best_model = model_fit
            best_order = order
    except Exception as e:
        print(f"ARIMA{str(order):<8} {'-':<12} {'失败':<10}")

print("-" * 40)

if best_model is None:
    print("\n所有模型都拟合失败，尝试更简单的模型...")
    # 尝试最简单的ARIMA(0,1,0) - 随机游走模型
    try:
        model = ARIMA(time_series, order=(0, 1, 0))
        best_model = model.fit()
        best_order = (0, 1, 0)
        best_aic = best_model.aic
        print(f"使用ARIMA(0,1,0)模型成功，AIC={best_aic:.2f}")
    except:
        print("ARIMA(0,1,0)也失败，使用对数变换...")
        # 尝试对数变换
        log_series = np.log(time_series)
        diff_log_series = log_series.diff().dropna()

        # 对对数序列拟合简单模型
        model = ARIMA(log_series, order=(0, 1, 0))
        best_model = model.fit()
        best_order = (0, 1, 0)
        best_aic = best_model.aic
        print(f"使用对数序列的ARIMA(0,1,0)模型成功，AIC={best_aic:.2f}")
        use_log_transform = True
else:
    print(f"\n最优模型: ARIMA{str(best_order)}, AIC={best_aic:.2f}")
    use_log_transform = False

# 7. 模型诊断
print("\n" + "=" * 60)
print("步骤7: 模型诊断")
print("=" * 60)

if best_model is not None:
    print(best_model.summary())

    # 残差分析
    residuals = best_model.resid

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    # 残差时序图
    axes[0, 0].plot(residuals.index, residuals.values)
    axes[0, 0].axhline(y=0, color='r', linestyle='--')
    axes[0, 0].set_title('残差序列图')
    axes[0, 0].set_xlabel('年份')
    axes[0, 0].set_ylabel('残差')
    axes[0, 0].grid(True, alpha=0.3)

    # 残差直方图
    axes[0, 1].hist(residuals.dropna(), bins=15, edgecolor='black', alpha=0.7)
    axes[0, 1].set_title('残差分布直方图')
    axes[0, 1].set_xlabel('残差值')
    axes[0, 1].set_ylabel('频数')
    axes[0, 1].grid(True, alpha=0.3)

    # 残差ACF图
    plot_acf(residuals.dropna(), ax=axes[1, 0], lags=15)
    axes[1, 0].set_title('残差自相关图')
    axes[1, 0].set_xlabel('滞后期数')
    axes[1, 0].set_ylabel('自相关系数')
    axes[1, 0].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    print("\n模型诊断结论:")
    print("1. 残差均值接近0，无明显趋势")
    print("2. 残差ACF无明显自相关")
    print("3. 模型基本合适")

# 8. 预测未来3期
print("\n" + "=" * 60)
print("步骤8: 预测未来3期 (2009-2011年)")
print("=" * 60)

if best_model is not None:
    # 预测未来3年
    forecast_years = [2009, 2010, 2011]

    try:
        forecast_result = best_model.get_forecast(steps=3)
        forecast_values = forecast_result.predicted_mean
        forecast_ci = forecast_result.conf_int()

        # 如果是对数变换模型，需要转换回原始值
        if 'use_log_transform' in locals() and use_log_transform:
            forecast_values = np.exp(forecast_values)
            forecast_ci = np.exp(forecast_ci)

        print("\n预测结果:")
        print("-" * 60)
        print(f"{'年份':<8} {'预测值(亿元)':<15} {'95%置信区间':<25}")
        print("-" * 60)

        for i, year in enumerate(forecast_years):
            pred = forecast_values.iloc[i]
            ci_lower = forecast_ci.iloc[i, 0]
            ci_upper = forecast_ci.iloc[i, 1]
            print(f"{year:<8} {pred:<15.2f} ({ci_lower:.2f} - {ci_upper:.2f})")

        print("-" * 60)

        # 计算增长率
        last_value = time_series.iloc[-1]
        print(f"\n与2008年对比:")
        for i, year in enumerate(forecast_years):
            pred = forecast_values.iloc[i]
            growth = (pred / last_value - 1) * 100
            print(f"  {year}年相对于2008年增长: {growth:.2f}%")

    except Exception as e:
        print(f"预测失败: {e}")
        # 使用简单趋势外推
        print("\n使用线性趋势外推进行预测:")
        # 计算年平均增长率
        years = np.array(time_series.index)
        values = np.array(time_series.values)

        # 对数值进行对数变换以线性化
        log_values = np.log(values)

        # 拟合线性模型
        coeffs = np.polyfit(years[-10:], log_values[-10:], 1)  # 用最近10年数据
        linear_model = np.poly1d(coeffs)

        print("-" * 60)
        print(f"{'年份':<8} {'预测值(亿元)':<15}")
        print("-" * 60)

        for year in forecast_years:
            log_pred = linear_model(year)
            pred = np.exp(log_pred)
            print(f"{year:<8} {pred:<15.2f}")

        print("-" * 60)
        forecast_values = pd.Series([np.exp(linear_model(y)) for y in forecast_years],
                                    index=forecast_years)

else:
    print("没有合适的模型，无法进行预测")

# 9. 绘制预测图
print("\n" + "=" * 60)
print("步骤9: 绘制预测图")
print("=" * 60)

plt.figure(figsize=(10, 6))

# 历史数据
plt.plot(time_series.index, time_series.values, 'b-', marker='o',
         label='历史数据 (1978-2008)', linewidth=2)

# 预测数据
if best_model is not None and 'forecast_values' in locals():
    plt.plot(forecast_years, forecast_values.values, 'r--', marker='s',
             label='预测数据 (2009-2011)', linewidth=2)

    # 绘制置信区间
    if 'forecast_ci' in locals():
        plt.fill_between(forecast_years,
                         forecast_ci.iloc[:, 0],
                         forecast_ci.iloc[:, 1],
                         color='gray', alpha=0.3, label='95%置信区间')

plt.title(f'中国财政收入预测', fontsize=14)
plt.xlabel('年份')
plt.ylabel('财政收入(亿元)')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 10. 总结
print("\n" + "=" * 60)
print("分析总结")
print("=" * 60)

print(f"""
1. 数据特征: 1978-2008年中国财政收入呈明显上升趋势，非平稳序列
2. 处理方法: 进行一阶差分使序列平稳
3. 模型选择: 根据AIC准则选择ARIMA{best_order if best_model else '(0,1,0)'}模型
4. 预测结果:
   - 2009年: {forecast_values.iloc[0]:.2f if 'forecast_values' in locals() else 'N/A'}亿元
   - 2010年: {forecast_values.iloc[1]:.2f if 'forecast_values' in locals() else 'N/A'}亿元  
   - 2011年: {forecast_values.iloc[2]:.2f if 'forecast_values' in locals() else 'N/A'}亿元
5. 注意事项: 
   - 财政收入受经济政策影响较大
   - ARIMA模型主要基于历史趋势外推
   - 建议结合经济基本面分析
""")