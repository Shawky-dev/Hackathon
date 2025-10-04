from fastapi import FastAPI, HTTPException, Query
from datetime import datetime, timedelta
import requests
import pytz

app=FastAPI()
BASE_URL = "https://s3-us-west-1.amazonaws.com/files.airnowtech.org"




@app.get("/past-data")

def get_realtime_data(hours: int= Query(3, description="number of past hours to fetch",gt=0 , le=168)
                      ):

        now=datetime.now(pytz.timezone("US/Eastern"))-timedelta(hours=3)
        results=[]


        for i in range(hours):
                 target_time = now - timedelta(hours=i)
                 year = target_time.strftime("%Y")
                 month = target_time.strftime("%m")
                 day = target_time.strftime("%d")
                 date = target_time.strftime("%Y%m%d")
                 hour = target_time.strftime("%H")

                 file_url=f"{BASE_URL}/airnow/{year}/{date}/HourlyAQObs_{date}{hour}.dat"
                 print("Trying URL:", file_url)
              
                 try:
                   response = requests.get(file_url, timeout=5)
                   if response.status_code == 200:
                        results.append({
                            "url": file_url,
                            "data": response.text.splitlines()[:5]
                                        })
                   else:
                        results.append({
                            "url": file_url,
                            "error": f"status {response.status_code}"
                                        })
                 except Exception as e:
                    results.append({
                        "url": file_url,
                        "error": str(e)
                                     })

        return {"requested_hours": hours, "results": results}


        