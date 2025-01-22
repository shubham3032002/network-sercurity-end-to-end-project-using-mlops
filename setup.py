from setuptools import find_packages,setup

from typing import List

requirement_lst:List[str]=[]
def get_requirements()->List[str]:
    try:
       with open('requirements.txt','r') as f :
          lines=f.readlines()
          for line in lines:
              requirement=line.strip()
              if requirement and requirement != '-e .':
               requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirements.txt not found")    
        
    return requirement_lst     

setup(
    name="NetworkSercurity",
    version="0.0.1",
    author="shubham",
    author_email="shubhammokal30@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()
)
     
            
    