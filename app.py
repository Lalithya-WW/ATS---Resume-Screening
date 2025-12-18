from flask import Flask, request, render_template, jsonify, redirect, url_for
import os
import re
from werkzeug.utils import secure_filename
import PyPDF2
import docx
from collections import Counter

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)