This is the description of the Group number 02.01, we will focus on making a tool for foodies that will present three restaurant recommendations for a group that want's to eat together. ChatGPT was used to assist with parts of the code and documentation.

Here is how it works

Folder structure:
Project_repo/
│
├── app.py                     # Main Streamlit app controller (routing + session setup)
├── session_init.py            # Ensures session_state variables are initialized
│
├── Show_homepage.py           # Homepage UI logic (select #participants)
├── Questionnaire.py           # Questionnaire input page
├── spider_chart.py            # Aggregation, radar charts, clustering (ML), AI summary
├── Show_api_results.py        # Restaurant result page (API scoring + display)
│
├── explanation.py             # AI helper functions (group summary)
├── api_client.py              # Restaurant API client (fetches & filters data)
│
├── About_us.py                # About Us page (team presentation)
│
├── Images/                    # Team photos & static assets
│
├── pages/                     # (Optional) Streamlit multipage folder
│
├── data/
│   └── sample_api_data.json   # Local fallback for testing API logic
│
├── requirements.txt           # Python + Streamlit dependencies
├── theme-info.txt             # Documentation of our custom Streamlit theme
└── README.md                  # Project documentation

About the Theme (config.toml):
We created a custom Streamlit theme for the app.
To avoid any risk of breaking the working project during submission, we did not include the active config.toml file.
Instead, we provide theme-info.txt, which contains the full theme configuration for documentation purposes as well as further explanation.