# Resume Screening System

A comprehensive web application that analyzes resumes against job descriptions and provides match scores based on skill alignment.

## Features

- **File Upload**: Supports PDF, DOCX, and TXT resume formats
- **Skill Extraction**: Automatically extracts skills from resumes and job descriptions
- **Match Scoring**: Calculates percentage match based on skill alignment
- **Detailed Analysis**: Shows matched, missing, and additional skills
- **Modern UI**: Responsive design with drag-and-drop file upload
- **Real-time Processing**: Instant results with loading indicators

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **File Processing**: PyPDF2, python-docx
- **NLP**: NLTK, spaCy
- **Deployment**: Can be deployed on any platform supporting Python

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone/Download the Project

Download or clone this project to your local machine.

### Step 2: Create a Virtual Environment (Recommended)

```bash
# Navigate to the project directory
cd resume_screener

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

### Step 5: Download NLTK Data

The application will automatically download required NLTK data on first run, but you can also do it manually:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

## Usage

### Running the Application

1. Make sure your virtual environment is activated
2. Navigate to the project directory
3. Run the application:

```bash
python app.py
```

4. Open your web browser and go to `http://localhost:5000`

### Using the Application

1. **Upload Resume**: Drag and drop or click to upload a resume file (PDF, DOCX, or TXT)
2. **Enter Job Description**: Paste the job description in the text area
3. **Analyze**: Click "Analyze Resume Match" to process
4. **View Results**:
   - Overall match score percentage
   - Matched skills (found in both resume and job description)
   - Missing skills (required but not found in resume)
   - Additional skills (in resume but not required)

## How It Works

### Skill Extraction

The system extracts skills using multiple approaches:

1. **Predefined Skills Database**: Matches against a comprehensive list of technical skills including:

   - Programming languages (Python, Java, JavaScript, etc.)
   - Frameworks (React, Django, Spring, etc.)
   - Databases (MySQL, MongoDB, PostgreSQL, etc.)
   - Cloud platforms (AWS, Azure, GCP, etc.)
   - Soft skills (Leadership, Communication, etc.)

2. **NLP Processing**: Uses NLTK and spaCy for:
   - Text tokenization
   - Stop word removal
   - Lemmatization
   - Keyword extraction

### Scoring Algorithm

- **Match Score = (Matched Skills / Total Required Skills) × 100**
- Skills are matched case-insensitively
- Partial matches are considered for compound skills
- Results include detailed breakdowns of matched, missing, and additional skills

## File Structure

```
resume_screener/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Frontend template
├── static/               # Static files (CSS, JS, images)
├── uploads/              # Temporary file uploads (auto-created)
└── .gitignore           # Git ignore file
```

## Configuration

### File Size Limits

- Maximum file size: 16MB
- Supported formats: PDF, DOCX, TXT

### Environment Variables

You can customize the application using environment variables:

- `FLASK_ENV`: Set to `development` for debug mode
- `UPLOAD_FOLDER`: Custom upload directory path
- `MAX_CONTENT_LENGTH`: Maximum file size in bytes

## Deployment

### Local Development

```bash
python app.py
```

### Production Deployment

For production deployment, use a WSGI server like Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Troubleshooting

### Common Issues

1. **spaCy Model Not Found**

   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **NLTK Data Missing**

   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   ```

3. **File Upload Errors**

   - Check file size (max 16MB)
   - Ensure file format is supported (PDF, DOCX, TXT)
   - Verify file is not corrupted

4. **Poor Match Scores**
   - Ensure job descriptions are detailed
   - Use industry-standard skill names
   - Check that resume contains relevant keywords

### Performance Tips

- For better accuracy, use detailed job descriptions
- Include both technical and soft skills in job descriptions
- Use standard industry terminology for skills
- Ensure resumes are well-formatted with clear skill sections

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support or questions:

- Check the troubleshooting section
- Review the code comments for implementation details
- Open an issue for bugs or feature requests

---

**Built for the ATS Hackathon - Making recruitment smarter with AI-powered resume screening.**
