import streamlit as st

def load_hero():
    st.markdown(
        """
        <div class="hero-card cyber-glass">

            <!-- Logos Row -->
            <div class="hero-logos">
                <img src="static/absher_logo.png" class="hero-logo absher-logo"/>
                <img src="static/tuwaiq_logo.png" class="hero-logo tuwaiq-logo"/>
            </div>

            <!-- Main Content -->
            <div class="hero-content">
                <div class="hero-left">
                    <h1>GART – Absher AI Behavior Guard</h1>
                    <span class="sub">حارس السلوك الذكي لأبشر</span>
                    <p>
                        Real-time AI system predicting risky logins using behavioral analytics.
                        <br/>
                        محرك ذكاء اصطناعي يقوم بتحليل السلوك للتنبؤ بمحاولات الدخول الخطرة.
                    </p>
                </div>

                <div class="hero-right">
                    <span class="hero-badge">AI • Cybersecurity • Behavioral Analytics</span>
                </div>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )
