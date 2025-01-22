from networksercurity.logging import logger
from networksercurity.Exception import custom_expection
import sys

def chech():
    try:
        logger.info("start")
        a=1/0
        print("this is will be printed")
        
    except Exception as e:
        raise custom_expection(e,sys)    
    
    

if __name__ =="__main__":
    chech()    