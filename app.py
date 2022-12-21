import os
import uuid
import flask
import urllib
import base64
from PIL import Image
from flask import Flask, request
from tensorflow.keras.models import load_model
from flask import Flask, make_response , render_template  , request , send_file
from tensorflow.keras.preprocessing.image import load_img , img_to_array

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = load_model('Animal1.hdf5')


ALLOWED_EXT = set(['jpg' , 'jpeg' , 'png' , 'jfif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT

classes = [ 'CAMEL',
 'CAT',
 'CATTLE',
 'CHICKEN',
 'CROW',
 'DEER',
 'DOG',
 'EAGLE',
 'ELEPHANT',
 'FOX',
 'GOAT',
 'HORSE',
 'LEOPARD',
 'LION',
 'MONKEY',
 'PARROT',
 'PEACOCK',
 'PIG',
 'RABBIT',
 'SHEEP',
 'SPARROW',
 'TIGER',]


def predict(filename , model):
    img = load_img(filename , target_size = (128 , 128))
    img = img_to_array(img)
    img = img.reshape(1 , 128 ,128 ,3)

    img = img.astype('float32')
    img = img/255.0
    result = model.predict(img)

    dict_result = {}
    for i in range(22):
        dict_result[result[0][i]] = classes[i]

    res = result[0]
    res.sort()
    res = res[::-1]
    prob = res[:3]
    
    prob_result = []
    class_result = []
 
    for i in range(3):
        prob_result.append((prob[i]*100).round(2))
        class_result.append(dict_result[prob[i]])
    
    if(prob_result[0]>70):
        status = "Detected"
    else:
        status = "Please enter a valid image of animal"

    return class_result , prob_result, status


@app.route('/')
def home():
        return render_template("index.html")

@app.route('/success' , methods = ['GET' , 'POST'])
def success():
    error = ''
    language = request.args.get('language')
    target_img=os.path.join('static/images')
    if request.method == 'POST':
        if(request.form):
            link = request.form.get('link')
            try :
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                # filename = '/new_image.png'
                filename= unique_filename+".jpg"
                img_path = os.path.join(target_img , filename)
                output = open(img_path , "wb")
                output.write(resource.read())
                output.close()
                img = filename

                class_result , prob_result, status = predict(img_path , model)

                predictions = {
                    
                      "class1":class_result[0],
                        "class2":class_result[1],
                        "class3":class_result[2],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
                        "status":status,
                    }
                pred = {
                    "status2":status
                    }
                
            except Exception as e : 
                print(str(e))
                error = 'This image from this site is not accesible or inappropriate input'

            if(len(error) == 0):
                return  render_template('success.html' , img  = img , predictions = predictions)
                # return make_response(pred, 200)
            else:
                return render_template('index.html' , error = error) 

            
        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(target_img , file.filename))
                img_path = os.path.join(target_img , file.filename)
                img = file.filename

                class_result , prob_result, status = predict(img_path , model)

                predictions = {
                      "class1":class_result[0],
                        "class2":class_result[1],
                        "class3":class_result[2],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
                        "status":status,
                }
                pred = {
                    "status2":status
                }

            else:
                error = "Please upload images of jpg , jpeg and png extension only"

            # headers = {"content -Type":"application/json"}
            if(len(error) == 0):
                return  render_template('success.html' , img  = img , predictions = predictions)
                # return make_response(pred, 200)?
            else:
                return render_template('index.html' , error = error)

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0")
