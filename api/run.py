from src.config import app
from src.controller import api_router
import uvicorn
import dotenv

dotenv.load_dotenv()

app.include_router(api_router)


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
