from fastapi import FastAPI, File, UploadFile, HTTPException

app = FastAPI()

@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")

    # Aquí irá la lógica de procesamiento asíncrono
    content = await file.read()

    return {"message": "Async processing started", "filename": file.filename}
