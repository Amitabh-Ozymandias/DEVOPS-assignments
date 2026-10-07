"""Render captured command logs (screenshots/logs) as Ubuntu-terminal style PNGs
and generate submission.md. Run after capture.sh."""
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "screenshots" / "logs"
OUT = ROOT / "screenshots"

USER_HOST = "amitabh@LAPTOP-3KF17VR3"
CWD = "/mnt/c/Users/USER/Downloads/terraform-s3-demo"

FONT = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
BOLD = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 15)
CW = int(FONT.getlength("M"))
LH = 19
COLS = 120
PAD = 14
BAR = 30

BG = (48, 10, 36)
FG = (238, 238, 236)
PALETTE = {
    30: (46, 52, 54), 31: (204, 0, 0), 32: (78, 154, 6), 33: (196, 160, 0),
    34: (52, 101, 164), 35: (117, 80, 123), 36: (6, 152, 154), 37: (211, 215, 207),
    90: (85, 87, 83), 91: (239, 41, 41), 92: (138, 226, 52), 93: (252, 233, 79),
    94: (114, 159, 207), 95: (173, 127, 168), 96: (52, 226, 226), 97: (238, 238, 236),
}
PROMPT_GREEN = (138, 226, 52)
PROMPT_BLUE = (114, 159, 207)

ANSI = re.compile(r"\x1b\[([0-9;]*)m")

STEPS = {
    "00-prereq": ("Prerequisites", "Confirm Terraform is installed and the AWS CLI is authenticated."),
    "01-init": ("terraform init", "Initializes the working directory and downloads the AWS provider."),
    "02-fmt": ("terraform fmt", "Formats all `.tf` files to the canonical style (no output = already formatted)."),
    "03-validate": ("terraform validate", "Checks the configuration for syntax and internal consistency."),
    "04-plan": ("terraform plan", "Previews the resources Terraform will create."),
    "05-apply": ("terraform apply", "Creates the S3 bucket, versioning and public access block after confirming with `yes`."),
    "06-show": ("terraform show", "Displays the current state of the managed resources."),
    "07-output": ("terraform output", "Prints the output values defined in `outputs.tf`."),
    "08-verify": ("Verify with AWS CLI", "Confirms the bucket exists in AWS with versioning enabled."),
    "09-destroy": ("terraform destroy", "Deletes all resources managed by this configuration after confirming with `yes`."),
}


def parse(line):
    """Split a line with ANSI codes into (text, colour, bold) segments."""
    segs, pos, fg, bold = [], 0, FG, False
    for m in ANSI.finditer(line):
        if m.start() > pos:
            segs.append((line[pos:m.start()], fg, bold))
        for code in (int(c) for c in (m.group(1) or "0").split(";") if c):
            if code == 0:
                fg, bold = FG, False
            elif code == 1:
                bold = True
            elif code == 22:
                bold = False
            elif code == 39:
                fg = FG
            elif code in PALETTE:
                fg = PALETTE[code]
        pos = m.end()
    if pos < len(line):
        segs.append((line[pos:], fg, bold))
    return segs


def wrap(segs):
    """Wrap segment list to COLS characters."""
    lines, cur, n = [], [], 0
    for text, fg, bold in segs:
        while text:
            room = COLS - n
            part, text = text[:room], text[room:]
            cur.append((part, fg, bold))
            n += len(part)
            if n >= COLS:
                lines.append(cur)
                cur, n = [], 0
    lines.append(cur)
    return lines


def prompt(cmd=""):
    segs = [(USER_HOST, PROMPT_GREEN, True), (":", FG, False), (CWD, PROMPT_BLUE, True), ("$ ", FG, False)]
    if cmd:
        segs.append((cmd, FG, False))
    return segs


def render(name):
    cmd = (LOGS / f"{name}.cmd").read_text().strip()[2:]
    raw = (LOGS / f"{name}.log").read_text(encoding="utf-8", errors="replace")
    answer = (LOGS / f"{name}.answer").read_text().strip()
    raw = raw.replace("\r", "").expandtabs(4)
    if answer:  # the typed confirmation is not echoed when stdin is piped
        raw = re.sub(r"(Enter a value:(?:\x1b\[[0-9;]*m)* (?:\x1b\[[0-9;]*m)*)", rf"\g<1>{answer}", raw)
    body = raw.rstrip("\n").split("\n") if raw.strip() else []

    rows = wrap(prompt(cmd))
    for line in body:
        rows += wrap(parse(line))
    rows += [prompt()]

    width = PAD * 2 + CW * COLS
    height = BAR + PAD * 2 + LH * len(rows)
    img = Image.new("RGB", (width, height), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, width, BAR], fill=(44, 44, 44))
    for i, c in enumerate([(237, 94, 82), (245, 190, 79), (98, 197, 84)]):
        d.ellipse([12 + i * 22, 9, 26 + i * 22, 23], fill=c)
    title = f"{USER_HOST}: {CWD}"
    d.text(((width - FONT.getlength(title)) / 2, 7), title, font=FONT, fill=(200, 200, 200))
    y = BAR + PAD
    for row in rows:
        x = PAD
        for text, fg, bold in row:
            d.text((x, y), text, font=BOLD if bold else FONT, fill=fg)
            x += CW * len(text)
        y += LH
    path = OUT / f"{name}.png"
    img.save(path)
    return cmd, raw


def main():
    md = [
        "# Session 18 — Submission",
        "",
        "## Task 1: Terraform S3 Demo",
        "",
        f"All commands were run in WSL Ubuntu from `{CWD}`.",
        "",
        "Project files: [main.tf](main.tf) · [variables.tf](variables.tf) · [outputs.tf](outputs.tf) · "
        "[provider.tf](provider.tf) · [terraform.tfvars](terraform.tfvars) · [README.md](README.md)",
        "",
    ]
    for i, name in enumerate(sorted(p.stem for p in LOGS.glob("*.cmd"))):
        title, desc = STEPS.get(name, (name, ""))
        cmd, raw = render(name)
        md += [
            f"### {i}. {title}",
            "",
            desc,
            "",
            f"![{title}](screenshots/{name}.png)",
            "",
        ]
    md += [
        "## Task 2: AWS Services Research",
        "",
        "| # | Service | Notes |",
        "|---|---|---|",
        "| 01 | IAM — Governance | [aws-services/01-iam/README.md](aws-services/01-iam/README.md) |",
        "| 02 | EC2 — Compute | [aws-services/02-ec2/README.md](aws-services/02-ec2/README.md) |",
        "| 03 | S3 — Storage | [aws-services/03-s3/README.md](aws-services/03-s3/README.md) |",
        "| 04 | VPC — Networking | [aws-services/04-vpc/README.md](aws-services/04-vpc/README.md) |",
        "| 05 | DynamoDB & RDS — Databases | [aws-services/05-dynamodb-rds/README.md](aws-services/05-dynamodb-rds/README.md) |",
        "",
    ]
    (ROOT / "submission.md").write_text("\n".join(md), encoding="utf-8")
    print("wrote submission.md")


if __name__ == "__main__":
    main()
