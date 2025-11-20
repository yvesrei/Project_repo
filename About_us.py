import streamlit as st


def show_about_us():
    st.title("About Us")
    st.subheader("Meet the FOODMINGLE Team")

    # ---- Group section ----
    # Put your group photo in e.g. `images/group_photo.jpg`
    st.image("Images/group_photo.jpg", use_column_width=True, caption="The FOODMINGLE team")

    st.markdown(
        """
        Motivated team of 5 Swiss young guys from Zürich, Luzern, Bern, and Appenzell Ausserrhoden -
        all studying at the University of St. Gallen.  
        Trying to solve the world's bigger problems by starting with the small ones (the FOODMINGLE problem).  

        *If choosing a restaurant takes longer than cooking the food, we consider that a societal emergency.*
        """
    )

    st.markdown("### Our Team")

    # Data for each team member
    members = [
        {
            "name": "Alexander Schön",
            "role": "Coding",
            "email": "alexander.schoen@student.unisg.ch",
            "image": "Images/alexander.jpg",
        },
        {
            "name": "Yves Reichelt",
            "role": "Coding",
            "email": "yves.reichelt@student.unisg.ch",
            "image": "Images/yves.jpg",
        },
        {
            "name": "Raphael Loacker",
            "role": "Coding",
            "email": "raphael.loacker@student.unisg.ch",
            "image": "Images/raphael.jpg",
        },
        {
            "name": "Loris Häcki",
            "role": "Presenting",
            "email": "loris.haecki@student.unisg.ch",
            "image": "Images/loris.jpg",
        },
        {
            "name": "Ian Pettenhofer",
            "role": "Presenting",
            "email": "ian.pettenhofer@student.unisg.ch",
            "image": "Images/ian.jpg",
        },
    ]

    # Layout: 2 columns per row for member cards
    cols = st.columns(2)

    for i, member in enumerate(members):
        col = cols[i % 2]   # cycle through column 0 and 1
        with col:
            # Individual member image (use placeholder if you don’t have them yet)
            st.image(member["image"], width=240)
            st.markdown(f"**{member['name']}**")
            st.write(member["role"])
            st.write(f"[{member['email']}](mailto:{member['email']})")

            # --- Project timeline section ---
    st.markdown("### Our Journey")

    st.markdown(
        """
        **October**

        - **10 October** – Initial idea and first brainstorming session  
        - **28 October** – Finalized the FOODMINGLE concept and overall structure  

        **November**

        - **7 November** – Split the team into frontend, backend/logic, and presenting roles  
        - **9–15 November** – Built the basic questionnaire flow and first version of the taste profile logic  
        - **15–20 November** – Connected the API logic and started mapping restaurant data to cuisines and atmospheres  
        - **20–25 November** – Integrated the group taste profile with the spider charts and built the first full end-to-end version  
        - **25 November** – First functioning version of the app  
        - **26–30 November** – Polished the code, improved the UI, and worked on documentation and the About Us page  

        **December**

        - **1 December** – Final adjustments and finishing touches for the hand-in  
                """
            )
    
def render_timeline():
    # CSS styles for the vertical timeline
    timeline_css = """
    <style>
    .timeline {
        position: relative;
        margin: 2rem 0;
        padding-left: 24px;
    }
    .timeline::before {
        content: "";
        position: absolute;
        left: 12px;
        top: 0;
        bottom: 0;
        width: 2px;
        background: #e0e0e0;
    }
    .timeline-month {
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .timeline-item {
        position: relative;
        margin-bottom: 1.2rem;
    }
    .timeline-item::before {
        content: "";
        position: absolute;
        left: 4px;
        top: 4px;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #ffffff;
        border: 2px solid #ff4b4b;
    }
    .timeline-date {
        font-weight: 600;
        margin-left: 24px;
    }
    .timeline-content {
        margin-left: 24px;
        color: #444444;
    }
    </style>
    """

    st.markdown("### Our Journey", unsafe_allow_html=True)
    st.markdown(timeline_css, unsafe_allow_html=True)

    # Define the events in order
    events = [
        {"month": "October", "date": "10 October",
         "text": "Initial idea and first brainstorming session."},
        {"month": "October", "date": "28 October",
         "text": "Finalized the FOODMINGLE concept and overall structure."},
        {"month": "November", "date": "7 November",
         "text": "Split the team into frontend, backend/logic, and presenting roles."},
        {"month": "November", "date": "9–15 November",
         "text": "Built the basic questionnaire flow and first version of the taste profile logic."},
        {"month": "November", "date": "15–20 November",
         "text": "Connected the API logic and started mapping restaurant data to cuisines and atmospheres."},
        {"month": "November", "date": "20–25 November",
         "text": "Integrated the group taste profile with the spider charts and built the first full end-to-end version."},
        {"month": "November", "date": "25 November",
         "text": "First functioning version of the app."},
        {"month": "November", "date": "26–30 November",
         "text": "Polished the code, improved the UI, and worked on documentation and the About Us page."},
        {"month": "December", "date": "1 December",
         "text": "Final adjustments and finishing touches for the hand-in."},
    ]

    # Render the timeline with month headings and items
    current_month = None
    st.markdown('<div class="timeline">', unsafe_allow_html=True)

    for event in events:
        # Print month heading once when it changes
        if event["month"] != current_month:
            current_month = event["month"]
            st.markdown(
                f'<div class="timeline-month">{current_month}</div>',
                unsafe_allow_html=True
            )

        # Print the individual event
        st.markdown(
            f'''
            <div class="timeline-item">
                <div class="timeline-date">{event["date"]}</div>
                <div class="timeline-content">{event["text"]}</div>
            </div>
            ''',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)