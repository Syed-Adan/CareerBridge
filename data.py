"""
data.py — Sample dataset of courses and internships.

Each listing is a plain dict with these keys:
  id          : unique string ID
  type        : "Course" or "Internship"
  title       : display name
  provider    : organisation offering it
  duration    : human-readable length
  description : one-sentence summary
  domain      : broad category for filtering
  paid        : True / False
"""

LISTINGS = [
    # ── Courses ───────────────────────────────────────────────────────────────
    {
        "id":          "c01",
        "type":        "Course",
        "title":       "Python for Beginners",
        "provider":    "CodeAcademy",
        "duration":    "4 weeks",
        "description": "Learn Python fundamentals: variables, loops, functions, and file handling. No prior coding experience needed.",
        "domain":      "Programming",
        "paid":        False,
    },
    {
        "id":          "c02",
        "type":        "Course",
        "title":       "Machine Learning with scikit-learn",
        "provider":    "DataSchool",
        "duration":    "6 weeks",
        "description": "Hands-on ML: regression, classification, clustering, and model evaluation using Python and scikit-learn.",
        "domain":      "Data Science",
        "paid":        True,
    },
    {
        "id":          "c03",
        "type":        "Course",
        "title":       "Web Development with React",
        "provider":    "Udemy",
        "duration":    "8 weeks",
        "description": "Build modern, responsive web apps using React, hooks, state management, and REST API integration.",
        "domain":      "Web Development",
        "paid":        True,
    },
    {
        "id":          "c04",
        "type":        "Course",
        "title":       "UI/UX Design Fundamentals",
        "provider":    "DesignLab",
        "duration":    "5 weeks",
        "description": "Learn user research, wireframing, Figma prototyping, and build a portfolio-ready case study.",
        "domain":      "Design",
        "paid":        False,
    },
    {
        "id":          "c05",
        "type":        "Course",
        "title":       "Data Analysis with Pandas",
        "provider":    "DataSchool",
        "duration":    "3 weeks",
        "description": "Explore and visualise real datasets using Pandas and Matplotlib. Includes three mini-projects.",
        "domain":      "Data Science",
        "paid":        False,
    },
    {
        "id":          "c06",
        "type":        "Course",
        "title":       "Deep Learning & Neural Networks",
        "provider":    "DeepAI Academy",
        "duration":    "12 weeks",
        "description": "Build CNNs, RNNs, and transformer models. Covers backpropagation, TensorFlow, and deployment basics.",
        "domain":      "AI / ML",
        "paid":        True,
    },
    {
        "id":          "c07",
        "type":        "Course",
        "title":       "Full Stack Django",
        "provider":    "RealPython",
        "duration":    "8 weeks",
        "description": "Build full-stack web apps with Django and PostgreSQL, then deploy with Docker.",
        "domain":      "Web Development",
        "paid":        True,
    },
    {
        "id":          "c08",
        "type":        "Course",
        "title":       "Music Production Basics",
        "provider":    "Berklee Online",
        "duration":    "10 weeks",
        "description": "Master DAWs, mixing, mastering, and sound design. Great for aspiring music producers.",
        "domain":      "Music",
        "paid":        True,
    },
    {
        "id":          "c09",
        "type":        "Course",
        "title":       "Cloud Computing with AWS",
        "provider":    "AWS Training",
        "duration":    "5 weeks",
        "description": "Understand EC2, S3, Lambda, and IAM. Prepares you for the AWS Cloud Practitioner exam.",
        "domain":      "Cloud / DevOps",
        "paid":        True,
    },
    {
        "id":          "c10",
        "type":        "Course",
        "title":       "Graphic Design with Adobe Suite",
        "provider":    "Coursera",
        "duration":    "6 weeks",
        "description": "Get started with Photoshop, Illustrator, and InDesign to create logos, posters, and brand identities.",
        "domain":      "Design",
        "paid":        False,
    },

    # ── Internships ───────────────────────────────────────────────────────────
    {
        "id":          "i01",
        "type":        "Internship",
        "title":       "Python Developer Intern",
        "provider":    "TechStart India",
        "duration":    "3 months",
        "description": "Work on backend Python scripts and automation tools at a fast-growing startup.",
        "domain":      "Programming",
        "paid":        True,
    },
    {
        "id":          "i02",
        "type":        "Internship",
        "title":       "Data Science Intern",
        "provider":    "AnalyticsHub",
        "duration":    "6 months",
        "description": "Analyse large datasets, build dashboards, and support the ML team with feature engineering.",
        "domain":      "Data Science",
        "paid":        True,
    },
    {
        "id":          "i03",
        "type":        "Internship",
        "title":       "Frontend Developer Intern",
        "provider":    "PixelCraft Studio",
        "duration":    "3 months",
        "description": "Design and build responsive UI components in React, working closely with the design team.",
        "domain":      "Web Development",
        "paid":        True,
    },
    {
        "id":          "i04",
        "type":        "Internship",
        "title":       "AI Research Intern",
        "provider":    "NeuralLab",
        "duration":    "6 months",
        "description": "Assist researchers in training NLP and vision models, run experiments, and document results.",
        "domain":      "AI / ML",
        "paid":        True,
    },
    {
        "id":          "i05",
        "type":        "Internship",
        "title":       "Graphic Design Intern",
        "provider":    "CreativeAtlas",
        "duration":    "2 months",
        "description": "Create social media graphics, brand assets, and marketing materials. Remote-friendly.",
        "domain":      "Design",
        "paid":        False,
    },
    {
        "id":          "i06",
        "type":        "Internship",
        "title":       "Music Content Curator Intern",
        "provider":    "StreamBeats",
        "duration":    "3 months",
        "description": "Curate playlists, write artist bios, and schedule content for a music streaming platform.",
        "domain":      "Music",
        "paid":        False,
    },
    {
        "id":          "i07",
        "type":        "Internship",
        "title":       "Cloud & DevOps Intern",
        "provider":    "InfraScale",
        "duration":    "4 months",
        "description": "Learn CI/CD pipelines, Docker containerisation, and AWS cloud deployment in a mentor-led programme.",
        "domain":      "Cloud / DevOps",
        "paid":        True,
    },
    {
        "id":          "i08",
        "type":        "Internship",
        "title":       "UX Research Intern",
        "provider":    "UserFirst Labs",
        "duration":    "3 months",
        "description": "Conduct user interviews, usability tests, and synthesise research insights for product teams.",
        "domain":      "Design",
        "paid":        True,
    },
]

# All unique domains — used to populate the filter dropdown
ALL_DOMAINS = sorted(set(item["domain"] for item in LISTINGS))