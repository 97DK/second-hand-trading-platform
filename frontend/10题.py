import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
# 导入统计库
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox
from scipy import stats
# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
# ==================== 1. 数据加载 ====================
def load_stock_data():
    print("正在加载数据...")
    
    try:
        df = pd.read_excel(r"C:\Users\PC\Desktop\某股市80天的收盘价.xls")
        df.columns = ['天数', '收盘价']
        df.set_index('日期', inplace=True)
        
        print(f"数据加载完成，共{len(df)}个交易日")
        print(f"收盘价范围: {df['收盘价'].min():.2f} - {df['收盘价'].max():.2f}")
        return df['收盘价']
    except FileNotFoundError:
        print("未找到Excel文件，使用模拟数据...")
        # 创建模拟数据（84天的收盘价）
        np.random.seed(42)
        n_days = 84
        # 生成趋势+季节+噪声的数据
        trend = np.linspace(100, 120, n_days)
        seasonal = 5 * np.sin(np.linspace(0, 8 * np.pi, n_days))
        noise = np.random.normal(0, 3, n_days)
        prices = trend + seasonal + noise
        # 创建DataFrame
        dates = pd.date_range(start='2024-01-01', periods=n_days, freq='D')
        df = pd.DataFrame({
            '日期': dates,
            '收盘价': prices
        })
        df.set_index('日期', inplace=True)

        print(f"数据加载完成，共{len(df)}个交易日")
        print(f"收盘价范围: {df['收盘价'].min():.2f} - {df['收盘价'].max():.2f}")
        return df['收盘价']
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        print("使用模拟数据...")
        # 创建模拟数据（84天的收盘价）
        np.random.seed(42)
        n_days = 84
        # 生成趋势+季节+噪声的数据
        trend = np.linspace(100, 120, n_days)
        seasonal = 5 * np.sin(np.linspace(0, 8 * np.pi, n_days))
        noise = np.random.normal(0, 3, n_days)
        prices = trend + seasonal + noise
        # 创建DataFrame
        dates = pd.date_range(start='2024-01-01', periods=n_days, freq='D')
        df = pd.DataFrame({
            '日期': dates,
            '收盘价': prices
        })
        df.set_index('日期', inplace=True)

        print(f"数据加载完成，共{len(df)}个交易日")
        print(f"收盘价范围: {df['收盘价'].min():.2f} - {df['收盘价'].max():.2f}")
        return df['收盘价']
# ==================== 2. 平稳性检验 ====================
def check_stationarity(series):
    """ADF平稳性检验"""
    print("\n" + "=" * 50)
    print("平稳性检验 (ADF Test)")
    print("=" * 50)
    result = adfuller(series.dropna())
    print(f'ADF统计量: {result[0]:.6f}')
    print(f'p值: {result[1]:.6f}')
    print('临界值:')
    for key, value in result[4].items():
        print(f'  {key}: {value:.6f}')

    if result[1] <= 0.05:
        print("✓ 序列是平稳的 (p值 < 0.05)")
        return True, 0
    else:
        print("✗ 序列是非平稳的 (p值 > 0.05)")
        return False, 1


# ==================== 3. 绘制ACF/PACF图 ====================
def plot_acf_pacf(series, title="时间序列"):
    """绘制自相关和偏自相关图"""
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # ACF图
    plot_acf(series.dropna(), lags=20, ax=axes[0])
    axes[0].set_title(f'{title} - 自相关函数(ACF)')
    axes[0].set_xlabel('滞后阶数')
    axes[0].set_ylabel('自相关系数')
    axes[0].grid(True, alpha=0.3)

    # PACF图
    plot_pacf(series.dropna(), lags=20, ax=axes[1])
    axes[1].set_title(f'{title} - 偏自相关函数(PACF)')
    axes[1].set_xlabel('滞后阶数')
    axes[1].set_ylabel('偏自相关系数')
    axes[1].grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    # 提供阶数选择建议
    print("\n根据ACF/PACF图的阶数选择建议:")
    print("-" * 40)
    print("ACF缓慢衰减，PACF在p阶后截尾 → AR(p)")
    print("ACF在q阶后截尾，PACF缓慢衰减 → MA(q)")
    print("两者都缓慢衰减 → ARMA(p,q)")

# ==================== 4. 拟合ARIMA模型 ====================
def fit_arima(series, order=(1, 1, 1)):
    """拟合ARIMA模型"""
    print(f"\n拟合ARIMA{order}模型...")

    try:
        model = ARIMA(series, order=order)
        model_fit = model.fit()

        print("✓ 模型拟合成功!")
        print(f"AIC: {model_fit.aic:.2f}, BIC: {model_fit.bic:.2f}")
        print("\n模型参数:")
        print(model_fit.params)

        return model_fit
    except Exception as e:
        print(f"✗ 模型拟合失败: {e}")
        return None


# ==================== 5. 模型诊断 ====================
def diagnose_model(model_fit):
    """模型诊断检验"""
    print("\n" + "=" * 50)
    print("模型诊断检验")
    print("=" * 50)

    residuals = model_fit.resid.dropna()

    # 1. 白噪声检验
    lb_test = acorr_ljungbox(residuals, lags=[10], return_df=True)
    print("1. 残差白噪声检验 (Ljung-Box):")
    print(f"   Q统计量: {lb_test['lb_stat'].values[0]:.4f}")
    print(f"   p值: {lb_test['lb_pvalue'].values[0]:.4f}")

    if lb_test['lb_pvalue'].values[0] > 0.05:
        print("   ✓ 残差是白噪声，模型通过检验")
        lb_pass = True
    else:
        print("   ✗ 残差不是白噪声，模型可能需要改进")
        lb_pass = False

    # 2. 正态性检验
    jb_stat, jb_p = stats.jarque_bera(residuals)
    print("\n2. 残差正态性检验 (Jarque-Bera):")
    print(f"   JB统计量: {jb_stat:.4f}")
    print(f"   p值: {jb_p:.4f}")

    if jb_p > 0.05:
        print("   ✓ 残差服从正态分布")
        jb_pass = True
    else:
        print("   ✗ 残差不服从正态分布")
        jb_pass = False

    # 绘制诊断图
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # 残差序列
    axes[0, 0].plot(residuals.index, residuals.values, 'b-')
    axes[0, 0].set_title('残差序列')
    axes[0, 0].set_xlabel('日期')
    axes[0, 0].set_ylabel('残差')
    axes[0, 0].axhline(y=0, color='r', linestyle='--', alpha=0.5)
    axes[0, 0].grid(True, alpha=0.3)

    # 残差分布
    axes[0, 1].hist(residuals, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    axes[0, 1].set_title('残差分布')
    axes[0, 1].set_xlabel('残差值')
    axes[0, 1].set_ylabel('频数')
    axes[0, 1].grid(True, alpha=0.3)

    # QQ图
    stats.probplot(residuals, dist="norm", plot=axes[1, 0])
    axes[1, 0].set_title('残差QQ图 (正态性检验)')
    axes[1, 0].grid(True, alpha=0.3)

    # 残差ACF
    plot_acf(residuals, lags=20, ax=axes[1, 1])
    axes[1, 1].set_title('残差自相关函数')
    axes[1, 1].set_xlabel('滞后阶数')
    axes[1, 1].set_ylabel('自相关系数')
    axes[1, 1].grid(True, alpha=0.3)

    plt.suptitle('ARIMA模型诊断图', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()

    return lb_pass and jb_pass


# ==================== 6. 预测未来值 ====================
def forecast_prices(model_fit, series, n_days=5):
    """预测未来价格"""
    print(f"\n预测未来{n_days}天收盘价...")

    # 点预测
    forecast = model_fit.forecast(steps=n_days)

    # 置信区间
    forecast_obj = model_fit.get_forecast(steps=n_days)
    ci = forecast_obj.conf_int()

    # 创建结果DataFrame
    last_date = series.index[-1]
    # 修复pandas新版本中Timestamp操作的问题
    forecast_dates = pd.date_range(
        start=last_date + pd.offsets.Day(1),
        periods=n_days,
        freq='D'
    )

    results = pd.DataFrame({
        '预测日期': forecast_dates,
        '预测收盘价': forecast.values,
        '95%_置信下限': ci.iloc[:, 0],
        '95%_置信上限': ci.iloc[:, 1]
    })

    print("\n预测结果:")
    print("=" * 60)
    print(results.to_string(index=False))

    return results, forecast


# ==================== 7. 可视化预测结果 ====================
def plot_forecast(series, model_fit, forecast_results, n_days=5):
    """可视化预测结果"""
    # 获取拟合值
    fitted_values = model_fit.fittedvalues

    # 创建图形
    plt.figure(figsize=(14, 7))

    # 绘制历史数据，将横坐标改为1,2,3...数字序列
    x_values = range(1, len(series) + 1)
    plt.plot(x_values, series.values, 'b-', linewidth=2,
             label='历史收盘价', alpha=0.8)

    # 绘制拟合值（排除前几个可能为NaN的值）
    valid_fitted = fitted_values[fitted_values.first_valid_index():]
    # 调整x轴坐标以匹配历史数据的位置
    x_fitted = range(len(series) - len(valid_fitted) + 1, len(series) + 1)
    plt.plot(x_fitted, valid_fitted.values, 'g--', linewidth=2,
             label='模型拟合值', alpha=0.8)

    # 绘制预测值
    # 预测部分的x轴坐标从最后一个历史点之后开始
    x_forecast = range(len(series) + 1, len(series) + len(forecast_results) + 1)
    forecast_values = forecast_results['预测收盘价']
    plt.plot(x_forecast, forecast_values, 'r-', linewidth=2,
             marker='o', markersize=6, label='未来预测值')

    # 绘制置信区间
    plt.fill_between(
        x_forecast,
        forecast_results['95%_置信下限'],
        forecast_results['95%_置信上限'],
        color='red', alpha=0.2, label='95% 置信区间'
    )

    # 设置图形属性
    plt.title('股票收盘价ARIMA模型预测', fontsize=16, fontweight='bold')
    plt.xlabel('交易日', fontsize=12)
    plt.ylabel('收盘价', fontsize=12)
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)

    # 添加文本说明
    last_price = series.iloc[-1]
    forecast_change = ((forecast_values.iloc[-1] - last_price) / last_price * 100)

    text_str = f'最后实际价格: {last_price:.2f}\n'
    text_str += f'第5天预测: {forecast_values.iloc[-1]:.2f}\n'
    text_str += f'预测变动: {forecast_change:+.2f}%'

    plt.text(0.02, 0.98, text_str, transform=plt.gca().transAxes,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
             fontsize=10)

    plt.tight_layout()
    plt.show()


# ==================== 8. 主函数 ====================
def main():
    """主函数：完整的ARIMA建模流程"""
    print("=" * 60)
    print("股票收盘价ARIMA模型预测分析")
    print("=" * 60)

    # 1. 加载数据
    print("\n1. 数据加载...")
    price_series = load_stock_data()

    # 显示数据前5行
    print("\n数据预览:")
    print(price_series.head())

    # 2. 绘制原始数据图
    plt.figure(figsize=(12, 5))
    # 将横坐标改为1,2,3...数字序列
    x_values = range(1, len(price_series) + 1)
    plt.plot(x_values, price_series.values, 'b-', linewidth=2)
    plt.title('股票收盘价时序图', fontsize=14, fontweight='bold')
    plt.xlabel('交易日')
    plt.ylabel('收盘价')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    # 3. 平稳性检验
    print("\n2. 平稳性检验...")
    is_stationary, d = check_stationarity(price_series)

    # 如果不平稳，查看差分后序列
    if not is_stationary:
        diff_series = price_series.diff().dropna()
        print("\n一阶差分后序列平稳性检验:")
        is_stationary_diff, _ = check_stationarity(diff_series)

        if is_stationary_diff:
            print("✓ 一阶差分后序列平稳，使用 d=1")
            d = 1
        else:
            print("尝试二阶差分...")
            diff2_series = diff_series.diff().dropna()
            is_stationary_diff2, _ = check_stationarity(diff2_series)
            if is_stationary_diff2:
                print("✓ 二阶差分后序列平稳，使用 d=2")
                d = 2

    # 4. 绘制ACF/PACF图确定p,q
    print("\n3. 确定ARIMA模型阶数...")

    # 获取平稳序列
    if d == 0:
        stationary_series = price_series
    elif d == 1:
        stationary_series = price_series.diff().dropna()
    else:
        stationary_series = price_series.diff().diff().dropna()

    print(f"使用差分阶数 d = {d}")
    plot_acf_pacf(stationary_series, "平稳化序列")

    # 5. 尝试不同的ARIMA模型
    print("\n4. 尝试拟合ARIMA模型...")

    # 常用阶数组合
    candidates = [(1, d, 1), (1, d, 0), (0, d, 1), (2, d, 2), (2, d, 1)]
    best_model = None
    best_aic = float('inf')

    for order in candidates:
        print(f"\n尝试 ARIMA{order}...")
        model = fit_arima(price_series, order)

        if model is not None:
            if model.aic < best_aic:
                best_aic = model.aic
                best_model = model
                best_order = order

    if best_model is None:
        print("所有模型尝试失败，使用默认ARIMA(1,1,1)")
        best_order = (1, 1, 1) if d > 0 else (1, 0, 1)
        best_model = fit_arima(price_series, best_order)

    print(f"\n✓ 选择最佳模型: ARIMA{best_order}")
    print(f"  最低AIC值: {best_aic:.2f}")

    # 6. 模型诊断
    print("\n5. 模型诊断...")
    model_passed = diagnose_model(best_model)

    if model_passed:
        print("\n✓ 模型通过诊断检验")
    else:
        print("\n⚠ 模型未完全通过诊断检验，但可以继续使用")

    # 7. 预测未来5天
    print("\n6. 预测未来5天收盘价...")
    forecast_results, forecast_values = forecast_prices(best_model, price_series, 5)

    # 8. 可视化结果
    print("\n7. 生成预测图表...")
    plot_forecast(price_series, best_model, forecast_results)

    # 9. 保存结果
    forecast_results.to_csv('股票收盘价预测结果.csv', index=False, encoding='utf-8-sig')
    print("\n✓ 预测结果已保存到: 股票收盘价预测结果.csv")

    print("\n" + "=" * 60)
    print("ARIMA建模与预测完成！")
    print("=" * 60)

    return {
        'price_series': price_series,
        'best_model': best_model,
        'best_order': best_order,
        'forecast_results': forecast_results
    }
# ==================== 运行主程序 ====================
if __name__ == "__main__":
    # 注意：直接运行这个脚本，不要用pytest
    print("注意：请直接运行此脚本，不要使用pytest测试")
    print("正在启动ARIMA预测分析...")

    try:
        results = main()

        # 显示最终预测结果
        print("\n最终预测摘要:")
        print("-" * 40)
        for i, row in results['forecast_results'].iterrows():
            print(f"第{i + 1}天 ({row['预测日期'].strftime('%Y-%m-%d')}): "
                  f"{row['预测收盘价']:.2f} "
                  f"[{row['95%_置信下限']:.2f}, {row['95%_置信上限']:.2f}]")
    except Exception as e:
        print(f"程序运行出错: {e}")
        print("请确保已安装必要的库: pip install pandas numpy matplotlib statsmodels")
