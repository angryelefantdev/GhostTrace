from fastapi import FastAPI, UploadFile, File,HTTPException
import mailbox
import tempfile
import os

app = FastAPI()
MAX_FILE_SIZE = 10 * 1024 * 1024  


buzzwords = {"email":1,"registration":3,"account":2,"verify":3,"welcome":1}


@app.post("/scan")
async def scan(file: UploadFile = File(...)):
    is_empty = True
    content = await file.read(MAX_FILE_SIZE + 1) 

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="...")

    emails = []
    grouped = {}
    accounts = []


    if len(content) > 0:
        is_empty = False

    
        temp_file = tempfile.NamedTemporaryFile(
        suffix=".mbox",
        delete=False
    )
    elif len(content) == 0:
        return {"message":"The file is empty."}

    try:
        temp_file.write(content)
        temp_file.close()

        aaa = mailbox.mbox(temp_file.name)
        try:
            for message in aaa:
                subject = (message["Subject"] or "").lower()
                sender = (message["From"] or "").strip("[]")
                
                
                domain = sender.split("@")[-1].lower()

                capitalize = domain.replace(".example","").capitalize()
                risk = 0
                for stuff in subject.split():
                    
                    if stuff in buzzwords:
                       
                        risk += buzzwords[stuff]
                    


                if risk >=2:
                    emails.append({"subject":subject,"sender": sender,"domain": domain,"service":capitalize,"risk":risk,"comment":"a risk for the account to be linked to this service"})
            

            for mail in emails:
                domainer = mail["domain"]
                if not domainer in grouped:
                    grouped[domainer] = []
                grouped[domainer].append({"subject":mail["subject"],"sender":mail["sender"],"risk":mail["risk"],"service":mail["service"]})
            count = 0
            for domain,mails in grouped.items():
                email_count = len(mails)
                highest_score = max(mail["risk"] for mail in mails)
                service_name = (mail["service"] for mail in mails)
                domain_name = domain
                
                accounts.append({"email_count":email_count,"domain_name":domain_name,"highest_score":highest_score,"service":service_name})
        except (OSError, ValueError) as error:
            raise HTTPException(
            status_code=400,
            detail="Could not process the uploaded mailbox."
            ) from error
        finally:
            aaa.close()
    finally:
        temp_file.close()
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)


    return {"filename": file.filename, "size": len(content),"is_empty": is_empty,"emails": emails,"grouped":grouped,"accounts":accounts}

