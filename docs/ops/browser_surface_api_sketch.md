---
id: browser_surface_api_sketch
title: Browser Surface API Sketch
type: ops-blueprint
---

# Browser Surface API Sketch

## Concept
APMultitool's future browser release will require a lightweight backend (Flask/FastAPI) that translates REST/GraphQL requests into the exact same `Job` dataclasses currently used by the Qt Desktop UI.

## Endpoint Mappings

### 1. Document Compiler (`POST /api/v1/compile`)
- **Action:** Merges PDF/DOCX files.
- **Payload Request:**
  ```json
  {
    "operation": "merge",
    "inputs": ["s3://bucket/upload1.pdf", "s3://bucket/upload2.docx"],
    "params": {
      "output_name": "Final_Exhibit_A.pdf",
      "preserve_bookmarks": true,
      "scale_to_letter": true
    }
  }
  ```
- **Response:** Job ID to poll via WebSocket or `/status`.

### 2. Bates Stamping (`POST /api/v1/bates`)
- **Action:** Applies Bates stamps to a specific file.
- **Payload Request:**
  ```json
  {
    "operation": "bates_stamp",
    "inputs": ["s3://bucket/Final_Exhibit_A.pdf"],
    "params": {
      "prefix": "DEF-APP-",
      "start_number": 1,
      "padding": 6,
      "font": "Helvetica-Bold"
    }
  }
  ```
- **Response:** Job ID.

### 3. File Room Tree Builder (`POST /api/v1/fileroom/blueprint`)
- **Action:** Generates an empty directory zip archive based on a blueprint.
- **Payload Request:**
  ```json
  {
    "matter_id": "24-CIV-9901",
    "blueprint_type": "civil_litigation"
  }
  ```
- **Response:** A signed download URL returning a `.zip` file of the generated folder hierarchy.

### 4. Job Status & Polling (`GET /api/v1/jobs/{job_id}`)
- **Action:** Replaces the Qt `QThread` signal emission.
- **Response:**
  ```json
  {
    "status": "processing",
    "progress_percent": 45,
    "current_file": "upload2.docx"
  }
  ```

## Verdict
The core `EngineJobWorker` translates perfectly to a Celery worker executing these exact JSON definitions. No new `core/` business logic is required.
