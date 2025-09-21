## AI jewellery 3D model designer

A **Streamlit app** that generates jewellery designs with **OpenAI (GPT & DALL·E 3)** and converts them into **3D models** using **CSM**.

### Features
- Generate jewellery design prompts (GPT).
- Create images with DALL·E 3.
- Convert images to `.glb` mesh 3D models via CSM.
- View and download 3D models in-app.

### Installation & running the app

Clone the repository and install dependencies:
```bash
git clone https://github.com/werefin/Jewellery-Design-Bot.git
cd Jewellery-Design-Bot
pip install -r requirements.txt
```

Configure your API keys:
```bash
export OPENAI_API_KEY = "openai_api_key"
export CSM_API_KEY = "csm_api_key"
```

Launch the app:
```bash
streamlit run app.py
```

Then, open `http://localhost:8501` in your browser.
