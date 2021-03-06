from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from twilio.twiml.messaging_response import MessagingResponse
from GoldStandard.gold_standard import GoldStandard
import numpy as np

app = Flask(__name__)
app.secret_key= 'supbros'
bootstrap = Bootstrap(app)
#csrf = CSRFProtect(app)
austd = GoldStandard()

#class UrlInput(FlaskForm):
	#url = StringField('URL', validators=[Required()])
	#submit = SubmitField('Submit')


@app.route('/sms', methods=['POST', 'GET'])
def sms_reply():
	number = request.form['From']
	msg = request.form['Body']

	#predict
	prediction = austd.predict_fakeness(msg.strip())

	resp = MessagingResponse()
	resp.message('Welcome to Austd! Retrieving the gold standard for {}'.format(msg))

	if prediction == 'not found':
		resp.message('Article not found :(')

	else:
		fake_or_real = prediction['prediction']
		if 'list' in str(type(fake_or_real)):
			fake_or_real = fake_or_real[0]
		if fake_or_real == 1.0:
			fake_or_real = 'too biased to be trusted'
		else:
			fake_or_real = 'safe'

		probability = prediction['probability'][0]

		if fake_or_real == 'safe':
			probability = np.min(probability)

		else:
			probability = np.max(probability)

		#resp.message("data info: {}".format(list(set(austd.data.label))))

		resp.message('This article seems like it\'s {}; there\'s a {}% chance that you shouldn\'t trust it.'
		.format(fake_or_real,str(int(probability * 100))))

		if prediction['tagged_bias'] is not None:
			resp.message('According to OpenSources, this website is tagged as \"{}\".'.format(prediction['tagged_bias']))

	return str(resp)


#@app.route('/')
#def index():
	#form = UrlInput()
	#if form.validate_on_submit():
		#pass
	#return render_template('index.html', form=form)




if __name__ == "__main__":
	app.run(debug=True)
