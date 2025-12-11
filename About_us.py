import streamlit as st


def show_about_us():
    st.title("About Us")
    st.subheader("Meet the FOODMINGLE Team!")

    # ---- Group section ----
    
    st.image("Images/group_photo.jpg", use_column_width=True, caption="The FOODMINGLE team")

    st.markdown(
        """
        Motivated team of 5 Swiss young guys from Zürich, Luzern, Bern, and Appenzell Ausserrhoden -
        all studying at the University of St. Gallen.  
        Trying to solve the world's bigger problems by starting with the small ones (the FOODMINGLE problem).  

        *If choosing a restaurant takes longer than cooking the food, we consider that a societal emergency.*
        """
    )
    st.markdown("<br><br>", unsafe_allow_html=True)

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
            "name": "Ian Pettenhofer",
            "role": "Presenting",
            "email": "ian.pettenhofer@student.unisg.ch",
            "image": "Images/ian.jpg",
        },
        {
            "name": "Loris Häcki",
            "role": "Presenting",
            "email": "loris.haecki@student.unisg.ch",
            "image": "Images/loris.jpg",
        },
        {
            "name": "Raphael Loacker",
            "role": "Coding",
            "email": "raphael.loacker@student.unisg.ch",
            "image": "Images/raphael.jpg",
        },
    ]

    # Layout: 2 columns per row for the first four member cards (vertical images)
    vertical_members = members[:4]
    horizontal_member = members[4]

    cols = st.columns(2)

    for i, member in enumerate(vertical_members):
        col = cols[i % 2]   # cycle through column 0 and 1
        with col:
            st.image(member["image"], use_column_width=True)
            st.markdown(f"**{member['name']}**")
            st.write(member["role"])
            st.write(f"[{member['email']}](mailto:{member['email']})")

    # Center the horizontal image below the four vertical ones
    spacer_left, center_col, spacer_right = st.columns([1, 2, 1])
    with center_col:
        st.image(horizontal_member["image"], width=420)
        st.markdown("<style>img {image-rendering: auto;}</style>", unsafe_allow_html=True)
        st.markdown(f"**{horizontal_member['name']}**")
        st.write(horizontal_member["role"])
        st.write(f"[{horizontal_member['email']}](mailto:{horizontal_member['email']})")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## A Final Message from Us")
    st.markdown(
        """
        Thank you for exploring FOODMINGLE: a project that started as a simple idea among friends
        and grew into something we are truly proud of.

        We hope our app brings people closer together, helps groups decide faster,
        and turns the stress of choosing a restaurant into something fun and effortless.

        *Made with late-night coding sessions, laughter, and way too many food debates.*
        """
    )
    