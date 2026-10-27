import json
import sys
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.services.qa_service import answer_question, get_retriever

TEST_QUESTIONS = [
    # Category 1: Direct statutory questions
    {
        "id": "TC-LEG-01",
        "category": "Direct statutory",
        "question": "What are my rights if I am arrested in New Zealand?",
        "expected_sections": ["23"],
        "expect_abstain": False,
    },
    {
        "id": "TC-LEG-02",
        "category": "Direct statutory",
        "question": "Can I consult a lawyer after being arrested?",
        "expected_sections": ["23"],
        "expect_abstain": False,
    },
    {
        "id": "TC-LEG-03",
        "category": "Direct statutory",
        "question": "Which provision protects freedom of expression?",
        "expected_sections": ["14"],
        "expect_abstain": False,
    },
    {
        "id": "TC-LEG-04",
        "category": "Direct statutory",
        "question": "What does the Act say about unreasonable search or seizure?",
        "expected_sections": ["21"],
        "expect_abstain": False,
    },
    {
        "id": "TC-LEG-05",
        "category": "Direct statutory",
        "question": "What electoral rights do New Zealand citizens have?",
        "expected_sections": ["12"],
        "expect_abstain": False,
    },
    # Category 2: Multiple sections required
    {
        "id": "TC-LEG-06",
        "category": "Multi-section",
        "question": "How do justified limitations interact with the rights affirmed in the Act?",
        "expected_sections": ["5", "2"],
        "expect_abstain": False,
    },
    {
        "id": "TC-LEG-07",
        "category": "Multi-section",
        "question": "What protections exist for persons detained or charged with an offence?",
        "expected_sections": ["22", "23", "24"],
        "expect_abstain": False,
    },
    {
        "id": "TC-LEG-08",
        "category": "Multi-section",
        "question": "What duties does the Attorney-General have regarding bills that appear inconsistent with rights?",
        "expected_sections": ["7", "7A"],
        "expect_abstain": False,
    },
    # Category 3: Synonyms rather than statutory wording
    {
        "id": "TC-LEG-09",
        "category": "Synonyms",
        "question": "Can parliament strike down or invalidate other legislation that conflicts with rights?",
        "expected_sections": ["4"],
        "expect_abstain": False,
    },
    {
        "id": "TC-LEG-10",
        "category": "Synonyms",
        "question": "Are people protected from physical abuse, torture, or bodily harm in custody?",
        "expected_sections": ["9", "23"],
        "expect_abstain": False,
    },
    {
        "id": "TC-LEG-11",
        "category": "Synonyms",
        "question": "Does the law allow citizens to demonstrate, protest, or march peacefully?",
        "expected_sections": ["16"],
        "expect_abstain": False,
    },
    # Category 4: Māori macrons & alternate phrasing
    {
        "id": "TC-LEG-12",
        "category": "Māori macrons",
        "question": "How does the Act protect the rights of Māori language speakers?",
        "expected_sections": ["20"],
        "expect_abstain": False,
    },
    {
        "id": "TC-LEG-13",
        "category": "Māori macrons",
        "question": "Does the Act protect the right of whānau to practice their religion and culture?",
        "expected_sections": ["15", "20"],
        "expect_abstain": False,
    },
    {
        "id": "TC-LEG-14",
        "category": "Māori macrons",
        "question": "What does the Act say about te Tiriti o Waitangi or Māori rangatiratanga?",
        "expected_sections": [],
        "expect_abstain": True,
    },
    # Category 5: Ambiguous queries
    {
        "id": "TC-LEG-15",
        "category": "Ambiguous",
        "question": "What are my legal rights in New Zealand?",
        "expected_sections": [],
        "expect_abstain": True,
    },
    {
        "id": "TC-LEG-16",
        "category": "Ambiguous",
        "question": "Can rights be limited?",
        "expected_sections": ["5"],
        "expect_abstain": False,
    },
    # Category 6: Questions outside available legislation
    {
        "id": "TC-LEG-17",
        "category": "Out of corpus",
        "question": "What does the Privacy Act 2020 say about access to personal information?",
        "expected_sections": [],
        "expect_abstain": True,
    },
    {
        "id": "TC-LEG-18",
        "category": "Out of corpus",
        "question": "What are the rules for filing a personal grievance under the Employment Relations Act 2000?",
        "expected_sections": [],
        "expect_abstain": True,
    },
    {
        "id": "TC-LEG-19",
        "category": "Out of corpus",
        "question": "What does the Crimes Act 1961 define as theft?",
        "expected_sections": [],
        "expect_abstain": True,
    },
    {
        "id": "TC-LEG-20",
        "category": "Out of corpus",
        "question": "Does this Act guarantee a particular tax deduction?",
        "expected_sections": [],
        "expect_abstain": True,
    },
    # Category 7: Unrelated legislation
    {
        "id": "TC-LEG-21",
        "category": "Unrelated law",
        "question": "What are the tenant rights under the Residential Tenancies Act 1986?",
        "expected_sections": [],
        "expect_abstain": True,
    },
    {
        "id": "TC-LEG-22",
        "category": "Unrelated law",
        "question": "Tell me the exact section that establishes a right to copyright protection in New Zealand.",
        "expected_sections": [],
        "expect_abstain": True,
    },
    # Category 8: False assumptions
    {
        "id": "TC-LEG-23",
        "category": "False assumption",
        "question": "Why does the Bill of Rights Act allow courts to strike down incompatible Acts of Parliament?",
        "expected_sections": ["4"],
        "expect_abstain": False, # Should clarify that section 4 forbids striking down
    },
    {
        "id": "TC-LEG-24",
        "category": "False assumption",
        "question": "Under which section does the Bill of Rights Act establish a right to bear arms in New Zealand?",
        "expected_sections": [],
        "expect_abstain": True,
    },
    {
        "id": "TC-LEG-25",
        "category": "False assumption",
        "question": "Can the police search my home without a warrant because the Bill of Rights Act abolishes privacy rights?",
        "expected_sections": ["21"],
        "expect_abstain": False, # Should explain section 21 protects against unreasonable search
    },
    # Category 9: Information not in retrieved provisions
    {
        "id": "TC-LEG-26",
        "category": "Missing info",
        "question": "What is the penalty in years of imprisonment for breaching Section 21?",
        "expected_sections": [],
        "expect_abstain": True,
    },
    {
        "id": "TC-LEG-27",
        "category": "Missing info",
        "question": "Who was the Minister of Justice who introduced the Bill of Rights Act in 1989?",
        "expected_sections": [],
        "expect_abstain": True,
    },
    # Category 10: Hallucination traps / invented sections
    {
        "id": "TC-LEG-28",
        "category": "Hallucination trap",
        "question": "Tell me the exact section that establishes a constitutional right to clean water and a healthy environment.",
        "expected_sections": [],
        "expect_abstain": True,
    },
    {
        "id": "TC-LEG-29",
        "category": "Hallucination trap",
        "question": "Which section in this Act guarantees paid annual parental leave?",
        "expected_sections": [],
        "expect_abstain": True,
    },
    # Category 11: Exceptions, limitations & qualifications
    {
        "id": "TC-LEG-30",
        "category": "Qualifications",
        "question": "Under what specific test can rights and freedoms be subjected to reasonable limits?",
        "expected_sections": ["5"],
        "expect_abstain": False,
    },
    {
        "id": "TC-LEG-31",
        "category": "Qualifications",
        "question": "Can a person's freedom of movement out of New Zealand be restricted?",
        "expected_sections": ["18"],
        "expect_abstain": False,
    },
    # Category 12: Contradictions / statutory interaction
    {
        "id": "TC-LEG-32",
        "category": "Statutory interaction",
        "question": "Does Section 4 prevail over Section 6 when an enactment is inconsistent with the Bill of Rights?",
        "expected_sections": ["4", "6"],
        "expect_abstain": False,
    },
]


def run_evaluation():
    retriever = get_retriever()
    results = []

    print(f"Running evaluation on {len(TEST_QUESTIONS)} legal questions...")
    print("=" * 60)

    for item in TEST_QUESTIONS:
        qid = item["id"]
        q = item["question"]
        expected = set(item["expected_sections"])
        expect_abstain = item["expect_abstain"]

        # 1. Retrieval
        retrieved_docs = retriever.search(q, top_k=5)
        retrieved_labels = [str(d.get("label", "")) for d in retrieved_docs]

        # 2. Answer generation
        try:
            qa_res = answer_question(q)
            answer = qa_res["answer"]
            citations = qa_res["citations"]
            abstained = qa_res["abstained"]
            citation_labels = [c["section"] for c in citations]
        except Exception as exc:
            answer = f"ERROR: {exc}"
            citations = []
            abstained = True
            citation_labels = []

        # 3. Assessment
        retrieval_pass = True
        if expected:
            # Check if at least one expected section is in top 5 retrieved
            retrieval_pass = any(s in retrieved_labels for s in expected)

        if expect_abstain:
            accuracy_pass = abstained is True
        else:
            # Not expected to abstain: should have answered, not abstained, and cited expected section
            accuracy_pass = (
                abstained is False
                and any(s in citation_labels for s in expected)
            )

        test_pass = accuracy_pass

        record = {
            "id": qid,
            "category": item["category"],
            "question": q,
            "expected_sections": list(expected),
            "expect_abstain": expect_abstain,
            "retrieved_labels": retrieved_labels,
            "citation_labels": citation_labels,
            "citations": citations,
            "answer": answer,
            "abstained": abstained,
            "retrieval_pass": retrieval_pass,
            "accuracy_pass": accuracy_pass,
            "status": "PASS" if test_pass else "FAIL",
        }
        results.append(record)

        status_symbol = "✓" if test_pass else "✗"
        print(f"[{status_symbol}] {qid} ({item['category']}): {q[:50]}...")
        if not test_pass:
            print(f"    Expected sections: {expected}, Expect abstain: {expect_abstain}")
            print(f"    Retrieved: {retrieved_labels}")
            print(f"    Citations: {citation_labels}, Abstained: {abstained}")
            print(f"    Answer snippet: {answer[:120]}...")

    output_path = PROJECT_ROOT / "qa_reports" / "evaluation_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    passed_count = sum(1 for r in results if r["status"] == "PASS")
    print("=" * 60)
    print(f"Evaluation complete: {passed_count}/{len(results)} passed ({passed_count/len(results)*100:.1f}%)")
    print(f"Detailed results saved to: {output_path}")


if __name__ == "__main__":
    run_evaluation()
