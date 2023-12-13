# LLM Evolution Tracking

To run, simply set up a new python environment using

```
python -m venv .venv/
. .venv/bin/activate
pip install ipython pandas diskcache openai
```

Then run 
```
python runner.py
```

At this point, the new results can be loaded form results using 
```
import pandas as pd
results = pd.read_csv('output_data/<output>'





