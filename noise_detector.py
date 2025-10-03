import pyaudio as pa
import numpy as np
import time as t
from flask import Flask, Response, render_template, render_template_string

app = Flask(__name__)

CHUNK = 1024
FORMAT = pa.paInt16
CHANNELS = 2
RATE = 44100

def monalisa_noise():
   
    p = pa.PyAudio()
    try:
       
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            data_np = np.frombuffer(data, dtype=np.int16)
            
           
            rms = np.sqrt(np.mean(np.square(data_np)))
            if rms == 0:
                db = -120
            else:
                db = 20 * np.log10(rms / np.iinfo(np.int16).max)

            scaled_db = int(max(0, (db + 120 / 1.2)))
            scaled_db = min(300, scaled_db)
            
           
            yield f"data: {scaled_db}\n\n"
            
            t.sleep(0.1)
    finally:
        
        stream.stop_stream()
        stream.close()
        p.terminate()

@app.route('/noise')
def noise_stream():
    """
    This route serves the real-time noise data to the frontend in HTML

    using Server-Sent Events (SSE).
    """
    return Response(monalisa_noise(), mimetype='text/event-stream')

@app.route('/')
def index():
    return render_template("index.html")
    return render_template_string("""
       
    """)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)