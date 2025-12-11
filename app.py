import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
import os
import base64


MODEL_FILE = "gart_model.pkl"
HISTORY_FILE = "gart_user_history.csv"
ABSHER_LOGO_PATH = "absher_logo.png.png"
TUWAIQ_LOGO_PATH = "tuwaiq_logo.png.png"


st.set_page_config(
    page_title="GART – Absher AI Behavior Guard",
    layout="wide"
)


def load_css(file_name: str):
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file '{file_name}' not found. Using default Streamlit style.")

load_css("style.css")


@st.cache_data
def load_logo_base64(path: str):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

absher_b64 = load_logo_base64(ABSHER_LOGO_PATH) if os.path.exists(ABSHER_LOGO_PATH) else None
tuwaiq_b64 = load_logo_base64(TUWAIQ_LOGO_PATH) if os.path.exists(TUWAIQ_LOGO_PATH) else None


COUNTRY_OPTIONS = [
    
    "Saudi Arabia (KSA)",
    "United Arab Emirates",
    "Qatar",
    "Bahrain",
    "Kuwait",
    "Oman",
    
    "Jordan",
    "Egypt",
    "Morocco",
    "Algeria",
    "Tunisia",
    "Lebanon",
    "Iraq",
    "Syria",
    "Palestine",
    "Yemen",
    "Sudan",
    
    "United States",
    "United Kingdom",
    "Canada",
    "Germany",
    "France",
    "Spain",
    "Italy",
    "Netherlands",
    "Switzerland",
    "India",
    "Pakistan",
    "Philippines",
    "China",
    "Japan",
    "South Korea",
    "Brazil",
    "South Africa",
    
    "Other",
]


HIGH_RISK_COUNTRIES = {
    "Iraq",
    "Syria",
    "Yemen",
    "Sudan",
    "Brazil",        
    "South Africa",  
}

def map_country_to_model(country_ui: str) -> str:
    """
    Map the UI country selection to the 3 categories
    the model was trained on: KSA, Unknown, HighRiskCountry
    """
    if country_ui in ["Saudi Arabia (KSA)", "KSA"]:
        return "KSA"
    if country_ui in HIGH_RISK_COUNTRIES:
        return "HighRiskCountry"
    return "Unknown"



ACTION_OPTIONS = [
    
    "view_profile",
    "view_services",
    "view_violations",
    "view_vehicle_list",
    "view_passport_details",

    
    "update_mobile",
    "update_email",
    "update_address",
    "renew_id",
    "replace_lost_id",
    "digital_id_access",

    "renew_passport",
    "issue_passport",
    "replace_lost_passport",

    "renew_driver_license",
    "replace_lost_license",
    "pay_violation",

    "vehicle_transfer",
    "renew_vehicle_registration",
    "insurance_verification",

    "issue_worker_exit_reentry",
    "cancel_exit_reentry",
    "update_sponsor",
    "renew_worker_iqama",

    "issue_birth_certificate",
    "add_newborn",
    "book_civil_appointment",

    "book_appointment",
    "cancel_appointment",
    "reschedule_appointment",

    "pay_fees",
    "pay_ticket",
    "pay_gov_services",

    "report_cybercrime",
    "emergency_alert",
    "travel_permission_status",
]

def map_action_to_model(action_ui: str) -> str:
    """
    Map the UI action selection to the 4 action categories
    used when training the model: view, pay, renew_passport, update_mobile
    """
    if action_ui.startswith("view_"):
        return "view"

    if action_ui.startswith("pay_") or action_ui in ["pay_gov_services"]:
        return "pay"

    if "passport" in action_ui and "renew" in action_ui:
        return "renew_passport"

    if action_ui in [
        "update_mobile",
        "update_email",
        "update_address",
        "digital_id_access",
    ]:
        return "update_mobile"

    
    return "view"



model = joblib.load(MODEL_FILE)


history_cols = [
    "timestamp", "user_id", "country", "device", "action", "hour",
    "VPN", "failed_logins", "typing_speed",
    "model_risk", "behavior_risk", "final_risk",
    "level", "decision"
]

if os.path.exists(HISTORY_FILE):
    history_df = pd.read_csv(HISTORY_FILE)
else:
    history_df = pd.DataFrame(columns=history_cols)

if "events" not in st.session_state:
    st.session_state["events"] = history_df.to_dict(orient="records")



def compute_behavior_deviation(user_id, attempt_row, full_history):
    """
    Returns (behavior_risk_score 0-100, reasons list) based on this user's history.
    History uses the same columns as attempt_row: country, device, action, hour, VPN, failed_logins, typing_speed
    """
    user_hist = full_history[full_history["user_id"] == user_id]

    if user_hist.empty:
        return 0, ["First login or limited history – baseline is being established for this user."]

    reasons = []
    diffs = 0
    checks = 0

    checks += 1
    common_country = user_hist["country"].mode()[0]
    if attempt_row["country"].iloc[0] != common_country:
        diffs += 1
        reasons.append(
            f"Unusual country: user usually logs in from {common_country}, "
            f"now from {attempt_row['country'].iloc[0]}."
        )

    checks += 1
    common_device = user_hist["device"].mode()[0]
    if attempt_row["device"].iloc[0] != common_device:
        diffs += 1
        reasons.append(
            f"Unusual device: typical device is {common_device}, "
            f"now using {attempt_row['device'].iloc[0]}."
        )

    checks += 1
    action_col = "action_model" if "action_model" in user_hist.columns else "action"
    common_action = user_hist[action_col].mode()[0]
    current_action = attempt_row["action"].iloc[0]
    if current_action != common_action:
        diffs += 1
        reasons.append(
            f"Unusual action: usual action is {common_action}, "
            f"now requesting {current_action}."
        )

    checks += 1
    avg_hour = user_hist["hour"].mean()
    hour_now = attempt_row["hour"].iloc[0]
    if abs(hour_now - avg_hour) > 5:
        diffs += 1
        reasons.append(
            f"Unusual time: average login around {avg_hour:.1f}h, now at {hour_now}h."
        )

    checks += 1
    avg_speed = user_hist["typing_speed"].mean()
    speed_now = attempt_row["typing_speed"].iloc[0]
    if abs(speed_now - avg_speed) > 2:
        diffs += 1
        reasons.append(
            f"Typing pattern changed: normal speed ~{avg_speed:.1f} chars/sec, now {speed_now:.1f}."
        )

    checks += 1
    avg_fail = user_hist["failed_logins"].mean()
    fails_now = attempt_row["failed_logins"].iloc[0]
    if fails_now >= avg_fail + 2:
        diffs += 1
        reasons.append(
            f"More failed logins than usual: average {avg_fail:.1f}, now {fails_now}."
        )

    deviation_ratio = diffs / max(checks, 1)
    behavior_risk = int(deviation_ratio * 100)

    if behavior_risk == 0:
        reasons.append("Behavior closely matches user’s historical pattern.")

    return behavior_risk, reasons



st.markdown('<div class="cyber-bg">', unsafe_allow_html=True)


logos_html = ""
if absher_b64 or tuwaiq_b64:
    logos_html = "<div class='hero-logos'>"
    if absher_b64:
        logos_html += f"<img src='data:image/png;base64,{absher_b64}' class='hero-logo absher-logo' />"
    if tuwaiq_b64:
        logos_html += f"<img src='data:image/png;base64,{tuwaiq_b64}' class='hero-logo tuwaiq-logo' />"
    logos_html += "</div>"

title_text = "GART – Absher AI Behavior Guard"
title_html = "".join([f"<span class='hero-char'>{c if c != ' ' else '&nbsp;'}</span>" for c in title_text])

st.markdown(
    f"""
<div class="hero-card cyber-glass">
<div class="hero-content-centered">
{logos_html}
<span class="hero-badge">AI • Cybersecurity • Behavioral Analytics</span>
<h1>{title_html}</h1>
<span class="sub">حارس السلوك الذكي لأبشر</span>
<p>
Real-time AI engine that learns each citizen’s digital behavior and predicts risky logins or actions before fraud happens.
<br/>محرك ذكاء اصطناعي يتعلّم سلوك المستخدم ويكشف محاولات الدخول أو العمليات المشبوهة قبل وقوع الاختراق.
</p>
</div>
</div>
""",
    unsafe_allow_html=True
)

st.markdown("<div class='spacer-md'></div>", unsafe_allow_html=True)


tab_live, tab_soc = st.tabs(
    ["🧪 Live Risk Check | محاكاة الدخول", "🛡 SOC Dashboard | لوحة المراقبة الأمنية"]
)


with tab_live:
    st.markdown("<h3 style='text-align: center; color: #d4af37; margin-bottom: 2rem;'>Simulated Absher Login | محاكاة تسجيل الدخول في أبشر</h3>", unsafe_allow_html=True)

    with st.form("login_form"):
        col1, col2 = st.columns(2)

        with col1:
            user_id = st.number_input(
                "User ID (معرّف المستخدم)", min_value=1, max_value=999999, value=1
            )

            country_ui = st.selectbox(
                "Country / الدولة",
                options=COUNTRY_OPTIONS,
                index=0,
            )

            device_type = st.selectbox("Device / الجهاز", ["mobile", "desktop"])

            action_ui = st.selectbox(
                "Action / الخدمة المطلوبة",
                ACTION_OPTIONS,
                index=0,
            )

        with col2:
            time_of_day = st.slider(
                "Time of day (hour) / وقت الدخول", 0, 23, datetime.now().hour
            )
            failed_logins_last_hour = st.number_input(
                "Failed logins in last hour / عدد المحاولات الفاشلة في ساعة",
                min_value=0, max_value=10, value=0
            )
            is_vpn = st.selectbox(
                "Using VPN? / استخدام VPN",
                [0, 1],
                format_func=lambda x: "Yes / نعم" if x == 1 else "No / لا"
            )
            typing_speed = st.slider(
                "Typing speed (chars/sec) / سرعة الكتابة",
                min_value=1.0, max_value=10.0, value=4.0
            )

        submitted = st.form_submit_button("Check Risk | تقييم مستوى الخطورة", use_container_width=True)

    if submitted:
        country_model = map_country_to_model(country_ui)
        action_model = map_action_to_model(action_ui)

        features_row = pd.DataFrame([{
            "user_id": user_id,
            "time_of_day": time_of_day,
            "country": country_model,
            "device_type": device_type,
            "failed_logins_last_hour": failed_logins_last_hour,
            "action_type": action_model,
            "is_vpn": is_vpn,
            "typing_speed": typing_speed
        }])

        prob_attack = model.predict_proba(features_row)[0][1]
        model_risk = int(prob_attack * 100)

        attempt_for_behavior = pd.DataFrame([{
            "user_id": user_id,
            "country": country_ui,  
            "country_model": country_model,  
            "device": device_type,
            "action": action_model,
            "hour": time_of_day,
            "VPN": "Yes" if is_vpn == 1 else "No",
            "failed_logins": failed_logins_last_hour,
            "typing_speed": typing_speed
        }])

        behavior_risk, behavior_reasons = compute_behavior_deviation(
            user_id, attempt_for_behavior, history_df
        )

        final_risk = min(100, int(0.6 * model_risk + 0.4 * behavior_risk))

        if final_risk < 30:
            level = "LOW"
            color = "🟢"
            decision = "Allow"
            message = "Login allowed – behavior and risk are within normal range."
        elif final_risk < 60:  
            level = "MEDIUM"
            color = "🟡"
            decision = "Challenge"
            message = "Require additional verification (OTP / Face ID)."
        else:
            level = "HIGH"
            color = "🔴"
            decision = "Block"
            message = "Block request and alert the security team."

        st.markdown("### Risk Evaluation | تقييم مستوى الخطورة")
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Model risk", f"{model_risk}/100")
        col_r2.metric("Behavior risk", f"{behavior_risk}/100")
        col_r3.metric("Final risk", f"{final_risk}/100")

        st.success(f"Final level: {color} **{level}**  •  Decision: **{decision}**")
        st.write(message)

        st.markdown("#### Behavioral Analysis | تحليل السلوك")
        for r in behavior_reasons:
            st.markdown(f"- {r}")

        
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_id,
            "country": country_ui,  
            "device": device_type,
            "action": action_ui,  
            "action_model": action_model,  
            "hour": time_of_day,
            "VPN": "Yes" if is_vpn == 1 else "No",
            "failed_logins": failed_logins_last_hour,
            "typing_speed": typing_speed,
            "model_risk": model_risk,
            "behavior_risk": behavior_risk,
            "final_risk": final_risk,
            "level": level,
            "decision": decision
        }

        history_df = pd.concat([history_df, pd.DataFrame([record])], ignore_index=True)
        history_df.to_csv(HISTORY_FILE, index=False)
        st.session_state["events"].append(record)


with tab_soc:
    st.markdown("### Security Operations Overview | لوحة المراقبة الأمنية")

    if not st.session_state["events"]:
        st.info("No login attempts yet. Use the **Live Risk Check** tab to generate events.")
    else:
        log_df = pd.DataFrame(st.session_state["events"])

        
        col_a, col_b, col_c, col_d = st.columns(4)
        total = len(log_df)
        blocked = (log_df["decision"] == "Block").sum()
        challenged = (log_df["decision"] == "Challenge").sum()
        allowed = (log_df["decision"] == "Allow").sum()
        unique_users = log_df["user_id"].nunique()

        col_a.metric("Total attempts", total)
        col_b.metric("Blocked", blocked)
        col_c.metric("Challenged", challenged)
        col_d.metric("Allowed", allowed)

        st.markdown("<div class='spacer-xs'></div>", unsafe_allow_html=True)

        
        high_risk_df = log_df[log_df["level"] == "HIGH"]
        high_risk_count = len(high_risk_df)
        high_risk_pct = (high_risk_count / total * 100) if total > 0 else 0

        med_risk_df = log_df[log_df["level"] == "MEDIUM"]

        col_hr1, col_hr2, col_hr3 = st.columns(3)
        col_hr1.metric("High-risk attempts (HIGH)", high_risk_count)
        col_hr2.metric("High-risk percentage", f"{high_risk_pct:.1f}%")
        col_hr3.metric("Unique users", unique_users)

        st.markdown("<div class='spacer-sm'></div>", unsafe_allow_html=True)

        
        st.markdown("#### Risk level distribution | توزيع مستويات الخطورة")
        risk_counts = (
            log_df["level"]
            .value_counts()
            .reindex(["LOW", "MEDIUM", "HIGH"], fill_value=0)
        )
        
        
        risk_chart_html = f"""
        <div id="risk-chart" style="width: 100%; height: 400px;"></div>
        <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
        <script type="text/javascript">
            var chartDom = document.getElementById('risk-chart');
            var myChart = echarts.init(chartDom);
            var option = {{
                backgroundColor: 'transparent',
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{b}}: {{c}} ({{d}}%)'
                }},
                legend: {{
                    orient: 'horizontal',
                    bottom: '0%',
                    textStyle: {{
                        color: '#ffffff',
                        fontSize: 14
                    }}
                }},
                series: [
                    {{
                        name: 'Risk Level',
                        type: 'pie',
                        radius: ['40%', '70%'],
                        avoidLabelOverlap: false,
                        itemStyle: {{
                            borderRadius: 10,
                            borderColor: '#0a0f1e',
                            borderWidth: 2
                        }},
                        label: {{
                            show: true,
                            position: 'outside',
                            formatter: '{{b}}: {{c}}',
                            color: '#ffffff',
                            fontSize: 14,
                            fontWeight: 'bold'
                        }},
                        emphasis: {{
                            label: {{
                                show: true,
                                fontSize: 18,
                                fontWeight: 'bold'
                            }},
                            itemStyle: {{
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }}
                        }},
                        labelLine: {{
                            show: true,
                            lineStyle: {{
                                color: '#ffffff'
                            }}
                        }},
                        data: [
                            {{
                                value: {risk_counts['LOW']}, 
                                name: 'LOW',
                                itemStyle: {{
                                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                        {{ offset: 0, color: '#10b981' }},
                                        {{ offset: 1, color: '#059669' }}
                                    ])
                                }}
                            }},
                            {{
                                value: {risk_counts['MEDIUM']}, 
                                name: 'MEDIUM',
                                itemStyle: {{
                                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                        {{ offset: 0, color: '#f59e0b' }},
                                        {{ offset: 1, color: '#d97706' }}
                                    ])
                                }}
                            }},
                            {{
                                value: {risk_counts['HIGH']}, 
                                name: 'HIGH',
                                itemStyle: {{
                                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                        {{ offset: 0, color: '#ef4444' }},
                                        {{ offset: 1, color: '#dc2626' }}
                                    ])
                                }}
                            }}
                        ]
                    }}
                ]
            }};
            myChart.setOption(option);
            window.addEventListener('resize', function() {{
                myChart.resize();
            }});
        </script>
        """
        st.components.v1.html(risk_chart_html, height=450)

        st.markdown("<div class='spacer-sm'></div>", unsafe_allow_html=True)

        
        st.markdown("#### Top countries by attempts (model view) | أكثر الدول من حيث المحاولات")
        country_counts = log_df["country"].value_counts().head(10)
        if not country_counts.empty:
            countries_list = country_counts.index.tolist()
            attempts_list = country_counts.values.tolist()
            
            country_chart_html = f"""
            <div id="country-chart" style="width: 100%; height: 400px;"></div>
            <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
            <script type="text/javascript">
                var chartDom = document.getElementById('country-chart');
                var myChart = echarts.init(chartDom);
                var option = {{
                    backgroundColor: 'transparent',
                    tooltip: {{
                        trigger: 'axis',
                        axisPointer: {{
                            type: 'shadow'
                        }},
                        formatter: '{{b}}: {{c}} attempts'
                    }},
                    grid: {{
                        left: '3%',
                        right: '4%',
                        bottom: '3%',
                        top: '3%',
                        containLabel: true
                    }},
                    xAxis: {{
                        type: 'value',
                        axisLine: {{
                            lineStyle: {{
                                color: '#ffffff'
                            }}
                        }},
                        splitLine: {{
                            lineStyle: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }},
                        axisLabel: {{
                            color: '#ffffff'
                        }}
                    }},
                    yAxis: {{
                        type: 'category',
                        data: {countries_list[::-1]},
                        axisLine: {{
                            lineStyle: {{
                                color: '#ffffff'
                            }}
                        }},
                        axisLabel: {{
                            color: '#ffffff',
                            fontSize: 12
                        }}
                    }},
                    series: [
                        {{
                            name: 'Attempts',
                            type: 'bar',
                            data: {attempts_list[::-1]},
                            itemStyle: {{
                                borderRadius: [0, 10, 10, 0],
                                color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                                    {{ offset: 0, color: '#3b82f6' }},
                                    {{ offset: 1, color: '#60a5fa' }}
                                ])
                            }},
                            emphasis: {{
                                itemStyle: {{
                                    color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                                        {{ offset: 0, color: '#2563eb' }},
                                        {{ offset: 1, color: '#3b82f6' }}
                                    ])
                                }}
                            }},
                            label: {{
                                show: true,
                                position: 'right',
                                color: '#ffffff',
                                fontWeight: 'bold'
                            }}
                        }}
                    ]
                }};
                myChart.setOption(option);
                window.addEventListener('resize', function() {{
                    myChart.resize();
                }});
            </script>
            """
            st.components.v1.html(country_chart_html, height=450)

        st.markdown("<div class='spacer-sm'></div>", unsafe_allow_html=True)

        
        st.markdown("#### Attempts by action type | توزيع المحاولات حسب نوع الخدمة")
        action_counts = log_df["action"].value_counts().head(10)
        if not action_counts.empty:
            actions_list = action_counts.index.tolist()
            action_attempts_list = action_counts.values.tolist()
            
            action_chart_html = f"""
            <div id="action-chart" style="width: 100%; height: 400px;"></div>
            <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
            <script type="text/javascript">
                var chartDom = document.getElementById('action-chart');
                var myChart = echarts.init(chartDom);
                var option = {{
                    backgroundColor: 'transparent',
                    tooltip: {{
                        trigger: 'axis',
                        axisPointer: {{
                            type: 'shadow'
                        }}
                    }},
                    grid: {{
                        left: '3%',
                        right: '4%',
                        bottom: '3%',
                        top: '3%',
                        containLabel: true
                    }},
                    xAxis: {{
                        type: 'category',
                        data: {actions_list},
                        axisLine: {{
                            lineStyle: {{
                                color: '#ffffff'
                            }}
                        }},
                        axisLabel: {{
                            color: '#ffffff',
                            rotate: 45,
                            fontSize: 11
                        }}
                    }},
                    yAxis: {{
                        type: 'value',
                        axisLine: {{
                            lineStyle: {{
                                color: '#ffffff'
                            }}
                        }},
                        splitLine: {{
                            lineStyle: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }},
                        axisLabel: {{
                            color: '#ffffff'
                        }}
                    }},
                    series: [
                        {{
                            name: 'Attempts',
                            type: 'bar',
                            barWidth: '15%',
                            data: {action_attempts_list},
                            itemStyle: {{
                                borderRadius: [10, 10, 0, 0],
                                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                    {{ offset: 0, color: '#10b981' }},
                                    {{ offset: 1, color: '#059669' }}
                                ])
                            }},
                            emphasis: {{
                                itemStyle: {{
                                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                        {{ offset: 0, color: '#34d399' }},
                                        {{ offset: 1, color: '#10b981' }}
                                    ])
                                }}
                            }},
                            label: {{
                                show: true,
                                position: 'top',
                                color: '#ffffff',
                                fontWeight: 'bold'
                            }}
                        }}
                    ]
                }};
                myChart.setOption(option);
                window.addEventListener('resize', function() {{
                    myChart.resize();
                }});
            </script>
            """
            st.components.v1.html(action_chart_html, height=450)

        st.markdown("<div class='spacer-sm'></div>", unsafe_allow_html=True)

        
        st.markdown("#### Last login attempts | آخر محاولات الدخول")
        st.dataframe(
            log_df.sort_values("timestamp", ascending=False).head(50),
            use_container_width=True
        )

        
        st.markdown("---")
        st.markdown("### User Insight & Risk History | ملف المستخدم السلوكي")

        try:
            log_df["user_id"] = log_df["user_id"].astype(int)
        except Exception:
            pass

        user_ids = sorted(log_df["user_id"].unique().tolist())
        selected_user = st.selectbox(
            "Select User ID to inspect | اختر معرّف المستخدم",
            user_ids,
            key="user_inspect"
        )

        user_df = log_df[log_df["user_id"] == selected_user].copy()
        user_df["timestamp"] = pd.to_datetime(user_df["timestamp"], errors="coerce")
        user_df = user_df.sort_values("timestamp")

        if not user_df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Attempts for this user", len(user_df))
            c2.metric("Average final risk", f"{user_df['final_risk'].mean():.1f}/100")
            c3.metric("Last decision", user_df.iloc[-1]["decision"])

            st.markdown("#### Risk timeline for this user | تطوّر مستوى الخطورة لهذا المستخدم")
            line_df = user_df.set_index("timestamp")[["final_risk"]]
            st.line_chart(line_df, width="stretch")

            st.markdown("#### History for this user | سجل هذا المستخدم")
            st.dataframe(
                user_df[[
                    "timestamp", "country", "device", "action",
                    "hour", "VPN", "failed_logins",
                    "typing_speed", "final_risk", "level", "decision"
                ]],
                use_container_width=True
            )


st.markdown("</div>", unsafe_allow_html=True)