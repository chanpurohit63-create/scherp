"""Fix the homework grading test to handle the nested submission structure."""
import re

path = "e2e_full_test.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '''        # Teacher grades submission
        status, body, err = req("GET", f"/api/portal/teacher/homework/{hw_id}/submissions", ttoken)
        if status == 200 and isinstance(body, list) and body:
            sub_id = body[0]["id"]
            status, body, err = req("PUT", f"/api/portal/teacher/homework/{hw_id}/submissions/{sub_id}/grade?grade=A&feedback=Excellent", ttoken)
            grade_ok = status == 200
            log("8.5", "Teacher grades homework", "200 + graded", f"{status}", grade_ok,
                err=str(err) if err else (str(body) if not grade_ok else None))
        else:
            log("8.5", "Teacher grades homework", "200 + graded", f"submissions={status} {body}", False,
                err="No submissions found to grade")'''

new = '''        # Teacher grades submission
        status, body, err = req("GET", f"/api/portal/teacher/homework/{hw_id}/submissions", ttoken)
        if status == 200 and isinstance(body, list) and body:
            sub = body[0]
            sub_id = sub.get("submission", sub).get("id", sub.get("id"))
            if sub_id:
                status, body, err = req("PUT", f"/api/portal/teacher/homework/{hw_id}/submissions/{sub_id}/grade?grade=A&feedback=Excellent", ttoken)
                grade_ok = status == 200
                log("8.5", "Teacher grades homework", "200 + graded", f"{status}", grade_ok,
                    err=str(err) if err else (str(body) if not grade_ok else None))
            else:
                log("8.5", "Teacher grades homework", "200 + graded", f"submission={body[0]}", False,
                    err="Could not extract submission id")
        else:
            log("8.5", "Teacher grades homework", "200 + graded", f"submissions={status} {body}", False,
                err="No submissions found to grade")'''

assert old in content, "Grading test block not found"
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Grading test fixed")