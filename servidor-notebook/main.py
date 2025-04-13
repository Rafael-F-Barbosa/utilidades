from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from nbconvert import HTMLExporter
import nbformat
from nbconvert.preprocessors import Preprocessor

from pathlib import Path
import time

app = FastAPI()


class TruncateOutputPreprocessor(Preprocessor):
    def __init__(self, text_max_length=200, list_max_length=5, **kwargs):
        self.text_max_length = text_max_length
        self.list_max_length = list_max_length
        super().__init__(**kwargs)


    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type == 'code':
            for output in cell.get('outputs', []):
                if 'text' in output:
                    output['text'] = self._truncate(output['text'])
                if 'traceback' in output:
                    output['traceback'] = self._truncate_traceback(output['traceback'])
        return cell, resources
    

    def _truncate_traceback(self, content):
        if isinstance(content, str):
            return content[-self.text_max_length:] + '...' if len(content) > self.text_max_length else content
        
        elif isinstance(content, list):
            if(len(content) < (2*self.list_max_length + 2)):
                return content
            
            content_cleaned = []

            content_begining = content[:self.list_max_length]

            content_ending = content[-self.list_max_length:]

            content_cleaned = content_begining + ["\n", "...", "\n" ] +content_ending

            return self._trucante_list_element(content_cleaned)
        return content

    def _truncate(self, content):
        if isinstance(content, str):
            return \
                content[:self.text_max_length] + '...'  + content[-self.text_max_length:] if \
                len(content) > (2*self.text_max_length + 1) \
                else content
        elif isinstance(content, list):
            if(len(content) < (2*self.list_max_length + 2)):
                return content
            
            content_cleaned = []

            content_begining = content[:self.list_max_length]

            content_ending = content[-self.list_max_length:]

            content_cleaned = content_begining + ["\n", "...", "\n" ] +content_ending

            return self._trucante_list_element(content_cleaned)
        
        return content
    
    def _trucante_list_element(self, l):
        new_list = []

        for i in l:
            if isinstance(i, str):
                new_list.append(
                    i[:self.text_max_length] + '\n' +'...' + '\n'  + i[-self.text_max_length:] if \
                    len(i) > (2*self.text_max_length + 1) \
                    else i
                )

        return new_list 
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
# Helper function to load the notebook content
def load_notebook():
    notebook_path = Path("notebook-grande.ipynb")
    if not notebook_path.exists():
        raise HTTPException(status_code=404, detail="Notebook file not found.")
    
    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook_content = nbformat.read(f, as_version=4)
    return notebook_content


# Endpoint to return HTML content for a specific page
@app.get("/api/get-notebook/html", response_class=HTMLResponse)
async def get_notebook_html(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1)):
    try:
        time.sleep(5)
        notebook_content = load_notebook()

        # Get the notebook cells
        cells = notebook_content.get("cells", [])
        
        # Implement pagination
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_cells = cells[start_index:end_index]

        # paginated_cells = truncate_cell_outputs(paginated_cells)

        if not paginated_cells:
            raise HTTPException(status_code=404, detail="No content for this page.")

        # Convert the paginated cells to HTML
        html_exporter = HTMLExporter()

        # Preprocessor trucantes notebook
        html_exporter.register_preprocessor(TruncateOutputPreprocessor, enabled=True)

        notebook_content["cells"] = paginated_cells
        body, _ = html_exporter.from_notebook_node(notebook_content)

        return body  # Returning the HTML content as the response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Endpoint to get metadata, including total pages and whether there are more pages
@app.get("/api/get-notebook/metadata")
async def get_notebook_metadata(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1)):
    try:
        notebook_content = load_notebook()

        # Get the notebook cells
        cells = notebook_content.get("cells", [])
        total_cells = len(cells)
        
        # Calculate total number of pages
        total_pages = (total_cells + page_size - 1) // page_size  # Round up division
        has_more = page < total_pages  # Check if there are more pages

        return JSONResponse(content={
            "current_page": page,
            "total_pages": total_pages,
            "has_more": has_more
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/api/convert-notebook-to-html", response_class=HTMLResponse)
async def convert_notebook_to_html():
    try:
        notebook_content = load_notebook()

        # Convert the entire notebook to HTML
        html_exporter = HTMLExporter()
        body, _ = html_exporter.from_notebook_node(notebook_content)

        # Save the HTML content to a local file
        output_path = Path("notebook.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(body)

        return {"message": f"Notebook successfully converted and saved to {output_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
# Running
# uvicorn main:app --reload --port 5000