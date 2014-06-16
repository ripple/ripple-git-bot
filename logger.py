#!/usr/bin/python

# The Log Processing Function:

def logproc(logs):
    """Correctly Orders Raw Unordered Heroku Logs Based On Their Number."""
    logs = str(logs)
    lines = []
    for line in logs.split("\n"):
        if ": " in line:
            line = line.split(": ", 1)[1]
        if ". " in line:
            line = line.split(". ", 1)
        else:
            line = ("0", line)
        line = (int(line[0]), line[1])
        lines.append(line)
    lines.sort()
    out = ""
    for num, line in lines:
        out += str(num)+". "+line+"\n"
    return out[:-1]

# Running Log Processing:

if __name__ == "__main__":
    print(logproc(raw_input("Paste Logs: ")))
