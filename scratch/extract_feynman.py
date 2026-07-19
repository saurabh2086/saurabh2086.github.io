import subprocess

# Get the file contents from the specific commit
commit_hash = "bb845d3"
file_path = "bda3/ch5/ch5_section5.html"

res = subprocess.run(["git", "show", f"{commit_hash}:{file_path}"], capture_output=True, text=True)
content = res.stdout

# Extract content inside <div class="mode-feynman hidden"> ... </div>
# Since there is nested <div>, let's trace matching tags or use simple line limits.
lines = content.split('\n')

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if '<div class="mode-feynman hidden">' in line:
        start_idx = i
        break

if start_idx != -1:
    # Look for the closing </div> at the end of the feynman container
    # In bb845d3, it was right before the References section or bottom script.
    for i in range(start_idx, len(lines)):
        if '</div>' in lines[i] and ('<!-- References' in lines[i+1] or '<!-- References' in lines[i+2] or '<section class="mt-20' in lines[i+1] or '<section class="mt-20' in lines[i+2]):
            end_idx = i
            break

if start_idx != -1 and end_idx != -1:
    feynman_block = '\n'.join(lines[start_idx:end_idx+1])
    with open("scratch_feynman_lecture.html", "w") as f:
        f.write(feynman_block)
    print(f"Extracted block from line {start_idx} to {end_idx}")
else:
    print(f"Failed to extract. Start: {start_idx}, End: {end_idx}")
