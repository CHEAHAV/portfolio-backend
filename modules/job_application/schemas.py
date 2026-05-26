from pydantic import BaseModel

class JobApplicationSchema(BaseModel):
    id           : str
    parent_id    : str
    full_name    : str
    email        : str 
    phone_number : str 
    gender       : str 
    portfolio    : str 
    linkedin_url : str | None = None
    github_url   : str | None = None
    other_url    : str | None = None
    about_you    : str | None = None
    upload_cv    : str 
    status       : str 