# Student Report Management (Streamlit)

A professional starter for a Streamlit-based student report system.

## Features
- Authentication (streamlit-authenticator)
- Manage students, subjects, and marks
- SQLite database via SQLModel
- Multi-page Streamlit app
- Theming via `.streamlit/config.toml`

## Project Structure
```
sytems students/
├─ .streamlit/
│  └─ config.toml
├─ requirements.txt
├─ src/
│  ├─ app.py
│  ├─ components/
│  │  └─ forms.py
│  ├─ models/
│  │  └─ schemas.py
│  ├─ pages/
│  │  ├─ 1_Students.py
│  │  ├─ 2_Subjects.py
│  │  └─ 3_Marks.py
│  ├─ services/
│  │  └─ db.py
│  └─ utils/
│     └─ auth.py
└─ tests/
```

## Quickstart
1. Create/activate your venv
2. Install dependencies
3. Run Streamlit app

### Windows PowerShell
```powershell
& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run src/app.py
```

If `streamlit` is not on PATH, run:
```powershell
& ".\.venv\Scripts\python.exe" -m streamlit run src/app.py
```

## Notes
- Default login: username `teacher1`, password `teacher123`.
- A local SQLite file `students.db` is created automatically.
- Update auth settings in `.streamlit/auth.yaml` after first run.
