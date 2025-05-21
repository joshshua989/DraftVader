# ---------------------- RESTART (Development) ----------------------
def restart():
    # Determine the current Python interpreter and script name
    python_executable = sys.executable
    script_name = sys.argv[0]

    # Platform-specific process start
    if platform.system() == "Windows":
        # Start a detached process on Windows
        subprocess.Popen(
            [python_executable, "-m", "streamlit", "run", script_name],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        # Start a detached process on Unix-based systems (Linux/Mac)
        subprocess.Popen(
            [python_executable, "-m", "streamlit", "run", script_name],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    # Wait 10 seconds to allow the new instance to start
    time.sleep(10)

    # Shut down the current process
    pid = os.getpid()
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.send_signal(signal.SIGTERM)
    parent.send_signal(signal.SIGTERM)

# Use columns to center the restart button
col1, col2, col3 = st.columns([2, 1, 2])

# Add the restart button for local testing
with col2:
    if st.button("🔁 Restart App"):
        st.warning("Restarting the app...")
        restart()
# ---------------------- RESTART (Development) ----------------------