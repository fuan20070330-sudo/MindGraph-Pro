import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime

# --- 1. 基础配置与样式 ---
st.set_page_config(page_title="灵图 Pro - 医工交叉科研平台", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    /* 建议框样式：强制文字为白色 */
    .advice-box { 
        background-color: #1c2128; 
        padding: 20px; 
        border-left: 5px solid #00fbff; 
        border-radius: 10px; 
        margin-bottom: 15px;
        color: #FFFFFF !important; 
    }
    .advice-box b, .advice-box span { color: #00fbff !important; }
    .action-step { 
        background-color: rgba(0, 251, 255, 0.08); 
        border-radius: 4px; 
        padding: 6px 10px; 
        margin: 4px 0; 
        font-size: 0.9em; 
        border-left: 2px solid #00fbff; 
        color: #FFFFFF !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 数据库逻辑 (持久化用户档案) ---
conn = sqlite3.connect('mindgraph_pro_v5.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT, email TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS records(username TEXT, cai_score REAL, timestamp TEXT, type TEXT)')
conn.commit()

# --- 3. 深度邮件报告函数 ---
def send_professional_report(target_email, username, cai_score, history_df, top_factors):
    smtp_host = "smtp.163.com" 
    smtp_user = "fuan20070330@163.com"   # <--- 修改这里
    smtp_pass = "SPZ7Xy6ppfq9HaYB"      # <--- 修改这里
    
    # 专业分析语段
    level = "稳态" if cai_score < 40 else "警戒" if cai_score < 70 else "高压"
    trend_desc = "趋于平缓" if len(history_df) < 2 else ("上升" if history_df['CAI指数'].iloc[-1] > history_df['CAI指数'].iloc[-2] else "下降")
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #007bff;">灵图 Pro (MindGraph) 专业应激分析报告</h2>
        <p>尊敬的 <b>{username}</b> 同学：</p>
        <div style="background: #f4f7f6; padding: 15px; border-radius: 8px;">
            <p><b>当前评估状态：</b><span style="font-size: 20px; color: #d9534f;">{cai_score:.1f}% ({level})</span></p>
            <p><b>动态演变趋势：</b>{trend_desc}</p>
        </div>
        <h3>🔍 核心应激源分析</h3>
        <p>根据 MSCM 动力学模型，您当前的压力主要来源于：<b>{', '.join(top_factors)}</b>。</p>
        <h3>📊 历史监测数据</h3>
        <table border="1" style="border-collapse: collapse; width: 100%; text-align: center;">
            <tr style="background: #eee;"><th>时间</th><th>CAI 指数</th><th>测评模式</th></tr>
            {"".join([f"<tr><td>{r['时间']}</td><td>{r['CAI指数']}</td><td>{r['类型']}</td></tr>" for _, r in history_df.tail(5).iterrows()])}
        </table>
        <h3>💡 深度专家建议</h3>
        <ul>
            <li><b>认知重构：</b>针对{top_factors[0]}，建议采用课题分离法，降低过度卷入感。</li>
            <li><b>生理调节：</b>若CAI持续高于60%，请强制执行15分钟正念或规律睡眠补偿。</li>
        </ul>
        <hr>
        <p style="font-size: 12px; color: #777;">本报告由 SDFMU 医工交叉实验室算法自动生成。定期监测有助于建立心理韧性。祝好。</p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = target_email
    msg['Subject'] = Header(f"【灵图报告】{username}的应激动力学分析", 'utf-8')
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL(smtp_host, 465)
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [target_email], msg.as_string())
        server.quit()
        return True
    except: return False

# --- 4. 权重矩阵与引擎 (保持学术性) ---
PROFILE_MATRIX = {
    "平衡发展型 (General)": {"学业适应": 0.85, "未来规划": 0.75, "成就动机": 0.70, "睡眠质量": 0.92, "生活自理": 0.55, "环境适应": 0.60, "经济压力": 0.65, "人际关系": 0.82, "社交依赖": 0.55},
    "学业冲刺型 (Academic)": {"学业适应": 0.98, "未来规划": 0.92, "成就动机": 0.95, "睡眠质量": 0.95, "生活自理": 0.45, "环境适应": 0.50, "经济压力": 0.60, "人际关系": 0.55, "社交依赖": 0.35},
    "社交活跃型 (Social)": {"学业适应": 0.72, "未来规划": 0.65, "成就动机": 0.68, "睡眠质量": 0.88, "生活自理": 0.60, "环境适应": 0.75, "经济压力": 0.70, "人际关系": 0.96, "社交依赖": 0.92}
}

ADVICE_DB = {
    "学业适应": ["信息卸载：书面记录待办释放脑力", "脑力冷却：执行25/5分钟循环工作法"],
    "未来规划": ["最小行动：仅关注下周可控任务", "概率校准：客观评估风险发生率"],
    "成就动机": ["过程评价：记录今日努力而非结果", "防御性悲观：设定底线预案"],
    "睡眠质量": ["刺激控制：15min不睡则离开床铺", "光照调节：睡前1h低亮度环境"],
    "生活自理": ["1平米原则：从整理桌面微小区域开始", "习惯锚定：建立固定起床仪式"],
    "环境适应": ["感官恢复：接触自然声音或绿植", "领地建立：摆放个人化旧物"],
    "经济压力": ["去情绪化记录：仅记录不进行评判", "财务带宽：固定日期处理账单"],
    "人际关系": ["课题分离：识别并拒绝他人情绪绑架", "我向沟通：只陈述事实与感受"],
    "社交依赖": ["数字断舍离：设定手机禁入区", "单向输入：进行30分钟深度阅读"]
}

def calculation_engine(inputs, resilience, weights):
    scores_map = {k: (v ** 1.7) * weights.get(k, 1.0) for k, v in inputs.items()}
    total_raw = sum(scores_map.values())
    resilience_buffer = 1 - (resilience * 0.3)
    max_theoretical = sum(weights.values()) * 1.15
    anxiety_idx = (total_raw / max_theoretical) * 100 * resilience_buffer
    return max(0, min(anxiety_idx, 100.0)), scores_map

# --- 5. 核心逻辑控制 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🧠 灵图 Pro (MindGraph)")
    auth_choice = st.sidebar.radio("用户验证", ["登录", "注册"])
    if auth_choice == "注册":
        reg_user = st.text_input("设置用户名")
        reg_email = st.text_input("绑定电子邮箱")
        reg_pass = st.text_input("设置密码", type='password')
        if st.button("完成注册"):
            c.execute('INSERT INTO users VALUES (?,?,?)', (reg_user, reg_pass, reg_email))
            conn.commit()
            st.success("账号已创建，请切换至登录界面")
    else:
        log_user = st.sidebar.text_input("用户名")
        log_pass = st.sidebar.text_input("密码", type='password')
        if st.sidebar.button("进入系统"):
            c.execute('SELECT * FROM users WHERE username=? AND password=?', (log_user, log_pass))
            res = c.fetchone()
            if res:
                st.session_state.logged_in, st.session_state.username, st.session_state.email = True, log_user, res[2]
                st.rerun()
            else: st.sidebar.error("验证失败")

# --- 6. 登录后的科研主界面 ---
else:
    st.sidebar.title(f"👤 {st.session_state.username}")
    if st.sidebar.button("安全退出"):
        st.session_state.logged_in = False
        st.rerun()

    user_type = st.sidebar.selectbox("选择当前评价分型", list(PROFILE_MATRIX.keys()))
    
    with st.sidebar:
        st.markdown("---")
        # 采集 9 维数据
        f1 = st.slider("学业适应", 0.0, 1.0, 0.4); f2 = st.slider("未来规划", 0.0, 1.0, 0.3)
        f3 = st.slider("成就动机", 0.0, 1.0, 0.5); f4 = st.slider("睡眠质量", 0.0, 1.0, 0.3)
        f5 = st.slider("生活自理", 0.0, 1.0, 0.2); f6 = st.slider("环境适应", 0.0, 1.0, 0.4)
        f7 = st.slider("经济压力", 0.0, 1.0, 0.2); f8 = st.slider("人际关系", 0.0, 1.0, 0.3)
        f9 = st.slider("社交依赖", 0.0, 1.0, 0.4); res_val = st.slider("🛡️ 心理弹性", 0.0, 1.0, 0.5)

    tab1, tab2 = st.tabs(["🎯 实时评估", "📊 历史档案"])
    
    u_in = {"学业适应": f1, "未来规划": f2, "成就动机": f3, "睡眠质量": f4, "生活自理": f5, "环境适应": f6, "经济压力": f7, "人际关系": f8, "社交依赖": f9}
    val, w_map = calculation_engine(u_in, res_val, PROFILE_MATRIX[user_type])

    with tab1:
        c1, c2 = st.columns([1.2, 1])
        with c1:
            df_r = pd.DataFrame(dict(r=list(u_in.values()), theta=list(u_in.keys())))
            fig = px.line_polar(df_r, r='r', theta='theta', line_close=True, range_r=[0,1])
            fig.update_traces(fill='toself', fillcolor='rgba(0, 251, 255, 0.2)', line_color='#00fbff')
            fig.update_layout(polar=dict(bgcolor='#161b22'), paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.metric("核心焦虑指数 (CAI)", f"{val:.1f}%")
            top_3 = [f[0] for f in sorted(w_map.items(), key=lambda x: x[1], reverse=True)[:3]]
            if st.button("🚀 存档并发送深度分析报告"):
                # 持久化存储
                c.execute('INSERT INTO records VALUES (?,?,?,?)', (st.session_state.username, val, datetime.now().strftime("%m-%d %H:%M"), user_type.split(' ')[0]))
                conn.commit()
                # 读取最新历史用于邮件
                c.execute('SELECT cai_score, timestamp, type FROM records WHERE username=?', (st.session_state.username,))
                h_data = pd.DataFrame(c.fetchall(), columns=['CAI指数', '时间', '类型'])
                if send_professional_report(st.session_state.email, st.session_state.username, val, h_data, top_3):
                    st.success("专业报告已存入档案并发送至您的邮箱！")
                else: st.error("邮件通道异常，数据已保存在云端档案。")
            
            st.write("---")
            for f in top_3:
                st.markdown(f'<div class="advice-box"><b>优先干预项: {f}</b><br>{"<br>".join([f"· {s}" for s in ADVICE_DB[f]])}</div>', unsafe_allow_html=True)

    with tab2:
        c.execute('SELECT cai_score, timestamp, type FROM records WHERE username=?', (st.session_state.username,))
        all_recs = pd.DataFrame(c.fetchall(), columns=['CAI指数', '时间', '类型'])
        if not all_recs.empty:
            st.subheader("📈 心理应激动力学追踪图谱")
            fig_l = px.line(all_recs, x="时间", y="CAI指数", color="类型", markers=True)
            fig_l.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_l, use_container_width=True)
            st.dataframe(all_recs, use_container_width=True)
        else: st.info("暂无历史记录，请在‘实时评估’页完成首次存档。")