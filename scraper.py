import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

BASE_URL = "https://myschool.ng/classroom/english-language?page={}"

questions = []

page = 1

while True:
    url = BASE_URL.format(page)
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    if r.status_code != 200:
        break

    soup = BeautifulSoup(r.text, "lxml")

    blocks = soup.find_all("div", class_="media question-item mb-4")

    if not blocks:
        break

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


pdf = canvas.Canvas("english_questions.pdf", pagesize=A4)

width, height = A4
y = height - 40

q_num = 1

for q in questions:

    pdf.drawString(40, y, f"Question {q_num}")
    y -= 20

    text = pdf.beginText(40, y)
    text.textLines(q["question"])
    pdf.drawText(text)

    y -= 40

    for opt in q["options"]:
        pdf.drawString(60, y, opt)
        y -= 20

    y -= 20

    if y < 100:
        pdf.showPage()
        y = height - 40

    q_num += 1

pdf.save()

print("PDF created: english_questions.pdf")
