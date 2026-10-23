"""
Build the synthetic enterprise meeting series SYN001 and its ground truth.

WHY THIS EXISTS
---------------
No public corpus annotates how decisions relate ACROSS meetings, and the
AMI held-out series contain almost no SAME or CONTRADICTORY relations.
SYN001 is a small hand-authored benchmark that:

  * covers all four relation types (REVISED, REFINES, SAME, CONTRADICTORY)
  * moves out of AMI's design-a-remote-control domain into an enterprise
    software project (the system's intended use)
  * contains HARD NEGATIVES - decisions that share wording but not subject
    (a driver survey "at Pune in February" vs the Pune pilot going live in
    February; a customer web portal vs the mechanics' mobile app)
  * contains PROPOSALS THAT WERE NOT AGREED, which a correct extractor must
    not report as decisions

PROVENANCE / CIRCULARITY
------------------------
The transcripts and ground truth were written for this project with an
LLM writing assistant - NOT with Gemini, the model under evaluation - and
the ground truth below was fixed BEFORE the system was run on the data.
It is still LLM-authored text:
dialogue is cleaner and decisions more explicit than in real meetings, so
extraction on SYN001 will be easier than on AMI. Use SYN001 for relation-type
coverage, not as a headline extraction number. The team should review the
transcripts for realism before publication.

CONTRADICTORY is defined operationally: the later decision conflicts with an
earlier one and NOBODY in the meeting acknowledges the change (in SYN001c the
chair who made the earlier call is absent; in SYN001d the earlier email-only
decision is never mentioned).

Usage:
    python data/synthetic/build_synthetic.py
Writes SYN001a-d.json (QMSum format, loadable by app.pipeline.load_qmsum)
and SYN001_gold.json next to this script.
"""

import json
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent

SERIES = "SYN001"

P, A, M, T, S = "Priya", "Arjun", "Meera", "Tom", "Sara"


# ============================================================
# TRANSCRIPTS
# ============================================================

MEETINGS = {}

MEETINGS["a"] = {
    "summary": (
        "Kickoff of FleetCare, a maintenance scheduling platform for the "
        "company's truck depots. Operations described missed services and "
        "41 unplanned breakdowns last quarter. The team agreed to host on "
        "AWS (already vendor-assessed), to use PostgreSQL as the primary "
        "database for the scheduling service, to pilot at the Pune depot "
        "with go-live on 15 January, and to build the mechanics' app for "
        "Android only in the first release since all company phones are "
        "Android. Tom's idea of SMS alerts was parked pending input from "
        "depot leads."
    ),
    "turns": [
        (P, "Okay, I think everyone's here. Let's get started, thanks for making time. So this is the kickoff for FleetCare, the maintenance scheduling platform."),
        (T, "Morning."),
        (P, "Quick round of intros for Sara since she's new to the group?"),
        (S, "Yeah, hi, I'm Sara, I handle security and compliance. Mostly the audits and vendor reviews."),
        (A, "Arjun, engineering lead. I'll own the build."),
        (M, "Meera, data and analytics. I'll be doing the reporting side and, later, the breakdown predictions."),
        (T, "And Tom, operations. Basically I'm the one whose mechanics are going to use this thing every day, so, no pressure."),
        (P, "Right. So the problem. Tom, do you want to describe it?"),
        (T, "Sure. Right now maintenance is scheduled on a shared spreadsheet per depot. Trucks miss services, parts aren't ordered on time, and when a truck breaks down on the highway we lose two, three days. Last quarter we had forty-one unplanned breakdowns across the four depots."),
        (M, "And about a third of those were trucks that were already overdue for service according to the spreadsheet. So the data was there, nobody acted on it."),
        (P, "Okay. So today I want to settle the foundational things so Arjun's team can start. Hosting, database, the pilot plan, and what the mechanics' app looks like. Let's start with hosting."),
        (A, "So two options really. We run it in our own server room at head office, or we go to the cloud. My strong preference is cloud. The server room is already at capacity and we don't have anyone on call at weekends."),
        (S, "From my side cloud is fine as long as it's a provider we've already done a vendor assessment on. We did AWS last year for the billing system. Azure we haven't reviewed."),
        (T, "Does cloud mean it goes down when the depot internet goes down?"),
        (A, "The server side won't, but the depot would lose access, yes. We'll come back to that with the app design."),
        (P, "Cost-wise?"),
        (A, "For the pilot it's small. I estimated around eight hundred dollars a month."),
        (P, "Okay. Any objections to AWS?"),
        (M, "None from me. The billing data is already there, so joining to it later is easier."),
        (P, "Then let's lock it: FleetCare will be hosted on AWS. Sara, you don't need a new vendor review."),
        (S, "Correct, the existing assessment covers it."),
        (P, "Good. Database."),
        (A, "For the scheduling service I want PostgreSQL. Work orders, trucks, parts, schedules, it's all very relational. And the team knows it well."),
        (M, "Works for me. I'd want read access for reporting, maybe a replica later."),
        (T, "I don't have an opinion on databases, I'll be honest."),
        (P, "Ha, fair. Arjun, is anybody arguing for something else?"),
        (A, "Someone on my team floated MongoDB, but I don't see the reason for it here."),
        (P, "Okay, so PostgreSQL is the primary database for the scheduling service. Agreed?"),
        (A, "Agreed."),
        (M, "Yes."),
        (P, "Next, the pilot. Tom, which depot?"),
        (T, "Pune. It's our biggest depot, sixty-two trucks, and the depot manager there actually wants this. Nagpur would fight us."),
        (A, "Pune also has the best network connection of the four, which helps."),
        (P, "Timeline? I'd like something running before the financial year planning."),
        (A, "If we start next week, a usable pilot by mid January is realistic. Not polished, but usable."),
        (T, "Mid January is good for us. December is peak season and I don't want to change anything in December."),
        (P, "So the pilot goes live at the Pune depot on the fifteenth of January. Let's write that down as the target."),
        (A, "Yes. Fifteenth of Jan, Pune."),
        (M, "Will we have historical data loaded by then? I'd want at least a year of service history in it."),
        (A, "We can import the spreadsheets, yes. Cleaning them is another matter."),
        (M, "I'll help with that."),
        (P, "Okay, the mechanics' app."),
        (T, "The mechanics will use it on phones in the workshop. They need to see today's jobs, mark them done, log the parts used. Big buttons. Some of them wear gloves."),
        (A, "Question is Android, iOS, or both. Both roughly doubles the testing."),
        (T, "Every mechanic phone we issue is Android. The company bought Samsung handsets for all depots two years ago."),
        (A, "Then I'd say Android only for the first release. We can revisit iOS if it ever matters."),
        (S, "Company-issued devices also make device management easier for me, we already have MDM on those."),
        (P, "Android-only for release one, then. Everyone okay?"),
        (T, "Yep."),
        (M, "Fine."),
        (T, "One more idea. Maybe we send SMS alerts to the mechanics when a job is assigned? Some of them don't check apps."),
        (A, "SMS costs money per message and we'd need a gateway. Not sure."),
        (S, "And phone numbers are personal data, I'd want to look at that."),
        (P, "Let's park SMS. It's a good idea but we haven't got enough to decide. Tom, can you find out how many mechanics would actually want it?"),
        (T, "I can ask the depot leads."),
        (P, "Okay. Actions. Arjun, set up the AWS account and the repo this week. Meera, start pulling the spreadsheets together. Tom, the SMS question. Sara, can you send Arjun the AWS assessment document?"),
        (S, "Will do, today."),
        (A, "Sounds good."),
        (P, "Great. Same time in two weeks. Thanks all."),
    ],
}

MEETINGS["b"] = {
    "summary": (
        "Status meeting. AWS and the repository are set up, but the "
        "telematics vendor's new API (needed for odometer readings) slips to "
        "the second week of January, so the team agreed to move the Pune "
        "go-live from 15 January to 1 February rather than launch with "
        "manual readings. Because the back workshop bays at Pune have no "
        "signal, the team agreed the mechanics' Android app will work "
        "offline and sync later, with device-side timestamps and encrypted "
        "local storage. Operations will run an HR driver satisfaction "
        "survey at Pune in February, separate from FleetCare. Notifications "
        "for version one will be email only. Meera's idea of a reporting "
        "read replica was deferred until query load is known."
    ),
    "turns": [
        (P, "Morning everyone. Let's go straight into status. Arjun?"),
        (A, "Mixed news. The good part: the cloud account is set up, the repo's there, and we've got the work order screens working against a test database."),
        (P, "And the bad part?"),
        (A, "The telematics vendor. We need their API to get odometer readings from the trucks, that's what drives the service intervals. They told us on Monday their new API version won't be available until the second week of January."),
        (T, "So without it the system doesn't know when trucks are due?"),
        (A, "It can, if someone types the odometer readings in manually, but that's exactly the spreadsheet problem again."),
        (M, "And my due-date logic depends on that feed. Without it the overdue list is guesswork."),
        (P, "How much would that push us?"),
        (A, "Realistically two weeks after they deliver, to integrate and test. So end of January."),
        (T, "I'd rather go live late than go live with manual readings. The mechanics will lose trust on day one."),
        (P, "Okay. I don't love it, but I agree. So we're moving the Pune go-live from the fifteenth of January to the first of February. Everyone agree?"),
        (A, "Yes, first of Feb is realistic."),
        (T, "Agreed."),
        (M, "Agreed."),
        (P, "I'll tell the leadership group. Sara, anything that changes for you?"),
        (S, "No, just the timing of the security review, I'll move it."),
        (P, "Next item. Tom, the workshop connectivity issue you raised."),
        (T, "Yeah. I walked around Pune with a phone. The back workshop bays, where the heavy trucks go, have basically no signal. It's a metal shed."),
        (A, "That's important. If the app needs a connection to mark a job done, they'll just stop using it."),
        (A, "What I'd propose: the Android app works offline. It keeps the day's jobs on the phone, they can complete jobs and log parts with no signal, and it syncs when the phone gets a connection again."),
        (M, "As long as the sync keeps the actual completion time, not the sync time. Otherwise my reports are wrong."),
        (A, "Yes, we'd timestamp on the device."),
        (S, "The data on the phone needs to be encrypted. They're company devices with MDM, so that's manageable."),
        (P, "Cost to build?"),
        (A, "Maybe a week and a half extra. It fits inside the new date."),
        (P, "Then we go with it. The mechanics' Android app will support offline mode and sync later."),
        (T, "Good. That solves the shed."),
        (P, "Tom, you had something about a survey?"),
        (T, "Yes, separate from FleetCare really. HR wants us to run a driver satisfaction survey, and we thought Pune first because it's the biggest depot. Probably in February."),
        (M, "Paper or online?"),
        (T, "Online, a simple form, plus paper for anyone who wants it."),
        (P, "Do we need to coordinate it with the pilot? I don't want people confused by two new things at once."),
        (T, "Drivers don't use FleetCare, only mechanics do. So I think it's fine."),
        (P, "Okay. Then the driver survey runs at Pune in February, operations owns it, and it's not part of this project. Agreed?"),
        (T, "Agreed."),
        (P, "Notifications. Tom, what did the depot leads say about SMS?"),
        (T, "Honestly, mixed. The Pune lead said most mechanics would rather get an email to their work address, they all have one and it shows on the phone anyway. Nagpur didn't answer."),
        (S, "Email is much simpler for me. No personal numbers."),
        (A, "And email costs us nothing, we already have a mail service set up."),
        (P, "So for version one, notifications are email only. We can look at SMS later if people ask for it."),
        (A, "Fine by me."),
        (T, "Okay."),
        (M, "One question about the data. For reporting, I wanted to put a reporting database next to the main one, maybe a separate PostgreSQL read replica."),
        (A, "Let's not decide that today. I want to see how heavy your queries are first."),
        (M, "Fair, I'll send you some sample queries."),
        (P, "Okay, anything else? No? Thanks everyone."),
    ],
}

MEETINGS["c"] = {
    "summary": (
        "Technical meeting chaired by Arjun in Priya's absence. Legal "
        "classified maintenance records as personal data that must stay in "
        "India, so the team agreed to keep AWS but deploy everything, "
        "including backups, in the Mumbai region. Because checklists vary "
        "by truck model, the engineering team decided to store work orders "
        "for the scheduling service in MongoDB, with a nightly export for "
        "reporting. Early access to the telematics API works and the 1 "
        "February go-live was confirmed. For fleet customers who want to "
        "see service status, the team agreed on a responsive web portal "
        "rather than a native iPhone app, as a later phase."
    ),
    "turns": [
        (A, "Priya's out today, she asked me to run this one. Let's keep it quick. First, Sara has something on hosting."),
        (S, "Yes. Legal came back on the maintenance records. Because they include driver names and incident reports, they count as personal data, and our policy now is that personal data stays in India. So FleetCare can't just sit in any region."),
        (A, "We're currently in US East because that's the default the account came with."),
        (S, "That would have to change before the pilot."),
        (A, "Mumbai is the obvious one. ap-south-1. Everything we use is available there."),
        (M, "Latency from Pune is better too."),
        (T, "Does moving it delay anything?"),
        (A, "A couple of days. We haven't got production data in yet, so now's the time."),
        (A, "So, we stay with AWS, but everything gets deployed in the Mumbai region. Sara, does that satisfy legal?"),
        (S, "Yes, as long as backups also stay in Mumbai."),
        (A, "Backups too. Okay, done."),
        (A, "Second thing. The work orders. My team's been building the job templates, and every truck model has a different checklist. A Tata has a different service checklist from an Ashok Leyland, and the trailers are different again. The fields keep changing."),
        (M, "That's going to be messy to report on."),
        (A, "Right. So the team's view is that we store work orders in MongoDB. Each work order is one document with whatever checklist it needs. It's just simpler for this data."),
        (T, "Whatever makes it faster, honestly."),
        (M, "Can I still query it?"),
        (A, "Yes, there's a connector, and we'll export nightly to your reporting side."),
        (M, "Okay, then fine by me."),
        (A, "Alright, work orders go in MongoDB for the scheduling service then. I'll get the team started on the data model this week."),
        (A, "Next, the timeline. Where are we?"),
        (A, "The telematics vendor sent us early access to the new API on Tuesday. It works. So we're still on track for the first of February, no change there."),
        (T, "Good, I've told the Pune depot manager February first."),
        (A, "Yes, February first stands. Confirmed."),
        (M, "The data import is about seventy percent done. The Pune spreadsheets were the worst."),
        (T, "Sorry."),
        (M, "Ha, not your fault."),
        (A, "One more. Customer service asked whether customers could see their trucks' service status, the fleet customers who lease from us. They wanted an iPhone app."),
        (T, "Customers on iPhones, sure, a lot of them."),
        (A, "I don't want to build a native iOS app for that. A customer portal that's a responsive website works on iPhones and anything else."),
        (S, "Customer-facing means a separate login and a separate review from me."),
        (A, "Understood. So the customer service-status portal is web-based and responsive, no native app. It's a later phase, but let's agree the direction."),
        (M, "Agreed."),
        (T, "Yep."),
        (A, "Okay, thanks. I'll send notes to Priya."),
    ],
}

MEETINGS["d"] = {
    "summary": (
        "Final pre-go-live meeting. Testing at Pune showed several senior "
        "mechanics use personal iPhones rather than the company Android "
        "phones, so the team changed the earlier plan: the first release of "
        "the mechanics' app will support both Android and iOS, rebuilt in "
        "Flutter, with iOS following two weeks after Android. Hosting was "
        "re-confirmed as AWS Mumbai with no further change. Job assignment "
        "notifications to mechanics will be sent by SMS. Two contract "
        "mechanics were approved for Pune for February and March to cover "
        "the learning curve. The reporting dashboard was deferred to the "
        "next meeting."
    ),
    "turns": [
        (P, "Okay, welcome back everyone, and thanks Arjun for running the last one. A couple of things to close today before go-live. Tom, you've been testing with the mechanics."),
        (T, "Yes. We gave the test build to eight mechanics at Pune. Big finding: four of the senior mechanics have bought their own iPhones and they use their personal phones, not the company Samsung. They leave the Samsung in the locker."),
        (P, "So they can't use the app."),
        (T, "Not unless we force them to carry two phones, and they won't."),
        (S, "If they're personal devices I need a lighter enrolment, but it's doable, we did it for the sales team."),
        (A, "If we need iOS, I'd switch the app to Flutter. One codebase, Android and iOS. My team has used it. The current Android code is about three weeks old, we'd lose less than we think."),
        (P, "Does that affect February first?"),
        (A, "Android stays on schedule. iOS would follow two weeks later."),
        (P, "Okay. So we're changing the earlier plan: the first release of the mechanics' app supports both Android and iOS, built in Flutter, instead of Android-only. Agreed?"),
        (T, "Agreed, that's what the mechanics need."),
        (M, "Fine."),
        (S, "Agreed, with the enrolment."),
        (P, "Hosting check. Sara, are we fine?"),
        (S, "Yes. Everything's in AWS Mumbai, backups too. I re-checked last week."),
        (P, "So hosting stays on AWS in the Mumbai region, no further change."),
        (A, "Correct."),
        (P, "Next. Tom, something from the mechanics?"),
        (T, "They keep asking for text messages when a job is assigned to them. A lot of them don't open the app until they're told to."),
        (A, "We can use the AWS SMS service, it's about twenty paise a message."),
        (S, "Numbers would come from the HR system. For company staff I'm okay with that."),
        (T, "Then let's do SMS for job assignments."),
        (A, "Okay. Job assignment notifications to mechanics go out by SMS. I'll add it this sprint."),
        (P, "Okay, fine."),
        (P, "Last thing, staffing for the pilot. Tom?"),
        (T, "During go-live the Pune mechanics will be slower, they're learning the system. I'd like two contract mechanics for February and March to cover the workload."),
        (P, "Cost?"),
        (T, "About one lakh twenty thousand rupees a month for both."),
        (P, "That's within the pilot contingency. Approved: two contract mechanics at Pune for February and March."),
        (T, "Thanks."),
        (M, "Can we also talk about the reporting dashboard? I'd like to show the overdue list to the depot managers."),
        (P, "Let's do that next meeting, we're out of time."),
        (P, "Okay, thanks all. Big month coming."),
    ],
}


# ============================================================
# GROUND TRUTH (fixed before the system was run)
# ============================================================
# anchor: a unique substring of the turn where agreement is stated.

GOLD_DECISIONS = [
    ("G1",  "a", "Host FleetCare on AWS.",
     "FleetCare will be hosted on AWS"),
    ("G2",  "a", "Pilot goes live at the Pune depot on 15 January.",
     "goes live at the Pune depot on the fifteenth"),
    ("G3",  "a", "PostgreSQL is the primary database for the scheduling service.",
     "so PostgreSQL is the primary database"),
    ("G4",  "a", "The mechanics' app is Android-only in the first release.",
     "Android-only for release one"),

    ("G5",  "b", "Move the Pune go-live from 15 January to 1 February.",
     "moving the Pune go-live from the fifteenth"),
    ("G6",  "b", "The mechanics' Android app supports offline mode and syncs later.",
     "will support offline mode and sync later"),
    ("G7",  "b", "Operations runs a separate driver satisfaction survey at Pune in February.",
     "the driver survey runs at Pune in February"),
    ("G8",  "b", "Notifications are email only for version one.",
     "notifications are email only"),

    ("G9",  "c", "Stay on AWS but deploy everything, including backups, in the Mumbai region.",
     "everything gets deployed in the Mumbai region"),
    ("G10", "c", "Store work orders for the scheduling service in MongoDB.",
     "work orders go in MongoDB"),
    ("G11", "c", "The 1 February go-live is confirmed.",
     "February first stands"),
    ("G12", "c", "The customer service-status portal is a responsive website, not a native app.",
     "portal is web-based and responsive"),

    ("G13", "d", "The mechanics' app supports both Android and iOS in release one, built in Flutter.",
     "supports both Android and iOS"),
    ("G14", "d", "Hosting stays on AWS in the Mumbai region.",
     "hosting stays on AWS in the Mumbai region"),
    ("G15", "d", "Job assignment notifications to mechanics are sent by SMS.",
     "go out by SMS"),
    ("G16", "d", "Approve two contract mechanics at Pune for February and March.",
     "Approved: two contract mechanics"),
]

# (later, earlier, relation, rationale). Every other cross-meeting pair of
# gold decisions is UNRELATED, except those listed in AMBIGUOUS.
GOLD_RELATIONS = [
    ("G5",  "G2", "REVISED",       "go-live date changed, change acknowledged"),
    ("G6",  "G4", "REFINES",       "keeps Android app, adds offline mode"),
    ("G9",  "G1", "REFINES",       "keeps AWS, adds region constraint"),
    ("G10", "G3", "CONTRADICTORY", "MongoDB vs PostgreSQL for the same service; earlier decision never mentioned"),
    ("G11", "G5", "SAME",          "1 February re-confirmed"),
    ("G11", "G2", "REVISED",       "relative to 15 January the date has changed"),
    ("G13", "G4", "REVISED",       "Android-only explicitly changed to Android + iOS"),
    ("G14", "G9", "SAME",          "AWS Mumbai re-confirmed"),
    ("G14", "G1", "REFINES",       "keeps AWS, restates the Mumbai region detail"),
    ("G15", "G8", "CONTRADICTORY", "SMS vs email-only; earlier decision never mentioned"),
]

# Pairs where a reasonable annotator could defend more than one label.
# Excluded from scoring (counted as UNSURE).
AMBIGUOUS = [
    ("G13", "G6", "platform change to the same app; offline mode neither kept nor dropped explicitly"),
]

# Ideas raised but NOT agreed. A correct extractor reports none of these.
NON_DECISIONS = [
    ("a", "SMS alerts for job assignment (parked)", "Let's park SMS"),
    ("b", "PostgreSQL read replica for reporting (deferred)", "Let's not decide that today"),
    ("d", "Reporting dashboard for depot managers (deferred)", "Let's do that next meeting"),
]


# ============================================================
# BUILD
# ============================================================

def find_anchor(turns, letter, anchor):
    hits = [i for i, (_, text) in enumerate(turns) if anchor in text]
    if len(hits) != 1:
        raise ValueError(f"{SERIES}{letter}: anchor {anchor!r} matched {hits}")
    return hits[0]


def main() -> None:

    for letter, meeting in MEETINGS.items():
        data = {
            "topic_list": [],
            "general_query_list": [
                {"query": "Summarize the whole meeting.", "answer": meeting["summary"]}
            ],
            "specific_query_list": [],
            "meeting_transcripts": [
                {"speaker": speaker, "content": text}
                for speaker, text in meeting["turns"]
            ],
        }
        path = OUT_DIR / f"{SERIES}{letter}.json"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {path.name}  ({len(meeting['turns'])} turns)")

    gold = {
        "series_id": SERIES,
        "provenance": (
            "Written for this project with an LLM writing assistant (not "
            "Gemini, the model under evaluation); ground truth fixed before "
            "the system was run."
        ),
        "decisions": [
            {
                "gold_id": gid,
                "meeting": letter,
                "sequence_index": ord(letter) - ord("a") + 1,
                "text": text,
                "anchor_turn": find_anchor(MEETINGS[letter]["turns"], letter, anchor),
            }
            for gid, letter, text, anchor in GOLD_DECISIONS
        ],
        "relations": [
            {"later": later, "earlier": earlier, "relation": rel, "rationale": why}
            for later, earlier, rel, why in GOLD_RELATIONS
        ],
        "ambiguous": [
            {"later": later, "earlier": earlier, "note": note}
            for later, earlier, note in AMBIGUOUS
        ],
        "non_decisions": [
            {
                "meeting": letter,
                "text": text,
                "anchor_turn": find_anchor(MEETINGS[letter]["turns"], letter, anchor),
            }
            for letter, text, anchor in NON_DECISIONS
        ],
    }

    # Sanity: relations must point backwards in time between known ids.
    seq = {d["gold_id"]: d["sequence_index"] for d in gold["decisions"]}
    for rel in gold["relations"] + gold["ambiguous"]:
        assert seq[rel["later"]] > seq[rel["earlier"]], rel

    path = OUT_DIR / f"{SERIES}_gold.json"
    path.write_text(json.dumps(gold, indent=2, ensure_ascii=False), encoding="utf-8")

    counts = {}
    for rel in gold["relations"]:
        counts[rel["relation"]] = counts.get(rel["relation"], 0) + 1

    print(f"Wrote {path.name}")
    print(f"  gold decisions : {len(gold['decisions'])}")
    print(f"  gold relations : {len(gold['relations'])}  {counts}")
    print(f"  ambiguous      : {len(gold['ambiguous'])}")
    print(f"  non-decisions  : {len(gold['non_decisions'])}")


if __name__ == "__main__":
    main()
