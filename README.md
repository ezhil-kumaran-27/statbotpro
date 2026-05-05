# 📊 StatBot Pro — Autonomous CSV Data Analyst

> Infotact Solutions · AI R&D Wing · Confidential

---

## 📁 Project Structure

```
statbot_pro/
├── app.py                  ← Streamlit UI (light professional theme)
├── agent.py                ← LLM pipeline: question → code → result
├── security.py             ← Code security validator
├── utils.py                ← CSV loading, chart saving, safe exec
├── requirements.txt        ← Python dependencies
├── data/
│   └── sample_sales.csv    ← Built-in demo dataset (60 rows)
└── static/
    └── charts/             ← Auto-created; PNG charts saved here
```

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.10+
- pip
- Groq API key (get free at https://console.groq.com)

### 1. Unzip and enter folder
```bash
unzip statbot_pro.zip
cd statbot_pro
```

### 2. Create virtual environment (recommended)
```bash
python -m venv .venv

# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your Groq API key to `.env`
Open `.env` and replace the placeholder:
```
GROQ_API_KEY=your-groq-api-key-here
```

### 5. Run the app
```bash
streamlit run app.py
```

Opens at **http://localhost:8501**

---

## 🔑 Get a Free Groq API Key

1. Visit **https://console.groq.com**
2. Sign up or sign in with your account
3. Navigate to API Keys section
4. Click **Create API Key**
5. Copy the key and paste it into `.env`

---

## 🚀 Quick Start

1. Add your Groq API key to `.env`
2. Run `streamlit run app.py`
3. Click **"Load Sample Dataset"** to try the built-in sales data
4. Go to **"Ask StatBot"** tab and try:

```
What is the total revenue per region?
Plot monthly revenue as a line chart
Which sales rep has the highest total revenue?
Show a heatmap of average revenue by region and product
Plot a pie chart of revenue by category
What is the correlation between marketing spend and revenue?
Show the top 5 products by units sold as a bar chart
Plot revenue distribution as a histogram
```

---

## 🛡️ Security Architecture

| Layer | Mechanism |
|---|---|
| Regex scan | Blocks `os.system`, `subprocess`, `shutil`, `rm -rf`, etc. |
| AST inspection | Rejects any import not in the safe whitelist |
| Write-mode block | `open()` in write/append mode blocked |
| Network block | `requests`, `urllib`, `socket` imports blocked |
| Eval/Exec block | Raw `eval()` and `exec()` blocked |
| Isolated namespace | Code runs in a dict — cannot access global Python state |

---

## 🧩 How It Works

```
User Question
     │
     ▼
agent.py → _df_context()         # Build DataFrame description
     │
     ▼
call_claude()  ──►  Groq Mixtral 8x7B   # LLM generates Python code
     │◄── code block
     │
     ▼
security.py → validate_code()    # Regex + AST safety check
     │
     ▼
utils.py → safe_exec()           # Code runs in isolated namespace
     │
     ├── ANSWER variable  ──►  Displayed as text
     └── plt figure       ──►  Saved as PNG, shown + downloadable
```

---

## 🧪 Test Queries by Category

### Exploration
```
Show first 10 rows
What are the column names and their types?
How many rows and columns does this dataset have?
```

### Aggregation
```
What is the average, min, and max of each numeric column?
Total revenue per region
Which product category has the most sales?
```

### Trends
```
Plot monthly revenue trend as a line chart
Show a 3-month rolling average of revenue
```

### Visualizations
```
Bar chart of total revenue by region
Pie chart of revenue by category
Histogram of customer ratings
Scatter plot: marketing spend vs revenue
Heatmap of correlations between numeric columns
Box plot of revenue by product
```

### Rankings
```
Top 5 sales reps by total revenue
Products ranked by average customer rating
Which month had the highest revenue?
```

---

## 🛠️ Customization

### Change the Gemini model
In `app.py`, update `call_claude()`:
```python
model_name="gemini-1.5-flash",   # faster & cheaper
# or
model_name="gemini-1.5-pro",     # default — most capable
```

### Allow more libraries
Add to `SAFE_MODULES` in `security.py` and to the namespace dict in `agent.py`.

---

## 📦 Deployment Options

### Streamlit Cloud (Free)
1. Push project to GitHub (make sure to NOT commit your `.env` file)
2. Go to **share.streamlit.io**
3. Select your repo, set `app.py` as the main file
4. Add `GEMINI_API_KEY` in Settings → Secrets

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
```bash
docker build -t statbot-pro .
docker run -p 8501:8501 -e GEMINI_API_KEY=your-gemini-api-key-here statbot-pro
```

---

*StatBot Pro · Infotact Solutions · AI R&D Wing · Confidential*
