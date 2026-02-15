from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from main import run_reconciliation
import os
import uvicorn

app = FastAPI(title="DRA Transaction Reconciliation Ultra")

LATEST_REPORT = None

@app.get("/", response_class=HTMLResponse)
def dashboard():
    """
    Simple dashboard to trigger runs and view status.
    Uses Montserrat font and brand colors inline for simplicity.
    """
    global LATEST_REPORT
    
    report_link = ""
    if LATEST_REPORT and os.path.exists(LATEST_REPORT):
        report_link = f'''
        <div style="margin-top: 20px; padding: 20px; background: rgba(34, 197, 94, 0.1); border-radius: 8px; border: 1px solid #22c55e;">
            <strong>✅ Latest Report Available:</strong> <a href="/report" target="_blank" style="color: #121212; font-weight: 700;">{LATEST_REPORT}</a>
        </div>
        '''

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DRA Ultra Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Montserrat', sans-serif; background: #f8f9fa; color: #121212; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .container {{ background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 400px; text-align: center; }}
            h1 {{ color: #dd3333; margin-bottom: 10px; }}
            p {{ color: #6b7280; margin-bottom: 30px; }}
            .btn {{ background: #dd3333; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 16px; transition: background 0.2s; }}
            .btn:hover {{ background: #b52828; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>DRA Ultra</h1>
            <p>Automated Transaction Reconciliation</p>
            <form action="/run" method="post">
                <button type="submit" class="btn">Run Reconciliation Audit</button>
            </form>
            {report_link}
        </div>
    </body>
    </html>
    """

@app.post("/run")
def run_audit(background_tasks: BackgroundTasks):
    global LATEST_REPORT
    # Run synchronously for MVP simplicity, or background task in real prod
    report_file = run_reconciliation()
    LATEST_REPORT = report_file
    return {"status": "success", "report": report_file, "message": "Audit completed successfully. Go back to view report."}

@app.get("/report")
def get_report():
    global LATEST_REPORT
    if LATEST_REPORT and os.path.exists(LATEST_REPORT):
        return FileResponse(LATEST_REPORT)
    return {"error": "No report generated yet."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
