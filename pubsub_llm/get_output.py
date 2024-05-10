import subprocess
# keep subscribing to read new translation outputs
# to be run at the destination
while True:
    try:
        # Run the command
        subprocess.run(['python', 'subscribe_out.py'])
    except KeyboardInterrupt:
        print("Interrupted, exiting...")
        break