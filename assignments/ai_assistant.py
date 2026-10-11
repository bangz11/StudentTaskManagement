from datetime import date
from django.shortcuts import render, redirect
from .models import Assignment


def ai_assistant(request):
    if not request.user.is_authenticated:
        return redirect("login")

    assignments = Assignment.objects.filter(
        user=request.user
    ).order_by("due_date")

    answer = None
    question = ""

    if request.method == "POST":
        question = request.POST.get("question", "").strip().lower()

        if not assignments.exists():
            answer = (
                "You currently have no assignments. "
                "When your teacher assigns work, it will appear here."
            )

        else:
            unfinished = assignments.exclude(status="Completed")
            completed = assignments.filter(status="Completed")
            submitted = assignments.filter(
                submission_status="Submitted"
            )
            reviewed = assignments.filter(
                submission_status="Reviewed"
            )
            in_progress = assignments.filter(
                status="In Progress"
            )
            high_priority = unfinished.filter(priority="High")

            if any(word in question for word in [
                "hello", "hi", "hey", "help"
            ]):
                answer = (
                    "Hello! I'm your StudyFlow Assistant.\n\n"
                    "I can help you understand your assignments, "
                    "deadlines, priorities, progress, and submissions.\n\n"
                    "Try asking:\n"
                    "- What should I work on first?\n"
                    "- What is due soon?\n"
                    "- Show my high-priority assignments.\n"
                    "- What is my current progress?\n"
                    "- What have I submitted?"
                )

            elif any(word in question for word in [
                "first", "start", "urgent", "important",
                "work on", "do next"
            ]):
                if not unfinished.exists():
                    answer = (
                        "You have completed all your assignments. "
                        "Great job!"
                    )
                else:
                    if high_priority.exists():
                        candidates = high_priority
                    else:
                        candidates = unfinished

                    a = candidates.order_by("due_date").first()

                    days_left = (a.due_date - date.today()).days

                    if days_left < 0:
                        timing = "This assignment is overdue."
                    elif days_left == 0:
                        timing = "This assignment is due today."
                    elif days_left == 1:
                        timing = "This assignment is due tomorrow."
                    else:
                        timing = f"You have {days_left} days left."

                    answer = (
                        f"I recommend starting with: {a.title}\n\n"
                        f"Subject: {a.subject}\n"
                        f"Due: {a.due_date}\n"
                        f"Priority: {a.priority}\n"
                        f"Status: {a.status}\n\n"
                        f"{timing}\n"
                        "Focus on this assignment first because "
                        "of its deadline and priority."
                    )

            elif any(word in question for word in [
                "due", "deadline", "soon", "tomorrow", "today"
            ]):
                if unfinished.exists():
                    answer = "Here are your unfinished assignments:\n\n"

                    for a in unfinished:
                        days_left = (a.due_date - date.today()).days

                        if days_left < 0:
                            timing = "OVERDUE"
                        elif days_left == 0:
                            timing = "Due today"
                        elif days_left == 1:
                            timing = "Due tomorrow"
                        else:
                            timing = f"{days_left} days left"

                        answer += (
                            f"- {a.title}\n"
                            f"  Subject: {a.subject}\n"
                            f"  Due: {a.due_date}\n"
                            f"  Priority: {a.priority}\n"
                            f"  Status: {a.status}\n"
                            f"  {timing}\n\n"
                        )
                else:
                    answer = "You have no unfinished assignments."

            elif any(word in question for word in [
                "high", "priority"
            ]):
                if high_priority.exists():
                    answer = "Your high-priority unfinished work:\n\n"

                    for a in high_priority:
                        answer += (
                            f"- {a.title}\n"
                            f"  Subject: {a.subject}\n"
                            f"  Due: {a.due_date}\n"
                            f"  Status: {a.status}\n\n"
                        )
                else:
                    answer = (
                        "You currently have no unfinished "
                        "high-priority assignments."
                    )

            elif any(word in question for word in [
                "progress", "status", "doing"
            ]):
                answer = (
                    f"Your StudyFlow progress:\n\n"
                    f"Total assignments: {assignments.count()}\n"
                    f"Completed: {completed.count()}\n"
                    f"In Progress: {in_progress.count()}\n"
                    f"Not submitted: "
                    f"{assignments.filter(submission_status='Not Submitted').count()}\n"
                    f"Submitted: {submitted.count()}\n"
                    f"Reviewed: {reviewed.count()}"
                )

            elif any(word in question for word in [
                "submitted", "submission", "send", "sent"
            ]):
                if submitted.exists() or reviewed.exists():
                    answer = "Your submitted work:\n\n"

                    for a in assignments.filter(
                        submission_status__in=["Submitted", "Reviewed"]
                    ):
                        answer += (
                            f"- {a.title}\n"
                            f"  Submission: {a.submission_status}\n"
                            f"  Due: {a.due_date}\n\n"
                        )
                else:
                    answer = "You have not submitted any assignments yet."

            elif any(word in question for word in [
                "completed", "finished", "done"
            ]):
                if completed.exists():
                    answer = "Your completed assignments:\n\n"

                    for a in completed:
                        answer += (
                            f"- {a.title}\n"
                            f"  Subject: {a.subject}\n"
                            f"  Due: {a.due_date}\n\n"
                        )
                else:
                    answer = "You have not completed any assignments yet."

            elif any(word in question for word in [
                "list", "show", "all assignments"
            ]):
                answer = "Your StudyFlow assignments:\n\n"

                for a in assignments:
                    answer += (
                        f"- {a.title}\n"
                        f"  Subject: {a.subject}\n"
                        f"  Due: {a.due_date}\n"
                        f"  Priority: {a.priority}\n"
                        f"  Status: {a.status}\n"
                        f"  Submission: {a.submission_status}\n\n"
                    )

            elif any(word in question for word in [
                "how many", "count", "number"
            ]):
                answer = (
                    f"You currently have {assignments.count()} "
                    f"assignments.\n\n"
                    f"Completed: {completed.count()}\n"
                    f"In Progress: {in_progress.count()}\n"
                    f"High Priority: {high_priority.count()}\n"
                    f"Submitted: {submitted.count()}\n"
                    f"Reviewed: {reviewed.count()}"
                )

            else:
                answer = (
                    "I can help you with your StudyFlow data.\n\n"
                    "You can ask about:\n"
                    "- Assignments\n"
                    "- Deadlines\n"
                    "- What to work on first\n"
                    "- High-priority work\n"
                    "- Progress and status\n"
                    "- Submissions\n"
                    "- Completed work\n"
                    "- Assignment counts\n\n"
                    "Try asking your question in your own words."
                )

    return render(
        request,
        "assignments/ai_assistant.html",
        {
            "answer": answer,
            "question": question
        }
    )
