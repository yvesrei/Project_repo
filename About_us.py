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
            "image": "Images/Alexander.jpg",
        },
        {
            "name": "Yves Reichelt",
            "role": "Coding",
            "email": "yves.reichelt@student.unisg.ch",
            "image": "Images/Yves.jpg",
        },
        {
            "name": "Raphael Loacker",
            "role": "Coding",
            "email": "raphael.loacker@student.unisg.ch",
            "image": "Images/Raphael.jpg",
        },
        {
            "name": "Loris Häcki",
            "role": "Presenting",
            "email": "loris.haecki@student.unisg.ch",
            "image": "Images/Loris.jpg",
        },
        {
            "name": "Ian Pettenhofer",
            "role": "Presenting",
            "email": "ian.pettenhofer@student.unisg.ch",
            "image": "Images/Ian.jpg",
        },
    ]

    # Layout: 3 columns per row for member cards
    cols = st.columns(3)

    for i, member in enumerate(members):
        col = cols[i % 3]
        with col:
            # Individual member image (use placeholder if you don’t have them yet)
            st.image(member["image"], width=180, caption=member["name"])
            st.markdown(f"**{member['name']}**")
            st.write(member["role"])
            st.write(f"[{member['email']}](mailto:{member['email']})")