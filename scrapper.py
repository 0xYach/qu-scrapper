import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import textwrap

BASE_URL = "https://myschool.ng/classroom/english-language?page={}"

questions = []
page = 1

# --- Scraping loop ---
while True:
    url = BASE_URL.format(page)
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    if r.status_code != 200:
        break

    soup = BeautifulSoup(r.text, "lxml")

    # Adjust this selector if site structure changes
    blocks = soup.find_all("div", class_="media question-item mb-4")

    if not blocks:
        break  # End of pages

    for block in blocks:
        q_text = block.find("div", class_="question-desc")
        if not q_text:
            continue
        question = q_text.get_text(strip=True)

        options = []
        opt_tags = block.find_all("li")
        for opt in opt_tags:
            options.append(opt.get_text(strip=True))

        questions.append({
            "question": question,
            "options": options
        })

    page += 1

# --- PDF generation ---
pdf = canvas.Canvas("english_questions.pdf", pagesize=A4)
width, height = A4
y = height - 40
q_num = 1

def clean(text):
    # Remove unsupported characters
    return text.encode("latin-1", "ignore").decode("latin-1")

for q in questions:

    if y < 120:
        pdf.showPage()
        y = height - 40

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(40, y, f"Question {q_num}")
    y -= 18

    pdf.setFont("Helvetica", 10)
    wrapped_q = textwrap.wrap(clean(q["question"]), 85)
    for line in wrapped_q:
        pdf.drawString(40, y, line)
        y -= 15

    y -= 5
    for opt in q["options"]:
        wrapped_opt = textwrap.wrap(clean(opt), 80)
        for line in wrapped_opt:
            pdf.drawString(60, y, line)
            y -= 15

    y -= 20
    q_num += 1

pdf.save()
print("PDF created: english_questions.pdf")
