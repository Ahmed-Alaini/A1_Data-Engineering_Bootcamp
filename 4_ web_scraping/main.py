import subprocess   # I used this liberary to excute system commands which is better than os.system() in error handling and control

def run_task(name, script):
    print(f"{name}: start")
    try:
        subprocess.run(["python", script], check=True)
        print(f"\n******** {name} completed successfully ********\n")
    except subprocess.CalledProcessError as e:
        print(f"\n Error in {name}")
        print(f"Exit code: {e.returncode}")
        exit(1)

# running each task seprately to make the code clean
run_task("First (scraping the data)", "scraper.py")
run_task("Second (organizing files)", "organizer.py")
run_task("Third (processing the data)", "processor.py")

print("\n\n************* Task completed ************\n\n")
