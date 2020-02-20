import requests
from base64 import b64encode
import pickle
from azure.storage.blob import BlockBlobService
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import PyPDF2

app = Flask(__name__)
app.secret_key = 'mkljlnhkbjgvjfcdxsrzeawresdtfyguoiojkl;kmnjhbgytfre5643w52q4awserdtfgyuhijnBHGVYDRESW#@W$%^&*IOKMNBVCGFDRER%$&^&T*(UI'
ALLOWED_EXTENSIONS = set(['pdf'])
blob_service = BlockBlobService('snpstorage', '0WkI7xi5dH2hvBFx6HlMDIMDEKPEsXBQtowHyhHVFUjqZL+fazAYLN7ZD3eFzPry1hbkpPVQmRCDITNEUQ2zzA==')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            blob_service.create_blob_from_bytes(container_name='snpstore', blob_name=f'{filename}', blob=file.read())
            azure_url = f"https://pdfcognitiveservices.azurewebsites.net/api/PDFTrigger?name={filename}"
            r = requests.post(azure_url)
            x = pickle.loads(r.content)
            img = []
            img_text = []
            t = []
            text=[]
            for i in range(len(x[0][2])):
                img_text.append([b64encode(x[0][3][i][0]).decode(), i, x[0][2][i][0],x[0][4][0][0][i][1],', '.join(x[0][4][0][2][i][1]),', '.join(x[0][4][0][1][i][1])])
            for i in range(len(x[0][3])):
                img.append([i,b64encode(x[0][3][i][0]).decode(),', '.join(x[0][6][i][0])])
            flash('File successfully uploaded')
            if len(x[0][0]) > 0:
                for i in range(len(x[0][0])):
                    t.append(x[0][0][i][1])
            for i in range(len(x[0][5][0][1])):
                text.append([i,x[0][1][i],x[0][5][0][i][0][1],', '.join(x[0][5][0][2][i][1]),', '.join(x[0][5][0][1][i][1])])

            print(text[2][1][1])
            print('x')
            print('')

            return render_template('table.html',img_text=img_text,x=len(x[0][2]),z=len(x[0][3]),img_list=img,hyp=t,p=len(x[0][0]),text=text,j=len(x[0][5][0][1]))

        else:
            flash('Allowed file types are  pdf')
            return redirect(request.url)


if __name__ == "__main__":
    app.run()