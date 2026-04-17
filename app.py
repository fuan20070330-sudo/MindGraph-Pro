import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- 1. 核心 UI 样式 ---
st.set_page_config(page_title="MindGraph Pro v7.9", layout="wide")

st.markdown("""
    <style>
    .advice-box { background-color: #1c2128; padding: 20px; border-left: 5px solid #00fbff; border-radius: 10px; margin-bottom: 15px; color: #ffffff !important; }
    .action-step { background-color: rgba(0, 251, 255, 0.08); border-radius: 4px; padding: 6px 10px; margin: 4px 0; font-size: 0.95em; border-left: 2px solid #00fbff; }
    .stMetric { background-color: rgba(255,255,255,0.05); padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 状态记忆 ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 3. 专业干预库 ---
ADVICE_DB = {
    "学业适应": {"mech": "认知负荷理论", "steps": ["<b>信息卸载</b>：书面化所有待办。", "<b>25/5循环</b>：强制脑力冷却。"]},
    "未来规划": {"mech": "预见性应激调节", "steps": ["<b>最小行动</b>：锁定下周具体任务。", "<b>概率校准</b>：审视担忧真实发生率。"]},
    "成就动机": {"mech": "自我价值条件化", "steps": ["<b>非结果评价</b>：记录努力过程。", "<b>防御性悲观</b>：预演最坏情况对策。"]},
    "睡眠质量": {"mech": "内稳态控制", "steps": ["<b>15分钟法则</b>：睡不着即起床。", "<b>光暗切换</b>：睡前1h低照度。"]},
    "生活自理": {"mech": "环境秩序感", "steps": ["<b>1平米原则</b>：从整理桌面开始。", "<b>仪式重建</b>：锚定生活作息。"]},
    "环境适应": {"mech": "注意力恢复 (ART)", "steps": ["<b>视觉恢复</b>：眺望绿植3分钟。", "<b>心理领地</b>：摆放熟悉旧物。"]},
    "经济压力": {"mech": "稀缺心态认知", "steps": ["<b>财务透明</b>：记账去情绪化。", "<b>带宽释放</b>：定日检查开支。"]},
    "人际关系": {"mech": "课题分离理论", "steps": ["<b>边界识别</b>：分清谁的课题。", "<b>我向沟通</b>：表达感受而非指责。"]},
    "社交依赖": {"mech": "多巴胺反馈调节", "steps": ["<b>数字断舍离</b>：设定无手机区。", "<b>深度阅读</b>：重塑注意力环路。"]}
}

# --- 4. 动力学算法 (SCHM) ---
def calculation_engine(inputs, resilience):
    weights = {"学业适应": 0.85, "未来规划": 0.75, "成就动机": 0.70, "睡眠质量": 0.95, 
               "生活自理": 0.60, "环境适应": 0.55, "经济压力": 0.65, "人际关系": 0.80, "社交依赖": 0.50}
    scores_map = {k: (v ** 1.7) * weights.get(k, 1.0) for k, v in inputs.items()}
    total_raw = sum(scores_map.values())
    resilience_buffer = 1 - (resilience * 0.3) 
    max_val = sum(weights.values()) * 1.15
    anxiety_idx = (total_raw / max_val) * 100 * resilience_buffer
    return max(0, min(anxiety_idx, 100.0)), scores_map

# --- 5. 侧边栏：全因子采集 ---
with st.sidebar:
    st.header("🧬 临床变量采集")
    with st.expander("🎓 发展压力", expanded=True):
        f1 = st.slider("学业适应", 0.0, 1.0, 0.4)
        f2 = st.slider("未来规划", 0.0, 1.0, 0.3)
        f3 = st.slider("成就动机", 0.0, 1.0, 0.5)
    with st.expander("🛌 躯体与环境", expanded=True):
        f4 = st.slider("睡眠质量", 0.0, 1.0, 0.3)
        f5 = st.slider("生活自理", 0.0, 1.0, 0.2)
        f6 = st.slider("环境适应", 0.0, 1.0, 0.4)
        f7 = st.slider("经济压力", 0.0, 1.0, 0.2)
    with st.expander("🌐 社交与反馈"):
        f8 = st.slider("人际关系", 0.0, 1.0, 0.3)
        f9 = st.slider("社交依赖", 0.0, 1.0, 0.4)
    resilience_val = st.slider("🛡️ 心理弹性 (Resilience)", 0.0, 1.0, 0.5)
    
    st.write("---")
    if st.button("💾 记录本次评估点", use_container_width=True):
        current_inputs = {"学业适应": f1, "未来规划": f2, "成就动机": f3, "睡眠质量": f4, "生活自理": f5, "环境适应": f6, "经济压力": f7, "人际关系": f8, "社交依赖": f9}
        val, _ = calculation_engine(current_inputs, resilience_val)
        st.session_state.history.append({"时间": datetime.now().strftime("%H:%M:%S"), "焦虑指数": round(val, 1)})
        st.toast("评估数据已存入动态序列")

# --- 6. 主界面呈现 ---
st.title("🧠 MindGraph Pro v7.9")
st.caption("校园应激动力学监测系统 | SDFMU 医学信息与人工智能学院")

tab_diag, tab_trend = st.tabs(["🎯 实时诊断", "📉 趋势溯源"])

with tab_diag:
    user_inputs = {"学业适应": f1, "未来规划": f2, "成就动机": f3, "睡眠质量": f4, "生活自理": f5, "环境适应": f6, "经济压力": f7, "人际关系": f8, "社交依赖": f9}
    anxiety_val, weights_map = calculation_engine(user_inputs, resilience_val)
    
    col_l, col_r = st.columns([1.3, 1])
    with col_l:
        df_radar = pd.DataFrame(dict(r=list(user_inputs.values()), theta=list(user_inputs.keys())))
        fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True, range_r=[0, 1], title="应激因子级联雷达")
        fig.update_traces(fill='toself', fillcolor='rgba(0, 251, 255, 0.2)', line_color='#00fbff')
        fig.update_layout(polar=dict(bgcolor='rgba(16, 20, 30, 0.5)'), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.metric("核心焦虑指数 (CAI)", f"{anxiety_val:.1f}%", delta=f"弹性抵消 -{(resilience_val*30):.1f}%")
        st.write("---")
        st.subheader("💡 联合干预建议")
        top_3 = [f[0] for f in sorted(weights_map.items(), key=lambda x: x[1], reverse=True)[:3] if f[1] > 0.1]
        for factor in top_3:
            adv = ADVICE_DB.get(factor)
            st.markdown(f'<div class="advice-box"><span style="color:#00fbff; font-size:0.8em;"><b>{factor}</b></span><br>' + "".join([f'<div class="action-step">{s}</div>' for s in adv['steps']]) + '</div>', unsafe_allow_html=True)

with tab_trend:
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)
        # 趋势图
        fig_line = px.line(df_hist, x="时间", y="焦虑指数", markers=True, title="心理应激动态演变曲线")
        fig_line.update_traces(line_color='#00fbff', marker_size=8)
        fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_line, use_container_width=True)
        # 数据列表
        with st.expander("查看历史评估原始数据"):
            st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("💡 提示：在左侧侧边栏点击‘记录本次评估点’，即可生成动态趋势图。")

st.markdown("---")
if st.button("🗑️ 清空历史记录"):
    st.session_state.history = []
    st.rerun()