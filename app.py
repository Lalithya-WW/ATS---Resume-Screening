from flask import Flask, request, render_template, jsonify, redirect, url_for
import os
import re
from werkzeug.utils import secure_filename
import PyPDF2
import docx
from collections import Counter
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
from datetime import datetime
from fuzzywuzzy import fuzz
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# LinkedIn Profile URLs for job postings
TRUSTED_LINKEDIN_PROFILES = [
    "https://www.linkedin.com/in/zeeshan-ali-562109131",
    "https://www.linkedin.com/in/naman-vidyabhanu-387882148", 
    "https://www.linkedin.com/in/avinash-yadav-jeniga-10a1b31a0"
]

class LinkedInJobScraper:
    def __init__(self):
        """Initialize the LinkedIn job scraper"""
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
    def scrape_linkedin_posts(self, profile_urls, max_posts_per_profile=10):
        """Scrape job posts from LinkedIn profiles"""
        all_jobs = []
        
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            
            for profile_url in profile_urls:
                try:
                    print(f"Scraping profile: {profile_url}")
                    
                    # Navigate to profile activity page
                    activity_url = f"{profile_url}/recent-activity/"
                    driver.get(activity_url)
                    
                    # Wait for page to load
                    time.sleep(3)
                    
                    # Scroll to load more posts
                    for _ in range(3):
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                    
                    # Find posts that might be job-related
                    posts = driver.find_elements(By.CSS_SELECTOR, '[data-id*="activity"]')
                    
                    for post in posts[:max_posts_per_profile]:
                        try:
                            post_text = post.text.lower()
                            
                            # Check if post contains job-related keywords
                            job_keywords = [
                                'hiring', 'job', 'opportunity', 'position', 'role', 
                                'vacancy', 'opening', 'career', 'recruit', 'apply',
                                'developer', 'engineer', 'analyst', 'manager', 'intern'
                            ]
                            
                            if any(keyword in post_text for keyword in job_keywords):
                                # Extract job details
                                job_data = self.extract_job_details(post.text)
                                if job_data and job_data['title'] and job_data['description']:
                                    job_data['source_profile'] = profile_url
                                    job_data['scraped_at'] = datetime.now().isoformat()
                                    all_jobs.append(job_data)
                                    
                        except Exception as e:
                            print(f"Error processing post: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error scraping profile {profile_url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error initializing driver: {e}")
            # Fallback to mock job data for demonstration
            return self.get_mock_jobs()
            
        finally:
            try:
                driver.quit()
            except:
                pass
                
        # If no jobs found, return mock data
        if not all_jobs:
            return self.get_mock_jobs()
            
        return all_jobs[:20]  # Return max 20 jobs
    
    def extract_job_details(self, post_text):
        """Extract job details from post text"""
        lines = post_text.split('\n')
        
        # Simple extraction logic
        title = ""
        company = ""
        description = post_text
        
        # Look for job title patterns
        for line in lines[:5]:  # Check first few lines
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['developer', 'engineer', 'analyst', 'manager', 'intern', 'specialist']):
                title = line
                break
        
        # Look for company patterns
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['at ', 'company', 'inc', 'ltd', 'corp']):
                company = line
                break
                
        if not title:
            title = f"Job Opportunity - {datetime.now().strftime('%Y%m%d')}"
            
        return {
            'title': title.strip(),
            'company': company.strip(),
            'description': description.strip(),
            'requirements': self.extract_requirements(description),
            'location': self.extract_location(description)
        }
    
    def extract_requirements(self, text):
        """Extract job requirements from text"""
        requirements = []
        lines = text.lower().split('\n')
        
        # Look for requirement sections
        collecting = False
        for line in lines:
            line = line.strip()
            
            if any(keyword in line for keyword in ['requirements', 'skills', 'experience', 'qualifications', 'must have']):
                collecting = True
                continue
                
            if collecting and line:
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    requirements.append(line[1:].strip())
                elif ':' in line and len(line) < 100:
                    requirements.append(line)
                elif len(requirements) > 10:  # Stop if too many
                    break
                    
        return requirements[:10]  # Limit requirements
    
    def extract_location(self, text):
        """Extract location from text"""
        location_patterns = [
            r'location[:\s]+([^.\n]+)',
            r'based in ([^.\n]+)',
            r'office in ([^.\n]+)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*[A-Z]{2}',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
                
        return "Remote/Not Specified"
    
    def get_mock_jobs(self):
        """Return mock job data for demonstration"""
        return [
            {
                'title': 'Senior Python Developer',
                'company': 'Tech Solutions Inc',
                'description': 'We are seeking a skilled Python developer with experience in Django, Flask, and cloud technologies.',
                'requirements': ['Python', 'Django', 'Flask', 'AWS', 'SQL', 'Git'],
                'location': 'San Francisco, CA',
                'source_profile': 'Mock Data',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'title': 'Full Stack Developer',
                'company': 'Innovation Labs',
                'description': 'Looking for a full stack developer with React, Node.js, and MongoDB experience.',
                'requirements': ['React', 'Node.js', 'JavaScript', 'MongoDB', 'Express', 'CSS'],
                'location': 'New York, NY',
                'source_profile': 'Mock Data',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'title': 'Data Scientist',
                'company': 'DataFlow Corp',
                'description': 'Seeking data scientist with machine learning and Python experience.',
                'requirements': ['Python', 'Machine Learning', 'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow'],
                'location': 'Austin, TX',
                'source_profile': 'Mock Data',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'title': 'DevOps Engineer',
                'company': 'Cloud Systems',
                'description': 'DevOps engineer needed for AWS infrastructure and CI/CD implementation.',
                'requirements': ['AWS', 'Docker', 'Kubernetes', 'Jenkins', 'Terraform', 'Linux'],
                'location': 'Seattle, WA',
                'source_profile': 'Mock Data',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'title': 'Frontend Developer',
                'company': 'UI/UX Studios',
                'description': 'Frontend developer with modern JavaScript frameworks experience.',
                'requirements': ['React', 'Vue.js', 'JavaScript', 'TypeScript', 'CSS', 'HTML'],
                'location': 'Los Angeles, CA',
                'source_profile': 'Mock Data',
                'scraped_at': datetime.now().isoformat()
            }
        ]

class JobMatcher:
    def __init__(self):
        """Initialize the job matcher"""
        pass
        
    def calculate_advanced_match_score(self, resume_skills, job_requirements, job_description=""):
        """Calculate advanced match score using multiple algorithms"""
        
        if not resume_skills:
            resume_skills = []
        if not job_requirements:
            job_requirements = []
            
        # Convert to lowercase for matching
        resume_skills_lower = [skill.lower().strip() for skill in resume_skills]
        job_req_lower = [req.lower().strip() for req in job_requirements]
        
        # 1. Exact matching score
        exact_matches = set(resume_skills_lower) & set(job_req_lower)
        exact_score = (len(exact_matches) / len(job_req_lower)) * 100 if job_req_lower else 0
        
        # 2. Fuzzy matching for similar skills
        fuzzy_matches = 0
        fuzzy_matched_skills = []
        
        for job_req in job_req_lower:
            best_match_score = 0
            best_match_skill = ""
            
            for resume_skill in resume_skills_lower:
                similarity = fuzz.ratio(job_req, resume_skill)
                if similarity > best_match_score:
                    best_match_score = similarity
                    best_match_skill = resume_skill
                    
            if best_match_score >= 80:  # 80% similarity threshold
                fuzzy_matches += 1
                fuzzy_matched_skills.append(best_match_skill)
        
        fuzzy_score = (fuzzy_matches / len(job_req_lower)) * 100 if job_req_lower else 0
        
        # 3. Semantic similarity using simple word overlap (without sklearn for now)
        semantic_score = 0
        if job_description and resume_skills:
            try:
                # Simple word overlap scoring
                job_words = set(job_description.lower().split())
                resume_words = set(' '.join(resume_skills).lower().split())
                common_words = job_words.intersection(resume_words)
                if len(job_words) > 0:
                    semantic_score = (len(common_words) / len(job_words)) * 100
            except:
                semantic_score = 0
        
        # Combined score (weighted average)
        combined_score = (exact_score * 0.5) + (fuzzy_score * 0.3) + (semantic_score * 0.2)
        
        # Find missing skills
        all_matched = set(exact_matches) | set(fuzzy_matched_skills)
        missing_skills = [skill for skill in job_requirements if skill.lower() not in all_matched]
        matched_skills = [skill for skill in resume_skills if skill.lower() in all_matched]
        
        return {
            'total_score': round(combined_score, 2),
            'exact_score': round(exact_score, 2),
            'fuzzy_score': round(fuzzy_score, 2),
            'semantic_score': round(semantic_score, 2),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'total_required': len(job_requirements),
            'total_matched': len(all_matched)
        }
    
    def rank_jobs(self, resume_skills, jobs):
        """Rank jobs based on match score"""
        ranked_jobs = []
        
        for job in jobs:
            # Extract skills from job requirements and description
            job_skills = job.get('requirements', [])
            if isinstance(job_skills, str):
                job_skills = [job_skills]
                
            job_description = job.get('description', '')
            
            # Calculate match score
            match_result = self.calculate_advanced_match_score(
                resume_skills, job_skills, job_description
            )
            
            # Add match info to job
            job_with_score = job.copy()
            job_with_score.update({
                'match_score': match_result['total_score'],
                'exact_match_score': match_result['exact_score'],
                'fuzzy_match_score': match_result['fuzzy_score'],
                'semantic_match_score': match_result['semantic_score'],
                'matched_skills': match_result['matched_skills'],
                'missing_skills': match_result['missing_skills'],
                'total_required_skills': match_result['total_required'],
                'total_matched_skills': match_result['total_matched']
            })
            
            ranked_jobs.append(job_with_score)
        
        # Sort by match score (descending)
        ranked_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        
        return ranked_jobs[:10]  # Return top 10

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""

def extract_text_from_file(file_path):
    """Extract text from uploaded file based on extension"""
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.lower().endswith('.txt'):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading TXT: {e}")
            return ""
    return ""

def extract_skills_and_keywords(text):
    """Extract ONLY technical skills and keywords from text"""
    
    # TECHNICAL SKILLS ONLY - excluding soft skills and business skills
    technical_skills = [
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'csharp', 'php', 'ruby', 'go', 'rust',
        'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'jsx', 'tsx', 'perl',
        'dart', 'julia', 'erlang', 'haskell', 'assembly', 'vb.net', 'objective-c',
        
        # Frameworks and Libraries
        'react', 'angular', 'vue', 'nodejs', 'node.js', 'express', 'django', 'flask', 'spring', 'laravel',
        'bootstrap', 'tailwind', 'jquery', 'redux', 'vuex', 'tensorflow', 'pytorch', 'keras',
        'pandas', 'numpy', 'matplotlib', 'scikit-learn', 'sklearn', 'opencv', 'fastapi', 'nest',
        'nextjs', 'next.js', 'nuxt', 'ember', 'backbone', 'meteor', 'gatsby', 'svelte',
        'spring boot', 'hibernate', 'struts', 'asp.net', '.net', 'dotnet', 'mvc', 'wpf',
        
        # Databases
        'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'oracle',
        'sqlite', 'dynamodb', 'firebase', 'supabase', 'mariadb', 'neo4j', 'influxdb', 'couchdb',
        'sql server', 'mssql', 'nosql', 'graphql',
        
        # Cloud and DevOps
        'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github',
        'terraform', 'ansible', 'vagrant', 'chef', 'puppet', 'nginx', 'apache', 'linux',
        'ubuntu', 'centos', 'debian', 'bash', 'powershell', 'ci/cd', 'devops', 'microservices',
        'serverless', 'lambda', 'cloudformation', 'helm', 'istio', 'prometheus', 'grafana',
        
        # Data Science and AI
        'machine learning', 'deep learning', 'artificial intelligence', 'data science',
        'data analysis', 'data analytics', 'big data', 'hadoop', 'spark', 'kafka', 'tableau', 'power bi',
        'excel', 'statistics', 'regression', 'classification', 'clustering', 'nlp',
        'computer vision', 'neural networks', 'ai', 'ml', 'data mining', 'etl',
        'jupyter', 'anaconda', 'r studio', 'sas', 'spss',
        
        # Mobile Development
        'ios', 'android', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova',
        'mobile development', 'app development', 'swift ui', 'kotlin multiplatform',
        
        # Testing and Quality Assurance
        'testing', 'unit testing', 'integration testing', 'automation testing', 'selenium', 'jest', 'pytest',
        'junit', 'mocha', 'cypress', 'testng', 'cucumber', 'postman', 'qa', 'quality assurance',
        'tdd', 'bdd', 'test driven development',
        
        # Version Control and Development Tools
        'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial', 'version control',
        'jira', 'confluence', 'trello',
        
        # Security (Technical)
        'cybersecurity', 'information security', 'penetration testing', 'ethical hacking',
        'encryption', 'ssl', 'oauth', 'jwt', 'authentication', 'authorization',
        
        # Web Development
        'web development', 'frontend', 'backend', 'full stack', 'rest api', 'api development',
        'soap', 'json', 'xml', 'ajax', 'websockets', 'graphql', 'grpc',
        
        # Design and Development Tools (Technical)
        'figma', 'sketch', 'adobe xd', 'photoshop', 'illustrator', 'wireframing', 'prototyping',
        
        # Development Methodologies (Technical)
        'agile', 'scrum', 'kanban', 'waterfall', 'agile methodologies', 'sprint planning',
        
        # Operating Systems and Servers
        'windows', 'macos', 'unix', 'freebsd', 'windows server', 'iis',
        
        # Networking and Infrastructure
        'tcp/ip', 'http', 'https', 'dns', 'load balancing', 'cdn', 'vpc', 'vpn'
    ]
    
    # Convert text to lowercase for matching
    text_lower = text.lower()
    
    # Extract only predefined skills found in the text
    found_skills = []
    
    # Check for exact skill matches with better precision
    # Sort by length (longest first) to match compound skills first
    sorted_skills = sorted(technical_skills, key=len, reverse=True)
    
    for skill in sorted_skills:
        skill_lower = skill.lower()
        import re
        
        # Use strict word boundary matching
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        
        if re.search(pattern, text_lower):
            # Additional validation for common false positives
            if skill_lower in ['mongodb', 'mysql', 'postgresql', 'oracle', 'redis', 'cassandra']:
                # Be extra strict for database names - check for explicit mentions
                db_patterns = [
                    r'\b' + re.escape(skill_lower) + r'(?:\s+database|\s+db|\s*,|\s*\.|\s*;|\s*\n|\s*$)',
                    r'(?:database|db|nosql|sql).*?' + re.escape(skill_lower),
                    r'\b' + re.escape(skill_lower) + r'\s+(?:experience|skills?|knowledge|proficiency)'
                ]
                if any(re.search(pattern, text_lower) for pattern in db_patterns):
                    found_skills.append(skill)
            else:
                found_skills.append(skill)
    
    # Remove duplicates and return
    return list(set(found_skills))

def calculate_match_score(resume_skills, job_skills):
    """Calculate match percentage between resume and job description"""
    
    # Ensure we have skills from both sources
    if not resume_skills:
        resume_skills = []
    if not job_skills:
        job_skills = []
    
    # Convert to sets for intersection (case insensitive)
    resume_set = set(skill.lower().strip() for skill in resume_skills if skill.strip())
    job_set = set(skill.lower().strip() for skill in job_skills if skill.strip())
    
    # Calculate matches
    matches = resume_set.intersection(job_set)
    match_count = len(matches)
    total_required = len(job_set)
    
    # Handle edge cases
    if total_required == 0:
        return {
            'score': 0,
            'matched_skills': [],
            'missing_skills': [],
            'additional_skills': list(resume_set),
            'total_required': 0,
            'total_matched': 0
        }
    
    # Calculate percentage
    score = (match_count / total_required) * 100
    
    return {
        'score': round(score, 2),
        'matched_skills': [skill for skill in resume_skills if skill.lower() in matches],
        'missing_skills': [skill for skill in job_skills if skill.lower() in (job_set - resume_set)],
        'additional_skills': [skill for skill in resume_skills if skill.lower() in (resume_set - job_set)],
        'total_required': total_required,
        'total_matched': match_count
    }

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and job description processing"""
    
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file uploaded'}), 400
    
    file = request.files['resume']
    job_description = request.form.get('job_description', '')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not job_description.strip():
        return jsonify({'error': 'Job description is required'}), 400
    
    if file and allowed_file(file.filename):
        # Save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Extract text from resume
            resume_text = extract_text_from_file(file_path)
            
            if not resume_text.strip():
                return jsonify({'error': 'Could not extract text from resume'}), 400
            
            # Extract skills from resume and job description
            resume_skills = extract_skills_and_keywords(resume_text)
            job_skills = extract_skills_and_keywords(job_description)
            
            # Debug: Print extracted skills
            print(f"DEBUG - Resume skills found: {resume_skills}")
            print(f"DEBUG - Job skills found: {job_skills}")
            
            # Calculate match score
            match_result = calculate_match_score(resume_skills, job_skills)
            
            # Clean up uploaded file
            os.remove(file_path)
            
            # Return results with all skills info for preview
            return jsonify({
                'success': True,
                'filename': filename,
                'match_score': match_result['score'],
                'matched_skills': match_result['matched_skills'],
                'missing_skills': match_result['missing_skills'],
                'additional_skills': match_result['additional_skills'][:10],  # Limit to avoid clutter
                'total_required': match_result['total_required'],
                'total_matched': match_result['total_matched'],
                'resume_preview': resume_text[:500] + '...' if len(resume_text) > 500 else resume_text,
                'debug_info': {
                    'resume_skills_count': len(resume_skills),
                    'job_skills_count': len(job_skills),
                    'resume_skills_full': resume_skills,
                    'job_skills_full': job_skills,
                    'resume_skills_sample': resume_skills[:5],
                    'job_skills_sample': job_skills[:5]
                }
            })
            
        except Exception as e:
            # Clean up file on error
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type. Please upload PDF, DOCX, or TXT files.'}), 400

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/analyze-jobs', methods=['POST'])
def analyze_jobs():
    """Analyze LinkedIn job postings and match with resume"""
    
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file uploaded'}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Extract text from resume
            resume_text = extract_text_from_file(file_path)
            
            if not resume_text.strip():
                return jsonify({'error': 'Could not extract text from resume'}), 400
            
            # Extract skills from resume
            resume_skills = extract_skills_and_keywords(resume_text)
            
            print(f"DEBUG - Resume skills found: {resume_skills}")
            
            # Scrape LinkedIn job postings
            scraper = LinkedInJobScraper()
            jobs = scraper.scrape_linkedin_posts(TRUSTED_LINKEDIN_PROFILES)
            
            print(f"DEBUG - Found {len(jobs)} jobs")
            
            # Match and rank jobs
            matcher = JobMatcher()
            ranked_jobs = matcher.rank_jobs(resume_skills, jobs)
            
            # Clean up uploaded file
            os.remove(file_path)
            
            # Return results
            return jsonify({
                'success': True,
                'filename': filename,
                'resume_skills': resume_skills[:10],  # Show first 10 skills
                'total_resume_skills': len(resume_skills),
                'total_jobs_found': len(jobs),
                'top_matched_jobs': ranked_jobs,
                'resume_preview': resume_text[:300] + '...' if len(resume_text) > 300 else resume_text
            })
            
        except Exception as e:
            # Clean up file on error
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': f'Error processing request: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type. Please upload PDF, DOCX, or TXT files.'}), 400

@app.route('/get-sample-jobs')
def get_sample_jobs():
    """Get sample job postings for testing"""
    scraper = LinkedInJobScraper()
    sample_jobs = scraper.get_mock_jobs()
    
    return jsonify({
        'success': True,
        'jobs': sample_jobs,
        'total_jobs': len(sample_jobs)
    })

@app.route('/upload-multiple', methods=['POST'])
def upload_multiple_resumes():
    """Handle multiple resume uploads and rank candidates by match score"""
    
    # Check if files are uploaded
    if 'resumes' not in request.files:
        return jsonify({'error': 'No resume files uploaded'}), 400
    
    files = request.files.getlist('resumes')
    job_description = request.form.get('job_description', '')
    
    if not files or len(files) == 0:
        return jsonify({'error': 'No files selected'}), 400
    
    if not job_description.strip():
        return jsonify({'error': 'Job description is required'}), 400
    
    # Extract skills from job description once
    job_skills = extract_skills_and_keywords(job_description)
    
    if not job_skills:
        return jsonify({'error': 'No technical skills found in job description'}), 400
    
    candidates = []
    errors = []
    
    # Process each resume
    for file in files:
        if file.filename == '':
            continue
        
        if not allowed_file(file.filename):
            errors.append(f'{file.filename}: Invalid file type')
            continue
        
        try:
            # Save the file temporarily
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Extract text from resume
            resume_text = extract_text_from_file(file_path)
            
            if not resume_text.strip():
                errors.append(f'{filename}: Could not extract text')
                os.remove(file_path)
                continue
            
            # Extract skills from resume
            resume_skills = extract_skills_and_keywords(resume_text)
            
            # Calculate match score using advanced matching
            matcher = JobMatcher()
            match_result = matcher.calculate_advanced_match_score(
                resume_skills, job_skills, job_description
            )
            
            # Extract candidate name from resume (simple extraction)
            candidate_name = extract_candidate_name(resume_text, filename)
            
            # Store candidate data
            candidate_data = {
                'filename': filename,
                'candidate_name': candidate_name,
                'match_score': match_result['total_score'],
                'exact_match_score': match_result['exact_score'],
                'fuzzy_match_score': match_result['fuzzy_score'],
                'semantic_match_score': match_result['semantic_score'],
                'matched_skills': match_result['matched_skills'],
                'missing_skills': match_result['missing_skills'],
                'total_required': match_result['total_required'],
                'total_matched': match_result['total_matched'],
                'all_resume_skills': resume_skills[:15],  # Limit for display
                'resume_preview': resume_text[:300] + '...' if len(resume_text) > 300 else resume_text
            }
            
            candidates.append(candidate_data)
            
            # Clean up the file
            os.remove(file_path)
            
        except Exception as e:
            errors.append(f'{file.filename}: {str(e)}')
            if os.path.exists(file_path):
                os.remove(file_path)
            continue
    
    if not candidates:
        return jsonify({
            'error': 'No valid resumes could be processed',
            'errors': errors
        }), 400
    
    # Sort candidates by match score (descending)
    candidates.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Return results
    return jsonify({
        'success': True,
        'total_processed': len(candidates),
        'job_skills': job_skills,
        'candidates': candidates,
        'errors': errors if errors else None
    })

def extract_candidate_name(resume_text, filename):
    """Extract candidate name from resume text"""
    lines = resume_text.split('\n')
    
    # Try to find name in first few lines
    for line in lines[:10]:
        line = line.strip()
        
        # Skip empty lines and common headers
        if not line or len(line) < 3 or len(line) > 50:
            continue
        
        # Skip lines with common resume headers
        skip_keywords = ['resume', 'cv', 'curriculum vitae', 'profile', 'summary', 
                        'objective', 'experience', 'education', 'skills', 'contact',
                        'phone', 'email', 'address', '@']
        
        if any(keyword in line.lower() for keyword in skip_keywords):
            continue
        
        # Check if line looks like a name (2-4 words, mostly alphabetic)
        words = line.split()
        if 2 <= len(words) <= 4:
            if all(word.replace('-', '').replace("'", '').isalpha() for word in words):
                return line
    
    # Fallback to filename without extension
    return filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)