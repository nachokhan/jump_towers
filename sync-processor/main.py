import logging.config
from fastapi import FastAPI, File, UploadFile, HTTPException
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
from collections import Counter
import logging
import sys

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/process")
async def process_file(file: UploadFile = File(...)):

    logging.info(f"Recibiendo archivo: {file.filename}")

    if not file.filename.endswith('.csv'):
        logging.error("File is not a CSV.")
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    try:
        content = await file.read()
        logging.info("Reading file with size: %d bytes", len(content))

        df = pd.read_csv(StringIO(content.decode()))
        logging.info(f"CSV file loaded with {len(df)} rows.")

        df_clean = clean_data(df)
        logging.info(f"{len(df_clean)} rows after initial cleaning.")

        result = analyze_movements(df_clean)
        logging.info(f"Analysis completed with {len(result)} intervals.")

        output_path = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        pd.DataFrame(result).to_csv(output_path, index=False)
        logging.info(f"Reporte guardado en {output_path}")

        return result

    except Exception as e:
        logging.exception("Error processing file")
        raise HTTPException(status_code=500, detail=str(e))


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how="all")
    df.columns = df.columns.str.strip()

    df = df.copy()

    df["Latitude"] = pd.to_numeric(df.get("Latitude"), errors='coerce')
    df["Longitude"] = pd.to_numeric(df.get("Longitude"), errors='coerce')
    df = df[(df["Latitude"].notna()) & (df["Longitude"].notna())]
    df = df[(df["Latitude"] != 0) & (df["Longitude"] != 0)]
    logging.info(f"Filtered by lat/lon. Remaining rows: {len(df)}")

    # Parse timestamp
    if "LocalDateTime" in df.columns:
        df = df[df["LocalDateTime"].notna()]
        df["timestamp"] = pd.to_datetime(df["LocalDateTime"], format="%m/%d/%y %H:%M", errors="coerce")
    elif "UTCDateTime" in df.columns:
        df = df[df["UTCDateTime"].notna()]
        df["timestamp"] = pd.to_datetime(df["UTCDateTime"], format="%m/%d/%y %H:%M", errors="coerce")
    else:
        raise ValueError("Missing LocalDateTime or UTCDateTime column")

    df = df[df["timestamp"].notna()]
    df = df.sort_values("timestamp")

    if "State" not in df.columns:
        raise ValueError("Missing required column: 'State'")

    logging.info(f"Parsed timestamps. Remaining rows: {len(df)}")
    return df


def analyze_movements(df: pd.DataFrame) -> list:

    logging.info(f"Starting movement analysis for {len(df)} rows.")
    window_size = timedelta(minutes=10)
    jump_threshold = timedelta(minutes=5)
    result = []
    i = 0

    logging.info(f"Starting analysis of movements... Window size: {window_size}, Jump threshold: {jump_threshold}")

    for idx, row in df.iterrows():
        i += 1
        t = row["timestamp"]
        window_start = t - window_size
        window_end = t + window_size
        window_df = df[(df["timestamp"] >= window_start) & (df["timestamp"] <= window_end)]

        logging.debug(f"Counting states in window from {window_start} to {window_end} for timestamp {t}")
        states = window_df["State"].tolist()
        if not states:
            logging.debug(f"No states found in window {window_start} to {window_end} for timestamp {t}. Skipping...")
            continue

        logging.debug(f"Found {len(states)} states in the window.")
        most_common_state, count = Counter(states).most_common(1)[0]
        confidence = round(count / len(states), 2)

        logging.debug(f"Most common state: {most_common_state} with confidence {confidence}")

        # Detectar Tower Jump
        prev = df[df["timestamp"] < t].tail(1)
        next_ = df[df["timestamp"] > t].head(1)
        if i % 500 == 0:
            logging.info(f"Procesadas {i+1}/{len(df)} filas...({idx})")

        result.append({
            "start_time": window_start.isoformat(),
            "end_time": window_end.isoformat(),
            "State": most_common_state,
            "tower_jump": "yes" if jump else "no",
            "confidence": confidence
        })

    logging.info(f"Analysis completed with {len(result)} intervals.")
    return result
