import streamlit as st


def packages():
    st.subheader("Choose Your Plan")
    st.write("Select one of our subscription plans tailored to your needs:")

    plans = {
        "Free": {
            "Price": "$0/month",
            "Features": {
                "Basic Access": True,
                "Full Access": False,
                "Limited Support": True,
                "Priority Support": False,
                "Custom Integrations": False,
            },
        },
        "Standard": {
            "Price": "$10/month",
            "Features": {
                "Basic Access": True,
                "Full Access": True,
                "Limited Support": False,
                "Priority Support": True,
                "Custom Integrations": False,
            },
        },
        "Premium": {
            "Price": "$25/month",
            "Features": {
                "Basic Access": True,
                "Full Access": True,
                "Limited Support": False,
                "Priority Support": True,
                "Custom Integrations": True,
            },
        },
        "Enterprise": {
            "Price": "$50/month",
            "Features": {
                "Basic Access": True,
                "Full Access": True,
                "Limited Support": False,
                "Priority Support": True,
                "Custom Integrations": True,
            },
        },
    }

    col1, col2, col3, col4 = st.columns(4)

    css_style = """
    <style>
        .plan-container {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 350px; /* Adjust height as needed */
        }
        .plan-content {
            flex-grow: 0;
        }
        .plan-button {
            flex-grow: 0;
            margin-top: auto;
        }
    </style>
    """

    st.markdown(css_style, unsafe_allow_html=True)

    with col1:
        st.markdown(
            f"""
        <div class="plan-container">
            <div class="plan-content">
                <h3>Free</h3>
                <p><strong>Price:</strong> {plans['Free']['Price']}</p>
                <p><strong>Features:</strong></p>
                <ul style="list-style-type: none; padding: 0;">
                    <li>{'&#10004;' if plans['Free']['Features']['Basic Access'] else '&#10006;'} Basic Access</li>
                    <li>{'&#10004;' if plans['Free']['Features']['Full Access'] else '&#10006;'} Full Access</li>
                    <li>{'&#10004;' if plans['Free']['Features']['Limited Support'] else '&#10006;'} Limited Support</li>
                    <li>{'&#10004;' if plans['Free']['Features']['Priority Support'] else '&#10006;'} Priority Support</li>
                    <li>{'&#10004;' if plans['Free']['Features']['Custom Integrations'] else '&#10006;'} Custom Integrations</li>
                </ul>
            </div>
            <div class="plan-button">
                <button class="btn btn-primary" onclick="alert('You have selected the Free plan!')">Subscribe</button>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div class="plan-container">
            <div class="plan-content">
                <h3>Standard</h3>
                <p><strong>Price:</strong> {plans['Standard']['Price']}</p>
                <p><strong>Features:</strong></p>
                <ul style="list-style-type: none; padding: 0;">
                    <li>{'&#10004;' if plans['Standard']['Features']['Basic Access'] else '&#10006;'} Basic Access</li>
                    <li>{'&#10004;' if plans['Standard']['Features']['Full Access'] else '&#10006;'} Full Access</li>
                    <li>{'&#10004;' if plans['Standard']['Features']['Limited Support'] else '&#10006;'} Limited Support</li>
                    <li>{'&#10004;' if plans['Standard']['Features']['Priority Support'] else '&#10006;'} Priority Support</li>
                    <li>{'&#10004;' if plans['Standard']['Features']['Custom Integrations'] else '&#10006;'} Custom Integrations</li>
                </ul>
            </div>
            <div class="plan-button">
                <button class="btn btn-primary" onclick="alert('You have selected the Standard plan!')">Subscribe</button>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="plan-container">
            <div class="plan-content">
                <h3>Premium</h3>
                <p><strong>Price:</strong> {plans['Premium']['Price']}</p>
                <p><strong>Features:</strong></p>
                <ul style="list-style-type: none; padding: 0;">
                    <li>{'&#10004;' if plans['Premium']['Features']['Basic Access'] else '&#10006;'} Basic Access</li>
                    <li>{'&#10004;' if plans['Premium']['Features']['Full Access'] else '&#10006;'} Full Access</li>
                    <li>{'&#10004;' if plans['Premium']['Features']['Limited Support'] else '&#10006;'} Limited Support</li>
                    <li>{'&#10004;' if plans['Premium']['Features']['Priority Support'] else '&#10006;'} Priority Support</li>
                    <li>{'&#10004;' if plans['Premium']['Features']['Custom Integrations'] else '&#10006;'} Custom Integrations</li>
                </ul>
            </div>
            <div class="plan-button">
                <button class="btn btn-primary" onclick="alert('You have selected the Premium plan!')">Subscribe</button>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
        <div class="plan-container">
            <div class="plan-content">
                <h3>Enterprise</h3>
                <p><strong>Price:</strong> {plans['Enterprise']['Price']}</p>
                <p><strong>Features:</strong></p>
                <ul style="list-style-type: none; padding: 0;">
                    <li>{'&#10004;' if plans['Enterprise']['Features']['Basic Access'] else '&#10006;'} Basic Access</li>
                    <li>{'&#10004;' if plans['Enterprise']['Features']['Full Access'] else '&#10006;'} Full Access</li>
                    <li>{'&#10004;' if plans['Enterprise']['Features']['Limited Support'] else '&#10006;'} Limited Support</li>
                    <li>{'&#10004;' if plans['Enterprise']['Features']['Priority Support'] else '&#10006;'} Priority Support</li>
                    <li>{'&#10004;' if plans['Enterprise']['Features']['Custom Integrations'] else '&#10006;'} Custom Integrations</li>
                </ul>
            </div>
            <div class="plan-button">
                <button class="btn btn-primary" onclick="alert('You have selected the Enterprise plan!')">Subscribe</button>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.write("---")
    st.write("Contact us for more information or to customize your plan.")
