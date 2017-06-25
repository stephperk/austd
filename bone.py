from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from twilio.twiml.messaging_response import MessagingResponse 
from secret import secret_key

app = Flask(__name__)
app.secret_key= secret_key['flask']
bootstrap = Bootstrap(app)
csrf = CSRFProtect(app)


class UrlInput(FlaskForm):
	url = StringField('URL', validators=[Required()])
	submit = SubmitField('Submit')


@app.route('/sms', methods=['POST', 'GET'])
def sms_reply():
	number = request.form['From']
	msg = request.form['Body']

	resp = MessagingResponse()
	resp.message('Welcome to Austd! Retrieving the gold standard for {}'.format(msg))
	return str(resp)


@app.route('/')
def index():
	form = UrlInput()
	if form.validate_on_submit():
		pass
	return render_template('index.html', form=form)




if __name__ == "__main__":
	app.run(debug=True)