"""Generate realistic sample legal documents for visual acceptance testing.

Usage:
    python scripts/make_samples.py

Produces:
    samples/source/ca_motion.docx   — California motion for summary judgment
    samples/source/tx_motion.docx   — Texas motion for summary judgment
"""
from __future__ import annotations

from pathlib import Path

import docx


ROOT = Path(__file__).parent.parent
SAMPLES_DIR = ROOT / "samples"
SOURCE_DIR = SAMPLES_DIR / "source"


def make_ca_motion(path: Path) -> None:
    """Realistic California motion for summary judgment — ~3 pages at pleading spacing."""
    doc = docx.Document()

    doc.add_paragraph("SUPERIOR COURT OF THE STATE OF CALIFORNIA")
    doc.add_paragraph("FOR THE COUNTY OF LOS ANGELES")
    doc.add_paragraph("")

    doc.add_paragraph("MERIDIAN PACIFIC HOLDINGS, LLC,")
    doc.add_paragraph("        Plaintiff,")
    doc.add_paragraph("")
    doc.add_paragraph("    v.")
    doc.add_paragraph("")
    doc.add_paragraph("GREYSTONE CONSTRUCTION, INC.; DEREK ASHWORTH,")
    doc.add_paragraph("an individual; and DOES 1 through 20, inclusive,")
    doc.add_paragraph("        Defendants.")
    doc.add_paragraph("")
    doc.add_paragraph("Case No. 24STCV18842")
    doc.add_paragraph("Dept. 47")
    doc.add_paragraph("")
    doc.add_paragraph("NOTICE OF MOTION AND MOTION FOR SUMMARY JUDGMENT;")
    doc.add_paragraph("MEMORANDUM OF POINTS AND AUTHORITIES IN SUPPORT THEREOF")
    doc.add_paragraph("")
    doc.add_paragraph("Date:    October 14, 2026")
    doc.add_paragraph("Time:    8:30 a.m.")
    doc.add_paragraph("Place:   Department 47")
    doc.add_paragraph("         Stanley Mosk Courthouse")
    doc.add_paragraph("         111 N. Hill Street")
    doc.add_paragraph("         Los Angeles, CA 90012")
    doc.add_paragraph("")

    doc.add_paragraph("NOTICE OF MOTION AND MOTION")
    doc.add_paragraph("")
    doc.add_paragraph(
        "TO ALL PARTIES AND THEIR ATTORNEYS OF RECORD:"
    )
    doc.add_paragraph("")
    doc.add_paragraph(
        "PLEASE TAKE NOTICE that on October 14, 2026, at 8:30 a.m., or as soon "
        "thereafter as the matter may be heard, in Department 47 of the Stanley Mosk "
        "Courthouse, 111 N. Hill Street, Los Angeles, California, Plaintiff Meridian "
        "Pacific Holdings, LLC ('Meridian') will move this Court for summary judgment "
        "in its favor and against Defendants Greystone Construction, Inc. "
        "('Greystone'), Derek Ashworth ('Ashworth'), and Does 1 through 20 "
        "(collectively, 'Defendants')."
    )
    doc.add_paragraph("")
    doc.add_paragraph(
        "This motion is made pursuant to Code of Civil Procedure section 437c on the "
        "grounds that there is no triable issue as to any material fact and that "
        "Meridian is entitled to judgment as a matter of law on each and every cause "
        "of action asserted in the operative First Amended Complaint."
    )
    doc.add_paragraph("")
    doc.add_paragraph(
        "This motion is based on this Notice of Motion and Motion, the Memorandum of "
        "Points and Authorities set forth below, the Separate Statement of Undisputed "
        "Material Facts filed concurrently herewith, the Declarations of Robert M. "
        "Halvorsen and Karen D. Whitfield filed concurrently herewith, the Request for "
        "Judicial Notice filed concurrently herewith, the complete files and records "
        "in this action, and on such oral and documentary evidence as may be presented "
        "at the hearing of this matter."
    )

    doc.add_paragraph("")
    doc.add_paragraph("MEMORANDUM OF POINTS AND AUTHORITIES")
    doc.add_paragraph("")

    doc.add_paragraph("I.  INTRODUCTION")
    doc.add_paragraph("")
    doc.add_paragraph(
        "This action arises from Defendants' breach of a commercial construction "
        "contract and related fraudulent concealment of known structural defects in a "
        "mixed-use development project in the City of Santa Monica. The undisputed "
        "evidence establishes that Greystone Construction was retained to construct "
        "a 24,000-square-foot commercial building at 1450 Lincoln Boulevard, that "
        "Greystone and its principal Derek Ashworth knowingly substituted inferior "
        "subgrade materials in violation of the project specifications, and that this "
        "substitution caused the soil settlement and foundation cracking documented in "
        "the engineering report of Meridian's retained expert, Dr. Sandra Kwan, P.E."
    )
    doc.add_paragraph("")
    doc.add_paragraph(
        "Defendants have not disputed the central facts. Instead, they advance a "
        "limitations defense and argue that Meridian lacks standing because it "
        "acquired the property after the construction was substantially complete. "
        "Both arguments fail as a matter of law. The limitations period was tolled "
        "by Defendants' fraudulent concealment through the date Meridian first "
        "discovered the defects, and the assignment of claims was validly executed "
        "as part of the purchase agreement."
    )

    doc.add_paragraph("")
    doc.add_paragraph("II.  STATEMENT OF UNDISPUTED MATERIAL FACTS")
    doc.add_paragraph("")

    facts = [
        (
            "On March 15, 2021, Defendants entered into a written Construction "
            "Agreement with Pacific Rim Development Group, Inc. ('PRDG') to construct "
            "a four-story mixed-use building at 1450 Lincoln Boulevard, Santa Monica, "
            "California. (Halvorsen Decl. ¶ 3; Ex. 1 [Construction Agreement].)"
        ),
        (
            "The Construction Agreement incorporated by reference the Project "
            "Specifications prepared by structural engineer Marvin Okafor, P.E. of "
            "Okafor & Dunning Structural Consultants. The Specifications required "
            "compacted Class II aggregate base material, minimum R-value 78, for all "
            "subgrade work beneath the foundation slab. (Halvorsen Decl. ¶ 4; Ex. 2 "
            "[Project Specifications, Section 02721].)"
        ),
        (
            "During construction in the summer of 2021, Ashworth directed subcontractor "
            "Southwest Grading, LLC to substitute recycled Class III material, R-value "
            "42, without disclosing the substitution to PRDG, the project architect, or "
            "the City building inspector. (Ashworth Depo. 87:14-25, 91:3-16; Whitfield "
            "Decl. ¶ 6.)"
        ),
        (
            "Greystone submitted completion certificates to PRDG and the City of Santa "
            "Monica representing that all work was performed in conformance with the "
            "Project Specifications. Greystone received final payment of $2,187,000 on "
            "December 8, 2021. (Halvorsen Decl. ¶ 9; Ex. 5 [Completion Certificate]; "
            "Ex. 6 [Final Payment Record].)"
        ),
        (
            "On February 28, 2022, Meridian Pacific Holdings, LLC purchased the "
            "property from PRDG for $18,500,000. The purchase agreement included an "
            "express assignment of all construction-related warranty and tort claims "
            "from PRDG to Meridian. (Halvorsen Decl. ¶ 11; Ex. 7 [Purchase Agreement, "
            "Section 14.3].)"
        ),
        (
            "In November 2023, Meridian's tenant reported visible cracking in the "
            "ground-floor slab and settlement of the main entrance threshold. Meridian "
            "retained Dr. Sandra Kwan, P.E. of Pacific Geotechnical, Inc. to conduct "
            "a forensic investigation. Dr. Kwan's report, dated January 14, 2024, "
            "concluded that the subgrade materials were inconsistent with the Project "
            "Specifications and were the proximate cause of the observed settlement and "
            "cracking. (Kwan Expert Report, Jan. 14, 2024, pp. 18-22.)"
        ),
        (
            "Dr. Kwan calculated remediation costs of $892,500 to remove and replace "
            "the deficient subgrade and repair the affected slab areas. Meridian also "
            "sustained lost rental income of $124,300 attributable to the partial "
            "closure of the ground-floor retail space during the investigation period. "
            "(Kwan Expert Report, pp. 26-28; Halvorsen Decl. ¶ 16.)"
        ),
    ]

    for i, fact in enumerate(facts, 1):
        doc.add_paragraph(f"    {i}.  {fact}")
        doc.add_paragraph("")

    doc.add_paragraph("III.  ARGUMENT")
    doc.add_paragraph("")

    doc.add_paragraph("A.  Summary Judgment Standard")
    doc.add_paragraph("")
    doc.add_paragraph(
        "Summary judgment is proper where 'all the papers submitted show that there "
        "is no triable issue as to any material fact and that the moving party is "
        "entitled to a judgment as a matter of law.' (Code Civ. Proc., § 437c, "
        "subd. (c).) The moving party bears the initial burden of showing that one or "
        "more elements of the cause of action cannot be established or that there is "
        "a complete defense. (Aguilar v. Atlantic Richfield Co. (2001) 25 Cal.4th "
        "826, 850.) Once met, the burden shifts to the opposing party to show a "
        "triable issue of material fact. (Id. at p. 850-851.)"
    )

    doc.add_paragraph("")
    doc.add_paragraph("B.  Meridian Has Standing to Assert These Claims")
    doc.add_paragraph("")
    doc.add_paragraph(
        "California law is clear that construction defect claims may be assigned as "
        "part of a real property sale. (See, e.g., County of Santa Clara v. Atlantic "
        "Richfield Co. (2006) 137 Cal.App.4th 292, 318; Coppola v. Smith (2015) "
        "935 F.Supp.2d 1129, 1148 [applying Cal. law].)"
    )
    doc.add_paragraph("")
    doc.add_paragraph(
        "The Purchase Agreement between PRDG and Meridian expressly assigned 'all "
        "construction and design defect claims of every nature arising out of or "
        "related to the Property.' (Ex. 7, Section 14.3.) This language is broad "
        "enough to encompass both the breach of contract claim and the fraudulent "
        "concealment claim asserted here. Defendants cannot dispute the validity of "
        "the assignment — they have offered no evidence and cite no authority that "
        "would invalidate it."
    )

    doc.add_paragraph("")
    doc.add_paragraph("C.  The Statute of Limitations Was Tolled by Fraudulent Concealment")
    doc.add_paragraph("")
    doc.add_paragraph(
        "Defendants argue that the three-year limitations period for fraud "
        "(Code Civ. Proc., § 338, subd. (d)) and the four-year period for breach "
        "of written contract (id., § 337) began to run at project completion in "
        "December 2021. This argument ignores the well-established rule that "
        "fraudulent concealment tolls the limitations period until the plaintiff "
        "discovers, or through reasonable diligence should have discovered, the "
        "cause of action. (Bernson v. Browning-Ferris Industries (1994) 7 Cal.4th "
        "926, 931-932.)"
    )
    doc.add_paragraph("")
    doc.add_paragraph(
        "Here, Defendants actively concealed the subgrade substitution by submitting "
        "false completion certificates. Meridian had no reason to suspect defects "
        "until November 2023, when visible cracking first appeared. This action was "
        "filed on June 3, 2024, within months of the January 2024 expert report "
        "confirming the cause. Both limitations periods are satisfied."
    )

    doc.add_paragraph("")
    doc.add_paragraph("IV.  CONCLUSION")
    doc.add_paragraph("")
    doc.add_paragraph(
        "The undisputed evidence establishes that Defendants breached the Construction "
        "Agreement and concealed the breach, causing Meridian damages of at least "
        "$1,016,800. Defendants' affirmative defenses fail as a matter of law. "
        "Meridian respectfully requests that the Court grant summary judgment in "
        "Meridian's favor on each cause of action and schedule a hearing on damages "
        "in accordance with Code of Civil Procedure section 437c, subdivision (f)(1)."
    )
    doc.add_paragraph("")
    doc.add_paragraph("Dated: June 12, 2026")
    doc.add_paragraph("")
    doc.add_paragraph("Respectfully submitted,")
    doc.add_paragraph("")
    doc.add_paragraph("")
    doc.add_paragraph("_________________________________")
    doc.add_paragraph("ELENA R. VASQUEZ")
    doc.add_paragraph("Attorney for Plaintiff")
    doc.add_paragraph("MERIDIAN PACIFIC HOLDINGS, LLC")

    doc.save(str(path))


def make_tx_motion(path: Path) -> None:
    """Realistic Texas motion for summary judgment — Harris County District Court."""
    doc = docx.Document()

    doc.add_paragraph("IN THE DISTRICT COURT OF HARRIS COUNTY, TEXAS")
    doc.add_paragraph("133RD JUDICIAL DISTRICT")
    doc.add_paragraph("")
    doc.add_paragraph("LONE STAR ENERGY PARTNERS, LP,")
    doc.add_paragraph("        Plaintiff,")
    doc.add_paragraph("")
    doc.add_paragraph("v.")
    doc.add_paragraph("")
    doc.add_paragraph("PINNACLE OILFIELD SERVICES, INC. and")
    doc.add_paragraph("THOMAS B. CALLOWAY, Individually,")
    doc.add_paragraph("        Defendants.")
    doc.add_paragraph("")
    doc.add_paragraph("CAUSE NO. 2025-78432")
    doc.add_paragraph("")
    doc.add_paragraph("PLAINTIFF'S TRADITIONAL MOTION FOR SUMMARY JUDGMENT")
    doc.add_paragraph("")
    doc.add_paragraph("TO THE HONORABLE JUDGE OF SAID COURT:")
    doc.add_paragraph("")
    doc.add_paragraph(
        "Plaintiff Lone Star Energy Partners, LP ('Lone Star') files this Traditional "
        "Motion for Summary Judgment against Defendants Pinnacle Oilfield Services, "
        "Inc. ('Pinnacle') and Thomas B. Calloway ('Calloway') pursuant to Rule 166a "
        "of the Texas Rules of Civil Procedure, and in support thereof respectfully "
        "shows the Court as follows:"
    )

    doc.add_paragraph("")
    doc.add_paragraph("I.  BACKGROUND")
    doc.add_paragraph("")
    doc.add_paragraph(
        "This dispute arises from Defendants' breach of a Master Services Agreement "
        "('MSA') under which Pinnacle agreed to provide directional drilling and "
        "completion services for Lone Star's Permian Basin well program. Pinnacle "
        "completed work on five wells between January and September 2024, then "
        "submitted invoices totaling $4,872,000. Lone Star paid $2,000,000, "
        "withholding the balance pending resolution of Pinnacle's failure to meet "
        "agreed minimum production targets for three of the five wells."
    )
    doc.add_paragraph("")
    doc.add_paragraph(
        "Pinnacle now sues for the unpaid balance plus consequential damages. Lone "
        "Star counterclaims for breach of contract and seeks offset for costs "
        "incurred remedying the underperforming completions. Calloway, as Pinnacle's "
        "chief executive and personal guarantor under the MSA, is jointly and "
        "severally liable for amounts owed to Lone Star."
    )

    doc.add_paragraph("")
    doc.add_paragraph("II.  GROUNDS FOR MOTION")
    doc.add_paragraph("")
    doc.add_paragraph(
        "Summary judgment is appropriate on Lone Star's counterclaim and as a defense "
        "to Pinnacle's claim for the following reasons:"
    )
    doc.add_paragraph("")
    doc.add_paragraph(
        "    1.  The MSA expressly conditions final payment on achievement of the "
        "Minimum Performance Standards set forth in Exhibit B, which Pinnacle "
        "admittedly failed to meet on Wells 2, 3, and 5."
    )
    doc.add_paragraph("")
    doc.add_paragraph(
        "    2.  Pinnacle's own completion reports, produced in discovery, confirm "
        "that 30-day IP rates for Wells 2, 3, and 5 fell 38%, 41%, and 29% below "
        "the contractual minimums, respectively."
    )
    doc.add_paragraph("")
    doc.add_paragraph(
        "    3.  Calloway executed a personal guaranty on March 1, 2024 that "
        "expressly covers Lone Star's counterclaim damages and all attorneys' fees "
        "incurred in connection with enforcement."
    )

    doc.add_paragraph("")
    doc.add_paragraph("III.  ARGUMENT AND AUTHORITIES")
    doc.add_paragraph("")
    doc.add_paragraph("A.  Standard for Traditional Summary Judgment")
    doc.add_paragraph("")
    doc.add_paragraph(
        "A party is entitled to summary judgment if the summary judgment evidence "
        "shows that there is no genuine issue of material fact and the moving party "
        "is entitled to judgment as a matter of law. Tex. R. Civ. P. 166a(c); "
        "Nixon v. Mr. Property Management Co., 690 S.W.2d 546, 548 (Tex. 1985). "
        "Once the movant establishes its right to summary judgment, the burden shifts "
        "to the non-movant to raise a genuine issue of material fact. City of Houston "
        "v. Clear Creek Basin Auth., 589 S.W.2d 671, 678 (Tex. 1979)."
    )

    doc.add_paragraph("")
    doc.add_paragraph("B.  Lone Star Is Entitled to Judgment on Its Breach of Contract Counterclaim")
    doc.add_paragraph("")
    doc.add_paragraph(
        "The elements of a breach of contract claim under Texas law are: (1) a valid "
        "contract; (2) performance or tendered performance by the plaintiff; (3) "
        "breach by the defendant; and (4) damages resulting from the breach. "
        "USAA Texas Lloyds Co. v. Menchaca, 545 S.W.3d 479, 501 n.21 (Tex. 2018). "
        "All four elements are conclusively established here."
    )
    doc.add_paragraph("")
    doc.add_paragraph(
        "First, the MSA is a valid, integrated written agreement signed by authorized "
        "representatives of both Lone Star and Pinnacle. (App. Tab 1.) Second, Lone "
        "Star paid $2,000,000 and tendered full performance of its obligations. "
        "Third, as Pinnacle's own production reports confirm, Pinnacle failed to "
        "achieve the contractually required IP rates on three of five wells. Fourth, "
        "Lone Star's expert witness, Dr. Pamela Obi, has calculated remediation and "
        "lost production costs at $1,247,600 with reasonable certainty. (App. Tab 8, "
        "Obi Expert Report, pp. 14-19.)"
    )

    doc.add_paragraph("")
    doc.add_paragraph("C.  Calloway Is Liable Under His Personal Guaranty")
    doc.add_paragraph("")
    doc.add_paragraph(
        "Texas law enforces personal guarantees according to their terms. Lone Star "
        "Nat'l Bank, N.A. v. Heartland Payment Sys., Inc., 729 F.3d 421, 425 (5th "
        "Cir. 2013). Calloway's guaranty is unambiguous and extends to 'all amounts, "
        "including costs, expenses, and attorneys' fees, arising from or related to "
        "any claim or counterclaim under the MSA.' (App. Tab 2, Guaranty § 2.1.) "
        "Calloway cannot avoid liability by asserting that the underlying claim is "
        "disputed — the guaranty is expressly unconditional."
    )

    doc.add_paragraph("")
    doc.add_paragraph("IV.  PRAYER FOR RELIEF")
    doc.add_paragraph("")
    doc.add_paragraph(
        "For these reasons, Plaintiff Lone Star Energy Partners, LP respectfully "
        "prays that the Court:"
    )
    doc.add_paragraph("")
    doc.add_paragraph(
        "    (a)  Grant Lone Star's Traditional Motion for Summary Judgment on its "
        "breach of contract counterclaim;"
    )
    doc.add_paragraph(
        "    (b)  Enter judgment in favor of Lone Star against Pinnacle and Calloway, "
        "jointly and severally, in the amount of $1,247,600, plus pre-judgment "
        "interest at the rate of 8% per annum from the date of breach;"
    )
    doc.add_paragraph(
        "    (c)  Award Lone Star its reasonable and necessary attorneys' fees "
        "pursuant to Chapter 38 of the Texas Civil Practice and Remedies Code and "
        "under the terms of the MSA and Personal Guaranty; and"
    )
    doc.add_paragraph(
        "    (d)  Grant such other and further relief to which Lone Star may show "
        "itself entitled."
    )
    doc.add_paragraph("")
    doc.add_paragraph("Respectfully submitted,")
    doc.add_paragraph("")
    doc.add_paragraph("")
    doc.add_paragraph("_________________________________")
    doc.add_paragraph("JAMES R. THORNTON")
    doc.add_paragraph("State Bar No. 19987400")
    doc.add_paragraph("THORNTON & HAYES LLP")
    doc.add_paragraph("1600 Smith Street, Suite 4800")
    doc.add_paragraph("Houston, Texas 77002")
    doc.add_paragraph("Tel: (713) 555-0200")
    doc.add_paragraph("Fax: (713) 555-0201")
    doc.add_paragraph("jthornton@thorntonhayes.com")
    doc.add_paragraph("")
    doc.add_paragraph("ATTORNEYS FOR PLAINTIFF")
    doc.add_paragraph("LONE STAR ENERGY PARTNERS, LP")

    doc.save(str(path))


if __name__ == "__main__":
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    ca_path = SOURCE_DIR / "ca_motion.docx"
    tx_path = SOURCE_DIR / "tx_motion.docx"

    make_ca_motion(ca_path)
    print(f"Created: {ca_path}")

    make_tx_motion(tx_path)
    print(f"Created: {tx_path}")

    print("\nNext step: run doc-chameleon convert on each sample.")
    print("  python -m doc_chameleon.cli convert \\")
    print("    --input samples/source/ca_motion.docx \\")
    print("    --jurisdiction ca \\")
    print("    --output samples/output/ca_motion_ca.docx \\")
    print("    --attorney-name \"Elena R. Vasquez\" \\")
    print("    --attorney-sbn \"287451\" \\")
    print("    --firm \"Vasquez & Kimura LLP\" \\")
    print("    --address \"350 S. Grand Avenue, Suite 3400\" \\")
    print("    --city-state-zip \"Los Angeles, CA 90071\" \\")
    print("    --phone \"(213) 555-0188\" \\")
    print("    --email \"evasquez@vklawfirm.com\" \\")
    print("    --client \"Plaintiff, Meridian Pacific Holdings, LLC\"")
