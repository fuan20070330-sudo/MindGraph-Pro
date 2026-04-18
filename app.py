import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- 1. 核心配置与样式 ---
st.set_page_config(page_title="灵图 Pro - 医工交叉应激监测平台", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .advice-box { background-color: #1c2128; padding: 20px; border-left: 5px solid #00fbff; border-radius: 10px; margin-bottom: 15px; }
    .action-step { background-color: rgba(0, 251, 255, 0.08); border-radius: 4px; padding: 6px 10px; margin: 4px 0; font-size: 0.9em; border-left: 2px solid #00fbff; color: #e0e6ed; }
    .stMetric { background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 状态记忆 (用于趋势图) ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 3. 学术权重矩阵 (参考大学生压力源量表校准) ---
# 逻辑：不同分型下，9个维度的敏感系数权重分布不同
PROFILE_MATRIX = {
    "平衡发展型 (通用模型)": {
        "学业适应": 0.85, "未来规划": 0.75, "成就动机": 0.70, "睡眠质量": 0.92,
        "生活自理": 0.55, "环境适应": 0.60, "经济压力": 0.65, "人际关系": 0.82, "社交依赖": 0.55
    },
    "学业冲刺型 (高成就动机)": {
        "学业适应": 0.98, "未来规划": 0.92, "成就动机": 0.95, "睡眠质量": 0.95,
        "生活自理": 0.45, "环境适应": 0.50, "经济压力": 0.60, "人际关系": 0.55, "社交依赖": 0.35
    },
    "社交活跃型 (高社交负荷)": {
        "学业适应": 0.72, "未来规划": 0.65, "成就动机": 0.68, "睡眠质量": 0.88,
        "生活自理": 0.60, "环境适应": 0.75, "经济压力": 0.70, "人际关系": 0.96, "社交依赖": 0.92
    }
}

# --- 4. 临床干预处方库 ---
ADVICE_DB = {
    "学业适应": ["<b>信息卸载</b>：书面化所有待办，释放工作记忆。", "<b>脑力冷却</b>：严格执行 25/5 循环，预防认知过载。"],
    "未来规划": ["<b>最小行动</b>：锁定下周具体任务，对抗预见性焦虑。", "<b>概率校准</b>：审视担忧事件的真实发生率。"],
    "成就动机": ["<b>过程性评价</b>：记录今日努力点而非仅看结果。", "<b>防御性悲观</b>：为最坏情况准备一套备选方案。"],
    "睡眠质量": ["<b>刺激控制</b>：执行15分钟法则，睡不着即离开床铺。", "<b>褪黑素环境</b>：睡前1h切换至极低照度光环境。"],
    "生活自理": ["<b>1平米原则</b>：从整理桌面微小区域开始重建秩序。", "<b>锚定效应</b>：设定一个固定的起床仪式。"],
    "环境适应": ["<b>感官恢复</b>：寻找绿植或自然声音进行注意力恢复。", "<b>心理领地</b>：在当前环境摆放三件个人属性强的旧物。"],
    "经济压力": ["<b>财务去情绪化</b>：仅做客观收支记录，暂不进行价值判断。", "<b>带宽释放</b>：将大笔开支计划固定在特定日期检查。"],
    "人际关系": ["<b>课题分离</b>：识别哪些是对方的课题，拒绝过度共情。", "<b>我向沟通</b>：仅表达事实与感受，不进行动机推测。"],
    "社交依赖": ["<b>数字断舍离</b>：设定‘无手机区’，重塑深度专注环路。", "<b>单向输入</b>：尝试30分钟纯纸质阅读，降低多巴胺频率。"]
}

# --- 5. 核心动力学引擎 ---
def calculation_engine(inputs, resilience, weights):
    # 使用非线性幂函数模拟应激级联效应 (指数 1.7)
    scores_map = {k: (v ** 1.7) * weights.get(k, 1.0) for k, v in inputs.items()}
    total_raw = sum(scores_map.values())
    
    # 心理弹性对冲 (Max 30%)
    resilience_buffer = 1 - (resilience * 0.3) 
    
    # 归一化计算
    max_theoretical = sum(weights.values()) * 1.15
    anxiety_idx = (total_raw / max_theoretical) * 100 * resilience_buffer
    return max(0, min(anxiety_idx, 100.0)), scores_map

# --- 6. 侧边栏：多维数据采集 ---
with st.sidebar:
    st.header("👤 受试者特征分型")
    user_type = st.selectbox("请选择当前心理分型", list(PROFILE_MATRIX.keys()))
    current_weights = PROFILE_MATRIX[user_type]
    
    st.markdown("---")
    st.header("🧬 临床变量采集")
    with st.expander("🎓 发展压力维度", expanded=True):
        f1 = st.slider("学业适应压力", 0.0, 1.0, 0.4)
        f2 = st.slider("未来规划焦虑", 0.0, 1.0, 0.3)
        f3 = st.slider("成就动机负荷", 0.0, 1.0, 0.5)
    with st.expander("🛌 躯体与环境维度", expanded=True):
        f4 = st.slider("睡眠质量问题", 0.0, 1.0, 0.3)
        f5 = st.slider("生活自理障碍", 0.0, 1.0, 0.2)
        f6 = st.slider("环境适应难度", 0.0, 1.0, 0.4)
        f7 = st.slider("经济压力感知", 0.0, 1.0, 0.2)
    with st.expander("🌐 社交与反馈维度"):
        f8 = st.slider("人际关系张力", 0.0, 1.0, 0.3)
        f9 = st.slider("社交媒体依赖", 0.0, 1.0, 0.4)
    
    resilience_val = st.slider("🛡️ 心理弹性 (Resilience Buffer)", 0.0, 1.0, 0.5)
    
    if st.button("💾 记录本次动态评估", use_container_width=True):
        user_inputs = {"学业适应": f1, "未来规划": f2, "成就动机": f3, "睡眠质量": f4, "生活自理": f5, "环境适应": f6, "经济压力": f7, "人际关系": f8, "社交依赖": f9}
        val, _ = calculation_engine(user_inputs, resilience_val, current_weights)
        st.session_state.history.append({"时间": datetime.now().strftime("%H:%M:%S"), "CAI指数": round(val, 1), "类型": user_type.split(' ')[0]})
        st.toast(f"已存档: {user_type.split(' ')[0]}评估数据")

# --- 7. 主界面：实时仿真 ---
st.title("🧠 灵图 Pro (MindGraph)")
st.markdown(f"#### 基于 **MSCM v3.0** 多维应激协同干预模型的动态监测平台")

tab_diag, tab_trend = st.tabs(["🎯 实时诊断与干预", "📈 动态趋势溯源"])

with tab_diag:
    user_inputs = {"学业适应": f1, "未来规划": f2, "成就动机": f3, "睡眠质量": f4, "生活自理": f5, "环境适应": f6, "经济压力": f7, "人际关系": f8, "社交依赖": f9}
    anxiety_val, weights_map = calculation_engine(user_inputs, resilience_val, current_weights)
    
    col_l, col_r = st.columns([1.3, 1])
    with col_l:
        df_radar = pd.DataFrame(dict(r=list(user_inputs.values()), theta=list(user_inputs.keys())))
        fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True, range_r=[0, 1])
        fig.update_traces(fill='toself', fillcolor='rgba(0, 251, 255, 0.2)', line_color='#00fbff')
        fig.update_layout(polar=dict(bgcolor='rgba(16, 20, 30, 0.5)'), paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.metric("核心焦虑指数 (CAI)", f"{anxiety_val:.1f}%", delta=f"当前模式: {user_type.split(' ')[0]}")
        st.write("---")
        st.subheader("📋 临床级联合干预建议")
        # 提取当前分型下贡献度最高的前三因子
        top_3 = [f[0] for f in sorted(weights_map.items(), key=lambda x: x[1], reverse=True)[:3] if f[1] > 0.05]
        for factor in top_3:
            adv_steps = ADVICE_DB.get(factor, [])
            st.markdown(f'''
                <div class="advice-box">
                    <span style="color:#00fbff; font-weight:bold; font-size:1.1em;">Target: {factor}</span>
                    {"".join([f'<div class="action-step">{step}</div>' for step in adv_steps])}
                </div>
            ''', unsafe_allow_html=True)

with tab_trend:
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)
        fig_line = px.line(df_hist, x="时间", y="CAI指数", color="类型", markers=True, title="受试者应激水平历史波动曲线")
        fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_line, use_container_width=True)
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("💡 点击左侧‘记录本次动态评估’按钮，即可开始生成多模式历史追踪图谱。")

st.markdown("---")
st.caption("SDFMU 医学信息与人工智能学院 | 算法：MSCM-Dynamic-Weights v3.0 | 开发者：fuan")