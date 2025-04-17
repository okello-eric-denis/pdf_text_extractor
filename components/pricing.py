# components/pricing.py
import streamlit as st

from components.database import (
    get_user_subscription,
    get_user_upload_count,
    update_user_subscription,
)

# import stripe - commented out for now


# Initialize Stripe with your secret key - commented out for now
# stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
# stripe.product_link = st.secrets["stripe_link"]
# stripe.test_product_id = st.secrets["stripe_product_id"]
# stripe.end_point_secrete = st.secrets["STRIPE_ENDPOINT_SECRET"]

# Define plan details
PLANS = {
    "free": {
        "name": "Free Tier",
        "price": "$0",
        "upload_limit": 10,
        "features": [
            "Basic PDF text extraction",
            "TXT and CSV exports",
            "10 uploads per month",
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
        "stripe_price_id": "price_basic",
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
        "stripe_price_id": "price_premium",
    },
    "enterprise": {
        "name": "Enterprise",
        "price": "$39.99/month",
        "upload_limit": 500,
        "features": [
            "Advanced PDF text extraction",
            "All export formats",
            "500 uploads per month",
            "Priority support",
            "Additional AI features",
            "API access",
        ],
        "stripe_price_id": "price_enterprise",
    },
}


def handle_plan_change(user_id, plan_id):
    try:
        update_user_subscription(user_id, plan_id, PLANS[plan_id]["upload_limit"])
        st.success(f"Successfully changed to {PLANS[plan_id]['name']} plan!")
        return True
    except Exception as e:
        st.error(f"Error updating subscription: {str(e)}")
        return False


def packages():
    user_info = st.session_state.user_info
    user_id = user_info.get("id")
    user_email = user_info.get("email")

    current_subscription = get_user_subscription(user_id)
    current_plan = current_subscription.get("plan", "free")
    upload_count = get_user_upload_count(user_id)

    if "show_confirm_downgrade" not in st.session_state:
        st.session_state.show_confirm_downgrade = False
    if "show_confirm_upgrade" not in st.session_state:
        st.session_state.show_confirm_upgrade = False
    if "upgrade_plan" not in st.session_state:
        st.session_state.upgrade_plan = None

    st.title("Subscription Plans")
    st.write("Choose the plan that best fits your needs.")

    st.info(
        f"You are currently on the **{current_plan.capitalize()} Plan** with {upload_count}/{current_subscription.get('upload_limit', PLANS[current_plan]['upload_limit'])} uploads used."
    )

    # Display confirmation modal only, hide plans during confirmation
    if st.session_state.get("show_confirm_downgrade", False):
        st.warning(
            "Are you sure you want to downgrade to the Free plan? You will lose access to premium features."
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Downgrade", key="confirm_downgrade"):
                if handle_plan_change(user_id, "free"):
                    st.session_state.show_confirm_downgrade = False
        with col2:
            if st.button("No, Keep Current Plan", key="cancel_downgrade"):
                st.session_state.show_confirm_downgrade = False
        return

    if st.session_state.get("show_confirm_upgrade", False) and st.session_state.get(
        "upgrade_plan"
    ):
        upgrade_plan = st.session_state.upgrade_plan
        st.warning(
            f"Are you sure you want to get the {PLANS[upgrade_plan]['name']} plan? You will be charged {PLANS[upgrade_plan]['price']}."
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Upgrade", key="confirm_upgrade"):
                if handle_plan_change(user_id, upgrade_plan):
                    st.session_state.show_confirm_upgrade = False
                    st.session_state.upgrade_plan = None
        with col2:
            if st.button("No, Cancel", key="cancel_upgrade"):
                st.session_state.show_confirm_upgrade = False
                st.session_state.upgrade_plan = None
        return

    # Show plans if no confirmation modals are active
    cols = st.columns(len(PLANS))
    for i, (plan_id, plan) in enumerate(PLANS.items()):
        with cols[i]:
            st.subheader(plan["name"])
            st.write(f"**{plan['price']}**")
            st.write(f"**{plan['upload_limit']} uploads**")
            for feature in plan["features"]:
                st.write(f"\u2713 {feature}")

            if plan_id == current_plan:
                st.success("Current Plan")
            elif plan_id == "free" and current_plan != "free":
                st.button(
                    "Downgrade to Free",
                    key=f"btn_{plan_id}",
                    on_click=lambda: st.session_state.update(
                        {"show_confirm_downgrade": True}
                    ),
                )
            elif plan_id != "free" and plan_id != current_plan:
                if st.button(f"Upgrade to {plan['name']}", key=f"btn_{plan_id}"):
                    st.session_state.upgrade_plan = plan_id
                    st.session_state.show_confirm_upgrade = True
