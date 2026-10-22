# AttendAI — 3-hour hackathon MVP

A local Streamlit prototype for classroom attendance with:
- Student registration using a face photo
- OpenCV Haar-cascade face detection
- Lightweight image-appearance comparison for candidate matching
- Teacher review before saving attendance
- CSV reports and a dashboard

## Important limitation
This is a hackathon prototype, **not a reliable production biometric recognition system**. It uses simple grayscale appearance comparison, not a modern face-embedding model. Similarity scores are not probabilities or accuracy estimates. Lighting, pose, distance, occlusion, and similar-looking faces can cause errors. Always review matches manually. Do not use real student images without informed consent and authorization.

## Run on Windows

1. Install Python 3.10–3.12 if possible.
2. Open Command Prompt in this folder.
3. Create and activate a virtual environment:

   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   ```

4. Install packages:

   ```bat
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Start the app:

   ```bat
   streamlit run app.py
   ```

6. Streamlit will show a local URL, usually `http://localhost:8501`.

## Demo steps

1. Open **Register Students**.
2. Register a few consenting volunteers using clear, front-facing images. Keep the class name consistent (default `MCA-A`).
3. Open **Take Attendance** and upload a classroom/group photo.
4. Click **Detect & Match Faces**.
5. Review proposed results carefully. Unknown faces are not automatically assigned.
6. Confirm the reviewed records and download the CSV.
7. Open **Attendance Reports**.

## Team split for four people

- Member 1: test and improve face detection/matching in `detect_faces`, `crop_signature`, and `compare_signatures`.
- Member 2: data persistence, attendance logic, CSV output.
- Member 3: Streamlit interface and dashboard styling.
- Member 4: end-to-end testing, demo data, README, slides, presentation.

## Files

- `app.py` — complete Streamlit application
- `requirements.txt` — Python dependencies
- `data/students/` — registered face crops (local only)
- `data/attendance/` — saved CSV attendance reports
- `data/students.json` — student registry

Do not commit `data/`, real face photos, or private student information to a public repository.
