import os
import re
import time
import json
from pathlib import Path
from functools import lru_cache
from dotenv import load_dotenv

try:
    import requests
except Exception as e:
    requests = None
    print("Requests package import failed:", e)

try:
    from bs4 import BeautifulSoup
except Exception as e:
    BeautifulSoup = None
    print("BeautifulSoup import failed:", e)

# Load .env file
load_dotenv()

# Get GROQ API key and settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "groq-1")
# Optional override for the GROQ inference URL. If empty, a default will be used.
GROQ_API_URL = os.getenv("GROQ_API_URL")

# Gemini model
MODEL_NAME = "gemini-2.0-flash"
SOURCE_URL = "https://www.acharyaerptech.in/"
APPLICATION_PAGE = "/apply"
APPLICATION_URL = SOURCE_URL.rstrip('/') + APPLICATION_PAGE
DATA_STALE_HOURS = 12
DATA_FILE = Path(__file__).resolve().parent / "static" / "acharya_data.json"
SCRAPE_USER_AGENT = "Mozilla/5.0 (compatible; AcharyaBot/1.0; +https://www.acharyaerptech.in/)"

# Check API keys
if not GROQ_API_KEY:
    print("No model API key found. Set GROQ_API_KEY in .env.")

# GROQ availability flag
GROQ_AVAILABLE = bool(GROQ_API_KEY) and requests is not None


def call_groq(prompt_text, timeout=20):
    """Call a GROQ inference endpoint using requests. Returns a string or None on failure."""
    if not GROQ_AVAILABLE:
        return None

    url = GROQ_API_URL or f"https://api.groq.dev/v1/models/{GROQ_MODEL}/infer"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"input": prompt_text}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        print("GROQ request failed:", e)
        return None

    try:
        j = resp.json()
    except Exception:
        return resp.text

    # Try several common response formats
    if isinstance(j, dict):
        # Check common top-level fields
        for key in ("outputs", "result", "text", "response"):
            if key in j:
                val = j[key]
                if isinstance(val, str):
                    return val.strip()
                if isinstance(val, list) and val:
                    first = val[0]
                    if isinstance(first, dict):
                        for sub in ("content", "text", "output"):
                            if sub in first and isinstance(first[sub], str):
                                return first[sub].strip()
                    elif isinstance(first, str):
                        return first.strip()

    # Fallback to raw text
    return resp.text.strip()

SCRAPING_ENABLED = requests is not None and BeautifulSoup is not None
SCRAPING_DISABLED_MESSAGE = (
    "Note: live website scraping is unavailable in this environment, so answers are based on local fallback data."
)


def is_data_stale():
    if not DATA_FILE.exists():
        return True
    return (time.time() - DATA_FILE.stat().st_mtime) > DATA_STALE_HOURS * 3600


def save_site_data(data):
    try:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Failed to save local Acharya data:", e)


def extract_section(soup, keywords):
    for keyword in keywords:
        match = soup.find(string=re.compile(r"\b" + re.escape(keyword) + r"\b", re.I))
        if match:
            parent = match.parent
            if parent:
                return parent.get_text(" ", strip=True)
    return None


def scrape_site_data():
    if requests is None or BeautifulSoup is None:
        print("Skipping site scraping because requests or BeautifulSoup is unavailable.")
        return {}

    try:
        headers = {"User-Agent": SCRAPE_USER_AGENT}
        resp = requests.get(SOURCE_URL, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print("Failed to fetch Acharya site:", e)
        return {}

    try:
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print("Failed to parse Acharya site HTML:", e)
        return {}

    lower_text = soup.get_text(" ", strip=True).lower()
    data = {}

    if "bengaluru" in lower_text or "bangalore" in lower_text:
        data["location"] = "Bengaluru, Karnataka"

    fees_text = extract_section(soup, ["fee", "tuition", "scholarship"])
    if fees_text:
        data["fees"] = {"summary": fees_text}

    hostel_text = extract_section(soup, ["hostel", "boarding"])
    if hostel_text:
        data["hostel_fees"] = {"summary": hostel_text}

    placements_text = extract_section(soup, ["placement", "companies", "recruit"])
    if placements_text:
        data["placements"] = {"summary": placements_text}

    courses = []
    for li in soup.select("li"):
        li_text = li.get_text(" ", strip=True)
        if re.search(r"\b(course|program|branch|b\.tech|m\.ba|engineering|cse|ece|civil|mechanical)\b", li_text, re.I):
            courses.append(li_text)
    if courses:
        data["courses"] = {"engineering": list(dict.fromkeys(courses))}

    return data


def refresh_site_data():
    if SITE_DATA and not is_data_stale():
        return

    scraped = scrape_site_data()
    if scraped:
        SITE_DATA.clear()
        SITE_DATA.update(scraped)
        save_site_data(SITE_DATA)


PLACEMENT_HTML = """
<h3>📊 Acharya Institutes Placement Details</h3>

<table style=\"width:100%; border-collapse: collapse; margin-top:10px;\">
<tr>
<th style=\"border:1px solid #ccc; padding:8px;\">Year</th>
<th style=\"border:1px solid #ccc; padding:8px;\">Placement Rate</th>
<th style=\"border:1px solid #ccc; padding:8px;\">Highest Package</th>
<th style=\"border:1px solid #ccc; padding:8px;\">Average Package</th>
</tr>
<tr>
<td style=\"border:1px solid #ccc; padding:8px;\">2025</td>
<td style=\"border:1px solid #ccc; padding:8px;\">90%</td>
<td style=\"border:1px solid #ccc; padding:8px;\">65 LPA</td>
<td style=\"border:1px solid #ccc; padding:8px;\">7 LPA</td>
</tr>
<tr>
<td style=\"border:1px solid #ccc; padding:8px;\">2024</td>
<td style=\"border:1px solid #ccc; padding:8px;\">80%</td>
<td style=\"border:1px solid #ccc; padding:8px;\">21 LPA</td>
<td style=\"border:1px solid #ccc; padding:8px;\">7 LPA</td>
</tr>
<tr>
<td style=\"border:1px solid #ccc; padding:8px;\">2023</td>
<td style=\"border:1px solid #ccc; padding:8px;\">75-85%</td>
<td style=\"border:1px solid #ccc; padding:8px;\">45 LPA</td>
<td style=\"border:1px solid #ccc; padding:8px;\">5-7 LPA</td>
</tr>
<tr>
<td style=\"border:1px solid #ccc; padding:8px;\">2022</td>
<td style=\"border:1px solid #ccc; padding:8px;\">70%</td>
<td style=\"border:1px solid #ccc; padding:8px;\">21 LPA</td>
<td style=\"border:1px solid #ccc; padding:8px;\">4.25 LPA</td>
</tr>
<tr>
<td style=\"border:1px solid #ccc; padding:8px;\">2021</td>
<td style=\"border:1px solid #ccc; padding:8px;\">65-75%</td>
<td style=\"border:1px solid #ccc; padding:8px;\">8.25 LPA</td>
<td style=\"border:1px solid #ccc; padding:8px;\">3.5-5 LPA</td>
</tr>
</table>

<br>

<h4>🏢 Top Recruiters</h4>

<ul>
<li>Infosys</li>
<li>TCS</li>
<li>Wipro</li>
<li>Capgemini</li>
<li>IBM</li>
<li>Accenture</li>
<li>Oracle</li>
<li>Amazon</li>
<li>Dell</li>
<li>Bosch</li>
</ul>

<h4>📌 Best Placement Branches</h4>

<ul>
<li>CSE</li>
<li>ISE</li>
<li>AIML</li>
<li>Data Science</li>
</ul>
"""

FALLBACK_ANSWERS = {
    "admission": f"Acharya admission usually requires a completed application, 10+2 eligibility, and counselling. Submit your details here: <a href=\"{APPLICATION_URL}\" target=\"_blank\" rel=\"noopener\">Apply now</a>.",
    "courses": "Acharya offers engineering, MBA, B.Tech, and diploma programs. Visit the course brochure for specializations and intake details.",
    "placement": PLACEMENT_HTML,
    "hostel": "Hostel facilities include shared rooms, mess service, and 24/7 security. Contact admissions for availability and charges.",
    "library": "The library has books, journals, digital resources, and study spaces.",
    "campus": "Acharya campus has academic blocks, labs, hostels, sports facilities, and student support services.",
    "faculty": "Acharya faculty includes experienced professors and industry practitioners across departments.",
    "apply": f"To apply, submit your details at <a href=\"{APPLICATION_URL}\" target=\"_blank\" rel=\"noopener\">Apply now</a>.",
    "eligibility": "Most programs require a 10+2 pass with required subject scores. Contact Acharya admissions for exact eligibility.",
    "helpline": "Acharya admissions hotline: +91 74066 44449 / +91 97317 97677.",
    "events": "Acharya hosts cultural fests, seminars, workshops, and technical events throughout the year.",
}

SITE_DATA = {}

try:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            SITE_DATA = json.load(f)
except Exception as e:
    print("Failed to load local Acharya data:", e)

# Attempt to refresh site data but don't let network errors break module import
try:
    refresh_site_data()
except Exception as e:
    print("refresh_site_data() failed at import time:", e)


def get_site_answer(user_msg):
    if not SITE_DATA:
        return None

    text = user_msg.lower()

    if any(phrase in text for phrase in ["campus life"]):
        return (
            "Acharya campus life includes clubs, cultural events, sports, labs, and student support. "
            "Ask about hostels, events, or campus facilities for more details."
        )

    if any(term in text for term in ["admission", "apply", "eligibility"]):
        return f"Acharya admissions require a completed application, 10+2 eligibility, and counselling. Submit your details here: <a href=\"{APPLICATION_URL}\" target=\"_blank\" rel=\"noopener\">Apply now</a>."

    if any(term in text for term in ["placement", "job"]):
        return PLACEMENT_HTML

    answers = []

    if any(term in text for term in ["location", "campus"]):
        loc = SITE_DATA.get("location")
        if loc:
            answers.append(f"Acharya is located in {loc}.")

    include_general_fees = any(term in text for term in ["fee", "scholarship"])
    include_hostel_info = any(term in text for term in ["hostel"])
    include_college_term = "college" in text
    include_hostel_fee = include_hostel_info and "fee" in text

    def format_fee_block(fees_data):
        if isinstance(fees_data, str):
            return fees_data
        lines = []
        for key, value in fees_data.items():
            if isinstance(value, str):
                lines.append(value)
            else:
                lines.append(f"{key.replace('_', ' ').title()}: {value}")
        return "; ".join(lines)

    if include_hostel_info and include_college_term:
        fees = SITE_DATA.get("fees")
        if fees:
            answers.append("College fee: " + format_fee_block(fees))
        hostel = SITE_DATA.get("hostel_fees")
        if hostel:
            answers.append("Hostel fees: " + format_fee_block(hostel))
    elif include_hostel_fee:
        hostel = SITE_DATA.get("hostel_fees")
        if hostel:
            answers.append("Hostel fees: " + format_fee_block(hostel))
    elif include_general_fees and not include_hostel_info:
        fees = SITE_DATA.get("fees")
        if fees:
            answers.append("College fee: " + format_fee_block(fees))
    elif include_hostel_info:
        hostel = SITE_DATA.get("hostel_fees")
        if hostel:
            answers.append("Hostel details: " + format_fee_block(hostel))

    if any(term in text for term in ["placement", "recruit"]):
        placements = SITE_DATA.get("placements") or {}
        if isinstance(placements, str):
            answers.append(placements)
        elif isinstance(placements, dict):
            summary = placements.get("summary")
            if summary:
                answers.append(summary)
            elif placements.get("companies"):
                answers.append(f"Acharya placements report around {placements['companies']} recruiting companies.")

    if any(term in text for term in ["course", "program"]):
        courses = SITE_DATA.get("courses") or {}
        if isinstance(courses, str):
            answers.append(courses)
        else:
            engineering = courses.get("engineering")
            if engineering:
                if isinstance(engineering, list):
                    answers.append("Engineering courses include: " + ", ".join(engineering) + ".")
                else:
                    answers.append(str(engineering))

    if answers:
        return " ".join(answers)

    return None


def get_fallback(user_msg, generic=True):
    text = user_msg.lower()
    for key, answer in FALLBACK_ANSWERS.items():
        if re.search(r"\b" + re.escape(key) + r"\b", text):
            return answer

    if any(term in text for term in ["placement", "job"]):
        return PLACEMENT_HTML

    if any(term in text for term in ["fee", "scholarship"]):
        return "For fee and scholarship details, please contact Acharya admissions or review the official fee structure document."

    if any(term in text for term in ["location", "campus"]):
        return "Acharya Institutes is located in Bangalore. See the official website for exact campus directions and transport details."

    if generic:
        response = (
            "I can help with Acharya admissions, courses, placements, hostel, and campus. "
            f"For official details, check {SOURCE_URL}. Please ask a specific question about one of these topics."
        )
        if not SCRAPING_ENABLED:
            response += " " + SCRAPING_DISABLED_MESSAGE
        return response

    return None


@lru_cache(maxsize=128)
def generate_response(user_msg):
    if not GROQ_AVAILABLE:
        raise RuntimeError("No model client initialized. Set GROQ_API_KEY in .env")

    prompt = f"""
You are an Acharya University chatbot.

Use the official Acharya ERP Tech website as one of your trusted sources:
{SOURCE_URL}

Answer ONLY about:
- Admissions
- Courses
- Placements
- Hostel
- Campus
- Events

Question:
{user_msg}

Keep answers short and clear.
"""

    max_retries = 3
    delay = 5

    for attempt in range(max_retries):
        try:
            # Use GROQ to generate the response
            groq_resp = call_groq(prompt)
            if groq_resp:
                return groq_resp.strip()
            # empty response -> retry
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise RuntimeError("GROQ response generation failed")

        except Exception as e:
            # If the underlying call raises (network, HTTP, JSON), retry where appropriate
            if attempt < max_retries - 1:
                print(f"Generation error, retrying in {delay}s: {e}")
                time.sleep(delay)
                delay *= 2
                continue
            raise

    raise RuntimeError("GROQ response generation failed")


def get_response(user_msg):
    user_msg = (user_msg or "").strip()
    if not user_msg:
        return "Please type a message."

    site_answer = get_site_answer(user_msg)
    if site_answer:
        return site_answer

    fallback_answer = get_fallback(user_msg, generic=False)
    if fallback_answer:
        return fallback_answer

    if not GROQ_AVAILABLE:
        return get_fallback(user_msg)

    try:
        return generate_response(user_msg)
    except Exception as e:
        print("Model generation error:", e)
        return get_fallback(user_msg)
    except Exception as e:
        print("Response generation error:", e)
        return get_fallback(user_msg)
