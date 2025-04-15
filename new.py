import streamlit as st
import streamlit_shadcn_ui as ui


def pricing():
    cols = st.columns(3)
    with cols[0]:
        with ui.card(key="pricing1"):
            ui.element(
                "span",
                children=["Starter"],
                className="text-sm font-medium m-2",
                key="pricing_starter_0",
            )
            ui.element(
                "h1",
                children=["$0 per month"],
                className="text-2xl font-bold m-2",
                key="pricing_starter_1",
            )
            ui.element(
                "link_button",
                key="nst2_btn",
                text="Subscribe",
                variant="default",
                className="h-10 w-full rounded-md m-2",
                url="#",
            )
            ui.element(
                "p",
                children=[
                    "Ideal for individual users who want to get started with the Streamlit SaaS Template."
                ],
                className="text-xs font-medium m-2 mt-2 mb-2",
                key="pricing_starter_2",
            )
            ui.element(
                "p",
                children=["This includes: "],
                className="text-muted-foreground text-xs font-medium m-2",
                key="pricing_starter_3",
            )
            ui.element(
                "p",
                children=["- Access to all basic features."],
                className="text-muted-foreground text-xs font-medium m-1",
                key="pricing_starter_4",
            )
            ui.element(
                "p",
                children=["- Community support."],
                className="text-muted-foreground text-xs font-medium m-1",
                key="pricing_starter_5",
            )
            ui.element(
                "p",
                children=["- 1 active project."],
                className="text-muted-foreground text-xs font-medium m-1",
                key="pricing_starter_6",
            )

    with cols[1]:
        with ui.card(key="pricing2"):

            ui.element(
                "span",
                children=["Teams"],
                className="text-sm font-medium m-2",
                key="pricing_pro_0",
            )
            ui.element(
                "h1",
                children=["$100 per month"],
                className="text-2xl font-bold m-2",
                key="pricing_pro_1",
            )
            ui.element(
                "link_button",
                key="nst2_btn",
                text="Subscribe",
                variant="default",
                className="h-10 w-full rounded-md m-2",
                url="#",
            )
            ui.element(
                "p",
                children=["Perfect for small businesses requiring advanced features."],
                className="text-xs font-medium m-2 mt-2 mb-2",
                key="pricing_pro_2",
            )
            ui.element(
                "p",
                children=["This includes: "],
                className="text-muted-foreground text-xs font-medium m-2",
                key="pricing_pro_3",
            )
            ui.element(
                "p",
                children=["- 10GB Storage Access."],
                className="text-muted-foreground text-xs font-medium m-1",
                key="pricing_pro_4",
            )
            ui.element(
                "p",
                children=["- 625,000 API calls per month."],
                className="text-muted-foreground text-xs font-medium m-1",
                key="pricing_pro_5",
            )
            ui.element(
                "p",
                children=["- 10 active projects."],
                className="text-muted-foreground text-xs font-medium m-1",
                key="pricing_pro_6",
            )
            ui.element(
                "p",
                children=["- Priority email support."],
                className="text-muted-foreground text-xs font-medium m-1",
                key="pricing_pro_7",
            )

    with cols[2]:
        with ui.card(key="pricing3"):
            ui.element(
                "span",
                children=["Enterprise"],
                className="text-sm font-medium m-2",
                key="pricing_enterprise_0",
            )
            ui.element(
                "h1",
                children=["$500 per month"],
                className="text-2xl font-bold m-2",
                key="pricing_enterprise_1",
            )
            ui.element(
                "link_button",
                key="nst2_btn",
                text="Subscribe",
                variant="default",
                className="h-10 w-full rounded-md m-2",
                url="#",
            )
            ui.element(
                "p",
                children=[
                    "Designed for large companies and teams with specific needs."
                ],
                className="text-xs font-medium m-2",
                key="pricing_enterprise_2",
            )
            ui.element(
                "p",
                children=["This includes: "],
                className="text-muted-foreground text-xs font-medium m-2",
                key="pricing_enterprise_3",
            )
            ui.element(
                "p",
                children=["- 50GB Storage Access."],
                className="text-muted-foreground text-xs font-medium m-1",
                key="pricing_enterprise_4",
            )
            ui.element(
                "p",
                children=["- Unlimited API calls per month."],
                className="text-muted-foreground text-xs font-medium m-1",
                key="pricing_enterprise_5",
            )
            ui.element(
                "p",
                children=["- Unlimited active projects."],
                className="text-muted-foreground text-xs font-medium m-1",
                key="pricing_enterprise_6",
            )
            ui.element(
                "p",
                children=["- Dedicated account manager."],
                className="text-muted-foreground text-xs font-medium m-1",
                key="pricing_enterprise_7",
            )
            ui.element(
                "p",
                children=["- 24/7 priority support."],
                className="text-muted-foreground text-xs font-medium m-1",
                key="pricing_enterprise_8",
            )
    # with cols[3]:
    #     with ui.card(key="pricing3"):
    #         ui.element(
    #             "span",
    #             children=["Enterprise"],
    #             className="text-sm font-medium m-2",
    #             key="pricing_enterprise_0",
    #         )
    #         ui.element(
    #             "h1",
    #             children=["$500 per month"],
    #             className="text-2xl font-bold m-2",
    #             key="pricing_enterprise_1",
    #         )
    #         ui.element(
    #             "link_button",
    #             key="nst2_btn",
    #             text="Subscribe",
    #             variant="default",
    #             className="h-10 w-full rounded-md m-2",
    #             url="#",
    #         )
    #         ui.element(
    #             "p",
    #             children=[
    #                 "Designed for large companies and teams with specific needs."
    #             ],
    #             className="text-xs font-medium m-2",
    #             key="pricing_enterprise_2",
    #         )
    #         ui.element(
    #             "p",
    #             children=["This includes: "],
    #             className="text-muted-foreground text-xs font-medium m-2",
    #             key="pricing_enterprise_3",
    #         )
    #         ui.element(
    #             "p",
    #             children=["- 50GB Storage Access."],
    #             className="text-muted-foreground text-xs font-medium m-1",
    #             key="pricing_enterprise_4",
    #         )
    #         ui.element(
    #             "p",
    #             children=["- Unlimited API calls per month."],
    #             className="text-muted-foreground text-xs font-medium m-1",
    #             key="pricing_enterprise_5",
    #         )
    #         ui.element(
    #             "p",
    #             children=["- Unlimited active projects."],
    #             className="text-muted-foreground text-xs font-medium m-1",
    #             key="pricing_enterprise_6",
    #         )
    #         ui.element(
    #             "p",
    #             children=["- Dedicated account manager."],
    #             className="text-muted-foreground text-xs font-medium m-1",
    #             key="pricing_enterprise_7",
    #         )
    #         ui.element(
    #             "p",
    #             children=["- 24/7 priority support."],
    #             className="text-muted-foreground text-xs font-medium m-1",
    #             key="pricing_enterprise_8",
    #         )
