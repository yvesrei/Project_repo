This is the description of the Group number 02.01, we will focus on making a tool for foodies that will present three restaurant recommendations for a group that want's to eat together.

Here is how it works

Folder structure:
project/
│
├── app.py                   # Main Streamlit app (integrator)
│
├── features/
│   ├── questionnaire.py     # The form
│   ├── spider_chart.py      # Radar chart generation
│   ├── explanation.py       # Explanation generator
│   ├── api_client.py        # Calls restaurant API
│   ├── recommend.py         # ML scoring + top 3
│   └── ui_components.py     # Cards for results page
│
├── data/
│   └── sample_api_data.json # For testing without API (optional)
│
├── requirements.txt
└── README.md
