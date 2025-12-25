# Resume Screening System

A comprehensive web application that analyzes resumes against job descriptions and provides match scores based on skill alignment. Features LinkedIn job scraping, multiple resume analysis, and advanced matching algorithms.

## Features

### Single Resume Analysis

- **File Upload**: Supports PDF, DOCX, and TXT resume formats
- **Skill Extraction**: Automatically extracts skills from resumes and job descriptions
- **Match Scoring**: Calculates percentage match based on skill alignment
- **Detailed Analysis**: Shows matched, missing, and additional skills

### Multiple Resume Analysis

- **Batch Processing**: Upload and analyze multiple resumes simultaneously
- **LinkedIn Job Integration**: Scrape job postings from LinkedIn profiles
- **Job Ranking**: Automatically ranks candidates for each job opportunity
- **Advanced Matching**: Uses fuzzy matching and weighted scoring algorithms
- **Candidate Comparison**: Compare multiple candidates side-by-side

### User Interface

- **Modern UI**: Responsive design with drag-and-drop file upload
- **Real-time Processing**: Instant results with loading indicators
- **Interactive Results**: Expandable job details and candidate rankings
- **Visual Feedback**: Color-coded match scores and progress indicators

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **File Processing**: PyPDF2, python-docx
- **Text Analysis**: NLTK, FuzzyWuzzy, scikit-learn
- **Web Scraping**: Selenium, BeautifulSoup4, Requests
- **Deployment**: Gunicorn (production WSGI server)

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

**Note**: Chrome/Chromium browser and ChromeDriver are required for LinkedIn job scraping functionality. The application will work without it, but LinkedIn features will use mock data.

### Step 4: Download NLTK Data (Optional)

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

4. Open your web browser and go to:
   - `http://localhost:5000`
   - `http://127.0.0.1:5000`
   - `http://192.168.1.7:5000` (from other devices on your network)

### Using the Application

#### Single Resume Analysis

1. **Upload Resume**: Drag and drop or click to upload a resume file (PDF, DOCX, or TXT)
2. **Enter Job Description**: Paste the job description in the text area
3. **Analyze**: Click "Analyze Resume Match" to process
4. **View Results**:
   - Overall match score percentage
   - Matched skills (found in both resume and job description)
   - Missing skills (required but not found in resume)
   - Additional skills (in resume but not required)

#### Multiple Resume Analysis with LinkedIn Jobs

1. **Upload Multiple Resumes**: Click "Analyze Multiple Resumes" tab
2. **Upload Files**: Select multiple resume files (PDF, DOCX, or TXT)
3. **Choose Job Source**:
   - **Use Mock Jobs**: Analyzes against 5 sample job postings
   - **Scrape LinkedIn**: Fetches real jobs from configured LinkedIn profiles (requires ChromeDriver)
4. **View Results**:
   - Jobs are listed with expandable details
   - Candidates ranked by match score for each job
   - Detailed skill matching for each candidate
   - Visual indicators for match quality (color-coded scores)

## How It Works

### Skill Extraction

The system extracts skills using multiple approaches:

1. **Predefined Skills Database**: Matches against a comprehensive list of technical skills including:

   - Programming languages (Python, Java, JavaScript, C++, etc.)
   - Frameworks (React, Django, Spring, Flask, etc.)
   - Databases (MySQL, MongoDB, PostgreSQL, etc.)
   - Cloud platforms (AWS, Azure, GCP, etc.)
   - DevOps tools (Docker, Kubernetes, Jenkins, etc.)
   - Soft skills (Leadership, Communication, Teamwork, etc.)

2. **Text Processing**: Uses NLTK for:

   - Text tokenization
   - Stop word removal
   - Keyword extraction
   - N-gram matching for multi-word skills

3. **Fuzzy Matching**: Uses FuzzyWuzzy for:
   - Partial skill name matching
   - Handling variations in skill names
   - Acronym and abbreviation matching

### Scoring Algorithms

#### Basic Match Score

- **Match Score = (Matched Skills / Total Required Skills) × 100**
- Skills are matched case-insensitively
- Partial matches are considered for compound skills

#### Advanced Match Score (for multiple resumes)

Weighted scoring system that considers:

- **Exact Matches** (100% weight): Direct skill matches
- **Partial Matches** (60% weight): Similar skills using fuzzy matching
- **Related Skills** (30% weight): Skills in same category
- **Experience Bonus**: Additional points for years of experience
- **Education Bonus**: Points for relevant degrees

### LinkedIn Job Scraping

The application can scrape job postings from LinkedIn profiles:

- Navigates to profile activity pages
- Identifies job-related posts using keywords
- Extracts job titles, descriptions, and requirements
- Falls back to mock data if scraping fails or ChromeDriver is unavailable

## File Structure

```
resume_screener/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore file
├── templates/
│   └── index.html        # Frontend template with multiple tabs
├── static/               # Static files (currently unused - inline CSS/JS)
├── uploads/              # Temporary file uploads (auto-created, gitignored)
└── backend/
    └── services/         # Backend services (reserved for future use)
```

## API Endpoints

- `GET /` - Main application page
- `POST /upload` - Single resume analysis
- `POST /upload-multiple` - Multiple resume upload
- `POST /analyze-jobs` - Analyze resumes against job descriptions
- `POST /analyze-multiple-with-linkedin` - Analyze with LinkedIn job scraping
- `GET /get-sample-jobs` - Retrieve sample job postings
- `GET /health` - Health check endpoint

## Configuration

### File Size Limits

- Maximum file size: 16MB
- Supported formats: PDF, DOCX, TXT

### Environment Variables

You can customize the application using environment variables:

- `FLASK_ENV`: Set to `development` for debug mode
- `UPLOAD_FOLDER`: Custom upload directory path (default: `uploads/`)
- `MAX_CONTENT_LENGTH`: Maximum file size in bytes (default: 16MB)

### LinkedIn Configuration

To enable LinkedIn job scraping:

1. Install ChromeDriver matching your Chrome browser version
2. Add ChromeDriver to your system PATH
3. Update `TRUSTED_LINKEDIN_PROFILES` list in [app.py](app.py) with target LinkedIn profile URLs
4. The application will automatically use mock data if ChromeDriver is not available

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

1. **ChromeDriver/Selenium Errors**

   - Install ChromeDriver: Download from https://chromedriver.chromium.org/
   - Ensure ChromeDriver version matches your Chrome browser
   - Add to PATH or place in project directory
   - Application will use mock jobs if ChromeDriver is unavailable

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
   - Check file permissions

4. **Poor Match Scores**

   - Ensure job descriptions are detailed
   - Use industry-standard skill names
   - Check that resume contains relevant keywords
   - Verify resume format is parseable

5. **LinkedIn Scraping Not Working**
   - Falls back to mock data automatically
   - Check ChromeDriver installation
   - Verify LinkedIn profile URLs are correct
   - LinkedIn may block automated access (use mock data instead)

### Performance Tips

- For better accuracy, use detailed job descriptions with specific skill requirements
- Include both technical and soft skills in job descriptions
- Use standard industry terminology for skills
- Ensure resumes are well-formatted with clear skill sections
- When analyzing multiple resumes, limit to 10-20 for optimal performance
- LinkedIn scraping may be slow; consider using mock data for testing

## Features in Detail

### Single Resume Analysis

Perfect for quick one-on-one candidate evaluation against a specific job description.

### Multiple Resume Batch Analysis

- Upload 5-20 resumes simultaneously
- Automatically extracts candidate names from resumes or filenames
- Ranks candidates for each job opportunity
- Provides detailed skill breakdown for each candidate
- Color-coded scoring: Green (>70%), Yellow (40-70%), Red (<40%)

### LinkedIn Integration

- Scrapes job posts from configured LinkedIn profiles
- Extracts job titles, descriptions, and requirements
- Gracefully falls back to mock data if scraping fails
- Mock data includes 5 diverse job postings for testing

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
