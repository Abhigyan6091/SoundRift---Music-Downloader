@echo off
echo =======================================================
echo                 Starting SoundRift...
echo =======================================================
echo.
echo Opening your browser to http://localhost:8000
echo Do not close this black window while using the app!
echo.

:: Navigate to the project folder
cd "C:\Users\Abhigyan Sharma\OneDrive\Desktop\SoundRift"

:: Automatically open the default web browser
start http://localhost:8000

:: Run the FastAPI server using your Anaconda Python
"C:\Users\Abhigyan Sharma\anaconda3\python.exe" -m uvicorn main:app --port 8000

pause
