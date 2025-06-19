import pandas as pd
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from classify import classify

app = FastAPI(title="Log Classification System")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Simple upload form."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Log Classification</title></head>
    <body style="font-family: Arial; margin: 40px;">
        <h1>🔍 Log Classification System</h1>
        <h3>Upload CSV File</h3>
        <p>CSV must have 'source' and 'log_message' columns</p>
        <form action="/classify/" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".csv" required><br><br>
            <button type="submit">Classify Logs</button>
        </form>
        <p><a href="/docs">API Documentation</a></p>
    </body>
    </html>
    """

@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}

@app.post("/classify/")
async def classify_logs(file: UploadFile = File(...)):
    """Upload and classify CSV."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")
    
    try:
        # Save uploaded file
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process CSV
        df = pd.read_csv(temp_path)
        
        if "source" not in df.columns or "log_message" not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must have 'source' and 'log_message' columns")
        
        # Classify
        logs_data = list(zip(df["source"], df["log_message"]))
        df["target_label"] = classify(logs_data)
        
        # Save result
        os.makedirs("resources", exist_ok=True)
        output_path = "resources/output.csv"
        df.to_csv(output_path, index=False)
        
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return FileResponse(
            output_path,
            media_type='text/csv',
            filename=f"classified_{file.filename}"
        )
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()

@app.post("/classify-single/")
async def classify_single(source: str, log_message: str):
    """Classify single log message."""
    try:
        from classify import classify_log
        result = classify_log(source, log_message)
        return {"source": source, "log_message": log_message, "classification": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)