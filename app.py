from flask import Flask,render_template,request
import app
import Features_Extraction
import rf_model
import pickle
import pandas as pd
app=Flask(__name__)
@app.route('/')
def home():
	return render_template('home.html')

@app.route('/getURL',methods=['GET','POST'])
def getURL():
	if(request.method=='POST'):
		url=request.form['url']
		data,rank=Features_Extraction.generate_dataset(url)
		rfmodel=pickle.load(open('rfmodel.pkl','rb'))
		d=dict()
		c=0
		for i in rf_model.x_train.columns:
			d[i]=data[c]
			c+=1
		dff=pd.DataFrame(columns=rf_model.x_train.columns)
		dff=dff.append(d,ignore_index=True)
		
		prediction=rfmodel.predict(dff)
		
		
		if(prediction==-1):
			d_entry=open('blacklist.txt','a')
			d_entry.write("\n")
			d_entry.write(url)
			d_entry.close()
			value="Phishing Website"
			return render_template("home.html",error=value)
			
		elif(rank==-1):
			d_entry=open('blacklist.txt','a')
			d_entry.write("\n")
			d_entry.write(url)
			d_entry.close()
			value="Phishing Website"
			return render_template("home.html",error=value)
		else:
			value=url+""+" is not Phishing Website!!"
			return render_template("home.html",error=value)
@app.route('/getAbout')
def getAbout():
	return render_template('about.html')
@app.route('/getAbout1')
def getAbout1():
	return render_template('about1.html')

if __name__=="__main__":
	app.run(debug=True)
	