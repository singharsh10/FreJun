from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///call_records.db'
db = SQLAlchemy(app)

app.app_context().push()


class CallRecord(db.Model):
    """
    Call record database model. It stores from_number, to_number and
    start_time (which is the current time) in UTC timezone.
    id is db auto generated integer id which is also the primary key.
    """
    id = db.Column(db.Integer, primary_key=True)
    from_number = db.Column(db.String(20), nullable=False)
    to_number = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"CallRecord('{self.from_number}', '{self.to_number}', '{self.start_time}')"


db.create_all()


@app.route('/initiate-call', methods=['POST'])
def initiate_call():
    """
    POST endpoint which saves call records in the database.
    from_number and to_number in json body. It saves from_number,
    to_number and start_time(which is the current time) in UTC timezone.
    :return: {success=True} if record was inserted successfully,
             {success=False, error=errorMsg} otherwise.
    """
    data = request.get_json()
    from_number = data.get('from_number')
    to_number = data.get('to_number')
    if not from_number or not to_number:
        return jsonify({'success': False,
                        'error': 'Both from_number and to_number are required!'})

    call_detail = CallRecord(from_number=from_number, to_number=to_number)
    db.session.add(call_detail)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/call-report', methods=['GET'])
def call_report():
    """
    GET endpoint to fetch call records.
    phone is a mandatory query parameter.
    page query param specifies the page number to fetch.
    per_page specifies the maximum number of records which can be present in a single page.
    :return: call records as per the query parameters provided in the GET
             request. Please note that the response is paginated.
    """
    phone = request.args.get('phone')
    if not phone:
        return jsonify({'success': False, 'error': 'phone parameter is required'})
    try:
        page = int(request.args.get('page'))
    except:
        return jsonify({'success': False, 'error': 'Invalid page number'})

    try:
        per_page = int(request.args.get('per_page'))
    except:
        return jsonify({'success': False, 'error': 'Invalid per_page'})

    records = CallRecord.query.filter(
        (CallRecord.from_number == phone) | (CallRecord.to_number == phone)
    ).paginate(page=page, per_page=per_page, error_out=False)

    print(records.items)

    calls = []
    for record in records.items:
        calls.append({
            'id': record.id,
            'from_number': record.from_number,
            'to_number': record.to_number,
            'start_time': record.start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')
        })

    return jsonify({'success': True,
                    'data': calls,
                    'page': records.page,
                    'per_page': records.per_page})


if __name__ == '__main__':
    app.run(debug=True)