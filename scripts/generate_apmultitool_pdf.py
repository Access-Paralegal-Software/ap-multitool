from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    ListFlowable, ListItem, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUTPUT = "APMultitool_Beta1_Overview.pdf"

SLATE   = colors.HexColor("#1E2A3A")
ACCENT  = colors.HexColor("#2D6FE8")
MUTED   = colors.HexColor("#6B7A8D")
RULE    = colors.HexColor("#D0D8E4")
BG_PILL = colors.HexColor("#EBF1FB")

def build_styles():
    base = getSampleStyleSheet()

    styles = {}

    styles["doc_title"] = ParagraphStyle(
        "doc_title",
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=32,
        textColor=SLATE,
        spaceAfter=4,
    )

    styles["beta_pill"] = ParagraphStyle(
        "beta_pill",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=ACCENT,
        spaceAfter=14,
    )

    styles["intro"] = ParagraphStyle(
        "intro",
        fontName="Helvetica",
        fontSize=11,
        leading=17,
        textColor=MUTED,
        spaceAfter=24,
    )

    styles["section_heading"] = ParagraphStyle(
        "section_heading",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=18,
        textColor=SLATE,
        spaceBefore=20,
        spaceAfter=8,
    )

    styles["body"] = ParagraphStyle(
        "body",
        fontName="Helvetica",
        fontSize=10.5,
        leading=16,
        textColor=SLATE,
        spaceAfter=10,
    )

    styles["bullet_item"] = ParagraphStyle(
        "bullet_item",
        fontName="Helvetica",
        fontSize=10.5,
        leading=16,
        textColor=SLATE,
    )

    styles["ordered_item"] = ParagraphStyle(
        "ordered_item",
        fontName="Helvetica",
        fontSize=10.5,
        leading=16,
        textColor=SLATE,
    )

    return styles


def bullet_list(items, s):
    return ListFlowable(
        [ListItem(Paragraph(t, s["bullet_item"]), leftIndent=14, bulletColor=ACCENT, value="bullet") for t in items],
        bulletType="bullet",
        leftIndent=18,
        bulletFontSize=8,
        bulletOffsetY=1,
        spaceAfter=4,
    )


def ordered_list(items, s):
    return ListFlowable(
        [ListItem(Paragraph(t, s["ordered_item"]), leftIndent=14) for t in items],
        bulletType="1",
        leftIndent=18,
        bulletFontSize=10.5,
        bulletFormat="%s.",
        start=1,
        spaceAfter=4,
    )


def build_story(s):
    story = []

    # ── Header block ──────────────────────────────────────────────
    story.append(Paragraph("APMultitool Beta 1 Overview", s["doc_title"]))
    story.append(Paragraph("BETA 1  ·  WINDOWS", s["beta_pill"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=16))

    story.append(Paragraph(
        "APMultitool Beta 1 for Windows is now live and available to a small group of trusted testers.",
        s["intro"],
    ))
    story.append(Paragraph(
        "This is the first shipped tool in a planned suite of paralegal tools built around real-world "
        "workflows, starting with the way Renee and her team actually handle documents, packets, and matters.",
        s["intro"],
    ))

    # ── What we have shipped ──────────────────────────────────────
    story.append(KeepTogether([
        Paragraph("What we have shipped", s["section_heading"]),
        HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=10),
        bullet_list([
            "A Windows-only beta installer (Beta 1).",
            "A download page that clearly labels the build as beta.",
            "Tester-friendly instructions that explain what to try and how to send feedback.",
            "A working feedback loop based on simple email replies and optional support bundles.",
        ], s),
    ]))

    # ── How we are framing the beta ───────────────────────────────
    story.append(KeepTogether([
        Paragraph("How we are framing the beta", s["section_heading"]),
        HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=10),
        bullet_list([
            "It is clearly presented as an <b>early beta</b>, not a finished 1.0.",
            "The site explains that Windows may show a standard “protected your PC” message because this is a new app building reputation.",
            "Testers are told what to click if they intentionally downloaded APMultitool and want to continue, and to cancel if they did not.",
        ], s),
        Spacer(1, 8),
        Paragraph(
            "The goal is to be honest about rough edges while still giving people a real, usable tool.",
            s["body"],
        ),
    ]))

    # ── Who this beta is for ──────────────────────────────────────
    story.append(KeepTogether([
        Paragraph("Who this beta is for", s["section_heading"]),
        HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=10),
        bullet_list([
            "Trusted testers and early adopters inside the existing network.",
            "People willing to try everyday tasks in Compiler, Bates, and File Room.",
            "People comfortable giving simple, honest feedback in plain language.",
        ], s),
    ]))

    # ── How feedback flows ────────────────────────────────────────
    story.append(KeepTogether([
        Paragraph("How feedback flows", s["section_heading"]),
        HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=10),
        Paragraph("For this first phase, feedback is intentionally simple:", s["body"]),
        ordered_list([
            "Use APMultitool on normal work for a short session.",
            "When something feels confusing, broken, or rough, reply by email.",
            "Include what you were trying to do, what you expected, and what actually happened.",
            "Add a screenshot or support bundle if it helps.",
        ], s),
        Spacer(1, 8),
        Paragraph(
            "This keeps the loop lightweight and personal while we are still shaping the product.",
            s["body"],
        ),
    ]))

    # ── Why this matters ──────────────────────────────────────────
    story.append(KeepTogether([
        Paragraph("Why this matters", s["section_heading"]),
        HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=10),
        Paragraph("This beta proves that APMultitool is no longer an idea or prototype:", s["body"]),
        bullet_list([
            "There is a real installer, in real testers’ hands.",
            "There is a clear way for people to try it.",
            "There is a straightforward way for them to talk back to us.",
        ], s),
        Spacer(1, 8),
        Paragraph(
            "From here, every round of feedback feeds into polish, stability, and the rest of the "
            "paralegal tool suite that will follow.",
            s["body"],
        ),
    ]))

    return story


def main():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=letter,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
        title="APMultitool Beta 1 Overview",
        author="APMultitool",
    )

    s = build_styles()
    story = build_story(s)
    doc.build(story)
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
