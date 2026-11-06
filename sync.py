import subprocess


def run(command):
    print(f"\n> {command}")
    result = subprocess.run(command, shell=True)

    if result.returncode != 0:
        print("\n❌ Something went wrong.")
        exit(1)


print("================================")
print("     WATCHLIST TRACKER SYNC     ")
print("================================")

run("git add .")
run('git commit -m "Update watchlist"')
run("git push")

print("\n✓ Your watchlist has been uploaded!")
print("✓ GitHub Pages will update shortly.")
