# components/pricing.py
import streamlit as st
import stripe

from components.database import get_user_subscription, get_user_upload_count

# Initialize Stripe with your secret key
stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
stripe.product_link = st.secrets["stripe_link"]
stripe.test_product_id = st.secrets["stripe_product_id"]
stripe.end_point_secrete = st.secrets["STRIPE_ENDPOINT_SECRET"]
# Define plan details
PLANS = {
    "free": {
        "name": "Free Tier",
        "price": "$0",
        "upload_limit": 10,
        "features": [
            "Basic PDF text extraction",
            "TXT and CSV exports",
            "5 uploads per month",
        ],
        "stripe_price_id": None,
    },
    "basic": {
        "name": "Basic",
        "price": "$9.99/month",
        "upload_limit": 50,
        "features": [
            "Enhanced PDF text extraction",
            "All export formats",
            "50 uploads per month",
            "Email support",
        ],
        "stripe_price_id": "prod_S8KYEhYoCp3d0d",
    },
    "premium": {
        "name": "Premium",
        "price": "$19.99/month",
        "upload_limit": 200,
        "features": [
            "Advanced PDF text extraction",
            "All export formats",
            "200 uploads per month",
            "Priority support",
            "Additional AI features",
        ],
        "stripe_price_id": "prod_S8KYEhYoCp3d0d",
    },
    "Enterprise": {
        "name": "Enterprise",
        "price": "$19.99/month",
        "upload_limit": 200,
        "features": [
            "Advanced PDF text extraction",
            "All export formats",
            "200 uploads per month",
            "Priority support",
            "Additional AI features",
        ],
        "stripe_price_id": "prod_S8KYEhYoCp3d0d",
    },
}


def create_checkout_session(price_id, user_id, user_email):
    """Create a Stripe checkout session"""
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=user_email,
            client_reference_id=user_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                },
            ],
            mode="subscription",
            success_url=f"{st.secrets.get('BASE_URL', 'http://localhost:8501')}/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{st.secrets.get('BASE_URL', 'http://localhost:8501')}/?canceled=true",
        )
        return checkout_session
    except Exception as e:
        st.error(f"Error creating checkout session: {str(e)}")
        return None


def packages():
    # Get current user info
    user_info = st.session_state.user_info
    user_id = user_info.get("id")
    user_email = user_info.get("email")

    # Get subscription details
    current_subscription = get_user_subscription(user_id)
    current_plan = current_subscription.get("plan", "free")
    upload_count = get_user_upload_count(user_id)

    st.title("Subscription Plans")
    st.write("Choose the plan that best fits your needs.")

    # Display current subscription info
    st.info(
        f"You are currently on the **{current_plan.capitalize()} Plan** with {upload_count}/{current_subscription['upload_limit']} uploads used."
    )

    # Show packages in columns
    cols = st.columns(len(PLANS))

    for i, (plan_id, plan) in enumerate(PLANS.items()):
        with cols[i]:
            st.subheader(plan["name"])
            st.write(f"**{plan['price']}**")
            st.write(f"**{plan['upload_limit']} uploads**")
            for feature in plan["features"]:
                st.write(f"✓ {feature}")

            if plan_id == current_plan:
                st.success("Current Plan")
            elif plan_id == "free":
                st.button(
                    "Downgrade to Free",
                    key=f"btn_{plan_id}",
                    on_click=lambda: st.session_state.update(
                        {"show_confirm_downgrade": True}
                    ),
                )
            else:
                # Create a button for paid plans
                if st.button(f"Upgrade to {plan['name']}", key=f"btn_{plan_id}"):
                    if plan["stripe_price_id"]:
                        checkout_session = create_checkout_session(
                            plan["stripe_price_id"], user_id, user_email
                        )
                        if checkout_session:
                            st.markdown(
                                f"""
                            <meta http-equiv="refresh" content="0;url={checkout_session.url}">
                            """,
                                unsafe_allow_html=True,
                            )
                            st.write("Redirecting to payment page...")
                    else:
                        st.error("Price ID not configured for this plan.")

    # Display confirmation for downgrade
    if st.session_state.get("show_confirm_downgrade", False):
        st.warning(
            "Are you sure you want to downgrade to the Free plan? You will lose access to some features."
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Downgrade"):
                # Implement downgrade logic here
                # Update subscription in the database
                st.success("Successfully downgraded to Free plan.")
                st.session_state.pop("show_confirm_downgrade")
                st.experimental_rerun()
        with col2:
            if st.button("No, Keep Current Plan"):
                st.session_state.pop("show_confirm_downgrade")
                st.experimental_rerun()
