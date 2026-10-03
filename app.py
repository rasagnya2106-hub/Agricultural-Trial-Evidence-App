import streamlit as st

from tools import search_trials, compare_trials, get_trial_sources


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Agricultural Trial Evidence App",
    page_icon="🌱",
    layout="wide",
)


# =========================================================
# TITLE
# =========================================================

st.title("🌱 Agricultural Trial Evidence App")

st.write(
    "Search agricultural trial records, compare results, "
    "and inspect original evidence sources."
)


# =========================================================
# SEARCH SECTION
# =========================================================

st.header("🔎 Search Trials")

col1, col2, col3 = st.columns(3)

with col1:

    crop = st.selectbox(
        "Crop",
        [
            "All",
            "Wheat",
            "Potato",
        ],
    )


with col2:

    product = st.selectbox(
        "Product",
        [
            "All",
            "Harvest Plus",
            "Root Boost",
        ],
    )


with col3:

    country = st.selectbox(
        "Country",
        [
            "All",
            "France",
            "Germany",
            "Spain",
        ],
    )


col4, col5 = st.columns(2)

with col4:

    trial_type = st.selectbox(
        "Trial Type",
        [
            "All",
            "Scientific",
            "Demonstration",
        ],
    )


with col5:

    year_options = [
        "All",
        2021,
        2023,
        2024,
        2025,
    ]

    year = st.selectbox(
        "Year",
        year_options,
    )


search_button = st.button(
    "Search Trials",
    type="primary",
)


# =========================================================
# SEARCH RESULTS
# =========================================================

if search_button:

    results = search_trials(
        crop=None if crop == "All" else crop,
        product=None if product == "All" else product,
        country=None if country == "All" else country,
        year=None if year == "All" else year,
        trial_type=None if trial_type == "All" else trial_type,
    )

    st.session_state["search_results"] = results


if "search_results" in st.session_state:

    results = st.session_state["search_results"]

    st.subheader(
        f"Results ({len(results)})"
    )

    if not results:

        st.info(
            "No matching agricultural trials were found."
        )

    else:

        for trial in results:

            with st.expander(
                f"{trial['trial_id']} — "
                f"{trial['crop']} — "
                f"{trial['product']} — "
                f"{trial['country']} — "
                f"{trial['year']}"
            ):

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.write(
                        f"**Trial Type:** "
                        f"{trial['trial_type']}"
                    )

                with col2:

                    treatment = trial[
                        "treatment_yield_kg_ha"
                    ]

                    if treatment is not None:

                        st.write(
                            f"**Treatment:** "
                            f"{treatment:,.0f} kg/ha"
                        )

                    else:

                        st.write(
                            "**Treatment:** Not reported"
                        )

                with col3:

                    control = trial[
                        "control_yield_kg_ha"
                    ]

                    if control is not None:

                        st.write(
                            f"**Control:** "
                            f"{control:,.0f} kg/ha"
                        )

                    else:

                        st.write(
                            "**Control:** Not reported"
                        )

                st.write(
                    f"**Source:** {trial['source']}"
                )

                if trial["notes"]:

                    st.write(
                        f"**Notes:** {trial['notes']}"
                    )


# =========================================================
# SOURCE INSPECTION
# =========================================================

st.divider()

st.header("📚 Original Sources")

trial_id = st.text_input(
    "Enter a Trial ID to inspect its original sources",
    placeholder="Example: T03",
)

if st.button("View Sources"):

    if not trial_id.strip():

        st.warning(
            "Please enter a trial ID."
        )

    else:

        sources = get_trial_sources(
            trial_id.strip().upper()
        )

        if not sources:

            st.info(
                "No source records were found for this trial."
            )

        else:

            for source in sources:

                st.markdown(
                    f"### {source['source']}"
                )

                st.write(
                    f"**Source Type:** "
                    f"{source['source_type']}"
                )

                st.write(
                    f"**Treatment Yield:** "
                    f"{source['treatment_yield_kg_ha']} kg/ha"
                    if source["treatment_yield_kg_ha"]
                    is not None
                    else "**Treatment Yield:** Not reported"
                )

                st.write(
                    f"**Control Yield:** "
                    f"{source['control_yield_kg_ha']} kg/ha"
                    if source["control_yield_kg_ha"]
                    is not None
                    else "**Control Yield:** Not reported"
                )

                if source["notes"]:

                    st.write(
                        f"**Notes:** {source['notes']}"
                    )

                st.divider()


# =========================================================
# COMPARE TRIALS
# =========================================================

st.header("📊 Compare Trials")

trial_ids_input = st.text_input(
    "Enter Trial IDs separated by commas",
    placeholder="Example: T01, T02",
)

if st.button("Compare Trials"):

    trial_ids = [
        trial_id.strip().upper()
        for trial_id in trial_ids_input.split(",")
        if trial_id.strip()
    ]

    if not trial_ids:

        st.warning(
            "Please enter at least one Trial ID."
        )

    else:

        comparison = compare_trials(
            trial_ids
        )

        if not comparison:

            st.info(
                "No matching trials were found."
            )

        else:

            for trial in comparison:

                st.markdown(
                    f"### {trial['trial_id']} — "
                    f"{trial['country']} "
                    f"({trial['year']})"
                )

                treatment = trial[
                    "treatment_yield_kg_ha"
                ]

                control = trial[
                    "control_yield_kg_ha"
                ]

                if (
                    treatment is not None
                    and control is not None
                ):

                    st.write(
                        f"Treatment: "
                        f"{treatment:,.0f} kg/ha"
                    )

                    st.write(
                        f"Control: "
                        f"{control:,.0f} kg/ha"
                    )

                    st.write(
                        f"Difference: "
                        f"{trial['absolute_change_kg_ha']:,.0f} kg/ha"
                    )

                    if trial[
                        "percentage_change"
                    ] is not None:

                        st.write(
                            f"Percentage change: "
                            f"{trial['percentage_change']:.2f}%"
                        )

                else:

                    st.warning(
                        "Comparison cannot be calculated "
                        "because a treatment or control value "
                        "is missing."
                    )


# =========================================================
# AI AGENT SECTION
# =========================================================

st.divider()

st.header("🤖 Evidence Agent")

st.write(
    "Ask a natural-language question about the "
    "agricultural trial evidence."
)

question = st.text_area(
    "Your question",
    placeholder=(
        "Example: What evidence supports Root Boost "
        "improving potato yields?"
    ),
)

if st.button("Ask Evidence Agent"):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Agent is analyzing the evidence..."
        ):

            try:

                from agent import ask_agent

                result = ask_agent(
                    question.strip()
                )

                st.subheader(
                    "Answer"
                )

                st.write(
                    result["answer"]
                )

                st.subheader(
                    "🔧 Agent Activity"
                )

                activity = result.get(
                    "tool_activity",
                    []
                )

                if not activity:

                    st.write(
                        "No tools were called."
                    )

                else:

                    for item in activity:

                        with st.expander(
                            f"Step {item['step']}: "
                            f"{item['tool']}"
                        ):

                            st.write(
                                "**Arguments:**"
                            )

                            st.json(
                                item["arguments"]
                            )

                            st.write(
                                "**Tool Result:**"
                            )

                            st.json(
                                item["result"]
                            )

            except Exception as error:

                error_text = str(error)

                if (
                    "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                ):
                    st.warning(
                        "The AI model quota has been exhausted "
                        "for the current free-tier period."
                    )

                    st.info(
                        "The structured trial search, comparison, "
                        "and original-source features are still "
                        "available."
                    )

                elif (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                ):
                    st.warning(
                        "The AI model is temporarily unavailable. "
                        "Please try again later."
                    )

                else:
                    st.error(
                        "The AI agent encountered an error."
                    )

                st.caption(
                    f"Technical detail: {error}"
                )