from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

from translator.translate import translate
from translator.model import MAIN_DIRECTORY

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
        <html>
            <head>
                <title>Translator</title>
            </head>
            <body>
                <h1>English to German translator</h1>
                <center>
                    <form method="post" action="/translate">
                      <label for="englishInput">English phrase:</label>
                      <input type="text" id="englishInput" name="englishInput"><br><br>
                      <input type="submit" value="Submit">
                    </form>
                <center>
            </body>
        </html>
        """

@app.post('/translate')
async def perform_translation(englishInput: str = Form(...)):
    # germanOutput = translate([englishInput])[0]
    return {'english_input': englishInput, 'german_output': translate([englishInput])[0]}

if __name__ == '__main__':
    uvicorn.run(app)
