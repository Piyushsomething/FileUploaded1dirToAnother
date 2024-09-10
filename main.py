from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os
from typing import List

app = FastAPI()

# CORS middleware to allow frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create temp and main folders if they don't exist
os.makedirs("temp", exist_ok=True)
os.makedirs("main", exist_ok=True)

# Serve static files (for frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        with open(f"temp/{file.filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename, "status": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/temp-files/")
async def get_temp_files():
    files = os.listdir("temp")
    return {"files": files}

@app.delete("/temp-files/{filename}")
async def delete_temp_file(filename: str):
    try:
        os.remove(f"temp/{filename}")
        return {"status": "File deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/finalize/")
async def finalize_files(action: str = Query(..., regex="^(move|copy)$")):
    temp_files = os.listdir("temp")
    for file in temp_files:
        if action == "move":
            shutil.move(f"temp/{file}", f"main/{file}")
        elif action == "copy":
            shutil.copy2(f"temp/{file}", f"main/{file}")
    
    status = "Files moved to main folder" if action == "move" else "Files copied to main folder"
    return {"status": status}

@app.get("/main-files/")
async def get_main_files():
    files = os.listdir("main")
    return {"files": files}

@app.get("/main-files-info/")
async def get_main_files_info():
    files_info = []
    for file in os.listdir("main"):
        file_path = os.path.join("main", file)
        size = os.path.getsize(file_path)
        _, extension = os.path.splitext(file)
        files_info.append({
            "filename": file,
            "extension": extension,
            "size": size
        })
    return {"files_info": files_info}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)