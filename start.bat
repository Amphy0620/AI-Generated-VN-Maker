@echo off
:: Change to the directory where this .bat file is located
cd /d %~dp0

:: Check if the virtual environment exists
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip to the latest version
echo Upgrading pip...
pip install --upgrade pip

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Run the Python script
echo Running the script...
python app.py